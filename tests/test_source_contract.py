"""Real SDK, fake outbound provider: source coverage is not live acceptance."""

import asyncio
import json
from pathlib import Path

import httpx
import pytest
from agent_connector_sdk.auth.static import api_key_auth

from artcraft_api.api import ApiClientSystem
from artcraft_api.openapi_runtime import CONTRACT

ROOT = Path(__file__).resolve().parents[1]


def response_for(action):
    if "models" in action:
        return {"success": True, "models": [], "providers": []}
    if action == "get_folder_handler":
        return {
            "success": True,
            "folder": {
                "token": "folder_fixture",
                "name": "Fixture",
                "owner_user_token": "user_fixture",
                "last_media_thumbnails": [],
                "has_star": False,
                "is_orphaned": False,
                "created_at": "2026-10-12T00:00:00Z",
                "updated_at": "2026-10-12T00:00:00Z",
            },
        }
    if "folders" in action:
        return {"success": True, "folders": [], "maybe_cursor": None}
    return {"success": True, "tags": [], "maybe_cursor": None}


@pytest.mark.parametrize("action", sorted(CONTRACT["operations"]))
def test_every_reviewed_operation_dispatches_exact_route(action, monkeypatch):
    operation = CONTRACT["operations"][action]
    arguments = {"action": action}
    expected_path = operation["path"]
    for parameter in operation["parameters"]:
        if parameter["in"] == "path":
            arguments.setdefault("path", {})[parameter["name"]] = "fixture_token"
            expected_path = expected_path.replace(
                "{" + parameter["name"] + "}", "fixture_token"
            )
    monkeypatch.setenv("ARTCRAFT_FIXTURE_SESSION", "fixture-signed-session")
    requires = bool(operation["security"])
    seen = []

    def respond(request):
        seen.append(request)
        assert request.method == "GET"
        assert request.url.path == expected_path
        if requires:
            assert request.headers["session"] == "fixture-signed-session"
            assert "authorization" not in request.headers
        else:
            assert "session" not in request.headers
        return httpx.Response(200, json=response_for(action))

    client = ApiClientSystem(
        "https://artcraft.example.invalid",
        api_key_auth("env://ARTCRAFT_FIXTURE_SESSION", header="session")
        if requires
        else httpx.Auth(),
        credential_scheme="signed_session" if requires else None,
        allow_writes=not operation["read_only"],
        transport=httpx.MockTransport(respond),
    )
    try:
        assert client.execute(operation["domain"], arguments)["data"] == response_for(
            action
        )
        assert len(seen) == 1
    finally:
        client.close()


@pytest.mark.parametrize(
    "action", [a for a, op in CONTRACT["operations"].items() if not op["read_only"]]
)
def test_cache_effects_are_blocked_by_default(action):
    calls = []
    client = ApiClientSystem(
        "https://artcraft.example.invalid",
        httpx.Auth(),
        transport=httpx.MockTransport(lambda r: calls.append(r)),
    )
    op = CONTRACT["operations"][action]
    args = {"action": action}
    for p in op["parameters"]:
        if p["in"] == "path":
            args.setdefault("path", {})[p["name"]] = "fixture_token"
    try:
        with pytest.raises(PermissionError, match="Writes require"):
            client.execute(op["domain"], args)
        assert not calls
    finally:
        client.close()


def test_unknown_actions_and_mutating_gets_are_not_admitted():
    assert len(CONTRACT["operations"]) == 8
    assert all("job_status" not in op["path"] for op in CONTRACT["operations"].values())
    assert "omni_gen_video_models_handler" not in CONTRACT["operations"]
    assert {op["method"] for op in CONTRACT["operations"].values()} == {"GET"}
    client = ApiClientSystem("https://artcraft.example.invalid", httpx.Auth())
    try:
        with pytest.raises(ValueError):
            client.execute("omni_gen", {"action": "omni_api_video_generate_handler"})
    finally:
        client.close()


def test_public_schema_is_not_misrepresented_as_pinned_or_live():
    provenance = json.loads((ROOT / "api-spec/source-provenance.json").read_text())
    assert len(provenance["struct_checks"]) == 24
    assert all(not op["live_verified"] for op in provenance["operations"])
    assert (
        len(provenance["source_schema_additions"]["FolderThumbnailVideoPreviews"]) == 2
    )
    assert CONTRACT["security_schemes"]["signed_session"]["name"] == "session"


def test_provider_filter_is_a_closed_enum():
    client = ApiClientSystem("https://artcraft.example.invalid", httpx.Auth())
    try:
        with pytest.raises(ValueError):
            client.execute(
                "omni_gen",
                {
                    "action": "omni_gen_image_models_handler",
                    "query": {"provider": "invented-provider"},
                },
            )
    finally:
        client.close()


def test_native_mcp_catalog_call_and_effect_annotations(monkeypatch):
    from agent_connector_sdk.http.client import create_http_client
    from fastmcp import Client

    from artcraft_api import auth, openapi_runtime
    from artcraft_api.mcp_server import build_server

    auth.close_client()
    monkeypatch.setattr(auth, "load_config", lambda: None)
    monkeypatch.setenv("ARTCRAFT_API_BASE_URL", "https://artcraft.example.invalid")
    monkeypatch.setenv("ARTCRAFT_API_TOKEN_REF", "")
    monkeypatch.setenv("ARTCRAFT_API_ALLOW_WRITES", "false")
    monkeypatch.setenv("ENABLE_DELEGATION", "false")
    calls = []

    def respond(request):
        calls.append(request)
        assert "session" not in request.headers
        return httpx.Response(200, json=response_for("omni_gen_audio_models_handler"))

    monkeypatch.setattr(
        openapi_runtime,
        "create_http_client",
        lambda options, **kwargs: create_http_client(
            options, transport=httpx.MockTransport(respond)
        ),
    )

    async def call():
        async with Client(
            build_server(command_args=["--transport", "stdio"])
        ) as client:
            tools = {tool.name: tool for tool in await client.list_tools()}
            assert set(tools) == {
                "folders_operations",
                "omni_gen_operations",
                "tags_operations",
            }
            assert tools["omni_gen_operations"].annotations.read_only_hint
            assert not tools["folders_operations"].annotations.read_only_hint
            assert not tools["tags_operations"].annotations.read_only_hint
            result = await client.call_tool(
                "omni_gen_operations", {"action": "omni_gen_audio_models_handler"}
            )
            assert result.structured_content["data"]["success"] is True

    try:
        asyncio.run(call())
        assert len(calls) == 1
    finally:
        auth.close_client()

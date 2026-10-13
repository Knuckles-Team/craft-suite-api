"""Real SDK, fake outbound provider: source coverage is not live acceptance."""

import asyncio
import copy
import json
from pathlib import Path

import httpx
import pytest
from agent_connector_sdk.auth.static import api_key_auth

from craft_suite_api.api import ApiClientSystem
from craft_suite_api.openapi_client import ClientPolicy
from craft_suite_api.openapi_runtime import CONTRACT

ROOT = Path(__file__).resolve().parents[1]


RESPONSE_FIXTURES = {
    "get_folder_handler": {
        "folder": {
            "created_at": "2026-10-12T00:00:00Z",
            "has_star": False,
            "is_orphaned": False,
            "last_media_thumbnails": [],
            "name": "Fixture",
            "owner_user_token": "user_fixture",
            "token": "folder_fixture",
            "updated_at": "2026-10-12T00:00:00Z",
        },
        "success": True,
    },
    "list_folders_handler": {
        "folders": [
            {
                "created_at": "2026-10-12T00:00:00Z",
                "has_star": False,
                "is_orphaned": False,
                "last_media_thumbnails": [],
                "name": "Fixture",
                "owner_user_token": "user_fixture",
                "token": "folder_fixture",
                "updated_at": "2026-10-12T00:00:00Z",
            }
        ],
        "maybe_cursor": "cursor_fixture",
        "success": True,
    },
    "list_media_file_tags_handler": {
        "success": True,
        "tags": [
            {
                "tag_token": "tag_fixture",
                "tag_value": "Fixture",
                "tag_value_lowercase": "fixture",
                "use_count": 2,
            }
        ],
    },
    "list_tags_handler": {
        "maybe_cursor": "cursor_fixture",
        "success": True,
        "tags": [
            {
                "tag_token": "tag_fixture",
                "tag_value": "Fixture",
                "tag_value_lowercase": "fixture",
                "use_count": 2,
            }
        ],
    },
    "omni_gen_audio_models_handler": {
        "models": [
            {
                "full_name": "Synthetic audio fixture",
                "model": "suno_music",
                "text_prompt_supported": True,
            }
        ],
        "providers": [],
        "success": True,
    },
    "omni_gen_image_models_handler": {"models": [], "providers": [], "success": True},
    "omni_gen_mesh_models_handler": {"models": [], "providers": [], "success": True},
    "omni_gen_splat_models_handler": {"models": [], "providers": [], "success": True},
}


def response_for(action):
    return copy.deepcopy(RESPONSE_FIXTURES[action])


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
    monkeypatch.setenv("CRAFT_SUITE_FIXTURE_SESSION", "fixture-signed-session")
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
        api_key_auth("env://CRAFT_SUITE_FIXTURE_SESSION", header="session")
        if requires
        else httpx.Auth(),
        credential_scheme="signed_session" if requires else None,
        policy=ClientPolicy(allow_writes=not operation["read_only"]),
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

    from craft_suite_api import auth, openapi_client
    from craft_suite_api.mcp_server import build_server

    auth.close_client()
    monkeypatch.setattr(auth, "load_config", lambda: None)
    monkeypatch.setenv("CRAFT_SUITE_API_BASE_URL", "https://artcraft.example.invalid")
    monkeypatch.setenv("CRAFT_SUITE_API_TOKEN_REF", "")
    monkeypatch.setenv("CRAFT_SUITE_API_ALLOW_WRITES", "false")
    monkeypatch.setenv("ENABLE_DELEGATION", "false")
    calls = []

    def respond(request):
        calls.append(request)
        assert "session" not in request.headers
        return httpx.Response(200, json=response_for("omni_gen_audio_models_handler"))

    monkeypatch.setattr(
        openapi_client,
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


def test_unscoped_ingestion_is_unavailable():
    import importlib.util

    assert importlib.util.find_spec("craft_suite_api.kg_ingest") is None
    assert importlib.util.find_spec("craft_suite_api.api.api_client_base") is None


@pytest.mark.parametrize("action", ["list_tags_handler", "list_folders_handler"])
@pytest.mark.parametrize("limit", [-1, 2**32])
def test_unsigned_request_bounds_reject_overflow_before_network(action, limit):
    calls = []
    operation = CONTRACT["operations"][action]
    client = ApiClientSystem(
        "https://artcraft.example.invalid",
        httpx.Auth(),
        policy=ClientPolicy(allow_writes=True),
        transport=httpx.MockTransport(lambda r: calls.append(r)),
    )
    try:
        with pytest.raises(ValueError):
            client.execute(
                operation["domain"], {"action": action, "query": {"limit": limit}}
            )
        assert not calls
    finally:
        client.close()


def test_request_struct_parity_and_u32_bounds():
    from scripts.generate_source_contract import _request_fields

    provenance = json.loads((ROOT / "api-spec/source-provenance.json").read_text())
    checked = [op for op in provenance["operations"] if op["request_checks"]]
    assert {op["action"] for op in checked} == {
        "list_tags_handler",
        "list_folders_handler",
    }
    for operation in checked:
        check = operation["request_checks"][0]
        source = (ROOT / "tests/fixtures/request_structs.rs").read_text()
        assert _request_fields(source, check["struct"]) == check["fields"]
        assert check["fields"]["limit"] == "Option<u32>"
        parameter = next(
            p
            for p in CONTRACT["operations"][operation["action"]]["parameters"]
            if p["name"] == "limit"
        )
        assert parameter["schema"]["minimum"] == 0
        assert parameter["schema"]["maximum"] == 2**32 - 1
        assert parameter["required"] is False


@pytest.mark.parametrize(
    "action", [a for a, op in CONTRACT["operations"].items() if not op["read_only"]]
)
@pytest.mark.parametrize("accepted", [True, False])
@pytest.mark.parametrize("mode", ["legacy", "2026-07-28"])
def test_native_mcp_cache_effect_confirmation(action, accepted, mode, monkeypatch):
    from agent_connector_sdk.http.client import create_http_client
    from fastmcp import Client
    from fastmcp.client.elicitation import ElicitResult
    from mcp.shared.exceptions import MCPError

    from craft_suite_api import auth, openapi_client
    from craft_suite_api.mcp_server import build_server

    auth.close_client()
    monkeypatch.setattr(auth, "load_config", lambda: None)
    monkeypatch.setenv("CRAFT_SUITE_API_BASE_URL", "https://artcraft.example.invalid")
    monkeypatch.setenv("CRAFT_SUITE_API_TOKEN_REF", "env://CRAFT_SUITE_FIXTURE_SESSION")
    monkeypatch.setenv("CRAFT_SUITE_FIXTURE_SESSION", "synthetic-session")
    monkeypatch.setenv("CRAFT_SUITE_API_ALLOW_WRITES", "true")
    monkeypatch.setenv("ENABLE_DELEGATION", "false")
    calls, confirmations = [], []
    operation = CONTRACT["operations"][action]
    arguments = {"action": action}
    for parameter in operation["parameters"]:
        if parameter["in"] == "path":
            arguments.setdefault("path", {})[parameter["name"]] = "fixture_token"

    def respond(request):
        calls.append(request)
        assert request.method == "GET"
        assert request.headers["session"] == "synthetic-session"
        return httpx.Response(200, json=response_for(action))

    monkeypatch.setattr(
        openapi_client,
        "create_http_client",
        lambda options, **kwargs: create_http_client(
            options, transport=httpx.MockTransport(respond)
        ),
    )

    async def elicit(message, response_type, params, context):
        confirmations.append(message)
        return (
            ElicitResult(action="accept", content=True)
            if accepted
            else ElicitResult(action="decline")
        )

    async def call():
        async with Client(
            build_server(command_args=["--transport", "stdio"]),
            elicitation_handler=elicit,
            mode=mode,
        ) as client:
            if accepted and mode == "legacy":
                result = await client.call_tool(
                    operation["domain"] + "_operations", arguments
                )
                assert result.structured_content["data"] == response_for(action)
            else:
                with pytest.raises(MCPError, match="Write was not confirmed"):
                    await client.call_tool(
                        operation["domain"] + "_operations", arguments
                    )

    try:
        asyncio.run(call())
        assert len(confirmations) == int(mode == "legacy")
        if confirmations:
            assert action in confirmations[0]
        assert len(calls) == int(accepted and mode == "legacy")
    finally:
        auth.close_client()


def test_optional_session_media_tags_supports_anonymous_access():
    calls = []
    action = "list_media_file_tags_handler"

    def respond(request):
        calls.append(request)
        assert "session" not in request.headers
        assert "authorization" not in request.headers
        return httpx.Response(200, json=response_for(action))

    client = ApiClientSystem(
        "https://artcraft.example.invalid",
        httpx.Auth(),
        policy=ClientPolicy(allow_writes=True),
        transport=httpx.MockTransport(respond),
    )
    try:
        result = client.execute(
            "tags", {"action": action, "path": {"media_file_token": "public_fixture"}}
        )
        assert result["data"]["tags"][0]["tag_value"] == "Fixture"
        assert len(calls) == 1
    finally:
        client.close()


def test_served_prompts_match_admitted_capabilities():
    for path in (ROOT / "craft_suite_api/prompts").glob("*.json"):
        prompt = json.loads(path.read_text())
        assert set(prompt["tools"]) == {
            "folders_operations",
            "tags_operations",
            "omni_gen_operations",
        }
        assert "TODO" not in path.read_text()
        assert (
            "graph ingestion are unavailable"
            in prompt["instructions"]["core_directive"]
        )


def test_bounded_pattern_callback_preserves_json_schema_validation():
    from craft_suite_api.openapi_schema import validate

    validate("aaa", {"type": "string", "pattern": "^a+$"})
    with pytest.raises(ValueError, match="declared OpenAPI schema"):
        validate("private-invalid-fixture", {"type": "string", "pattern": "^a+$"})

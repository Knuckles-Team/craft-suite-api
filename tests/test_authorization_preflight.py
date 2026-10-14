"""Unreviewed authorization must stop before client creation or outbound traffic."""

import asyncio
import copy
from contextlib import closing

import httpx
import pytest
from agent_connector_sdk.auth.static import api_key_auth
from fastmcp import Client
from mcp.shared.exceptions import MCPError
from mcp.types import ElicitResult

from craft_suite_api import mcp
from craft_suite_api.api import ApiClientSystem
from craft_suite_api.mcp_server import build_server
from craft_suite_api.openapi_client import ClientPolicy
from craft_suite_api.openapi_runtime import CONTRACT

from .test_source_contract import response_for

REVIEWED_ACTIONS = (
    "get_folder_handler",
    "list_folders_handler",
    "list_media_file_tags_handler",
    "list_tags_handler",
    "omni_gen_audio_models_handler",
    "omni_gen_image_models_handler",
    "omni_gen_mesh_models_handler",
    "omni_gen_splat_models_handler",
    "status_alert_handler",
)
MISSING = object()
AUTHORIZATION_ERROR = "Action authorization requires reviewed provider evidence"


@pytest.fixture(params=[False, True], ids=["writes-disabled", "writes-enabled"])
def allow_writes(request):
    return request.param


@pytest.fixture(
    params=[
        pytest.param("unknown", id="unknown"),
        pytest.param(MISSING, id="missing"),
        pytest.param(None, id="malformed-null"),
        pytest.param("public", id="malformed-label"),
        pytest.param({"type": "operation"}, id="malformed-mapping"),
    ]
)
def declaration(request):
    return request.param


@pytest.fixture(params=REVIEWED_ACTIONS)
def rejected_operation(request, monkeypatch, allow_writes, declaration):
    action = request.param
    operation = copy.deepcopy(CONTRACT["operations"][action])
    if declaration is MISSING:
        operation.pop("security_declaration")
    else:
        operation["security_declaration"] = declaration
    monkeypatch.setitem(CONTRACT["operations"], action, operation)
    arguments = {"action": action}
    path = {
        p["name"]: "fixture_token" for p in operation["parameters"] if p["in"] == "path"
    }
    if path:
        arguments["path"] = path
    calls = {"factory": 0, "transport": 0, "confirmation": 0}

    def respond(_request):
        calls["transport"] += 1
        return httpx.Response(200, json=response_for(action))

    monkeypatch.setenv("CRAFT_SUITE_FIXTURE_SESSION", "synthetic-session")
    monkeypatch.setenv("ENABLE_DELEGATION", "false")
    with closing(
        ApiClientSystem(
            "https://craft.example.invalid",
            api_key_auth("env://CRAFT_SUITE_FIXTURE_SESSION", header="session"),
            credential_scheme="signed_session",
            policy=ClientPolicy(allow_writes=allow_writes),
            transport=httpx.MockTransport(respond),
        )
    ) as api:

        def factory():
            calls["factory"] += 1
            return api

        registrar = getattr(mcp, f"register_{operation['domain']}_tools")
        monkeypatch.setitem(registrar.keywords, "client_factory", factory)
        yield api, arguments, operation, calls


def test_api_denies_unreviewed_authorization_before_transport(rejected_operation):
    api, arguments, operation, calls = rejected_operation
    with pytest.raises(PermissionError, match=AUTHORIZATION_ERROR):
        api.execute(operation["domain"], arguments)
    assert calls == {"factory": 0, "transport": 0, "confirmation": 0}


def test_native_denies_before_client_factory_or_confirmation(rejected_operation):
    _api, arguments, operation, calls = rejected_operation

    async def elicit(_message, _response_type, _params, _context):
        calls["confirmation"] += 1
        return ElicitResult(action="accept", content={"confirmed": True})

    async def call():
        async with Client(
            build_server(command_args=["--transport", "stdio"]),
            elicitation_handler=elicit,
            mode="2026-07-28",
        ) as client:
            with pytest.raises(MCPError, match=AUTHORIZATION_ERROR):
                await client.call_tool(operation["domain"] + "_operations", arguments)

    asyncio.run(call())
    assert calls == {"factory": 0, "transport": 0, "confirmation": 0}

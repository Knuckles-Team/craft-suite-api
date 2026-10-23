"""Real protocol retries must preserve confirmation and single-dispatch boundaries."""

import asyncio
import copy

import httpx
import pytest
from fastmcp import Client
from mcp.shared.exceptions import MCPError
from mcp.types import ElicitResult, InputRequiredResult

from craft_suite_api import mcp, openapi_execution
from craft_suite_api.mcp_server import build_server
from craft_suite_api.openapi_runtime import CONTRACT, OpenApiTool, operation_inputs

from .conftest import native_tool
from .test_source_contract import response_for

EFFECTFUL = [a for a, op in CONTRACT["operations"].items() if not op["read_only"]]


@pytest.fixture(params=EFFECTFUL)
def effect_client(request, monkeypatch, synthetic_session_client):
    action = request.param
    operation = CONTRACT["operations"][action]
    arguments = {"action": action}
    path = {
        p["name"]: "fixture_token" for p in operation["parameters"] if p["in"] == "path"
    }
    if path:
        arguments["path"] = path
    requests = []

    def respond(outbound):
        requests.append(outbound)
        assert outbound.method == "GET"
        assert outbound.url.path == operation["path"].format_map(path)
        assert outbound.headers["session"] == "synthetic-session"
        return httpx.Response(200, json=response_for(action))

    with synthetic_session_client(respond, allow_writes=True) as api:
        registrar = getattr(mcp, f"register_{operation['domain']}_tools")
        monkeypatch.setitem(registrar.keywords, "client_factory", lambda: api)
        yield api, arguments, operation, requests


def altered_arguments(arguments):
    result = copy.deepcopy(arguments)
    if "path" in result:
        name = next(iter(result["path"]))
        result["path"][name] = "different_token"
    else:
        result["query"] = {"limit": 1}
    return result


@pytest.mark.parametrize(
    "decision",
    [
        "accept",
        "false",
        "non_boolean",
        "missing",
        "decline",
        "cancel",
        "changed_arguments",
        "changed_state",
        "missing_state",
        "missing_responses",
    ],
)
def test_modern_pending_then_bound_retry(effect_client, decision):
    _api, arguments, operation, requests = effect_client

    async def call():
        async with Client(
            build_server(command_args=["--transport", "stdio"]), mode="2026-07-28"
        ) as client:
            tool, native_arguments = native_tool(arguments)
            pending = await client.session.call_tool(
                tool, native_arguments, allow_input_required=True
            )
            assert isinstance(pending, InputRequiredResult)
            assert requests == []
            assert pending.request_state
            key = next(iter(pending.input_requests))
            responses = {
                key: ElicitResult(action="accept", content={"confirmed": True})
            }
            values = {"false": False, "non_boolean": "yes", "missing": None}
            if decision in values:
                responses[key] = ElicitResult(
                    action="accept", content={"confirmed": values[decision]}
                )
            if decision in {"decline", "cancel"}:
                responses[key] = ElicitResult(action=decision)
            state = {"changed_state": "wrong-binding", "missing_state": None}.get(
                decision, pending.request_state
            )
            retry = client.session.call_tool(
                tool,
                native_tool(altered_arguments(arguments))[1]
                if decision == "changed_arguments"
                else native_arguments,
                input_responses=None if decision == "missing_responses" else responses,
                request_state=state,
                allow_input_required=True,
            )
            if decision != "accept":
                message = (
                    "Invalid or expired requestState"
                    if decision in {"changed_arguments", "changed_state"}
                    else "Write was not confirmed"
                )
                with pytest.raises(MCPError, match=message):
                    await retry
                return
            result = await retry
            assert not isinstance(result, InputRequiredResult)
            assert not result.is_error
            assert result.structured_content["data"] == response_for(
                arguments["action"]
            )

    asyncio.run(call())
    assert len(requests) == int(decision == "accept")


def test_native_write_disabled_denies_before_prompt(effect_client):
    api, arguments, operation, requests = effect_client
    api.allow_writes = False

    async def call():
        async with Client(
            build_server(command_args=["--transport", "stdio"])
        ) as client:
            with pytest.raises(
                MCPError, match="Writes require explicit operator enablement"
            ):
                await client.session.call_tool(
                    *native_tool(arguments),
                    allow_input_required=True,
                )

    asyncio.run(call())
    assert requests == []


def test_missing_context_denies_without_dispatch(effect_client, monkeypatch):
    api, arguments, operation, requests = effect_client
    monkeypatch.setattr(openapi_execution, "get_context", lambda: None)
    tool = OpenApiTool(
        name="fixture",
        domain=operation["domain"],
        action=arguments["action"],
        client_factory=lambda: api,
        parameters=operation_inputs(operation["domain"], arguments["action"]),
    )
    with pytest.raises(PermissionError, match="not confirmed"):
        asyncio.run(tool.run(native_tool(arguments)[1]))
    assert requests == []

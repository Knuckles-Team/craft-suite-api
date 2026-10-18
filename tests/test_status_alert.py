"""Source-shaped service alerts through the real API client and native MCP."""

import asyncio
from contextlib import closing

import httpx
import pytest
from fastmcp import Client
from mcp.shared.exceptions import MCPError

from craft_suite_api import mcp
from .conftest import native_tool
from craft_suite_api.api import ApiClientSystem
from craft_suite_api.mcp_server import build_server

ACTION = "status_alert_handler"


@pytest.fixture
def status_client(monkeypatch):
    requests = []
    response = {"status_code": 200, "json": {}}

    def respond(request):
        requests.append(request)
        assert request.method == "GET"
        assert request.url == httpx.URL(
            "https://craft.example.invalid/v1/status_alert_check"
        )
        assert not request.content
        assert "session" not in request.headers
        assert "authorization" not in request.headers
        return httpx.Response(**response)

    with closing(
        ApiClientSystem(
            "https://craft.example.invalid",
            httpx.Auth(),
            transport=httpx.MockTransport(respond),
        )
    ) as api:
        monkeypatch.setitem(
            mcp.register_misc_tools.keywords, "client_factory", lambda: api
        )
        monkeypatch.setenv("ENABLE_DELEGATION", "false")
        yield api, requests, response


def call_native(arguments):
    async def run():
        async with Client(
            build_server(command_args=["--transport", "stdio"])
        ) as client:
            result = await client.call_tool(*native_tool(arguments))
            return result.structured_content

    return asyncio.run(run())


@pytest.mark.parametrize(
    "alert",
    [
        None,
        {"maybe_category": "down_for_maintenance", "maybe_message": None},
        {"maybe_category": None, "maybe_message": "Scheduled maintenance"},
        {
            "maybe_category": "down_for_maintenance",
            "maybe_message": "Scheduled maintenance",
        },
    ],
)
def test_status_complete_response_matches_api_and_native_mcp(status_client, alert):
    api, requests, response = status_client
    payload = {"success": True, "maybe_alert": alert, "refresh_interval_millis": 60000}
    response["json"] = payload
    arguments = {"action": ACTION}
    expected = {
        "action": ACTION,
        "status": 200,
        "content_type": "application/json",
        "data": payload,
    }
    assert api.allow_writes is False
    assert api.execute("misc", arguments) == expected
    assert len(requests) == 1
    assert call_native(arguments) == expected
    assert len(requests) == 2


@pytest.mark.parametrize(
    "payload",
    [
        {"maybe_alert": None, "refresh_interval_millis": 60000},
        {"success": True, "maybe_alert": None, "refresh_interval_millis": -1},
        {
            "success": True,
            "maybe_alert": {"maybe_category": "invented"},
            "refresh_interval_millis": 60000,
        },
    ],
)
def test_invalid_provider_status_is_rejected_on_both_surfaces(status_client, payload):
    api, requests, response = status_client
    response["json"] = payload
    with pytest.raises(ValueError, match="declared OpenAPI schema"):
        api.execute("misc", {"action": ACTION})
    with pytest.raises(MCPError, match="declared OpenAPI schema"):
        call_native({"action": ACTION})
    assert len(requests) == 2


def test_status_provider_error_is_not_retried(status_client):
    api, requests, response = status_client
    response.update(status_code=500, json={"error": "synthetic internal detail"})
    with pytest.raises(RuntimeError, match="500"):
        api.execute("misc", {"action": ACTION})
    with pytest.raises(MCPError, match="500"):
        call_native({"action": ACTION})
    assert len(requests) == 2


@pytest.mark.parametrize(
    "arguments",
    [
        {"action": "invented_handler"},
        {"action": ACTION, "query": {"provider": "invented"}},
        {"action": ACTION, "body": {}},
    ],
)
def test_status_rejects_undeclared_inputs_before_dispatch(status_client, arguments):
    api, requests, _ = status_client
    with pytest.raises(ValueError):
        api.execute("misc", arguments)
    with pytest.raises(MCPError):
        call_native(arguments)
    assert requests == []

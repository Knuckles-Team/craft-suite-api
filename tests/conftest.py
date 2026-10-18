from contextlib import closing
from unittest.mock import MagicMock

import httpx
import pytest
from agent_connector_sdk.auth.static import api_key_auth

from craft_suite_api.api import ApiClientSystem
from craft_suite_api.openapi_client import ClientPolicy


@pytest.fixture
def mock_api_client():
    client = MagicMock()
    client.get_system_status.return_value = {"status": "OK"}
    return client


@pytest.fixture
def synthetic_session_client(monkeypatch):
    """Create a closing synthetic-session client with caller-owned HTTP replies."""
    monkeypatch.setenv("CRAFT_SUITE_FIXTURE_SESSION", "synthetic-session")
    monkeypatch.setenv("ENABLE_DELEGATION", "false")

    def create(respond, *, allow_writes):
        return closing(
            ApiClientSystem(
                "https://craft.example.invalid",
                api_key_auth("env://CRAFT_SUITE_FIXTURE_SESSION", header="session"),
                credential_scheme="signed_session",
                policy=ClientPolicy(allow_writes=allow_writes),
                transport=httpx.MockTransport(respond),
            )
        )

    return create


def native_tool(arguments):
    """The per-operation tool name and its arguments for a contract call."""
    from craft_suite_api.openapi_runtime import operation_tool_name

    rest = {key: value for key, value in arguments.items() if key != "action"}
    return operation_tool_name(arguments["action"]), rest

"""CONN-CRAFT-SUITE-API-APPS-R007: the initial list is the backend plus the registry."""

from __future__ import annotations

import asyncio
import dataclasses
import json

import pytest
from fastmcp import Client
from scion_sdk.mcp.upstreams.activation import REGISTRY_TOOL_NAMES

import craft_suite_api
from craft_suite_api.backend import NAMESPACE, tool_names
from craft_suite_api.mcp_server import build_server
from craft_suite_api.upstreams import build_upstreams

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R007")

#: Every backend operation, served eagerly; the apps stay lazy.
BACKEND = frozenset(f"{NAMESPACE}_{name}" for name in tool_names().values())

# The fixture CLI serves exactly these tools, namespaced by app.
FIXTURE_TOOLS = ("read_demo", "write_demo", "ask_once")


def _declare_apps(monkeypatch, apps: tuple[str, ...]) -> None:
    """Serve the facade with only the named apps, all starting lazy."""
    monkeypatch.setattr(craft_suite_api.upstreams, "APPS", apps)
    monkeypatch.setattr(
        craft_suite_api,
        "connector",
        dataclasses.replace(craft_suite_api.connector, upstreams=build_upstreams()),
    )


def test_initial_list_is_tier1_plus_registry_only(
    app_cli_factory, monkeypatch, tmp_path
) -> None:
    # Roots unset: the activated child receives no root flag.
    argv_log = tmp_path / "argv.jsonl"
    monkeypatch.setenv("FAKE_APP_CLI_ARGV_FILE", str(argv_log))
    monkeypatch.setenv(
        "SCION_UPSTREAMS_INHERIT_ENV", "PATH,HOME,LANG,FAKE_APP_CLI_ARGV_FILE"
    )
    for var in (
        "CRAFT_SUITE_API_BASE_URL",
        "CRAFT_SUITE_READ_ROOTS",
        "CRAFT_SUITE_WRITE_ROOTS",
        "SCION_UPSTREAMS_FILE",
        "SCION_UPSTREAMS_DISABLED",
        "SCION_UPSTREAM_ACTIVATION",
    ):
        monkeypatch.delenv(var, raising=False)
    app_cli_factory("alpha")
    app_cli_factory("beta")
    _declare_apps(monkeypatch, ("alpha", "beta"))
    server = build_server(command_args=[])

    async def scenario() -> None:
        async with Client(server) as client:
            # A fresh session lists the backend and registry tools only...
            tools = {tool.name for tool in await client.list_tools()}
            assert tools == BACKEND | set(REGISTRY_TOOL_NAMES)
            assert len(tools) == len(BACKEND) + len(REGISTRY_TOOL_NAMES)
            # ...and has started no app process.
            assert not argv_log.exists()

            # One activation reveals that app's tools, and nothing else.
            result = await client.call_tool("registry_activate", {"namespace": "alpha"})
            assert result.structured_content == {
                "namespace": "alpha",
                "state": "active",
                "changed": True,
            }
            tools = {tool.name for tool in await client.list_tools()}
            assert tools == (BACKEND | set(REGISTRY_TOOL_NAMES)) | {
                f"alpha_{name}" for name in FIXTURE_TOOLS
            }
            assert len(tools) == len(BACKEND) + len(REGISTRY_TOOL_NAMES) + 3
            assert not any(name.startswith("beta_") for name in tools)

    asyncio.run(scenario())

    # The activated app started as a stdio child without root flags; beta,
    # which was never activated, never started.
    lines = [
        json.loads(line) for line in argv_log.read_text(encoding="utf-8").splitlines()
    ]
    assert lines == [["mcp"]]

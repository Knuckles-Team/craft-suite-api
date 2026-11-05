"""CONN-CRAFT-SUITE-API-APPS-R004: one missing CLI marks one upstream unavailable."""

from __future__ import annotations

import asyncio
import dataclasses
import json

import pytest
from fastmcp import Client
from scion_sdk.mcp.upstreams.model import UPSTREAM_SPAWN_FAILED

import craft_suite_api
from craft_suite_api.mcp_server import build_server
from craft_suite_api.upstreams import build_upstreams

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R004")

TIER1 = frozenset(
    {
        "craft_suite_get_folder_handler",
        "craft_suite_list_folders_handler",
        "craft_suite_status_alert_handler",
        "craft_suite_omni_gen_audio_models_handler",
        "craft_suite_omni_gen_image_models_handler",
        "craft_suite_omni_gen_mesh_models_handler",
        "craft_suite_omni_gen_splat_models_handler",
        "craft_suite_list_media_file_tags_handler",
        "craft_suite_list_tags_handler",
    }
)

# The fixture CLI serves exactly these tools, namespaced by app.
FIXTURE_TOOLS = ("read_demo", "write_demo", "ask_once")


def _declare_apps(monkeypatch, apps: tuple[str, ...]) -> None:
    """Serve the facade with only the named apps, as stdio children of <app>-cli."""
    monkeypatch.setattr(craft_suite_api.upstreams, "APPS", apps)
    monkeypatch.setattr(
        craft_suite_api,
        "connector",
        dataclasses.replace(craft_suite_api.connector, upstreams=build_upstreams()),
    )


def test_missing_cli_marks_one_upstream_unavailable(
    app_cli_factory, monkeypatch, tmp_path
) -> None:
    # Roots unset: no flag reaches any child. beta has no binary on PATH.
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
    # beta-cli is deliberately absent from PATH.
    _declare_apps(monkeypatch, ("alpha", "beta"))
    server = build_server(command_args=[])

    async def scenario() -> None:
        async with Client(server) as client:
            # Activation of the present app succeeds and its tools are callable.
            result = await client.call_tool("registry_activate", {"namespace": "alpha"})
            assert result.structured_content == {
                "namespace": "alpha",
                "state": "active",
                "changed": True,
            }
            tools = {tool.name for tool in await client.list_tools()}
            assert {f"alpha_{name}" for name in FIXTURE_TOOLS} <= tools
            read = await client.call_tool("alpha_read_demo", {"value": "hi"})
            assert read.is_error is False
            assert read.structured_content == {"value": "hi", "extra": ""}

            # The absent app still activates, but its listing never succeeds.
            result = await client.call_tool("registry_activate", {"namespace": "beta"})
            assert result.structured_content == {
                "namespace": "beta",
                "state": "active",
                "changed": True,
            }
            tools = {tool.name for tool in await client.list_tools()}
            assert not any(name.startswith("beta_") for name in tools)

            # The registry reports the spawn failure with its refusal code.
            status = {
                entry["namespace"]: entry
                for entry in (
                    await client.call_tool("registry_status", {})
                ).structured_content["result"]
            }
            assert status["beta"]["state"] == "unavailable"
            assert status["beta"]["last_error_code"] == UPSTREAM_SPAWN_FAILED
            assert status["alpha"]["state"] == "ready"

            # The server and Tier 1 stay up alongside the healthy app.
            assert TIER1 <= tools

    asyncio.run(scenario())

    # Only the present app ran as a stdio child, without any root flag.
    lines = [
        json.loads(line) for line in argv_log.read_text(encoding="utf-8").splitlines()
    ]
    assert lines == [["mcp"]]

"""CONN-CRAFT-SUITE-API-APPS-R010: phase 2 gate — full registry, remote and bridge.

Phase 2 enables all eleven declarations and proves the three halves of the
spec, against the fixture app CLIs (tests/fixtures/fake_app_cli.py):

- one app that dies at spawn (filmcraft) shows ``unavailable`` while the
  other ten stay callable under the default ``warn`` strategy;
- the example overlays of R005 and R006 switch one app's transport mode on
  the served registry: the remote example as shipped (photocraft goes
  ``http``) and the bridge example's shape (figcraft goes ``bridge``);
- a fixture app whose tool surface drifted (effectcraft) reports
  ``drifted`` against its pinned baseline fingerprint (R914.11).

The gate stays well under the suite's timeout budget: no real app binary is
ever resolved, every child is a fixture on a temporary PATH.
"""

from __future__ import annotations

import asyncio
import tomllib
from dataclasses import replace
from pathlib import Path

import pytest
from fastmcp import Client
from scion_sdk.mcp.upstreams.drift import fingerprint_tools

from craft_suite_api.backend import operation_count
from craft_suite_api.upstreams import (
    APPS,
    READ_ROOTS_SETTING,
    WRITE_ROOTS_SETTING,
    SandboxRoots,
    UpstreamDecl,
)

#: The initial list: every backend operation plus the four registry tools.
INITIAL = operation_count() + 4

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R010")

REPO = Path(__file__).resolve().parents[1]
FIXTURE_CLI = REPO / "tests" / "fixtures" / "fake_app_cli.py"
REMOTE_EXAMPLE = REPO / "docs" / "remote-upstreams.example.toml"
BRIDGE_EXAMPLE = REPO / "docs" / "bridge-upstreams.example.toml"

#: The app that dies before the handshake; the app with the drifted surface.
DIE_APP = "filmcraft"
DRIFT_APP = "effectcraft"


def _fixture_upstreams(baseline_fingerprint: str) -> tuple[UpstreamDecl, ...]:
    """All eleven declarations against the fixture CLIs: lazy, rootless.

    The drifted app pins the non-drift baseline fingerprint, so the extra
    parameter of its ``read_demo`` is the drift the registry must report.
    """
    return tuple(
        UpstreamDecl(
            name=app,
            kind="stdio",
            command=f"{app}-cli",
            args=("mcp",),
            sandbox=SandboxRoots(
                read=(),
                write=(),
                read_flag="--automation-read-root",
                write_flag="--automation-write-root",
            ),
            expected_fingerprint=baseline_fingerprint if app == DRIFT_APP else None,
        )
        for app in APPS
    )


def _baseline_fingerprint() -> str:
    """The fingerprint of the non-drift fixture tool surface.

    Probed once through a direct fixture client so the pin is computed by
    the same code the registry fingerprints with.
    """
    import os
    import sys

    from fastmcp.client.transports import StdioTransport

    async def probe() -> str:
        transport = StdioTransport(
            command=sys.executable,
            args=[str(FIXTURE_CLI), "mcp"],
            env={**os.environ, "FAKE_APP_CLI_APP": "baseline"},
        )
        async with Client(transport) as client:
            return fingerprint_tools(await client.list_tools())

    return asyncio.run(probe())


async def _expect_tools(client, expected: int) -> int:
    count = len(await client.list_tools())
    assert count == expected
    return count


async def _eleven_gate() -> dict:
    """One dying app, ten callable, and the drifted app reported drifted."""
    from craft_suite_api.mcp_server import build_server

    observations: dict = {}
    async with Client(build_server(command_args=[]), mode="legacy") as client:
        # The initial list (backend plus registry); every app is lazy, nothing spawns.
        await _expect_tools(client, INITIAL)

        for app in APPS:
            result = await client.call_tool("registry_activate", {"namespace": app})
            assert result.is_error is False, app

        # The initial tools plus three per live app; the dead one holds none.
        observations["tool_count"] = await _expect_tools(
            client, INITIAL + 3 * (len(APPS) - 1)
        )

        result = await client.call_tool("registry_status", {})
        entries = {
            entry["name"]: entry for entry in result.structured_content["result"]
        }
        observations["states"] = {
            name: entry["state"] for name, entry in entries.items()
        }
        assert entries[DIE_APP]["state"] == "unavailable"
        assert entries[DIE_APP]["last_error_code"] == "UPSTREAM_SPAWN_FAILED"
        assert entries[DRIFT_APP]["state"] == "drifted"
        assert {
            name for name, entry in entries.items() if entry["state"] == "ready"
        } == (set(APPS) - {DIE_APP, DRIFT_APP})

        # The ten live apps (including the drifted one) stay callable under
        # the default warn strategy.
        for app in APPS:
            if app == DIE_APP:
                continue
            result = await client.call_tool(f"{app}_read_demo", {"value": app})
            assert result.is_error is False, app
            assert result.structured_content["value"] == app
    return observations


def _served_kinds() -> dict[str, str]:
    """Serve the registry with the overlay in effect; each app's kind.

    The served check is the strongest validation: a refused overlay would
    fall back to the base declarations (all stdio) and fail the assertion.
    """
    from craft_suite_api.mcp_server import build_server

    async def kinds() -> dict[str, str]:
        async with Client(build_server(command_args=[])) as client:
            result = await client.call_tool("registry_status", {})
            return {
                entry["name"]: entry["kind"]
                for entry in result.structured_content["result"]
            }

    return asyncio.run(kinds())


def test_eleven_upstreams_isolated_failure_and_overlays(
    app_cli_factory, monkeypatch
) -> None:
    # Hygiene: no root grants, no disabled list, no pre-activation, no
    # overlay of an ambient environment.
    for var in (
        READ_ROOTS_SETTING,
        WRITE_ROOTS_SETTING,
        "SCION_UPSTREAMS_DISABLED",
        "SCION_UPSTREAM_ACTIVATION",
        "SCION_UPSTREAMS_FILE",
    ):
        monkeypatch.delenv(var, raising=False)

    # (b) the remote example overlay, exactly as shipped: one app goes
    # http, ten stay stdio.
    monkeypatch.setenv("SCION_UPSTREAMS_FILE", str(REMOTE_EXAMPLE))
    kinds = _served_kinds()
    assert len(kinds) == 11
    assert kinds["photocraft"] == "http"
    assert {name: kind for name, kind in kinds.items() if name != "photocraft"} == {
        name: "stdio" for name in APPS if name != "photocraft"
    }

    # (b) the bridge example, exactly as shipped: figcraft goes bridge,
    # ten stay stdio; the entry holds a loopback address and a token
    # reference, never a token value.
    entry = tomllib.loads(BRIDGE_EXAMPLE.read_text(encoding="utf-8"))["upstream"][0]
    assert entry["name"] == "figcraft"
    assert entry["kind"] == "bridge"
    assert entry["bridge"]["address"] == "127.0.0.1:47001"
    assert entry["bridge"]["token_ref"] == "env://CRAFT_SUITE_BRIDGE_TOKEN"
    monkeypatch.setenv("SCION_UPSTREAMS_FILE", str(BRIDGE_EXAMPLE))
    kinds = _served_kinds()
    assert kinds["figcraft"] == "bridge"
    assert {name: kind for name, kind in kinds.items() if name != "figcraft"} == {
        name: "stdio" for name in APPS if name != "figcraft"
    }
    monkeypatch.delenv("SCION_UPSTREAMS_FILE")

    # (a) + (c) the eleven fixture apps: one dies, one drifts, ten callable.
    app_cli_factory(DIE_APP, die=True)
    app_cli_factory(DRIFT_APP, drift=True)
    for app in APPS:
        if app not in (DIE_APP, DRIFT_APP):
            app_cli_factory(app)

    # Activate all eleven: the default cap of four namespaces is raised.
    monkeypatch.setenv("SCION_UPSTREAMS_MAX_ACTIVE_NAMESPACES", str(len(APPS)))
    monkeypatch.setenv("SCION_UPSTREAMS_CONNECT_TIMEOUT_S", "5")

    import craft_suite_api

    monkeypatch.setattr(
        craft_suite_api,
        "connector",
        replace(
            craft_suite_api.connector,
            upstreams=_fixture_upstreams(_baseline_fingerprint()),
        ),
    )

    observations = asyncio.run(_eleven_gate())
    assert observations["states"] == {
        **{app: "ready" for app in APPS if app not in (DIE_APP, DRIFT_APP)},
        DIE_APP: "unavailable",
        DRIFT_APP: "drifted",
    }

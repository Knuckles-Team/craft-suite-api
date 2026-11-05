"""CONN-CRAFT-SUITE-API-APPS-R003: the probe reports declared, undeclared and missing apps."""

from __future__ import annotations

import asyncio

import pytest

import craft_suite_api.probe as probe
from craft_suite_api.probe import APP_CLI_NOT_FOUND, APP_NO_MCP

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R003")


def test_probe_reports_declared_undeclared_and_missing(
    app_cli_factory, monkeypatch, tmp_path
) -> None:
    argv_log = tmp_path / "argv.jsonl"
    monkeypatch.setenv("FAKE_APP_CLI_ARGV_FILE", str(argv_log))
    app_cli_factory("alpha")
    app_cli_factory("beta", no_mcp=True)

    # A fixture CLI with mcp reports exposes_mcp true.
    result = asyncio.run(probe.probe_app("alpha", 20.0))
    assert result == {
        "app": "alpha",
        "exposes_mcp": True,
        "version": "0.0.1-fixture",
        "tool_count": 3,
    }

    # A fixture without mcp reports APP_NO_MCP.
    result = asyncio.run(probe.probe_app("beta", 20.0))
    assert result["app"] == "beta"
    assert result["exposes_mcp"] is False
    assert result["code"] == APP_NO_MCP

    # A missing binary reports APP_CLI_NOT_FOUND.
    result = asyncio.run(probe.probe_app("gamma", 20.0))
    assert result["code"] == APP_CLI_NOT_FOUND

    # The probe runs the child with no root flags.
    lines = argv_log.read_text(encoding="utf-8").splitlines()
    assert lines
    import json

    argv = json.loads(lines[0])
    assert "--automation-read-root" not in argv
    assert "--automation-write-root" not in argv

    # An undeclared app that exposes mcp makes the exit code non-zero.
    app_cli_factory("gamma")
    monkeypatch.setattr(probe, "APPS", ("alpha",))
    monkeypatch.setattr(probe, "REPROBED", ("gamma",))
    exit_code = probe.main([])
    assert exit_code != 0

    # Declared and undeclared apps that stay out of the suite exit clean.
    app_cli_factory("alpha", no_mcp=True)
    monkeypatch.setattr(probe, "REPROBED", ())
    # alpha (declared, no mcp) now drifts: the probe flags it.
    assert probe.main([]) != 0
    monkeypatch.setattr(probe, "APPS", ())
    monkeypatch.setattr(probe, "REPROBED", ("beta",))
    assert probe.main([]) == 0

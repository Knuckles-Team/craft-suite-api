"""CONN-CRAFT-SUITE-API-APPS-R002: eleven app upstreams, with roots that fail closed."""

from __future__ import annotations

import pytest
from scion_sdk.mcp.upstreams.stdio import build_stdio_command

from craft_suite_api.upstreams import (
    APPS,
    FLAGLESS_APPS,
    READ_ROOTS_SETTING,
    UPSTREAMS,
    WRITE_ROOTS_SETTING,
    build_upstreams,
)

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R002")


def test_eleven_apps_declared_with_roots_fail_closed(monkeypatch) -> None:
    # Eleven declarations, one per app, with unique namespaces.
    assert len(UPSTREAMS) == 11
    assert set(decl.name for decl in UPSTREAMS) == set(APPS)
    namespaces = [decl.effective_namespace for decl in UPSTREAMS]
    assert len(set(namespaces)) == 11

    # Every declaration is a stdio child of <app>-cli mcp.
    for decl in UPSTREAMS:
        assert decl.kind == "stdio"
        assert decl.command == f"{decl.name}-cli"
        assert decl.args == ("mcp",)
        assert decl.activation is None
        assert decl.sandbox is not None
        if decl.name in FLAGLESS_APPS:
            assert decl.sandbox.read_flag is None
            assert decl.sandbox.write_flag is None
        else:
            assert decl.sandbox.read_flag == "--automation-read-root"
            assert decl.sandbox.write_flag == "--automation-write-root"
    assert FLAGLESS_APPS == ("filmcraft", "cadcraft")

    # Both settings unset: no root flag reaches any command line.
    monkeypatch.delenv(READ_ROOTS_SETTING, raising=False)
    monkeypatch.delenv(WRITE_ROOTS_SETTING, raising=False)
    for decl in build_upstreams():
        command = build_stdio_command(decl)
        assert command == [f"{decl.name}-cli", "mcp"], command

    # One read root set: exactly one read flag pair, no write flag.
    monkeypatch.setenv(READ_ROOTS_SETTING, "/srv/artcraft-inbox")
    for decl in build_upstreams():
        command = build_stdio_command(decl)
        if decl.name in FLAGLESS_APPS:
            assert command == [f"{decl.name}-cli", "mcp"], command
            continue
        assert command == [
            f"{decl.name}-cli",
            "mcp",
            "--automation-read-root",
            "/srv/artcraft-inbox",
        ], command
        assert "--automation-write-root" not in command

    # A write root set on its own never borrows the read roots.
    monkeypatch.setenv(WRITE_ROOTS_SETTING, "/srv/artcraft-outbox")
    for decl in build_upstreams():
        command = build_stdio_command(decl)
        if decl.name in FLAGLESS_APPS:
            assert command == [f"{decl.name}-cli", "mcp"], command
            continue
        assert "--automation-write-root" in command
        assert command.count("--automation-read-root") == 1
        assert command.count("--automation-write-root") == 1


def test_flagless_apps_survive_exchange_binding(tmp_path) -> None:
    # With the artifact exchange bound, a flagless app keeps empty roots:
    # scion-sdk 0.8.1 appended the staging tree and refused to start.
    from scion_sdk.mcp.upstreams.exchange import ExchangeRuntime, bind_exchange_roots

    class _Settings:
        staging_root = tmp_path

    runtime = ExchangeRuntime(_Settings(), None, "craft-suite-api")  # type: ignore[arg-type]
    for decl in build_upstreams():
        bound = bind_exchange_roots(decl, runtime)
        if decl.name in FLAGLESS_APPS:
            assert bound.sandbox.read == () and bound.sandbox.write == ()
        else:
            assert bound.sandbox.read and bound.sandbox.write

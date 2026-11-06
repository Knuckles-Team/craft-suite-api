"""CONN-CRAFT-SUITE-API-APPS-R002: sixteen app upstreams, with roots that fail closed."""

from __future__ import annotations

import pytest
from scion_sdk.mcp.upstreams.stdio import build_stdio_command

from craft_suite_api.upstreams import (
    APPS,
    FLAGLESS_APPS,
    READ_ROOTS_SETTING,
    ROOT_FLAGS,
    UPSTREAMS,
    WRITE_ROOTS_SETTING,
    build_upstreams,
)

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R002")


def test_every_app_declared_with_roots_fail_closed(monkeypatch) -> None:
    # Sixteen declarations, one per app, with unique namespaces.
    assert len(UPSTREAMS) == 16
    assert set(decl.name for decl in UPSTREAMS) == set(APPS)
    namespaces = [decl.effective_namespace for decl in UPSTREAMS]
    assert len(set(namespaces)) == 16

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
            read_flag, write_flag = ROOT_FLAGS.get(
                decl.name, ("--automation-read-root", "--automation-write-root")
            )
            assert decl.sandbox.read_flag == read_flag
            assert decl.sandbox.write_flag == write_flag
    assert FLAGLESS_APPS == ("filmcraft", "cadcraft", "gridcraft", "lightcraft")
    assert ROOT_FLAGS == {
        "materialcraft": ("--read-root", "--write-root"),
        "solidcraft": ("--allow-path", "--allow-path"),
    }

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
        read_flag, write_flag = ROOT_FLAGS.get(
            decl.name, ("--automation-read-root", "--automation-write-root")
        )
        assert command == [
            f"{decl.name}-cli",
            "mcp",
            read_flag,
            "/srv/artcraft-inbox",
        ], command
        if write_flag != read_flag:
            assert write_flag not in command

    # A write root set on its own never borrows the read roots.
    monkeypatch.setenv(WRITE_ROOTS_SETTING, "/srv/artcraft-outbox")
    for decl in build_upstreams():
        command = build_stdio_command(decl)
        if decl.name in FLAGLESS_APPS:
            assert command == [f"{decl.name}-cli", "mcp"], command
            continue
        read_flag, write_flag = ROOT_FLAGS.get(
            decl.name, ("--automation-read-root", "--automation-write-root")
        )
        if read_flag == write_flag:
            # One flag grants both: one occurrence per root.
            assert command.count(read_flag) == 2
            assert (
                "/srv/artcraft-inbox" in command and "/srv/artcraft-outbox" in command
            )
        else:
            assert command.count(read_flag) == 1
            assert command.count(write_flag) == 1


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

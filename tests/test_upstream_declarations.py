"""CONN-CRAFT-SUITE-API-APPS-R002: nineteen app upstreams, with roots that fail closed."""

from __future__ import annotations

import pytest
from scion_sdk.mcp.upstreams.stdio import build_stdio_command

from craft_suite_api.upstreams import (
    APPS,
    FLAGLESS_APPS,
    NAMESPACES,
    READ_ROOTS_SETTING,
    ROOT_FLAGS,
    UPSTREAMS,
    WRITE_ROOTS_SETTING,
    build_upstreams,
)

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R002")

#: The two apps whose declared consent flags join the mcp command
#: (CONN-CRAFT-SUITE-API-APPS-R021); the base-shape checks below cover the
#: other seventeen.
CONSENT_APPS = ("mailcraft", "craft-anything")


def _root_flags(decl) -> tuple[str | None, str | None]:
    """The declaration's root flags; flagless apps hold none."""
    if decl.name in FLAGLESS_APPS:
        return None, None
    return ROOT_FLAGS.get(
        decl.name, ("--automation-read-root", "--automation-write-root")
    )


def _declaration_shape(decl) -> None:
    """The stdio child shape of R002 (the consent args of R021 aside)."""
    assert decl.kind == "stdio"
    assert decl.command == f"{decl.name}-cli"
    assert decl.activation is None
    assert decl.sandbox is not None
    if decl.name not in CONSENT_APPS:
        assert decl.args == ("mcp",)
    read_flag, write_flag = _root_flags(decl)
    assert decl.sandbox.read_flag == read_flag
    assert decl.sandbox.write_flag == write_flag


def test_every_app_declared_with_roots_fail_closed(monkeypatch) -> None:
    # Nineteen declarations, one per app, with unique namespaces.
    assert len(UPSTREAMS) == 19
    assert set(decl.name for decl in UPSTREAMS) == set(APPS)
    namespaces = [decl.effective_namespace for decl in UPSTREAMS]
    assert len(set(namespaces)) == 19
    # The app name that holds a hyphen names a different namespace.
    assert [
        decl.effective_namespace for decl in UPSTREAMS if decl.name == "craft-anything"
    ] == ["craftanything"]
    assert NAMESPACES == {"craft-anything": "craftanything"}

    # Every declaration is a stdio child of <app>-cli mcp (plus the
    # consent flags of CONN-CRAFT-SUITE-API-APPS-R021).
    for decl in UPSTREAMS:
        _declaration_shape(decl)
    assert FLAGLESS_APPS == (
        "filmcraft",
        "cadcraft",
        "gridcraft",
        "lightcraft",
        "craft-anything",
        "mailcraft",
    )
    assert ROOT_FLAGS == {
        "materialcraft": ("--read-root", "--write-root"),
        "solidcraft": ("--allow-path", "--allow-path"),
    }

    # Both settings unset: no root flag reaches any command line.
    monkeypatch.delenv(READ_ROOTS_SETTING, raising=False)
    monkeypatch.delenv(WRITE_ROOTS_SETTING, raising=False)
    for decl in build_upstreams():
        command = build_stdio_command(decl)
        assert command == [decl.command, *decl.args], command

    # One read root set: exactly one read flag pair, no write flag.
    monkeypatch.setenv(READ_ROOTS_SETTING, "/srv/artcraft-inbox")
    for decl in build_upstreams():
        command = build_stdio_command(decl)
        if decl.name in FLAGLESS_APPS:
            assert command == [decl.command, *decl.args], command
            continue
        read_flag, write_flag = _root_flags(decl)
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
            assert command == [decl.command, *decl.args], command
            continue
        read_flag, write_flag = _root_flags(decl)
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


@pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R021")
def test_consent_flags_join_the_mcp_command() -> None:
    # The proven workflows need two consent postures (verified against the
    # shipped binaries): mailcraft's headless default refuses everything, and
    # craft-anything's target-content tools serve only in Deep mode.
    args = {decl.name: decl.args for decl in UPSTREAMS}
    assert args["mailcraft"] == ("mcp", "--allow", "mailbox,send")
    assert args["craft-anything"] == ("mcp", "--deep")
    assert all(args[name] == ("mcp",) for name in args if name not in CONSENT_APPS)

    from scion_sdk.mcp.upstreams.stdio import build_stdio_command

    for decl in UPSTREAMS:
        command = build_stdio_command(decl)
        # The headless posture stays read-only: consent-gated code execution
        # and the refused power classes never reach a command line.
        assert "--allow-run" not in command
        if "--allow" in command:
            allowed = command[command.index("--allow") + 1]
            for refused in ("delete", "accounts", "settings", "input"):
                assert refused not in allowed, (decl.name, refused)

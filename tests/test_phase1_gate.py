"""CONN-CRAFT-SUITE-API-APPS-R009: phase 1 gate — the facade MVP with three apps.

Phase 1 declares photocraft, wordcraft and solidcraft only and proves,
against the fixture app CLIs (tests/fixtures/fake_app_cli.py), all five of
the spec: the initial list (backend plus registry), activation of one app through
the served registry tool, a read call through the activated namespace, a
write call whose elicitation reaches the client exactly once, and no root
flag on the child command line while the root settings are unset. The
opt-in live smoke (CRAFT_SUITE_LIVE=1) is not part of this gate: the CI
gate never needs the real CLIs.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import replace

import pytest

from craft_suite_api.backend import NAMESPACE, tool_names
from craft_suite_api.upstreams import (
    READ_ROOTS_SETTING,
    WRITE_ROOTS_SETTING,
    SandboxRoots,
    UpstreamDecl,
)

PHASE1 = ("photocraft", "wordcraft", "solidcraft")
TIER1 = frozenset(f"{NAMESPACE}_{name}" for name in tool_names().values())
REGISTRY = frozenset(
    {
        "registry_list_namespaces",
        "registry_activate",
        "registry_deactivate",
        "registry_status",
    }
)

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R009")


def _fixture_upstreams() -> tuple[UpstreamDecl, ...]:
    """The three phase 1 declarations: <app>-cli mcp, no roots, lazy."""
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
        )
        for app in PHASE1
    )


def _make_handler(elicited: list):
    """The client-side elicitation handler: counts every reach and accepts.

    fastmcp Client passes one call per server-initiated elicitation to the
    ``elicitation_handler``; the MCP SDK session advertises the elicitation
    capability only because this handler is set, which is what the registry
    checks before it forwards an upstream's question to the client.
    """

    async def handler(message, response_type, params, request_context):
        schema = getattr(params, "requested_schema", None) or {}
        elicited.append((message, schema))
        if set(schema.get("properties", {})) == {"value"}:
            choice = schema["properties"]["value"]
            enum = choice.get("enum")
            if enum:
                return {"value": enum[0]}
            one_of = choice.get("oneOf")
            if one_of:
                return {"value": one_of[0].get("const")}
            return {"value": True}
        return {"value": True}

    return handler


async def _gate(elicited: list) -> dict:
    """All five phase 1 checks in one session of the production server."""
    from fastmcp import Client

    from craft_suite_api.mcp_server import build_server

    observations: dict = {}
    # The gate client sits on the handshake era: the pooled upstream clients
    # are pinned legacy too, and the registry's elicitation pass-through
    # (R914.10) forwards over the handshake-era back channel.
    async with Client(
        build_server(command_args=[]),
        mode="legacy",
        elicitation_handler=_make_handler(elicited),
    ) as client:
        # (a) the initial list (backend plus registry): nine Tier 1 plus four registry.
        initial = {tool.name for tool in await client.list_tools()}
        observations["initial"] = initial
        assert initial == TIER1 | REGISTRY

        # (b) activation of one app through the served registry tool.
        result = await client.call_tool(
            "registry_activate", {"namespace": "photocraft"}
        )
        assert result.is_error is False
        assert result.structured_content == {
            "namespace": "photocraft",
            "state": "active",
            "changed": True,
        }
        activated = {tool.name for tool in await client.list_tools()}
        observations["activated"] = activated
        assert activated == initial | {
            "photocraft_read_demo",
            "photocraft_write_demo",
            "photocraft_ask_once",
        }

        # (c) a read call through the activated namespace.
        result = await client.call_tool("photocraft_read_demo", {"value": "gate"})
        assert result.is_error is False
        observations["read"] = result.structured_content
        assert result.structured_content == {"value": "gate", "extra": ""}

        # (d) a write call whose elicitation reaches the client exactly once.
        result = await client.call_tool("photocraft_write_demo", {"value": "gate"})
        assert result.is_error is False
        observations["write"] = result.structured_content
        assert result.structured_content == {"written": "gate"}
        observations["elicited"] = list(elicited)
        assert len(elicited) == 1

        # The registry reports the activated app ready and the rest inactive.
        result = await client.call_tool("registry_status", {})
        observations["status"] = {
            entry["name"]: entry["state"]
            for entry in result.structured_content["result"]
        }
        assert observations["status"] == {
            "photocraft": "ready",
            "wordcraft": "inactive",
            "solidcraft": "inactive",
        }
    return observations


def test_three_app_mvp_with_fixture_clis(
    app_cli_factory, tmp_path, monkeypatch
) -> None:
    argv_log = tmp_path / "argv.jsonl"
    # (e) observe the child command lines through the fixture knob.
    monkeypatch.setenv("FAKE_APP_CLI_ARGV_FILE", str(argv_log))
    for app in PHASE1:
        app_cli_factory(app)
    # The root settings are unset: the children must hold no root flag.
    monkeypatch.delenv(READ_ROOTS_SETTING, raising=False)
    monkeypatch.delenv(WRITE_ROOTS_SETTING, raising=False)
    # Pass the argv knob through to the registry-spawned fixture children.
    monkeypatch.setenv(
        "SCION_UPSTREAMS_INHERIT_ENV", "PATH,HOME,LANG,FAKE_APP_CLI_ARGV_FILE"
    )
    # Phase 1 declares three apps only; serve them, not the eleven import-time
    # declarations, so the fixture CLIs on the PATH are what get spawned.
    import craft_suite_api

    monkeypatch.setattr(
        craft_suite_api,
        "connector",
        replace(craft_suite_api.connector, upstreams=_fixture_upstreams()),
    )

    elicited: list = []
    observations = asyncio.run(_gate(elicited))

    # The one elicitation the client received is the write confirmation.
    message, schema = observations["elicited"][0]
    assert message == "Confirm writing 'gate'?"
    assert schema.get("required") == ["value"]

    # (e) every child ran with no root flag in its command line.
    lines = argv_log.read_text(encoding="utf-8").splitlines()
    assert lines, "no fixture child was spawned"
    for line in lines:
        argv = json.loads(line)
        assert argv[0] == "mcp"
        assert "--automation-read-root" not in argv
        assert "--automation-write-root" not in argv

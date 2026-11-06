"""CONN-CRAFT-SUITE-API-APPS-R006: bridge mode attaches one app to loopback."""

from __future__ import annotations

import asyncio
import tomllib
from pathlib import Path

import pytest
from fastmcp import Client
from scion_sdk.credentials.references import parse_secret_reference
from scion_sdk.credentials.resolver import EnvironmentCredentialResolver
from scion_sdk.mcp.upstreams.bridge import build_bridge_command, is_loopback_address
from scion_sdk.mcp.upstreams.model import (
    UPSTREAM_BRIDGE_NOT_LOOPBACK,
    BridgeDecl,
    UpstreamDecl,
    UpstreamError,
)
from scion_sdk.mcp.upstreams.overlay import merge_overlay

from craft_suite_api.mcp_server import build_server
from craft_suite_api.upstreams import UPSTREAMS

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R006")

EXAMPLE = Path(__file__).resolve().parents[1] / "docs" / "bridge-upstreams.example.toml"


def test_example_bridge_overlay_validates_and_remote_address_refuses(
    monkeypatch, tmp_path
) -> None:
    # The shipped example holds one bridge entry: a loopback address and a
    # token reference, never a token value.
    entries = tomllib.loads(EXAMPLE.read_text(encoding="utf-8"))["upstream"]
    assert len(entries) == 1
    entry = entries[0]
    assert entry["name"] == "figcraft"
    assert entry["kind"] == "bridge"
    assert entry["bridge"]["address"] == "127.0.0.1:47001"
    assert is_loopback_address(entry["bridge"]["address"])
    assert entry["bridge"]["token_ref"] == "env://CRAFT_SUITE_BRIDGE_TOKEN"
    assert parse_secret_reference(entry["bridge"]["token_ref"]).scheme == "env"

    # The shipped example validates as an operator overlay: one app switches
    # to the bridge, the other ten stay stdio.
    merged = merge_overlay(UPSTREAMS, overlay_file=EXAMPLE, disabled=())
    by_name = {decl.name: decl for decl in merged}
    assert by_name["figcraft"].kind == "bridge"
    assert by_name["figcraft"].bridge is not None
    assert by_name["figcraft"].bridge.address == "127.0.0.1:47001"
    assert by_name["figcraft"].bridge.token_ref == "env://CRAFT_SUITE_BRIDGE_TOKEN"
    assert {decl.kind for decl in merged if decl.name != "figcraft"} == {"stdio"}

    # The served registry carries the switch, and lazy activation starts no app.
    for var in (
        "CRAFT_SUITE_API_BASE_URL",
        "CRAFT_SUITE_READ_ROOTS",
        "CRAFT_SUITE_WRITE_ROOTS",
        "SCION_UPSTREAMS_DISABLED",
        "SCION_UPSTREAM_ACTIVATION",
    ):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("SCION_UPSTREAMS_FILE", str(EXAMPLE))
    server = build_server(command_args=[])

    async def statuses() -> dict[str, dict]:
        async with Client(server) as client:
            result = await client.call_tool("registry_status", {})
        return {
            entry["namespace"]: entry for entry in result.structured_content["result"]
        }

    served = asyncio.run(statuses())
    assert len(served) == len(UPSTREAMS) == 16
    assert served["figcraft"]["kind"] == "bridge"
    assert {entry["state"] for entry in served.values()} == {"inactive"}

    # A non-loopback bridge address refuses before any token is read.
    base = next(decl for decl in UPSTREAMS if decl.name == "figcraft")
    remote_decl = UpstreamDecl(
        name=base.name,
        kind="bridge",
        command=base.command,
        args=base.args,
        sandbox=base.sandbox,
        bridge=BridgeDecl(
            address="192.168.1.5:47001",
            token_ref="env://CRAFT_SUITE_BRIDGE_TOKEN",
        ),
    )
    with pytest.raises(UpstreamError) as refused:
        build_bridge_command(
            remote_decl,
            resolver=EnvironmentCredentialResolver(),
            run_root=tmp_path / "run",
        )
    assert refused.value.code == UPSTREAM_BRIDGE_NOT_LOOPBACK

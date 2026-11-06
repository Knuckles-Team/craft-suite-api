"""CONN-CRAFT-SUITE-API-APPS-R005: an overlay switches one app to streamable HTTP."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from fastmcp import Client
from scion_sdk.mcp.upstreams.model import UPSTREAM_SECRET_LITERAL, UpstreamDeclError
from scion_sdk.mcp.upstreams.overlay import merge_overlay

from craft_suite_api.mcp_server import build_server
from craft_suite_api.upstreams import UPSTREAMS

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R005")

EXAMPLE = Path(__file__).resolve().parents[1] / "docs" / "remote-upstreams.example.toml"


def test_example_overlay_validates_and_switches_one_app_to_http(
    monkeypatch, tmp_path
) -> None:
    # The shipped example overlay validates against the sixteen declarations:
    # one app becomes http, ten stay stdio, and the http declaration is clean
    # of the stdio transport fields.
    merged = merge_overlay(UPSTREAMS, overlay_file=EXAMPLE, disabled=())
    assert len(merged) == 16
    by_name = {decl.name: decl for decl in merged}
    assert sum(decl.kind == "http" for decl in merged) == 1
    assert sum(decl.kind == "stdio" for decl in merged) == 15
    remote = by_name["photocraft"]
    assert remote.kind == "http"
    assert remote.url == "https://apps.example.invalid/photocraft/mcp"
    assert remote.credential == "env://CRAFT_SUITE_PHOTO_CRAFT_TOKEN"
    assert remote.tls_profile == "default"
    assert remote.command is None
    for name, decl in by_name.items():
        if name != "photocraft":
            assert decl.kind == "stdio"
            assert decl.command == f"{name}-cli"

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
    assert len(served) == 16
    assert served["photocraft"]["kind"] == "http"
    assert {
        entry["kind"] for entry in served.values() if entry["namespace"] != "photocraft"
    } == {"stdio"}
    assert {entry["state"] for entry in served.values()} == {"inactive"}

    # An overlay holding a literal credential refuses with UPSTREAM_SECRET_LITERAL.
    literal = tmp_path / "literal-credential.toml"
    literal.write_text(
        "[[upstream]]\n"
        'name = "photocraft"\n'
        'kind = "http"\n'
        'url = "https://apps.example.invalid/photocraft/mcp"\n'
        'credential = "a-literal-secret-value"\n',
        encoding="utf-8",
    )
    with pytest.raises(UpstreamDeclError) as refused:
        merge_overlay(UPSTREAMS, overlay_file=literal, disabled=())
    assert refused.value.__cause__ is not None
    assert UPSTREAM_SECRET_LITERAL in str(refused.value.__cause__)

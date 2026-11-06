"""CONN-CRAFT-SUITE-API-APPS-R017: every app engine command is its own tool."""

from __future__ import annotations

import asyncio
import json

import pytest
from fastmcp import Client, FastMCP

from craft_suite_api.app_commands import (
    DISPATCH,
    MAX_NAME,
    AppCommandProvider,
    HideDispatchTools,
    build_command_tools,
    command_tool_name,
    dispatch_tool_names,
    parse_registry,
    signature_properties,
)
from craft_suite_api.upstreams import APPS

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R017")

PHOTO_RUN_SCHEMA = {
    "type": "object",
    "properties": {"id": {"type": "string"}, "params": {}, "wait": {}},
    "required": ["id"],
}


def test_every_declared_app_has_a_dispatch_entry() -> None:
    assert set(DISPATCH) == set(APPS)
    hidden = dispatch_tool_names(APPS)
    assert "photocraft_command_run" in hidden
    assert "wordcraft_execute" in hidden
    assert "lightcraft_run_command" in hidden
    # lightcraft's own MCP already serves one tool per command.
    assert DISPATCH["lightcraft"].generate is False


def test_registry_forms_parse() -> None:
    listing = [{"id": "file.new", "params": "{name?: str}"}, {"id": "file.new"}]
    assert [e["id"] for e in parse_registry(json.dumps(listing))] == ["file.new"]
    wrapped = {"commands": [{"id": "a.b"}, {"id": "c.d", "planned": True}]}
    assert [e["id"] for e in parse_registry(json.dumps(wrapped))] == ["a.b"]
    # A JSON listing followed by more text still parses.
    assert parse_registry(json.dumps(listing) + "\n[]\n")[0]["id"] == "file.new"
    text = (
        "2 commands (id — label [menu] (shortcut) params; * = undoable):\n"
        "node.create* — Create layer {type: rectangle|ellipse, x?, y?}\n"
        "view.zoomIn — Zoom In\n"
    )
    entries = parse_registry(text)
    assert [e["id"] for e in entries] == ["node.create", "view.zoomIn"]
    assert entries[0]["undoable"] is True
    assert entries[0]["params"] == "{type: rectangle|ellipse, x?, y?}"
    assert (
        parse_registry(json.dumps({"commands": []}), {"commands": [{"id": "s"}]})[0][
            "id"
        ]
        == "s"
    )
    assert parse_registry("not a listing") == []


def test_signature_names_parameters() -> None:
    props = signature_properties(
        '{"width":1..300000=1920,"mode":"rgb|gray"="rgb", name?: str, '
        "size?: [w,h] pt, opts?: {a, b}}"
    )
    assert list(props) == ["width", "mode", "name", "size", "opts"]
    assert props["size"]["description"] == "size?: [w,h] pt"
    assert signature_properties("{text, raw?, paragraphs?} (each line)") == {
        "text": {"description": "text"},
        "raw": {"description": "raw?"},
        "paragraphs": {"description": "paragraphs?"},
    }
    assert signature_properties("plane: XY|XZ") == {}
    assert signature_properties(None) == {}


def test_names_are_unique_and_bounded() -> None:
    taken: set[str] = set()
    assert (
        command_tool_name("photocraft", "file.new", taken) == "photocraft_cmd_file_new"
    )
    clash = command_tool_name("photocraft", "file-new", taken)
    assert clash != "photocraft_cmd_file_new" and clash.startswith(
        "photocraft_cmd_file_new"
    )
    long = command_tool_name("vectorcraft", "x." * 60, taken)
    assert len(long) <= MAX_NAME


def test_listing_stays_within_a_gateway_response() -> None:
    # A gateway reads tools/list as one response (8 MiB SSE cap); the largest
    # registry (about 1000 commands) must stay far below its share of it.
    entries = [
        {
            "id": f"cmd.n{i}",
            "label": "x" * 40,
            "params": "{" + "a?: " + "y" * 3000 + "}",
        }
        for i in range(1000)
    ]
    tools = build_command_tools(
        "photocraft", DISPATCH["photocraft"], entries, PHOTO_RUN_SCHEMA
    )
    size = sum(
        len(
            json.dumps(
                t.to_mcp_tool().model_dump(
                    mode="json", by_alias=True, exclude_none=True
                )
            )
        )
        for t in tools
    )
    assert size < 1_500_000, size


def test_schemas_carry_the_documented_parameters() -> None:
    entries = [
        {"id": "file.new", "label": "New", "params": "{width?: px, height?: px}"},
        {
            "id": "comp.new",
            "schema": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
    ]
    tools = {
        t.name: t
        for t in build_command_tools(
            "photocraft", DISPATCH["photocraft"], entries, PHOTO_RUN_SCHEMA
        )
    }
    new = tools["photocraft_cmd_file_new"]
    assert set(new.parameters["properties"]) == {"width", "height", "wait"}
    assert "Params: {width?: px, height?: px}" in new.description
    assert "ns:photocraft" in new.tags
    assert new.meta == {
        "scion/upstream": {"namespace": "photocraft", "upstream": "photocraft"}
    }
    # Names only: the fragments live once, in the description.
    assert new.parameters["properties"]["width"] == {}
    typed = tools["photocraft_cmd_comp_new"]
    assert typed.parameters["properties"]["name"] == {"type": "string"}
    assert typed.parameters["required"] == ["name"]


async def _serve_and_call():
    calls: list[dict] = []
    server = FastMCP("fixture")

    @server.tool(name="photocraft_command_run")
    def run(id: str, params: dict | None = None, wait: bool | None = None) -> dict:
        calls.append({"id": id, "params": params, "wait": wait})
        return {"ok": True, "id": id}

    provider = AppCommandProvider({})
    entries = [{"id": "file.new", "params": "{width?: px}"}]
    for tool in build_command_tools(
        "photocraft", DISPATCH["photocraft"], entries, PHOTO_RUN_SCHEMA
    ):
        provider._tools[tool.name] = tool
    provider._apps = {"photocraft": ("photocraft-cli", "mcp")}
    provider._loading = asyncio.ensure_future(asyncio.sleep(0))
    server.add_provider(provider)
    server.add_transform(HideDispatchTools(["photocraft_command_run"]))
    async with Client(server) as client:
        names = {t.name for t in await client.list_tools()}
        result = await client.call_tool(
            "photocraft_cmd_file_new", {"width": 64, "wait": True}
        )
    return names, result, calls


def test_command_tool_forwards_to_the_hidden_dispatch_tool() -> None:
    names, result, calls = asyncio.run(_serve_and_call())
    assert "photocraft_cmd_file_new" in names
    assert "photocraft_command_run" not in names
    assert calls == [{"id": "file.new", "params": {"width": 64}, "wait": True}]
    assert result.structured_content == {"ok": True, "id": "file.new"}


def test_an_app_without_a_binary_serves_no_command_tools(monkeypatch) -> None:
    monkeypatch.setenv("PATH", "/nonexistent")
    provider = AppCommandProvider({"photocraft": ("photocraft-cli", "mcp")})
    tools = asyncio.run(provider._list_tools())
    assert tools == []
    assert provider.counts == {"photocraft": 0}

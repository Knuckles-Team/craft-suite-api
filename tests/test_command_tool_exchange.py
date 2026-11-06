"""CONN-CRAFT-SUITE-API-APPS-R020: command tools run their own arguments through the exchange.

A command tool nests its arguments under the dispatch tool's ``params``,
where the exchange of the dispatch tool cannot see them. The command tool
therefore stages inputs, places relative outputs in the run and publishes
what the command wrote, and awaits a background job before publishing. The
app is a fake dispatch tool at the outbound boundary; the SDK exchange and
its filesystem stores run for real.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest
from fastmcp import Client, FastMCP

from craft_suite_api import app_commands
from craft_suite_api.app_commands import DISPATCH, build_command_tools

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R020")

RUN = {"type": "object", "properties": {"id": {}, "params": {}}}


@pytest.fixture
def exchange(monkeypatch, tmp_path):
    document = {
        "stores": {"objects": {"backend": "filesystem", "root": str(tmp_path / "o")}},
        "sinks": [
            {
                "name": "objects",
                "store": "objects",
                "bucket": "artcraft",
                "path_template": "{namespace}/{run}/{name}",
                "required": True,
            }
        ],
    }
    (tmp_path / "o" / "artcraft" / "in").mkdir(parents=True)
    (tmp_path / "o" / "artcraft" / "in" / "clip.mp4").write_bytes(b"clip-bytes")
    settings = tmp_path / "exchange.json"
    settings.write_text(json.dumps(document))
    monkeypatch.setenv("SCION_EXCHANGE_FILE", str(settings))
    monkeypatch.setenv("SCION_EXCHANGE_STAGING_ROOT", str(tmp_path / "staging"))
    monkeypatch.setattr(app_commands, "_EXCHANGE_RUNTIME", app_commands._UNSET)
    yield tmp_path
    monkeypatch.setattr(app_commands, "_EXCHANGE_RUNTIME", app_commands._UNSET)


def _server(entries, app, run):
    server = FastMCP("fixture")
    server.tool(name=f"{app}_{DISPATCH[app].run_tool}")(run)
    for tool in build_command_tools(app, DISPATCH[app], entries, RUN):
        server.add_tool(tool)
    return server


def test_nested_paths_are_staged_placed_and_published(exchange) -> None:
    seen: dict = {}

    def run(id: str, params: dict | None = None) -> dict:
        seen.update(params or {})
        Path(params["path"]).write_bytes(
            b"rendered:" + Path(params["src"]).read_bytes()
        )
        return {"path": params["path"]}

    entries = [{"id": "file.saveACopy", "params": "{path: str, src: str}"}]
    server = _server(entries, "photocraft", run)

    async def scenario():
        async with Client(server) as client:
            return await client.call_tool(
                "photocraft_cmd_file_saveACopy",
                {"src": "exchange://objects/in/clip.mp4", "path": "out/copy.png"},
                meta={"scion/run": "run-1"},
            )

    result = asyncio.run(scenario())
    staging = exchange / "staging"
    # The input was staged and the relative output placed inside the run.
    assert Path(seen["src"]).is_relative_to(staging)
    assert Path(seen["path"]).is_relative_to(staging)
    assert seen["path"].endswith("run-1/out/copy.png")
    published = (
        exchange / "o" / "artcraft" / "photocraft" / "run-1" / "out" / "copy.png"
    )
    assert published.read_bytes() == b"rendered:clip-bytes"
    artifacts = result.meta["scion/artifacts"]
    assert [a["name"] for a in artifacts] == ["out/copy.png"]


def test_a_background_job_is_awaited_before_its_output_is_published(
    exchange, monkeypatch
) -> None:
    monkeypatch.setattr(app_commands, "JOB_WAIT_S", 30.0)
    state = {"polls": 0, "path": None}

    def run(id: str, params: dict | None = None) -> object:
        if id == "file.exportMedia":
            state["path"] = params["path"]
            return {"job": 7, "poll": "jobs.list", "path": params["path"]}
        assert id == "jobs.list"
        state["polls"] += 1
        if state["polls"] < 2:
            return [{"id": 7, "finished": False, "progress": 0.5}]
        Path(state["path"]).write_bytes(b"mp4")
        return [{"id": 7, "finished": True, "result": {"path": state["path"]}}]

    entries = [{"id": "file.exportMedia", "params": '{"path":str}'}]
    server = _server(entries, "filmcraft", run)

    async def scenario():
        async with Client(server) as client:
            return await client.call_tool(
                "filmcraft_cmd_file_exportMedia",
                {"path": "promo.mp4"},
                meta={"scion/run": "run-2"},
            )

    result = asyncio.run(scenario())
    assert state["polls"] == 2
    assert result.structured_content["finished"] is True
    assert [a["name"] for a in result.meta["scion/artifacts"]] == ["promo.mp4"]
    published = exchange / "o" / "artcraft" / "filmcraft" / "run-2" / "promo.mp4"
    assert published.read_bytes() == b"mp4"


def test_a_failed_job_answers_an_error(exchange, monkeypatch) -> None:
    def run(id: str, params: dict | None = None) -> object:
        if id == "file.exportMedia":
            return {"job": 1, "poll": "jobs.list"}
        return [{"id": 1, "finished": True, "result": {"error": "I/O: denied"}}]

    entries = [{"id": "file.exportMedia", "params": '{"path":str}'}]
    server = _server(entries, "filmcraft", run)

    async def scenario():
        async with Client(server) as client:
            return await client.call_tool(
                "filmcraft_cmd_file_exportMedia",
                {"path": "promo.mp4"},
                raise_on_error=False,
            )

    result = asyncio.run(scenario())
    assert result.is_error
    assert "I/O: denied" in result.content[0].text


def test_only_real_output_paths_move_into_the_run() -> None:
    from craft_suite_api.app_commands import output_path_args

    assert output_path_args(
        {
            "output": "title-card.mp4",  # effectcraft renderQueue.add
            "path": "work",  # photocraft: a vector path's name, not a file
            "dir": "frames",
            "outputDir": "fill",
            "src": "exchange://objects/in/a.png",
            "file": "/abs/lut.cube",
            "size": 12,
        }
    ) == ("output", "dir", "outputDir")


def test_app_tools_keep_non_file_paths(exchange) -> None:
    import asyncio as _asyncio

    from fastmcp.server.providers.proxy import ProxyTool
    from scion_sdk.mcp.upstreams.exchange import ExchangeProxyTool

    from craft_suite_api.app_commands import ExchangeOutputPaths
    from craft_suite_api.upstreams import UPSTREAMS

    decl = next(d for d in UPSTREAMS if d.name == "effectcraft")
    runtime = app_commands._exchange_runtime()
    proxy = ProxyTool(lambda: None, name="effectcraft_set_property", parameters={})
    native = ExchangeProxyTool.bind(proxy, decl, runtime)

    async def call_next(name, version=None):
        return native

    wrapped = _asyncio.run(ExchangeOutputPaths().get_tool("x", call_next))
    assert isinstance(wrapped, ExchangeProxyTool) and wrapped is not native
    wrapped._call_path_args = app_commands.output_path_args(
        {"path": "transform/opacity", "value": 50}
    )
    assert wrapped._spec().path_args == ()
    wrapped._call_path_args = app_commands.output_path_args({"path": "frame.png"})
    assert wrapped._spec().path_args == ("path",)


def test_root_relative_apps_get_paths_relative_to_their_roots(exchange) -> None:
    from craft_suite_api.app_commands import ROOT_RELATIVE_APPS, root_relative

    runtime = app_commands._exchange_runtime()
    staging = exchange / "staging"
    assert {"materialcraft", "texturecraft"} <= ROOT_RELATIVE_APPS
    assert root_relative(
        {
            "dir": str(staging / "out" / "materialcraft" / "run-3" / "metal"),
            "path": str(staging / "in" / "texturecraft" / "run-3" / "shade.glb"),
            "paths": [str(staging / "out" / "x" / "a.png")],
            "name": "keep",
            "other": "/elsewhere/file.png",
        },
        runtime,
    ) == {
        "dir": "materialcraft/run-3/metal",
        "path": "texturecraft/run-3/shade.glb",
        "paths": ["x/a.png"],
        "name": "keep",
        "other": "/elsewhere/file.png",
    }

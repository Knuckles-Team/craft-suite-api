"""CONN-CRAFT-SUITE-API-APPS-R013..R016: the ArtCraft apps run through the SDK artifact exchange."""

from __future__ import annotations

import asyncio
import dataclasses
import json
from pathlib import Path

import pytest
from fastmcp import Client
from scion_sdk.exchange.config import read_exchange_settings, render_key

import craft_suite_api
from craft_suite_api.mcp_server import build_server
from craft_suite_api.upstreams import APPS, UPSTREAMS, build_upstreams

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "docs" / "exchange.example.json"


@pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R013")
def test_every_app_declares_the_exchange_binding() -> None:
    assert len(UPSTREAMS) == len(APPS) == 11
    for decl in UPSTREAMS:
        assert decl.exchange is not None
        assert decl.exchange.path_args == ("path", "dir", "out", "out_dir")


@pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R014")
def test_example_exchange_file_validates_and_renders_app_folders(monkeypatch) -> None:
    monkeypatch.setenv("SCION_EXCHANGE_FILE", str(EXAMPLE))
    settings = read_exchange_settings()
    assert settings is not None
    files = settings.sink("files")
    assert files is not None and files.bucket == "ArtCraft"
    key = render_key(
        files,
        namespace="photocraft",
        tool="doc_save",
        run="run1",
        name="out.png",
        date="2026-11-04",
    )
    assert key == "photocraft/2026-11-04/run1/out.png"
    objects = settings.sink("objects")
    assert (
        objects is not None and objects.required and objects.signed_url_ttl_s == 604800
    )
    for store in json.loads(EXAMPLE.read_text())["stores"].values():
        for reference in store.get("credentials", {}).values():
            assert reference.startswith(("env://", "openbao://"))


@pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R015")
@pytest.mark.timeout(300)
def test_fixture_app_reads_exchange_input_and_publishes_output(
    app_cli_factory, monkeypatch, tmp_path
) -> None:
    for var in (
        "CRAFT_SUITE_API_BASE_URL",
        "CRAFT_SUITE_READ_ROOTS",
        "CRAFT_SUITE_WRITE_ROOTS",
        "SCION_UPSTREAMS_FILE",
        "SCION_UPSTREAM_ACTIVATION",
    ):
        monkeypatch.delenv(var, raising=False)
    document = {
        "stores": {
            "objects": {"backend": "filesystem", "root": str(tmp_path / "objects")},
            "files": {"backend": "filesystem", "root": str(tmp_path / "share")},
        },
        "sinks": [
            {
                "name": "objects",
                "store": "objects",
                "bucket": "artcraft",
                "path_template": "artcraft/{namespace}/{date}/{run}/{name}",
                "required": True,
            },
            {"name": "files", "store": "files", "bucket": "ArtCraft"},
        ],
    }
    (tmp_path / "share" / "ArtCraft" / "in").mkdir(parents=True)
    (tmp_path / "share" / "ArtCraft" / "in" / "a.png").write_bytes(b"png-bytes")
    settings_file = tmp_path / "exchange.json"
    settings_file.write_text(json.dumps(document))
    monkeypatch.setenv("SCION_EXCHANGE_FILE", str(settings_file))
    monkeypatch.setenv("SCION_EXCHANGE_STAGING_ROOT", str(tmp_path / "staging"))
    app_cli_factory("alpha", files=True)
    monkeypatch.setattr(craft_suite_api.upstreams, "APPS", ("alpha",))
    monkeypatch.setattr(
        craft_suite_api,
        "connector",
        dataclasses.replace(craft_suite_api.connector, upstreams=build_upstreams()),
    )
    server = build_server(command_args=[])

    async def scenario():
        async with Client(server) as client:
            await client.call_tool("registry_activate", {"namespace": "alpha"})
            return await client.call_tool(
                "alpha_copy",
                {"src": "exchange://files/in/a.png", "path": "out.png"},
                meta={"scion/run": "run-1"},
            )

    result = asyncio.run(scenario())
    links = [block for block in result.content if block.type == "resource_link"]
    assert len(links) == 1
    share = list((tmp_path / "share" / "ArtCraft" / "alpha").rglob("run-1/out.png"))
    objects = list(
        (tmp_path / "objects" / "artcraft" / "artcraft" / "alpha").rglob(
            "run-1/out.png"
        )
    )
    assert share and share[0].read_bytes() == b"png-bytes"
    assert objects and objects[0].read_bytes() == b"png-bytes"


@pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R016")
def test_every_app_skill_states_input_forms_and_output_links() -> None:
    for app in APPS:
        text = (ROOT / "craft_suite_api" / "skills" / app / "SKILL.md").read_text()
        assert "## Files in and out" in text
        assert "exchange://<sink>/<key>" in text and "https" in text
        assert "relative path" in text and "links each output" in text


@pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R014")
def test_mcp_extra_carries_the_s3_sink_backend() -> None:
    import tomllib

    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    for extra in ("mcp", "all"):
        pins = " ".join(project["optional-dependencies"][extra])
        assert "scion-sdk[mcp,storage-s3]" in pins
    assert "craft-suite-api[mcp]==" in (ROOT / "docker" / "Dockerfile").read_text()

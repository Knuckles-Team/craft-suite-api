"""CONN-CRAFT-SUITE-API-APPS-R018: each app warms on its own; startup never blocks.

The registries are faked at the outbound boundary (``_read_registry``, the
stdio child); the provider, the session tracker, the forwarding, the
refusals and the readiness probe run for real behind a fastmcp server.
"""

from __future__ import annotations

import asyncio
import time

import pytest
from fastmcp import Client, FastMCP
from mcp.client.subscriptions import listen
from mcp.server.subscriptions import ToolsListChanged
from scion_sdk.mcp.change_events import serve_change_subscriptions

from craft_suite_api import _tier1_readiness, app_commands
from craft_suite_api.app_commands import (
    APP_REGISTRY_UNREADABLE,
    APP_WARMING,
    DISPATCH,
    AppCommandProvider,
    HideDispatchTools,
    SessionTracker,
    build_command_tools,
)

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R018")

RUN_SCHEMA = {
    "type": "object",
    "properties": {"id": {"type": "string"}, "params": {}},
    "required": ["id"],
}


class FakeRegistries:
    """Per-app registry reads: a gate per app, or a failure count."""

    def __init__(self, gates: dict[str, asyncio.Event], failures: dict[str, int]):
        self.gates = gates
        self.failures = dict(failures)
        self.reads: dict[str, int] = {}

    async def __call__(self, app, command, dispatch):
        self.reads[app] = self.reads.get(app, 0) + 1
        if self.failures.get(app, 0) > 0:
            self.failures[app] -= 1
            raise RuntimeError(f"{app} registry unreadable")
        if app in self.gates:
            await self.gates[app].wait()
        entries = [{"id": "file.new", "params": "{width?: px}"}]
        return build_command_tools(app, DISPATCH[app], entries, RUN_SCHEMA)


def _server(fake, monkeypatch, *, wait_s=0.2, retry_s=0.05, apps=None):
    monkeypatch.setattr(app_commands, "_read_registry", fake)
    calls: list[tuple[str, str]] = []
    server = FastMCP("fixture")
    apps = apps or ("photocraft", "filmcraft", "pdfcraft")
    for app in apps:

        def run(id: str, params: dict | None = None, _app: str = app) -> dict:
            calls.append((_app, id))
            return {"ok": True, "app": _app, "id": id}

        server.tool(name=f"{app}_{DISPATCH[app].run_tool}")(run)
    serve_change_subscriptions(server)
    tracker = SessionTracker(server)
    server.add_middleware(tracker)
    provider = AppCommandProvider(
        {app: (f"{app}-cli", "mcp") for app in apps},
        tracker=tracker,
        wait_s=wait_s,
        retry_s=retry_s,
        retries=2,
    )
    server.add_provider(provider)
    server.add_transform(
        HideDispatchTools([f"{app}_{DISPATCH[app].run_tool}" for app in apps])
    )
    return server, provider, calls


def test_listing_answers_at_once_and_each_app_lands_with_list_changed(
    monkeypatch,
) -> None:
    async def scenario():
        film_gate = asyncio.Event()
        fake = FakeRegistries({"filmcraft": film_gate}, {})
        server, provider, _ = _server(fake, monkeypatch)
        async with Client(server) as client:
            started = time.monotonic()
            await client.list_tools()
            # The listing never waits for the warming app.
            assert time.monotonic() - started < 1.0
            for _ in range(50):
                if provider.warmup.states["photocraft"] == "Ready":
                    break
                await asyncio.sleep(0.01)
            first = {t.name for t in await client.list_tools()}
            assert "photocraft_cmd_file_new" in first
            assert "filmcraft_cmd_file_new" not in first
            assert provider.warmup.states["filmcraft"] == "warming"
            async with listen(client.session, tools_list_changed=True) as sub:
                film_gate.set()
                event = await asyncio.wait_for(sub.__anext__(), 5)
            assert isinstance(event, ToolsListChanged)
            later = {t.name for t in await client.list_tools()}
            assert "filmcraft_cmd_file_new" in later

    asyncio.run(scenario())


def test_a_call_to_a_warming_app_waits_then_refuses_retryable(monkeypatch) -> None:
    async def scenario():
        gate = asyncio.Event()
        fake = FakeRegistries({"filmcraft": gate}, {})
        server, provider, calls = _server(fake, monkeypatch, wait_s=0.2)
        async with Client(server) as client:
            started = time.monotonic()
            result = await client.call_tool(
                "filmcraft_cmd_file_new", {}, raise_on_error=False
            )
            waited = time.monotonic() - started
            assert 0.15 <= waited < 2.0, waited
            assert result.is_error
            assert result.structured_content["code"] == APP_WARMING
            assert result.structured_content["retryable"] is True
            assert result.structured_content["retry_after_s"] > 0
            assert calls == []
            # The other apps serve meanwhile.
            ok = await client.call_tool("photocraft_cmd_file_new", {"width": 8})
            assert ok.structured_content == {
                "ok": True,
                "app": "photocraft",
                "id": "file.new",
            }

    asyncio.run(scenario())


def test_a_call_that_lands_inside_the_wait_is_served(monkeypatch) -> None:
    async def scenario():
        gate = asyncio.Event()
        fake = FakeRegistries({"filmcraft": gate}, {})
        server, _, calls = _server(fake, monkeypatch, wait_s=5.0)
        async with Client(server) as client:
            asyncio.get_running_loop().call_later(0.1, gate.set)
            result = await client.call_tool("filmcraft_cmd_file_new", {})
            assert result.structured_content["app"] == "filmcraft"
            assert calls == [("filmcraft", "file.new")]

    asyncio.run(scenario())


def test_one_failed_app_never_blocks_the_others_and_is_retried(monkeypatch) -> None:
    async def scenario():
        fake = FakeRegistries({}, {"pdfcraft": 1})
        server, provider, _ = _server(fake, monkeypatch, retry_s=0.3)
        async with Client(server) as client:
            for _ in range(100):
                if provider.warmup.settled:
                    break
                await asyncio.sleep(0.01)
            assert provider.warmup.states == {
                "photocraft": "Ready",
                "filmcraft": "Ready",
                "pdfcraft": "Degraded",
            }
            refused = await client.call_tool(
                "pdfcraft_cmd_file_new", {}, raise_on_error=False
            )
            assert refused.is_error
            assert refused.structured_content["code"] == APP_REGISTRY_UNREADABLE
            assert refused.structured_content["retryable"] is True
            # The background retry loads it.
            for _ in range(200):
                if provider.warmup.states["pdfcraft"] == "Ready":
                    break
                await asyncio.sleep(0.01)
            assert provider.warmup.states["pdfcraft"] == "Ready"
            assert fake.reads["pdfcraft"] == 2
            names = {t.name for t in await client.list_tools()}
            assert "pdfcraft_cmd_file_new" in names

    asyncio.run(scenario())


def test_readiness_waits_for_every_app_to_settle(monkeypatch) -> None:
    monkeypatch.delenv("CRAFT_SUITE_API_BASE_URL", raising=False)

    async def scenario():
        gate = asyncio.Event()
        fake = FakeRegistries({"filmcraft": gate}, {"pdfcraft": 5})
        server, provider, _ = _server(fake, monkeypatch, retry_s=10.0)
        async with Client(server) as client:
            await client.list_tools()
            for _ in range(100):
                if provider.warmup.states["pdfcraft"] == "Backoff":
                    break
                await asyncio.sleep(0.01)
            warming = await _tier1_readiness()
            assert warming.ready is False
            assert warming.detail["apps_warming"] == "filmcraft"
            assert warming.detail["apps_failed"] == "pdfcraft"
            gate.set()
            for _ in range(100):
                if provider.warmup.settled:
                    break
                await asyncio.sleep(0.01)
            settled = await _tier1_readiness()
            # A failed app never holds readiness.
            assert settled.ready is True
            assert settled.detail["apps_ready"] == 2
            assert settled.detail["apps_warming"] == ""
            assert settled.detail["app_command_tools"] == 2

    try:
        asyncio.run(scenario())
    finally:
        monkeypatch.setattr(app_commands, "WARMUP", None)

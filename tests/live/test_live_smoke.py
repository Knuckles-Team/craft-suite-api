"""CONN-CRAFT-SUITE-API-APPS-R009: the opt-in live smoke against the real app CLIs.

Runs only on a host that carries the Phase 1 app command-line programs, and
only when ``CRAFT_SUITE_LIVE=1``. Each Phase 1 app is activated through the
production server and must list exactly its snapshot tool count — the same
numbers the content tier committed (``content/snapshots/<app>.tools.json``).
The CI gate never needs the real CLIs: without the setting the test skips.
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SNAPSHOTS = REPO / "content" / "snapshots"

#: The Phase 1 apps, per CONN-CRAFT-SUITE-API-APPS-R009.
APPS = ("photocraft", "wordcraft", "solidcraft")

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R009")


def _clis_present() -> tuple[str, ...]:
    """The app CLIs the host does not carry."""
    return tuple(app for app in APPS if shutil.which(f"{app}-cli") is None)


@pytest.fixture
def live_host():
    if os.environ.get("CRAFT_SUITE_LIVE") != "1":
        pytest.skip("live smoke is opt-in: set CRAFT_SUITE_LIVE=1")
    missing = _clis_present()
    if missing:
        pytest.skip(
            f"host does not carry: {', '.join(f'{name}-cli' for name in missing)}"
        )
    yield


def test_each_activated_app_lists_its_snapshot_tool_count(live_host) -> None:
    from fastmcp import Client

    from craft_suite_api.mcp_server import build_server

    async def smoke() -> dict[str, int]:
        async with Client(build_server(command_args=[]), mode="legacy") as client:
            counts: dict[str, int] = {}
            for app in APPS:
                result = await client.call_tool("registry_activate", {"namespace": app})
                assert result.is_error is False, app
                tools = await client.list_tools()
                counts[app] = len(
                    {tool.name for tool in tools if tool.name.startswith(f"{app}_")}
                )
        return counts

    counts = asyncio.run(smoke())
    for app in APPS:
        snapshot = json.loads(
            (SNAPSHOTS / f"{app}.tools.json").read_text(encoding="utf-8")
        )
        assert counts[app] == len(snapshot["tools"]), (
            f"{app}: live {counts[app]} tools, snapshot {len(snapshot['tools'])}"
        )

"""Probe the ArtCraft app CLIs for MCP support (CONN-CRAFT-SUITE-API-APPS-R003).

The suite declares the apps that expose an ``mcp`` subcommand. This probe
re-checks the declared apps and the not-yet-declared names after each app
update. It prints one JSON result per app, writes no file, and exits
non-zero when the declared set has drifted from what the hosts carry: a
declared app that no longer exposes ``mcp`` or an undeclared app that now
does.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import sys
from collections.abc import Sequence
from typing import Any

from scion_sdk.config import setting

from .upstreams import APPS

#: The names the suite may declare later, re-probed on every run.
REPROBED = ("lightcraft", "designcraft", "gridcraft")

#: A binary the suite expects but the host does not carry.
APP_CLI_NOT_FOUND = "APP_CLI_NOT_FOUND"
#: A binary that does not answer the MCP handshake over ``mcp``.
APP_NO_MCP = "APP_NO_MCP"

TIMEOUT_DEFAULT_S = 20
TIMEOUT_MIN_S = 5
TIMEOUT_MAX_S = 120

__all__ = [
    "APP_CLI_NOT_FOUND",
    "APP_NO_MCP",
    "REPROBED",
    "main",
    "probe_app",
    "probe_suite",
]


def resolve_timeout(cli_value: float | None) -> float:
    """The probe timeout: the CLI flag, else the setting, else the start value."""
    if cli_value is not None:
        value = cli_value
    else:
        raw = setting("CRAFT_SUITE_PROBE_TIMEOUT_S", "")
        value = float(raw) if raw else float(TIMEOUT_DEFAULT_S)
    if not TIMEOUT_MIN_S <= value <= TIMEOUT_MAX_S:
        raise ValueError(
            f"probe timeout must be within {TIMEOUT_MIN_S}..{TIMEOUT_MAX_S} seconds"
        )
    return value


async def probe_app(app: str, timeout_s: float) -> dict[str, Any]:
    """One app: the handshake result, or the refusal code for a bad binary.

    The child runs ``<app>-cli mcp`` with no root flags, exactly as the
    registry would start it; the handshake and the tool list prove the MCP
    surface, not the banner.
    """
    binary = shutil.which(f"{app}-cli")
    if binary is None:
        return {"app": app, "exposes_mcp": False, "code": APP_CLI_NOT_FOUND}
    from fastmcp import Client
    from fastmcp.client.transports import StdioTransport

    try:
        # env=os.environ keeps the child a normal operator child: the stdio
        # transport sanitizes the child environment when env is None.
        async with Client(
            StdioTransport(binary, ["mcp"], env=os.environ.copy()),
            timeout=timeout_s,
            mode="legacy",
        ) as client:
            info = await client.session.initialize()
            tools = await client.list_tools()
    except Exception:
        return {"app": app, "exposes_mcp": False, "code": APP_NO_MCP}
    return {
        "app": app,
        "exposes_mcp": True,
        "version": info.server_info.version,
        "tool_count": len(tools),
    }


async def probe_suite(apps: Sequence[str], timeout_s: float) -> list[dict[str, Any]]:
    """One result per app, in the order given."""
    return [await probe_app(app, timeout_s) for app in apps]


def main(argv: Sequence[str] | None = None) -> int:
    """Run the probe over the declared apps plus the re-probed names.

    The results and the drift notes go to stderr: this module lives in the
    served package, whose stdout stays free for the stdio JSON-RPC channel
    (the stdout-writes gate). The console script is the operator surface.
    """
    parser = argparse.ArgumentParser(
        prog="craft-suite-probe",
        description="Report which ArtCraft app CLIs expose an MCP surface.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help=(
            f"handshake timeout in seconds "
            f"({TIMEOUT_MIN_S}..{TIMEOUT_MAX_S}); the setting "
            f"CRAFT_SUITE_PROBE_TIMEOUT_S otherwise"
        ),
    )
    args = parser.parse_args(argv)
    try:
        timeout_s = resolve_timeout(args.timeout)
    except ValueError as exc:
        parser.error(str(exc))
    results = asyncio.run(probe_suite((*APPS, *REPROBED), timeout_s))
    for result in results:
        print(json.dumps(result, sort_keys=True), file=sys.stderr)
    declared = set(APPS)
    for result in results:
        drifted = (result["app"] in declared) != bool(result["exposes_mcp"])
        if not drifted:
            continue
        state = "exposes" if result["exposes_mcp"] else "no longer exposes"
        kind = "declared" if result["app"] in declared else "undeclared"
        print(f"{kind} app {result['app']} {state} mcp", file=sys.stderr)
    return (
        1
        if any(
            (result["app"] in declared) != bool(result["exposes_mcp"])
            for result in results
        )
        else 0
    )

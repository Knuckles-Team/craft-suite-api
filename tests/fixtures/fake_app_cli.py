#!/usr/bin/env python
"""A fixture app command-line program for the facade gates.

It serves an MCP surface on ``mcp`` over stdio with one read tool
(``read_demo``), one write tool (``write_demo``, which elicits a
confirmation once) and one eliciting tool (``ask_once``). Test knobs are
environment variables:

- ``FAKE_APP_CLI_APP``         the app name (default: the program stem)
- ``FAKE_APP_CLI_VERSION``     the reported server version
- ``FAKE_APP_CLI_ARGV_FILE``   appends the full argv as one JSON line
- ``FAKE_APP_CLI_NO_MCP``      ``1``: refuse the ``mcp`` subcommand
- ``FAKE_APP_CLI_DIE_ON_MCP``  ``1``: exit at once, before the handshake
- ``FAKE_APP_CLI_TOOL_DRIFT``  ``1``: give ``read_demo`` an extra parameter
- ``FAKE_APP_CLI_FILES``       ``1``: also serve ``copy`` (read ``src``, write ``path``)

The tests place one copy per app on the PATH under the name
``<app>-cli`` and point the registry overlay at the copy.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys

from fastmcp import Context, FastMCP


def _argv_file() -> str | None:
    return os.environ.get("FAKE_APP_CLI_ARGV_FILE")


def _register_files(mcp: FastMCP) -> None:
    """Serve ``copy`` when ``FAKE_APP_CLI_FILES=1`` (the artifact exchange proof)."""
    if os.environ.get("FAKE_APP_CLI_FILES") != "1":
        return

    @mcp.tool
    def copy(src: str, path: str) -> str:
        """Copy the file at ``src`` to ``path``."""
        target = pathlib.Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(pathlib.Path(src).read_bytes())
        return f"copied:{target.name}"


def main() -> int:
    app = os.environ.get("FAKE_APP_CLI_APP") or pathlib.Path(sys.argv[0]).stem
    if app.endswith("-cli"):
        app = app.removesuffix("-cli")
    argv_file = _argv_file()
    if argv_file:
        with open(argv_file, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(sys.argv[1:]) + "\n")

    if os.environ.get("FAKE_APP_CLI_NO_MCP") == "1":
        print(f"{app}-cli: no mcp subcommand in this fixture", file=sys.stderr)
        return 2
    if len(sys.argv) < 2 or sys.argv[1] != "mcp":
        print(f"usage: {app}-cli mcp", file=sys.stderr)
        return 2
    if os.environ.get("FAKE_APP_CLI_DIE_ON_MCP") == "1":
        print(f"{app}-cli: fixture dies before the handshake", file=sys.stderr)
        return 1

    mcp = FastMCP(
        app,
        version=os.environ.get("FAKE_APP_CLI_VERSION", "0.0.1"),
    )

    drift = os.environ.get("FAKE_APP_CLI_TOOL_DRIFT") == "1"

    if drift:

        @mcp.tool
        def read_demo(value: str, extra: str = "", drifted: str = "") -> dict[str, str]:
            """Read tool of the fixture app (drifted input schema)."""
            return {"value": value, "extra": extra, "drifted": drifted}

    else:

        @mcp.tool
        def read_demo(value: str, extra: str = "") -> dict[str, str]:
            """Read tool of the fixture app."""
            return {"value": value, "extra": extra}

    @mcp.tool
    async def write_demo(ctx: Context, value: str) -> dict[str, str]:
        """Write tool of the fixture app; confirms through elicitation once."""
        result = await ctx.elicit(
            f"Confirm writing {value!r}?",
            {"answer": {"type": "boolean"}},
            response_title="Write confirmation",
        )
        if getattr(result, "action", None) != "accept":
            return {"cancelled": "true", "value": value}
        return {"written": value}

    @mcp.tool
    async def ask_once(ctx: Context) -> dict[str, str]:
        """Eliciting tool of the fixture app; asks exactly one question."""
        result = await ctx.elicit(
            "Which app are you?",
            {"answer": {"type": "string"}},
            response_title="App identity",
        )
        answer = getattr(result, "data", None) or {}
        if isinstance(answer, dict):
            answer = answer.get("answer", "")
        return {"answer": str(answer)}

    _register_files(mcp)
    mcp.run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
"""Generate and gate the ArtCraft suite content tier (CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R006).

Modes:
  --refresh  start each app CLI, read tools/list and the server version,
             and write content/snapshots/<app>.tools.json
  --write    render the ontology, skill and prompts from the app sources
             and snapshots, and write the generated files
  --check    render in memory and compare bytes with the committed files
             (the offline drift gate; needs no app CLI)
  --live     refresh each app CLI and compare each fresh tool fingerprint
             with the committed snapshot (the live drift gate;
             needs the app CLIs)

The tool names in a snapshot are the upstream names; the generators add the
namespace prefix when they write content.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from scion_sdk.manifest.tool_schema import compatibility_fingerprint

from craft_suite_api.content_gen.errors import (
    CONTENT_SNAPSHOT_MISSING,
    ContentError,
)
from craft_suite_api.content_gen.ontology import render_ontology
from craft_suite_api.content_gen.prompts import render_prompts, unassigned_tools
from craft_suite_api.content_gen.skill import render_skill
from craft_suite_api.content_gen.sources import (
    AppSource,
    ToolInfo,
    ToolSnapshot,
    load_app_source,
    load_snapshot,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONTENT_DIR = REPO_ROOT / "content"
DEFAULT_PACKAGE_DIR = REPO_ROOT / "craft_suite_api"

REFRESH_TIMEOUT_DEFAULT_S = 30
REFRESH_TIMEOUT_MIN_S = 5
REFRESH_TIMEOUT_MAX_S = 300


class Layout:
    """The four content directories of one checkout."""

    def __init__(self, content_dir: Path, package_dir: Path) -> None:
        self.apps_dir = content_dir / "apps"
        self.snapshots_dir = content_dir / "snapshots"
        self.ontology_dir = package_dir / "ontology"
        self.skills_dir = package_dir / "skills"
        self.prompts_dir = package_dir / "prompts"

    def ontology_file(self, app: str) -> Path:
        return self.ontology_dir / f"artcraft-{app}.ttl"

    def skill_file(self, app: str) -> Path:
        return self.skills_dir / app / "SKILL.md"

    def prompt_file(self, name: str) -> Path:
        return self.prompts_dir / name


def load_sources(layout: Layout) -> dict[str, AppSource]:
    """Every authored app source, keyed by app name."""
    sources = {}
    if layout.apps_dir.is_dir():
        for path in sorted(layout.apps_dir.glob("*.yml")):
            sources[load_app_source(path).app] = load_app_source(path)
    return sources


def load_snapshots(layout: Layout) -> dict[str, ToolSnapshot]:
    """Every committed tool snapshot, keyed by app name."""
    snapshots = {}
    if layout.snapshots_dir.is_dir():
        for path in sorted(layout.snapshots_dir.glob("*.tools.json")):
            snapshot = load_snapshot(path)
            snapshots[snapshot.app] = snapshot
    return snapshots


def render_app(source: AppSource, snapshot: ToolSnapshot) -> Mapping[str, str]:
    """All generated file texts for one app, keyed by file name."""
    rendered = {
        f"artcraft-{source.app}.ttl": render_ontology(source, snapshot),
        f"{source.app}/SKILL.md": render_skill(source, snapshot),
    }
    rendered.update(render_prompts(source, snapshot))
    return rendered


def _rendered_to_paths(
    layout: Layout, app: str, rendered: Mapping[str, str]
) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for name, _text in rendered.items():
        if name.startswith("artcraft-"):
            paths[name] = layout.ontology_file(app)
        elif name.endswith("SKILL.md"):
            paths[name] = layout.skill_file(app)
        else:
            paths[name] = layout.prompt_file(name)
    return paths


def resolve_refresh_timeout(cli_value: float | None) -> float:
    """The refresh timeout: the flag, else the setting, else the start value."""
    import os

    if cli_value is not None:
        value = cli_value
    else:
        raw = os.environ.get("CRAFT_SUITE_CONTENT_REFRESH_TIMEOUT_S", "")
        value = float(raw) if raw else float(REFRESH_TIMEOUT_DEFAULT_S)
    if not REFRESH_TIMEOUT_MIN_S <= value <= REFRESH_TIMEOUT_MAX_S:
        raise ValueError(
            f"refresh timeout must be within {REFRESH_TIMEOUT_MIN_S}.."
            f"{REFRESH_TIMEOUT_MAX_S} seconds"
        )
    return value


async def refresh_app(app: str, timeout_s: float) -> ToolSnapshot:
    """One live snapshot: the CLI's tool list and server version."""
    binary = shutil.which(f"{app}-cli")
    if binary is None:
        raise ContentError(
            CONTENT_SNAPSHOT_MISSING, f"{app}: {app}-cli is not on the PATH"
        )
    from fastmcp import Client
    from fastmcp.client.transports import StdioTransport

    try:
        # mode="legacy" talks to the app CLIs' protocol era directly; the
        # stdio transport sanitizes the child environment when env is None,
        # so the refresh passes the operator environment through.
        async with Client(
            StdioTransport(binary, ["mcp"], env=os.environ.copy()),
            timeout=timeout_s,
            mode="legacy",
        ) as client:
            info = await client.session.initialize()
            tools = await client.list_tools()
    except Exception as exc:
        raise ContentError(
            CONTENT_SNAPSHOT_MISSING,
            f"{app}: MCP handshake failed: {type(exc).__name__}",
        ) from None
    entries: list[dict[str, Any]] = []
    for tool in sorted(tools, key=lambda item: item.name):
        schema = getattr(tool, "parameters", None)
        if not isinstance(schema, dict):
            schema = getattr(tool, "input_schema", None)
        entries.append(
            {
                "name": str(tool.name),
                "description": str(tool.description or ""),
                "input_schema": dict(schema) if isinstance(schema, dict) else {},
            }
        )
    entries.sort(key=lambda item: item["name"])
    return ToolSnapshot(
        app=app,
        version=str(info.server_info.version or ""),
        tools=tuple(
            ToolInfo(
                name=e["name"],
                description=e["description"],
                input_schema=e["input_schema"],
            )
            for e in entries
        ),
    )


def snapshot_json(snapshot: ToolSnapshot) -> str:
    """The committed snapshot bytes: sorted tools with schema, app, version."""
    return (
        json.dumps(
            {
                "app": snapshot.app,
                "version": snapshot.version,
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.input_schema,
                    }
                    for tool in snapshot.tools
                ],
            },
            indent=2,
            ensure_ascii=True,
        )
        + "\n"
    )


async def refresh_all(
    apps: Mapping[str, AppSource], layout: Layout, timeout_s: float
) -> None:
    """Write the live snapshot of every app that carries a source file."""
    for app in sorted(apps):
        snapshot = await refresh_app(app, timeout_s)
        path = layout.snapshots_dir / f"{app}.tools.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(snapshot_json(snapshot), encoding="utf-8")
        unassigned = unassigned_tools(apps[app], snapshot)
        note = f" (unassigned: {', '.join(unassigned)})" if unassigned else ""
        print(
            f"refreshed {app}: {len(snapshot.tools)} tools, v{snapshot.version}{note}"
        )


def write_all(layout: Layout) -> int:
    """Render every app and write the generated files."""
    sources = load_sources(layout)
    snapshots = load_snapshots(layout)
    for app, source in sorted(sources.items()):
        if app not in snapshots:
            raise ContentError(
                CONTENT_SNAPSHOT_MISSING,
                f"{app}: content/apps/{app}.yml has no snapshot",
            )
        snapshot = snapshots[app]
        rendered = render_app(source, snapshot)
        paths = _rendered_to_paths(layout, app, rendered)
        for name, text in rendered.items():
            path = paths[name]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        unassigned = unassigned_tools(source, snapshot)
        note = f" (unassigned: {', '.join(unassigned)})" if unassigned else ""
        print(f"wrote {app}: {len(rendered)} files{note}")
    return 0


def _display_path(path: Path) -> str:
    """The path relative to the repo root, or absolute when it lives elsewhere."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def check_all(layout: Layout) -> int:
    """The offline drift gate: compare the render with the committed bytes."""
    sources = load_sources(layout)
    snapshots = load_snapshots(layout)
    drifted = 0
    for app, source in sorted(sources.items()):
        if app not in snapshots:
            raise ContentError(
                CONTENT_SNAPSHOT_MISSING,
                f"{app}: content/apps/{app}.yml has no snapshot",
            )
        snapshot = snapshots[app]
        rendered = render_app(source, snapshot)
        paths = _rendered_to_paths(layout, app, rendered)
        for name, text in rendered.items():
            path = paths[name]
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                print(f"CONTENT_DRIFT: {_display_path(path)}")
                drifted += 1
    if drifted:
        print(f"CONTENT_DRIFT: {drifted} file(s) differ from their sources")
        return 1
    print(f"check clean: {len(sources)} apps")
    return 0


def fingerprint_map(snapshot: ToolSnapshot) -> dict[str, str]:
    """The committed snapshot as name -> compatibility fingerprint."""
    return {
        tool.name: compatibility_fingerprint(tool.name, tool.input_schema, None)
        for tool in snapshot.tools
    }


async def live_check(layout: Layout) -> int:
    """The live drift gate: compare fresh fingerprints with the committed ones."""
    sources = load_sources(layout)
    snapshots = load_snapshots(layout)
    stale = 0
    for app in sorted(sources):
        if app not in snapshots:
            raise ContentError(
                CONTENT_SNAPSHOT_MISSING,
                f"{app}: content/apps/{app}.yml has no snapshot",
            )
        live = await refresh_app(app, REFRESH_TIMEOUT_DEFAULT_S)
        fresh = {
            tool.name: compatibility_fingerprint(tool.name, tool.input_schema, None)
            for tool in live.tools
        }
        committed = fingerprint_map(snapshots[app])
        added = sorted(set(fresh) - set(committed))
        removed = sorted(set(committed) - set(fresh))
        changed = sorted(
            name
            for name in set(fresh) & set(committed)
            if fresh[name] != committed[name]
        )
        if added or removed or changed:
            stale += 1
            print(
                f"CONTENT_SNAPSHOT_STALE: {app}: "
                f"added={added} removed={removed} changed={changed}"
            )
    if stale:
        print(f"CONTENT_SNAPSHOT_STALE: {stale} app(s) drifted from their snapshots")
        return 1
    print(f"live gate clean: {len(sources)} apps")
    return 0


def main(argv: list[str] | None = None) -> int:
    """The console entry point of the content generator."""
    parser = argparse.ArgumentParser(
        prog="craft-suite-content",
        description="Generate and gate the ArtCraft suite content tier.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="offline drift gate")
    mode.add_argument("--write", action="store_true", help="write generated files")
    mode.add_argument("--refresh", action="store_true", help="write live snapshots")
    mode.add_argument("--live", action="store_true", help="live drift gate")
    parser.add_argument("--content-dir", type=Path, default=None)
    parser.add_argument("--package-dir", type=Path, default=None)
    parser.add_argument("--refresh-timeout", type=float, default=None)
    args = parser.parse_args(argv)
    layout = Layout(
        args.content_dir or DEFAULT_CONTENT_DIR,
        args.package_dir or DEFAULT_PACKAGE_DIR,
    )
    if args.refresh_timeout is not None:
        resolve_refresh_timeout(args.refresh_timeout)
    try:
        if args.refresh or args.live:
            timeout_s = resolve_refresh_timeout(args.refresh_timeout)
        else:
            timeout_s = REFRESH_TIMEOUT_DEFAULT_S
        if args.refresh:
            asyncio.run(refresh_all(load_sources(layout), layout, timeout_s))
            return 0
        if args.live:
            return asyncio.run(live_check(layout))
        if args.write:
            return write_all(layout)
        return check_all(layout)
    except ContentError as exc:
        print(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())

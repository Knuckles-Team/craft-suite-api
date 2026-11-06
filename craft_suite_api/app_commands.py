"""Every app command as its own typed tool (CONN-CRAFT-SUITE-API-APPS-R017).

Each suite app keeps an engine command registry (hundreds of commands) and
reaches it through one dispatch tool, such as ``photocraft_command_run`` with
``id=...``. This module serves each registry command as one tool,
``<app>_cmd_<command id>``, whose description carries the app's own
parameter documentation and whose input schema names the command's
parameters. A call forwards to the app's dispatch tool on this same server,
so the activation gate, the pool, the artifact exchange and the audit apply
unchanged. The dispatch tools themselves are routed to, not listed.

The registries are read at serve time from the installed app binaries, so
the tool set always matches the apps in the image; nothing is generated
into the repository. An app whose registry cannot be read serves no command
tools and logs the refusal code; it never blocks the server.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import re
import shutil
from collections.abc import Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any

from fastmcp.server.providers import Provider
from fastmcp.server.transforms import Transform
from fastmcp.tools import Tool, ToolResult
from mcp.types import ToolAnnotations
from scion_sdk.upstream_wire import UPSTREAM_META_KEY, UPSTREAM_META_NAMESPACE_KEY

__all__ = [
    "APP_REGISTRY_UNREADABLE",
    "COMMAND_TOOL_INFIX",
    "DISPATCH",
    "AppCommandProvider",
    "Dispatch",
    "HideDispatchTools",
    "build_command_tools",
    "command_tool_name",
    "parse_registry",
    "signature_properties",
]

_logger = logging.getLogger(__name__)

#: A registry that could not be listed or parsed; the app serves no command tools.
APP_REGISTRY_UNREADABLE = "APP_REGISTRY_UNREADABLE"

COMMAND_TOOL_INFIX = "cmd"
#: The longest tool name served; longer names keep a stable hash suffix.
MAX_NAME = 64
#: The longest description served; the app's own docs are cut past it.
MAX_DESCRIPTION = 1000
#: A context argument's own description is cut past this many characters.
MAX_CONTEXT_DESCRIPTION = 120
LIST_TIMEOUT_S = 90.0


@dataclass(frozen=True)
class Dispatch:
    """How one app lists and runs its registry commands.

    ``list_tool``/``run_tool`` are the app's own (unnamespaced) tool names;
    ``id_arg``/``params_arg`` are the run tool's argument names. ``list_args``
    asks the listing for the richest form the app offers. An app whose own
    MCP already serves one tool per command has ``generate=False``: only its
    dispatch tools are hidden.
    """

    list_tool: str
    run_tool: str
    id_arg: str = "id"
    params_arg: str = "params"
    list_args: dict[str, Any] = field(default_factory=dict)
    hidden: tuple[str, ...] = ()
    generate: bool = True

    @property
    def dispatch_tools(self) -> tuple[str, ...]:
        return (self.run_tool, *self.hidden)


_ID = Dispatch("command_list", "command_run")
#: Per app, as served by each app's ``mcp`` (verified against the shipped
#: binaries by ``craft-suite-probe``).
DISPATCH: dict[str, Dispatch] = {
    "photocraft": _ID,
    "wordcraft": Dispatch("list_commands", "execute", id_arg="command"),
    "pdfcraft": _ID,
    "solidcraft": Dispatch("list_commands", "execute", id_arg="command"),
    "vectorcraft": Dispatch("command_list", "command_run", hidden=("run_command",)),
    "figcraft": Dispatch("list_commands", "run_command", id_arg="command"),
    "effectcraft": Dispatch(
        "command_list",
        "command_run",
        list_args={"schemas": True},
        hidden=("execute_command",),
    ),
    "filmcraft": _ID,
    "soundcraft": Dispatch("list_commands", "execute", id_arg="command"),
    "deckcraft": Dispatch("list_commands", "run_command", id_arg="command"),
    "cadcraft": Dispatch("list_commands", "execute", id_arg="command"),
    "designcraft": Dispatch("list_commands", "execute", id_arg="command"),
    "gridcraft": Dispatch("list_commands", "execute_command", id_arg="command"),
    "lightcraft": Dispatch(
        "command_list", "command_run", hidden=("run_command",), generate=False
    ),
    "materialcraft": _ID,
    "texturecraft": _ID,
}

# figcraft lists text lines: ``id[*] — label {params}`` (``*`` = undoable).
_TEXT_LINE = re.compile(r"^(?P<id>[A-Za-z0-9_.:/\-]+)(?P<undo>\*)? — (?P<rest>.*)$")
_KEY = re.compile(r'^\s*"?(?P<key>[A-Za-z_][A-Za-z0-9_]*)"?\s*(?P<opt>\?)?')
_PAIRS = {"{": "}", "[": "]", "(": ")"}


def _unwrap(obj: Any) -> list[Any]:
    if isinstance(obj, dict):
        for key in ("commands", "items", "result"):
            if isinstance(obj.get(key), list):
                return list(obj[key])
        return []
    return list(obj) if isinstance(obj, list) else []


def parse_registry(text: str, structured: Any = None) -> list[dict[str, Any]]:
    """The command entries of one app's listing: JSON (any wrapper) or text lines.

    Every entry has an ``id``; duplicate ids keep the first entry. A
    listing in no known form returns no entry.
    """
    entries: list[Any] = _unwrap(structured) if structured is not None else []
    stripped = text.strip()
    if not entries and stripped[:1] in "[{":
        try:
            obj, _ = json.JSONDecoder().raw_decode(stripped)
        except ValueError:
            obj = None
        entries = _unwrap(obj)
    if not entries:
        for line in stripped.splitlines():
            match = _TEXT_LINE.match(line.strip())
            if match:
                entries.append(
                    {
                        "id": match["id"],
                        "undoable": bool(match["undo"]),
                        "label": match["rest"].split(" {", 1)[0],
                        "params": "{" + match["rest"].split(" {", 1)[1]
                        if " {" in match["rest"]
                        else None,
                    }
                )
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            continue
        if entry["id"] in seen or entry.get("planned") is True:
            continue
        seen.add(entry["id"])
        out.append(entry)
    return out


def _top_level_segments(signature: str) -> list[str]:
    """The comma-separated segments directly inside the outermost ``{...}``."""
    start = signature.find("{")
    if start < 0 or signature[:start].strip():
        return []
    depth, quote, segments, current = 0, "", [], []
    closers: list[str] = []
    for char in signature[start:]:
        if quote:
            current.append(char)
            if char == quote:
                quote = ""
            continue
        if char in "\"'" and depth >= 1:
            quote = char
            current.append(char)
            continue
        if char in _PAIRS:
            depth += 1
            closers.append(_PAIRS[char])
            if depth == 1:
                continue
        elif closers and char == closers[-1]:
            depth -= 1
            closers.pop()
            if depth == 0:
                segments.append("".join(current))
                return segments
        if depth == 1 and char == ",":
            segments.append("".join(current))
            current = []
            continue
        current.append(char)
    return segments


def signature_properties(signature: Any) -> dict[str, dict[str, Any]]:
    """The named parameters of an app's documented ``{key?: ...}`` signature.

    Each parameter keeps its own documentation fragment as its description;
    the value type stays open because the apps document types in prose.
    """
    if not isinstance(signature, str):
        return {}
    props: dict[str, dict[str, Any]] = {}
    for segment in _top_level_segments(signature):
        match = _KEY.match(segment)
        if not match:
            continue
        tail = segment[match.end() :].lstrip()
        if tail and tail[0] not in ":=|(,?" and not tail.startswith("→"):
            continue
        key = match["key"]
        if key not in props:
            props[key] = {"description": segment.strip()[:300]}
    return props


def command_tool_name(app: str, command_id: str, taken: set[str]) -> str:
    """``<app>_cmd_<id>`` with non-name characters as ``_``; unique and bounded."""
    slug = re.sub(r"[^A-Za-z0-9_]+", "_", command_id).strip("_") or "command"
    name = f"{app}_{COMMAND_TOOL_INFIX}_{slug}"
    digest = hashlib.sha256(command_id.encode()).hexdigest()[:8]
    if len(name) > MAX_NAME:
        name = f"{name[: MAX_NAME - 9]}_{digest}"
    if name in taken:
        name = f"{name[: MAX_NAME - 9]}_{digest}"
    taken.add(name)
    return name


def _description(app: str, entry: dict[str, Any]) -> str:
    label = str(entry.get("label") or entry["id"])
    parts = [f"{app}: {label} (command `{entry['id']}`)."]
    params = entry.get("params")
    if isinstance(params, str) and params:
        parts.append(f"Params: {params}")
    menu = entry.get("menu") or entry.get("location") or entry.get("panel")
    if isinstance(menu, list):
        menu = " > ".join(str(m) for m in menu)
    if menu:
        parts.append(f"Menu: {menu}.")
    if entry.get("needsDocument"):
        parts.append("Needs an open document.")
    text = " ".join(parts)
    return text if len(text) <= MAX_DESCRIPTION else text[: MAX_DESCRIPTION - 1] + "…"


def _context_spec(spec: Any) -> dict[str, Any]:
    """A dispatch context argument, trimmed: its type and a short description."""
    if not isinstance(spec, dict):
        return {}
    out = {k: spec[k] for k in ("type", "anyOf", "minimum") if k in spec}
    description = str(spec.get("description") or "")
    if description:
        out["description"] = description[:MAX_CONTEXT_DESCRIPTION]
    return out


def _schema(entry: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    schema = entry.get("schema")
    if isinstance(schema, dict) and schema.get("type") == "object":
        props = dict(schema.get("properties") or {})
        required = list(schema.get("required") or [])
    else:
        # Names only: each fragment is already in the description's Params
        # text, and repeating it per property would double the listing.
        props = {key: {} for key in signature_properties(entry.get("params"))}
        required = []
    for key, spec in context.items():
        props.setdefault(key, _context_spec(spec))
    out: dict[str, Any] = {
        "type": "object",
        "properties": props,
        "additionalProperties": True,
    }
    if required:
        out["required"] = required
    return out


def _annotations(entry: dict[str, Any]) -> ToolAnnotations | None:
    """Read-only hints only where the app marks a command as not mutating.

    Unset hints keep the MCP defaults; the listing stays small enough for a
    gateway to read in one response.
    """
    if entry.get("mutates") is False:
        return ToolAnnotations(readOnlyHint=True, destructiveHint=False)
    return None


class CommandTool(Tool):
    """One registry command; a call runs the app's dispatch tool with it."""

    command_id: str
    dispatch_name: str
    id_arg: str
    params_arg: str
    context_args: tuple[str, ...] = ()

    async def run(self, arguments: dict[str, Any]) -> ToolResult:
        from fastmcp.server.dependencies import get_context

        args = dict(arguments or {})
        forwarded: dict[str, Any] = {
            key: args.pop(key) for key in self.context_args if key in args
        }
        forwarded[self.id_arg] = self.command_id
        forwarded[self.params_arg] = args
        ctx = get_context()
        return await ctx.fastmcp.call_tool(self.dispatch_name, forwarded)


def build_command_tools(
    app: str, dispatch: Dispatch, entries: Sequence[dict[str, Any]], run_schema: Any
) -> list[Tool]:
    """One tool per registry entry of ``app``."""
    run_props = dict((run_schema or {}).get("properties") or {})
    context = {
        key: spec
        for key, spec in run_props.items()
        if key not in (dispatch.id_arg, dispatch.params_arg)
    }
    taken: set[str] = set()
    tools: list[Tool] = []
    for entry in entries:
        schema = _schema(entry, context)
        own = set(schema["properties"]) - set(context)
        tools.append(
            CommandTool(
                name=command_tool_name(app, entry["id"], taken),
                description=_description(app, entry),
                parameters=schema,
                annotations=_annotations(entry),
                title=str(entry.get("label") or entry["id"])[:80],
                tags={f"ns:{app}"},
                # The same group metadata the SDK stamps on the app's own tools,
                # so a gateway loads and unloads them with their app.
                meta={
                    UPSTREAM_META_KEY: {
                        UPSTREAM_META_NAMESPACE_KEY: app,
                        "upstream": app,
                    }
                },
                command_id=entry["id"],
                dispatch_name=f"{app}_{dispatch.run_tool}",
                id_arg=dispatch.id_arg,
                params_arg=dispatch.params_arg,
                context_args=tuple(k for k in context if k not in own),
            )
        )
    return tools


async def _read_registry(
    app: str, command: Sequence[str], dispatch: Dispatch
) -> list[Tool]:
    """List one app's registry over a short-lived stdio child (no file roots)."""
    from fastmcp import Client
    from fastmcp.client.transports import StdioTransport

    binary = shutil.which(command[0])
    if binary is None:
        _logger.warning("%s: %s (binary not found)", APP_REGISTRY_UNREADABLE, app)
        return []
    transport = StdioTransport(binary, list(command[1:]), env=os.environ.copy())
    async with Client(transport, timeout=LIST_TIMEOUT_S) as client:
        listed = {tool.name: tool for tool in await client.list_tools()}
        run = listed.get(dispatch.run_tool)
        if dispatch.list_tool not in listed or run is None:
            _logger.warning("%s: %s (no registry tools)", APP_REGISTRY_UNREADABLE, app)
            return []
        result = await client.call_tool(
            dispatch.list_tool, dict(dispatch.list_args), raise_on_error=False
        )
    text = "".join(getattr(block, "text", "") for block in result.content)
    entries = parse_registry(text, result.structured_content)
    if not entries:
        _logger.warning("%s: %s (empty listing)", APP_REGISTRY_UNREADABLE, app)
        return []
    return build_command_tools(app, dispatch, entries, run.input_schema)


class AppCommandProvider(Provider):
    """Serves every declared app's registry commands as tools.

    ``apps`` maps an app name to its listing command line. The registries
    load once, concurrently, when the server starts (or on the first
    listing); a failed app logs ``APP_REGISTRY_UNREADABLE`` and serves none.
    """

    def __init__(self, apps: dict[str, Sequence[str]]) -> None:
        super().__init__()
        self._apps = {
            app: tuple(cmd)
            for app, cmd in apps.items()
            if app in DISPATCH and DISPATCH[app].generate
        }
        self._tools: dict[str, Tool] = {}
        self._loading: asyncio.Task[None] | None = None
        self.counts: dict[str, int] = {}

    async def _load_one(self, app: str) -> None:
        try:
            tools = await _read_registry(app, self._apps[app], DISPATCH[app])
        except Exception as exc:  # noqa: BLE001 - an app failure never blocks the server; the cause is logged
            _logger.warning("%s: %s: %r", APP_REGISTRY_UNREADABLE, app, exc)
            tools = []
        self.counts[app] = len(tools)
        for tool in tools:
            self._tools[tool.name] = tool

    async def _load(self) -> None:
        await asyncio.gather(*(self._load_one(app) for app in self._apps))
        _logger.info("app command tools: %s", json.dumps(self.counts, sort_keys=True))

    async def _ready(self) -> None:
        if self._loading is None:
            self._loading = asyncio.ensure_future(self._load())
        await asyncio.shield(self._loading)

    @asynccontextmanager
    async def lifespan(self):
        if self._apps and self._loading is None:
            self._loading = asyncio.ensure_future(self._load())
        yield

    async def _list_tools(self) -> Sequence[Tool]:
        await self._ready()
        return list(self._tools.values())

    async def _get_tool(self, name: str, version: Any = None) -> Tool | None:
        if not any(
            name.startswith(f"{app}_{COMMAND_TOOL_INFIX}_") for app in self._apps
        ):
            return None
        await self._ready()
        return self._tools.get(name)


class HideDispatchTools(Transform):
    """Drops the apps' single-command dispatch tools from listings only.

    The generated command tools route through them, so a call by name still
    resolves; a client lists one tool per command, never the router.
    """

    def __init__(self, names: Sequence[str]) -> None:
        self._names = frozenset(names)

    async def list_tools(self, tools: Sequence[Tool]) -> Sequence[Tool]:
        return [tool for tool in tools if tool.name not in self._names]


def dispatch_tool_names(apps: Sequence[str]) -> list[str]:
    """The namespaced dispatch tool names of ``apps``."""
    return [
        f"{app}_{name}"
        for app in apps
        if app in DISPATCH
        for name in DISPATCH[app].dispatch_tools
    ]

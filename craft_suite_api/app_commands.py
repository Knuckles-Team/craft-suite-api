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
import contextlib
import hashlib
import json
import logging
import os
import re
import shutil
import time
import weakref
from collections.abc import Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any

from fastmcp.server.middleware import Middleware
from fastmcp.server.providers import Provider
from fastmcp.server.transforms import Transform
from fastmcp.tools import Tool, ToolResult
from mcp.types import ToolAnnotations
from mcp_types.version import MODERN_PROTOCOL_VERSIONS
from scion_sdk.upstream_wire import UPSTREAM_META_KEY, UPSTREAM_META_NAMESPACE_KEY

__all__ = [
    "APP_REGISTRY_UNREADABLE",
    "APP_WARMING",
    "WARMUP",
    "AppWarmup",
    "SessionTracker",
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
#: A call to a command of an app whose registry is still loading (retryable).
APP_WARMING = "APP_WARMING"

WARMING, READY, FAILED = "warming", "ready", "failed"
#: How long a call to a warming app waits for that app before refusing.
WARMUP_WAIT_S = 20.0
#: The base delay before a failed registry load is retried (grows linearly).
REGISTRY_RETRY_S = 15.0
#: How many times a failed registry load is retried in the background.
REGISTRY_RETRIES = 3

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


#: Prose type words the apps use, mapped to JSON Schema types.
_TYPE_WORDS = {
    "bool": "boolean",
    "boolean": "boolean",
    "str": "string",
    "string": "string",
    "text": "string",
    "path": "string",
    "url": "string",
    "hex": "string",
    "color": "string",
    "colour": "string",
    "int": "integer",
    "integer": "integer",
    "uint": "integer",
    "index": "integer",
    "count": "integer",
    "number": "number",
    "num": "number",
    "float": "number",
    "px": "number",
    "pt": "number",
    "pts": "number",
    "deg": "number",
    "degrees": "number",
    "ppi": "number",
    "dpi": "number",
    "ms": "number",
    "s": "number",
    "seconds": "number",
    "frames": "number",
    "percent": "number",
    "%": "number",
    "mm": "number",
    "u8": "integer",
    "u16": "integer",
    "u32": "integer",
    "u64": "integer",
    "i32": "integer",
    "i64": "integer",
    "usize": "integer",
    "f32": "number",
    "f64": "number",
    "double": "number",
}
#: Words that name a type, never an enum member; a choice that holds one is
#: a type union and stays open.
_OPEN_WORDS = frozenset(_TYPE_WORDS) | {
    "id",
    "ids",
    "name",
    "names",
    "ref",
    "handle",
    "object",
    "array",
    "list",
    "null",
    "any",
    "value",
    "json",
    "base64",
}
_RANGE = re.compile(r"^(?P<lo>-?\d+(?:\.\d+)?)\s*(?:\.\.|–)\s*(?P<hi>-?\d+(?:\.\d+)?)")
_IDENT = re.compile(r"^[A-Za-z][A-Za-z0-9_\-]*$")


def _split_top(text: str, sep: str) -> list[str]:
    """``text`` split on ``sep`` outside quotes and brackets."""
    parts, current, depth, quote = [], [], 0, ""
    for char in text:
        if quote:
            current.append(char)
            if char == quote:
                quote = ""
            continue
        if char in "\"'":
            quote = char
        elif char in "[{(":
            depth += 1
        elif char in "]})":
            depth -= 1
        elif char == sep and depth == 0:
            parts.append("".join(current))
            current = []
            continue
        current.append(char)
    parts.append("".join(current))
    return parts


def _literal(text: str) -> Any:
    try:
        return json.loads(text)
    except ValueError:
        return None


def _choices(expr: str) -> list[str] | None:
    """The enum members of ``a|b|c`` or ``"a"|"b"``; ``None`` for a union."""
    if "…" in expr or "..." in expr:
        return None
    inner = expr
    if len(expr) >= 2 and expr[0] == expr[-1] == '"' and expr.count('"') == 2:
        inner = expr[1:-1]
    members = [part.strip().strip('"') for part in inner.split("|")]
    if len(members) < 2:
        return None
    if any(not _IDENT.match(m) or m.lower() in _OPEN_WORDS for m in members):
        return None
    return members


def fragment_schema(segment: str) -> dict[str, Any]:
    """A compact JSON schema for one documented parameter, or ``{}`` (open).

    Derived from the apps' prose signatures: ``"x":px``, ``"angle":-3600..3600=0``,
    ``"mode":"rgb|gray"="rgb"``, ``flip?: bool``, ``size?: [w,h] pt``,
    ``style?: straight|elbow|curved``. Only forms read without doubt are
    typed; anything else stays open, so a valid call is never refused.
    """
    match = _KEY.match(segment)
    if not match:
        return {}
    tail = segment[match.end() :].strip()
    tail = tail.lstrip('"').strip()
    if tail.startswith("?"):
        tail = tail[1:].strip()
    default_text: str | None = None
    if tail.startswith("="):
        default_text = tail[1:].strip()
        expr = ""
    elif tail.startswith(":"):
        expr = tail[1:].strip()
    else:
        return {}
    if expr:
        pieces = _split_top(expr, "=")
        if len(pieces) == 2:
            expr, default_text = pieces[0].strip(), pieces[1].strip()
    if default_text and "|" in default_text.split(" (")[0]:
        # ``pt=612|"210 mm"``: the default lists alternative value forms.
        return {}
    # Drop a trailing prose note: ``bool (… default true)`` or ``— …``.
    expr = re.split(r"\s+\(|\s+—\s|\s+-\s", expr, maxsplit=1)[0].strip()
    expr = expr.rstrip("?").strip()
    spec: dict[str, Any] = {}
    if expr.startswith("["):
        spec["type"] = "array"
    elif expr.startswith("{"):
        spec["type"] = "object"
    elif range_match := _RANGE.match(expr):
        lo, hi = float(range_match["lo"]), float(range_match["hi"])
        spec = {"type": "number", "minimum": lo, "maximum": hi}
        if lo.is_integer() and hi.is_integer():
            spec["minimum"], spec["maximum"] = int(lo), int(hi)
    elif (members := _choices(expr)) is not None:
        spec = {"type": "string", "enum": members}
    elif expr:
        word = expr.split()[0].strip('",').lower()
        if word in ("true", "false"):
            spec["type"] = "boolean"
        elif word in _TYPE_WORDS and len(expr.split()) <= 2 and "|" not in expr:
            spec["type"] = _TYPE_WORDS[word]
    if default_text:
        value = _literal(default_text.split()[0].rstrip(",)"))
        kind = spec.get("type")
        if kind is None and isinstance(value, bool | int | float | str):
            # An untyped parameter with a literal default takes its type.
            kind = (
                "boolean"
                if isinstance(value, bool)
                else ("string" if isinstance(value, str) else "number")
            )
            spec["type"] = kind
        if kind is not None and fits_value(kind, value):
            if "enum" not in spec or value in spec["enum"]:
                spec["default"] = value
    return spec


def fits_value(kind: str, value: Any) -> bool:
    """Whether ``value`` is an instance of JSON Schema type ``kind``."""
    if kind == "boolean":
        return isinstance(value, bool)
    if kind == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if kind == "number":
        return isinstance(value, int | float) and not isinstance(value, bool)
    if kind == "string":
        return isinstance(value, str)
    return False


def typed_properties(signature: Any) -> dict[str, dict[str, Any]]:
    """Each documented parameter with the schema :func:`fragment_schema` derives."""
    if not isinstance(signature, str):
        return {}
    props: dict[str, dict[str, Any]] = {}
    for segment in _top_level_segments(signature):
        match = _KEY.match(segment)
        if not match or match["key"] in props:
            continue
        rest = segment[match.end() :].lstrip()
        if rest and rest[0] not in ':=|(,?"' and not rest.startswith("→"):
            continue
        props[match["key"]] = fragment_schema(segment)
    return props


def _schema(entry: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    schema = entry.get("schema")
    params = entry.get("params")
    if not (isinstance(schema, dict) and schema.get("type") == "object"):
        # pdfcraft publishes its JSON schema in ``params`` itself.
        schema = params if isinstance(params, dict) else None
    if isinstance(schema, dict) and schema.get("type") == "object":
        props = dict(schema.get("properties") or {})
        required = list(schema.get("required") or [])
    else:
        # Typed where the prose reads without doubt, open otherwise; the
        # fragment's documentation stays once, in the description's Params.
        props = typed_properties(params)
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


#: The longest a command tool waits for a background job it started.
JOB_WAIT_S = 900.0
_UNSET: Any = object()
_EXCHANGE_RUNTIME: Any = _UNSET


def _exchange_runtime() -> Any:
    """The artifact exchange of this server's apps, or ``None`` when unset."""
    global _EXCHANGE_RUNTIME
    if _EXCHANGE_RUNTIME is _UNSET:
        from scion_sdk.mcp.upstreams.exchange import load_exchange_runtime

        from .upstreams import UPSTREAMS

        try:
            _EXCHANGE_RUNTIME = load_exchange_runtime(UPSTREAMS, "craft-suite-api")
        except Exception as exc:  # noqa: BLE001 - a bad exchange setting never breaks a call; the SDK refuses it at startup
            _logger.warning("command tools run without the exchange: %r", exc)
            _EXCHANGE_RUNTIME = None
    return _EXCHANGE_RUNTIME


def _caller() -> str:
    """The calling actor, as the SDK's exchange records it."""
    try:
        from scion_sdk.identity import current_actor

        return current_actor().actor_id
    except Exception:  # noqa: BLE001 - no identity in scope is an anonymous call
        return "anonymous"


def _request_meta(context: Any) -> Any:
    """The request's ``_meta`` (it carries a caller-chosen ``scion/run``)."""
    meta = getattr(getattr(context, "request_context", None), "meta", None)
    if meta is None or isinstance(meta, dict):
        return meta
    dump = getattr(meta, "model_dump", None)
    return dump(by_alias=True) if callable(dump) else None


def _result_json(result: Any) -> Any:
    text = "".join(getattr(block, "text", "") for block in (result.content or []))
    try:
        return json.loads(text)
    except ValueError:
        return None


def _find_job(listing: Any, job: Any) -> dict[str, Any] | None:
    entries = listing.get("jobs") if isinstance(listing, dict) else listing
    if not isinstance(entries, list):
        return None
    return next(
        (e for e in entries if isinstance(e, dict) and e.get("id") == job), None
    )


#: Command parameters that name an output file; a relative value with a file
#: extension lands in the run folder. The same names also carry non-file
#: values (photocraft's ``"path": "work"`` names a vector path), which have no
#: extension and pass through unchanged.
FILE_OUTPUT_ARGS = ("path", "out", "output", "outputPath", "outPath")
#: Command parameters that name an output folder; a relative value lands in
#: the run folder.
DIR_OUTPUT_ARGS = ("dir", "out_dir", "outDir", "outputDir")


def output_path_args(arguments: dict[str, Any]) -> tuple[str, ...]:
    """The arguments of one call whose relative values are run output paths."""
    from pathlib import PurePosixPath

    names: list[str] = []
    for key, value in arguments.items():
        if not isinstance(value, str) or not value or "://" in value:
            continue
        if PurePosixPath(value).is_absolute():
            continue
        if key in DIR_OUTPUT_ARGS or (
            key in FILE_OUTPUT_ARGS and PurePosixPath(value).suffix
        ):
            names.append(key)
    return tuple(names)


class CommandTool(Tool):
    """One registry command; a call runs the app's dispatch tool with it.

    The command's own arguments run through the artifact exchange here, before
    they are nested under the dispatch tool's ``params``: an
    ``exchange://``/``https`` input is staged, a relative ``path``/``dir``/
    ``out``/``out_dir`` lands in the run's output folder, and the files the
    command wrote are published to the sinks after it returns. A command that
    answers with a background job (``{"job": n, "poll": "jobs.list"}``) is
    awaited, bounded by ``JOB_WAIT_S``, so its output exists before it is
    published (CONN-CRAFT-SUITE-API-APPS-R020).
    """

    command_id: str
    dispatch_name: str
    id_arg: str
    params_arg: str
    context_args: tuple[str, ...] = ()
    app: str = ""

    async def _forward(
        self, ctx: Any, context: dict[str, Any], params: dict[str, Any]
    ) -> Any:
        forwarded = {**context, self.id_arg: self.command_id, self.params_arg: params}
        result = await ctx.fastmcp.call_tool(self.dispatch_name, forwarded)
        return await self._await_job(ctx, context, result)

    async def _await_job(self, ctx: Any, context: dict[str, Any], result: Any) -> Any:
        started = _result_json(result)
        if not (
            isinstance(started, dict)
            and "job" in started
            and isinstance(started.get("poll"), str)
        ):
            return result
        deadline = time.monotonic() + JOB_WAIT_S
        delay = 0.5
        while time.monotonic() < deadline:
            await asyncio.sleep(delay)
            delay = min(delay * 1.5, 5.0)
            listing = await ctx.fastmcp.call_tool(
                self.dispatch_name,
                {**context, self.id_arg: started["poll"], self.params_arg: {}},
            )
            job = _find_job(_result_json(listing), started["job"])
            if job is None:
                return result
            if job.get("finished") or job.get("done") is True:
                outcome = job.get("result")
                failed = isinstance(outcome, dict) and "error" in outcome
                payload = {**started, "finished": True, "result": outcome}
                return ToolResult(
                    content=json.dumps(payload),
                    structured_content=payload,
                    is_error=failed,
                )
        payload = {**started, "finished": False, "waited_s": JOB_WAIT_S}
        return ToolResult(content=json.dumps(payload), structured_content=payload)

    async def run(self, arguments: dict[str, Any]) -> ToolResult:
        from fastmcp.server.dependencies import get_context

        args = dict(arguments or {})
        context: dict[str, Any] = {
            key: args.pop(key) for key in self.context_args if key in args
        }
        ctx = get_context()
        runtime = _exchange_runtime()
        if runtime is None:
            return await self._forward(ctx, context, args)
        from fastmcp.exceptions import ToolError
        from scion_sdk.exchange.inputs import ExchangeInputError
        from scion_sdk.exchange.run import ExchangeCall, exchange_call
        from scion_sdk.exchange.staging import ExchangeRunError

        spec = ExchangeCall(
            namespace=self.app,
            tool=self.name,
            connector=runtime.connector,
            path_args=output_path_args(args),
            caller=_caller(),
        )
        try:
            return await exchange_call(
                args,
                lambda prepared: self._forward(ctx, context, prepared),
                settings=runtime.settings,
                backends=runtime.backends,
                spec=spec,
                meta=_request_meta(ctx),
            )
        except (ExchangeInputError, ExchangeRunError) as exc:
            raise ToolError(str(exc)) from None


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
                app=app,
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


class AppWarmup:
    """Each app's registry state, as the readiness probe and the calls read it.

    ``warming`` until the first load attempt settles, then ``ready`` (its
    tools are served) or ``failed`` (it serves none and is retried in the
    background). Every state change is an :class:`asyncio.Event` per app, so
    a call can wait on one app without waiting on the others
    (CONN-CRAFT-SUITE-API-APPS-R018).
    """

    def __init__(self, apps: Sequence[str]) -> None:
        self.states: dict[str, str] = dict.fromkeys(apps, WARMING)
        self.counts: dict[str, int] = {}
        self.started = time.monotonic()
        self.settled_at: dict[str, float] = {}
        self._events: dict[str, asyncio.Event] = {}

    def _event(self, app: str) -> asyncio.Event:
        if app not in self._events:
            self._events[app] = asyncio.Event()
            if self.states.get(app) != WARMING:
                self._events[app].set()
        return self._events[app]

    def settle(self, app: str, state: str, count: int) -> None:
        self.states[app] = state
        self.counts[app] = count
        self.settled_at.setdefault(app, round(time.monotonic() - self.started, 3))
        self._event(app).set()

    async def wait(self, app: str, timeout_s: float) -> str:
        """The app's state after waiting at most ``timeout_s`` for it to settle."""
        if self.states.get(app) == WARMING and timeout_s > 0:
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(self._event(app).wait(), timeout_s)
        return self.states.get(app, FAILED)

    @property
    def settled(self) -> bool:
        return all(state != WARMING for state in self.states.values())

    def readiness_detail(self) -> dict[str, Any]:
        """Scalar fields for ``/ready``; the server is ready once every app settled."""

        def named(state: str) -> str:
            return ",".join(sorted(a for a, s in self.states.items() if s == state))

        return {
            "apps_ready": sum(1 for s in self.states.values() if s == READY),
            "apps_warming": named(WARMING),
            "apps_failed": named(FAILED),
            "app_command_tools": sum(self.counts.values()),
            # Seconds from server start until the last app settled (None: warming).
            "apps_settled_s": max(self.settled_at.values(), default=0.0)
            if self.settled
            else None,
        }


#: The live warm-up state of the running server (``None`` before it serves).
WARMUP: AppWarmup | None = None


def _refusal_tool(name: str, app: str, code: str, retry_after_s: float) -> Tool:
    """A stand-in for a command tool whose app cannot serve it yet."""

    class _Refusal(Tool):
        async def run(self, arguments: dict[str, Any]) -> ToolResult:
            payload = {
                "refused": True,
                "code": code,
                "app": app,
                "tool": name,
                "retryable": True,
                "retry_after_s": retry_after_s,
            }
            text = (
                f"{code}: {app} is still loading its command registry; "
                f"retry after {retry_after_s:g} s"
                if code == APP_WARMING
                else f"{code}: {app}'s command registry could not be read; "
                f"it is retried in the background, retry after {retry_after_s:g} s"
            )
            return ToolResult(content=text, structured_content=payload, is_error=True)

    return _Refusal(
        name=name,
        description=f"{app} command (refused: {code})",
        parameters={"type": "object", "additionalProperties": True},
        tags={f"ns:{app}"},
    )


class SessionTracker(Middleware):
    """Announces a tool-list change to every client that can hear it.

    fastmcp sends ``notifications/tools/list_changed`` only inside a request.
    An app whose registry lands later publishes ``ToolsListChanged`` on the
    server's change bus, which every ``subscriptions/listen`` stream
    (2026-07-28 clients, the fleet's sync runner) receives, and notifies each
    handshake-era session the server has seen on its standalone stream.
    """

    def __init__(self, server: Any = None) -> None:
        self.server = server
        self.sessions: weakref.WeakSet[Any] = weakref.WeakSet()

    async def on_message(self, context, call_next):  # noqa: ANN001 - fastmcp hook
        ctx = context.fastmcp_context
        if ctx is not None:
            with contextlib.suppress(Exception):
                # ``ctx.session`` is a per-request proxy; a handshake-era
                # connection behind it lives as long as the client's session.
                connection = getattr(ctx.session, "_connection", None)
                version = getattr(connection, "protocol_version", None)
                if connection is not None and version not in MODERN_PROTOCOL_VERSIONS:
                    self.sessions.add(connection)
        return await call_next(context)

    async def notify_tools_changed(self) -> int:
        """Publish the change; returns how many channels it went out on."""
        sent = 0
        if self.server is not None:
            from mcp.server.subscriptions import ToolsListChanged
            from scion_sdk.mcp.change_events import change_bus

            with contextlib.suppress(LookupError):
                await change_bus(self.server).publish(ToolsListChanged())
                sent += 1
        for session in list(self.sessions):
            try:
                await session.send_tool_list_changed()
                sent += 1
            except Exception:  # noqa: BLE001 - a closed session is dropped, never raised
                self.sessions.discard(session)
        return sent


class AppCommandProvider(Provider):
    """Serves every declared app's registry commands as tools.

    ``apps`` maps an app name to its listing command line. Every app's
    registry loads in its own background task when the server starts; a
    listing never waits for it. Each app's tools appear as soon as its own
    registry has loaded, and every known session is sent
    ``tools/list_changed``. A call to a command of an app still warming
    waits up to ``wait_s`` for that app alone, then answers the typed,
    retryable refusal ``APP_WARMING``; an app whose registry could not be
    read refuses ``APP_REGISTRY_UNREADABLE`` and is retried in the
    background (CONN-CRAFT-SUITE-API-APPS-R018).
    """

    def __init__(
        self,
        apps: dict[str, Sequence[str]],
        *,
        tracker: SessionTracker | None = None,
        wait_s: float = WARMUP_WAIT_S,
        retry_s: float = REGISTRY_RETRY_S,
        retries: int = REGISTRY_RETRIES,
    ) -> None:
        super().__init__()
        self._apps = {
            app: tuple(cmd)
            for app, cmd in apps.items()
            if app in DISPATCH and DISPATCH[app].generate
        }
        self._tools: dict[str, Tool] = {}
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self.tracker = tracker
        self.wait_s = wait_s
        self.retry_s = retry_s
        self.retries = retries
        self.warmup = AppWarmup(tuple(self._apps))

    @property
    def counts(self) -> dict[str, int]:
        return self.warmup.counts

    async def _load_one(self, app: str) -> None:
        """Load one app's registry, retrying a failure in the background."""
        for attempt in range(self.retries + 1):
            try:
                tools = await _read_registry(app, self._apps[app], DISPATCH[app])
            except Exception as exc:  # noqa: BLE001 - an app failure never blocks the server; the cause is logged
                _logger.warning("%s: %s: %r", APP_REGISTRY_UNREADABLE, app, exc)
                tools = []
            if tools:
                for tool in tools:
                    self._tools[tool.name] = tool
                self.warmup.settle(app, READY, len(tools))
                _logger.info(
                    "app %s ready: %d command tools after %.1f s",
                    app,
                    len(tools),
                    time.monotonic() - self.warmup.started,
                )
                if self.tracker is not None:
                    await self.tracker.notify_tools_changed()
                return
            self.warmup.settle(app, FAILED, 0)
            if attempt < self.retries:
                await asyncio.sleep(self.retry_s * (attempt + 1))

    def start(self) -> None:
        """Start each app's load once; idempotent."""
        global WARMUP
        WARMUP = self.warmup
        for app in self._apps:
            if app not in self._tasks:
                self._tasks[app] = asyncio.ensure_future(self._load_one(app))

    @asynccontextmanager
    async def lifespan(self):
        self.start()
        try:
            yield
        finally:
            for task in self._tasks.values():
                task.cancel()

    async def _list_tools(self) -> Sequence[Tool]:
        self.start()
        return list(self._tools.values())

    def _app_of(self, name: str) -> str | None:
        for app in self._apps:
            if name.startswith(f"{app}_{COMMAND_TOOL_INFIX}_"):
                return app
        return None

    async def _get_tool(self, name: str, version: Any = None) -> Tool | None:
        app = self._app_of(name)
        if app is None:
            return None
        self.start()
        if name in self._tools:
            return self._tools[name]
        state = await self.warmup.wait(app, self.wait_s)
        if name in self._tools:
            return self._tools[name]
        if state == WARMING:
            return _refusal_tool(name, app, APP_WARMING, self.retry_s / 3 or 1.0)
        if state == FAILED:
            return _refusal_tool(name, app, APP_REGISTRY_UNREADABLE, self.retry_s)
        return None


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

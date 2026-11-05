"""The authored app source and the tool snapshot the renders read."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

#: The parents a domain class may name (CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R003).
ALLOWED_PARENTS = frozenset({"CreativeWork", "Document", "Artifact", "App", "AppTool"})


@dataclass(frozen=True)
class AppClass:
    """One domain class of an app, naming one allowed parent."""

    name: str
    parent: str
    description: str = ""


@dataclass(frozen=True)
class Functionality:
    """One use case: an ordered tool list the prompt walks through."""

    name: str
    description: str
    tools: tuple[str, ...]
    steps: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AppSource:
    """The authored half of an app's content: ``content/apps/<app>.yml``."""

    app: str
    summary: str
    classes: tuple[AppClass, ...]
    functionalities: tuple[Functionality, ...]


@dataclass(frozen=True)
class ToolInfo:
    """One tool from the snapshot, in its upstream name."""

    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolSnapshot:
    """The generated half: ``content/snapshots/<app>.tools.json``."""

    app: str
    version: str
    tools: tuple[ToolInfo, ...]

    def names(self) -> frozenset[str]:
        return frozenset(tool.name for tool in self.tools)


def load_app_source(path: Path) -> AppSource:
    """Parse one authored app source; the app name must match the file."""
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    app = document.get("app")
    if not isinstance(app, str) or app != path.stem:
        raise ValueError(f"{path.name}: the app name must match the file name")
    classes = tuple(
        AppClass(
            name=str(item["name"]),
            parent=str(item["parent"]),
            description=str(item.get("description", "")),
        )
        for item in document.get("classes", [])
        if isinstance(item, dict) and item.get("name")
    )
    functionalities = tuple(
        Functionality(
            name=str(item["name"]),
            description=str(item.get("description", "")),
            tools=tuple(str(t) for t in item.get("tools", [])),
            steps=tuple(str(s) for s in item.get("steps", [])),
        )
        for item in document.get("functionality", [])
        if isinstance(item, dict) and item.get("name")
    )
    return AppSource(
        app=app,
        summary=str(document.get("summary", "")).strip(),
        classes=classes,
        functionalities=functionalities,
    )


def load_snapshot(path: Path) -> ToolSnapshot:
    """Parse one committed tool snapshot, sorted by tool name."""
    document = json.loads(path.read_text(encoding="utf-8"))
    tools = tuple(
        ToolInfo(
            name=str(item["name"]),
            description=str(item.get("description", "")),
            input_schema=dict(item.get("input_schema", {}) or {}),
        )
        for item in document.get("tools", [])
        if isinstance(item, dict) and item.get("name")
    )
    tools = tuple(sorted(tools, key=lambda tool: tool.name))
    return ToolSnapshot(
        app=str(document.get("app", path.stem.split(".")[0])),
        version=str(document.get("version", "")),
        tools=tools,
    )


def first_sentence(text: str) -> str:
    """The first sentence of a tool description, for tables and prompts."""

    text = text.strip()
    match = re.search(r"[^.!\?]+[.!\?]", text)
    if match is None:
        return text
    return match.group(0).strip()

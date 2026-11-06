"""The generated backend description and the names derived from it (R007)."""

from __future__ import annotations

import hashlib
import json
from functools import cache
from importlib import resources
from typing import Any

__all__ = [
    "CLASS_KEY",
    "NAMESPACE",
    "backend_document",
    "file_parts",
    "operation_classes",
    "operation_count",
    "operation_id",
    "tool_names",
]

NAMESPACE = "craft_suite"
CLASS_KEY = "x-craft-suite-class"


@cache
def backend_document() -> dict[str, Any]:
    """The generated backend description, packaged with the connector."""
    text = resources.files(__package__).joinpath("backend_openapi.json").read_text()
    return json.loads(text)


def operation_count() -> int:
    """The number of operations the backend document describes."""
    return len(_operations())


def _operations() -> list[dict[str, Any]]:
    return [
        operation
        for item in backend_document()["paths"].values()
        for operation in item.values()
        if isinstance(operation, dict) and "operationId" in operation
    ]


@cache
def operation_classes() -> dict[str, str]:
    """operationId -> ``read`` or the governance class of the write."""
    return {op["operationId"]: op[CLASS_KEY] for op in _operations()}


@cache
def file_parts() -> dict[str, frozenset[str]]:
    """operationId -> the multipart fields carried as base64 text."""
    parts = {}
    for op in _operations():
        content = op.get("requestBody", {}).get("content", {})
        schema = content.get("multipart/form-data", {}).get("schema", {})
        names = frozenset(
            name
            for name, prop in schema.get("properties", {}).items()
            if prop.get("contentEncoding") == "base64"
        )
        if names:
            parts[op["operationId"]] = names
    return parts


#: The longest served name: the MCP limit, less the namespace prefix.
MAX_NAME = 64 - len(NAMESPACE) - 1


def _short(operation: str) -> str:
    if len(operation) <= MAX_NAME:
        return operation
    digest = hashlib.sha256(operation.encode()).hexdigest()[:6]
    return f"{operation[: MAX_NAME - 7].rstrip('_')}_{digest}"


@cache
def tool_names() -> dict[str, str]:
    """operationId -> tool name (before the namespace); long ids are shortened."""
    return {op: _short(op) for op in operation_classes()}


@cache
def _operations_by_name() -> dict[str, str]:
    return {name: op for op, name in tool_names().items()}


def operation_id(tool_name: str) -> str:
    """The operationId behind a tool name, namespaced or not."""
    prefix = f"{NAMESPACE}_"
    name = tool_name[len(prefix) :] if tool_name.startswith(prefix) else tool_name
    return _operations_by_name().get(name, name)

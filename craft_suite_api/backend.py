"""The backend API as one typed tool per operation (CONN-CRAFT-SUITE-API-R007).

fastmcp's OpenAPI provider turns the generated description
(``backend_openapi.json``, built by ``scripts/generate_backend_tools.py``)
into tools named ``craft_suite_<operationId>``. They run on a sub-server
mounted into the connector server, so the governance middleware below sees
only backend calls, never the app upstreams.

Governance (CONN-CRAFT-SUITE-API-R006, R008): every call is refused with a
typed result while the backend is not configured; every write needs the
operator's write switch and a confirmation (elicited, or ``confirm=true``),
and every write decision is written to the audit log.
"""

from __future__ import annotations

import base64
import binascii
import copy
import logging
import warnings
from dataclasses import dataclass
from typing import Any

import mcp.types as mt
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.providers.openapi import OpenAPIProvider
from fastmcp.server.providers.openapi.routing import HTTPRoute
from fastmcp.tools import Tool, ToolResult
from mcp.types import InputRequiredResult, ToolAnnotations
from scion_sdk.mcp.confirmation import confirmation_refusal, ctx_confirm_destructive

from .backend_catalog import (
    CLASS_KEY,
    NAMESPACE,
    backend_document,
    file_parts,
    operation_classes,
    operation_count,
    operation_id,
    tool_names,
)
from .error_authority import BACKEND_CONFIG_INVALID, BACKEND_NOT_CONFIGURED

__all__ = [
    "BACKEND_CONFIG_INVALID",
    "CLASS_KEY",
    "CONFIRM_PARAMETER",
    "NAMESPACE",
    "WRITES_DISABLED",
    "BackendGovernance",
    "backend_document",
    "build_backend_server",
    "Gate",
    "file_parts",
    "operation_classes",
    "operation_count",
    "operation_id",
    "tool_names",
]

CONFIRM_PARAMETER = "confirm"
WRITES_DISABLED = "WRITES_DISABLED"
INVALID_UPLOAD = "INVALID_UPLOAD"

CONFIRM_SCHEMA = {
    "type": "boolean",
    "default": False,
    "description": (
        "Explicitly confirm this write. Needed only when the client cannot "
        "answer a confirmation prompt."
    ),
}

REFUSAL_SCHEMA = {
    "type": "object",
    "properties": {
        "cancelled": {"const": True},
        "operation": {"type": "string"},
        "reason": {"type": "string"},
        "write_class": {"type": "string"},
    },
    "required": ["cancelled", "operation"],
}

_audit = logging.getLogger("craft_suite_api.audit")


def _write_class(route: HTTPRoute) -> str:
    return str(route.extensions.get(CLASS_KEY, "write"))


def _component(route: HTTPRoute, component: Any) -> None:
    """Tag, annotate and widen each tool for governance."""
    if not isinstance(component, Tool):
        return
    klass = _write_class(route)
    read_only = klass == "read"
    component.tags = set(component.tags) | {"backend", klass}
    component.annotations = ToolAnnotations(
        readOnlyHint=read_only,
        destructiveHint=route.method.upper() == "DELETE",
        idempotentHint=route.method.upper() in ("GET", "PUT", "DELETE"),
        openWorldHint=True,
    )
    if not read_only:
        parameters = copy.deepcopy(component.parameters)
        parameters.setdefault("properties", {})[CONFIRM_PARAMETER] = CONFIRM_SCHEMA
        component.parameters = parameters
    if component.output_schema is not None:
        output = {k: v for k, v in component.output_schema.items() if k != "$defs"}
        widened: dict[str, Any] = {"type": "object", "anyOf": [output, REFUSAL_SCHEMA]}
        if "$defs" in component.output_schema:
            widened["$defs"] = component.output_schema["$defs"]
        component.output_schema = widened


def _refusal(operation: str, reason: str, klass: str) -> ToolResult:
    payload = {
        "cancelled": True,
        "operation": operation,
        "reason": reason,
        "write_class": klass,
    }
    return ToolResult(structured_content=payload)


def _decode_files(operation: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Turn base64 file parts of an upload into binary multipart parts."""
    decoded = dict(arguments)
    for name in file_parts().get(operation, ()):
        if not isinstance(decoded.get(name), str):
            continue
        try:
            content = base64.b64decode(decoded[name], validate=True)
        except binascii.Error as exc:
            raise ToolError(f"{INVALID_UPLOAD}: {name} is not base64") from exc
        decoded[name] = (name, content, "application/octet-stream")
    return decoded


@dataclass(frozen=True)
class Gate:
    """The operator's switches the governance applies."""

    configured: bool
    allow_writes: bool
    #: The refusal code every call answers with; set when the settings are
    #: present but unusable (``BACKEND_CONFIG_INVALID``).
    refusal: str | None = None


class BackendGovernance(Middleware):
    """Typed refusals and audit for every backend call."""

    def __init__(self, gate: Gate) -> None:
        self.configured = gate.configured
        self.allow_writes = gate.allow_writes
        self.refusal = gate.refusal

    async def on_call_tool(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next,
    ):
        operation = operation_id(context.message.name)
        name = f"{NAMESPACE}_{tool_names().get(operation, operation)}"
        klass = operation_classes().get(operation)
        if klass is None:
            return await call_next(context)
        arguments = dict(context.message.arguments or {})
        confirm = arguments.pop(CONFIRM_PARAMETER, False) is True
        if self.refusal is not None:
            return _refusal(name, self.refusal, klass)
        if not self.configured:
            return _refusal(name, BACKEND_NOT_CONFIGURED, klass)
        if klass == "read":
            return await call_next(context)
        return await self._write(
            context, call_next, operation, klass, arguments, confirm
        )

    async def _write(self, context, call_next, operation, klass, arguments, confirm):
        name = f"{NAMESPACE}_{tool_names()[operation]}"
        ctx = context.fastmcp_context
        if not self.allow_writes:
            _audit.info(
                "refused",
                extra={"tool": name, "write_class": klass, "reason": WRITES_DISABLED},
            )
            return _refusal(name, WRITES_DISABLED, klass)
        decision = await ctx_confirm_destructive(
            ctx, name, confirmation_arguments=arguments, explicit_confirm=confirm
        )
        if isinstance(decision, InputRequiredResult):
            return decision
        if decision is not True:
            _audit.info("unconfirmed", extra={"tool": name, "write_class": klass})
            payload = confirmation_refusal(ctx, name)
            payload["write_class"] = klass
            return ToolResult(structured_content=payload)
        context.message.arguments = _decode_files(operation, arguments)
        _audit.info("sent", extra={"tool": name, "write_class": klass})
        return await call_next(context)


def build_backend_server(client: Any, gate: Gate) -> FastMCP:
    """The sub-server holding one tool per backend operation."""
    with warnings.catch_warnings():
        # The SDK's governed client is an httpx client; fastmcp accepts it.
        warnings.filterwarnings("ignore", message=".*httpx.AsyncClient.*deprecated")
        provider = OpenAPIProvider(
            backend_document(),
            client=client,
            mcp_component_fn=_component,
            mcp_names=tool_names(),
        )
    server = FastMCP("craft-suite-backend")
    server.add_provider(provider)
    server.add_middleware(BackendGovernance(gate))
    return server

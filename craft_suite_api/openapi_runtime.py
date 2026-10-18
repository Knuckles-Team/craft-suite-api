"""Native MCP registration for the reviewed operation contract."""

from typing import Any

from agent_connector_sdk.mcp.concurrency import run_blocking
from fastmcp.tools import Tool, ToolResult
from mcp.types import InputRequiredResult, ToolAnnotations
from pydantic import Field

from .openapi_execution import confirm_write, require_authorization
from .openapi_schema import CONTRACT, validate


PREFIX = "craft_suite"


def operation_tool_name(action: str) -> str:
    """The per-operation tool name for one reviewed contract action."""
    return f"{PREFIX}_{action}"


def operation_inputs(domain: str, action: str) -> dict[str, Any]:
    """The input schema of one action: its discriminated branch, without ``action``."""
    inputs, _outputs = CONTRACT["schemas"][domain]
    branch = next(
        item
        for item in inputs["oneOf"]
        if item["properties"]["action"]["enum"] == [action]
    )
    properties = {k: v for k, v in branch["properties"].items() if k != "action"}
    schema: dict[str, Any] = {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": [name for name in branch.get("required", []) if name != "action"],
    }
    if "$defs" in inputs:
        schema["$defs"] = inputs["$defs"]
    return schema


class OpenApiTool(Tool):
    """One reviewed OpenAPI operation with its typed inputs and response variants.

    Authorization is checked before the client is built, and a write is
    confirmed before any outbound request, exactly as for the contract.
    """

    domain: str = Field(exclude=True)
    action: str = Field(exclude=True)
    client_factory: Any = Field(exclude=True)

    async def run(self, arguments):
        validate(arguments, self.parameters)
        operation = CONTRACT["operations"][self.action]
        require_authorization(operation, CONTRACT)
        client = self.client_factory()
        call = {"action": self.action, **arguments}
        confirmation = await confirm_write(operation, call, client)
        if isinstance(confirmation, InputRequiredResult):
            return confirmation
        result = await run_blocking(client.execute, self.domain, call)
        return ToolResult(structured_content=result)


def register_domain(mcp, domain, client_factory):
    """Register one tool per reviewed operation of ``domain``."""
    _inputs, outputs = CONTRACT["schemas"][domain]
    for action in CONTRACT["domains"][domain]:
        operation = CONTRACT["operations"][action]
        read_only = bool(operation["read_only"])
        mcp.add_tool(
            OpenApiTool(
                name=operation_tool_name(action),
                domain=domain,
                action=action,
                client_factory=client_factory,
                description=operation.get("summary") or action.replace("_", " "),
                parameters=operation_inputs(domain, action),
                output_schema=outputs,
                tags={domain, "operation"},
                annotations=ToolAnnotations(
                    readOnlyHint=read_only,
                    destructiveHint=not read_only and operation["method"] == "DELETE",
                    idempotentHint=operation["method"] in ("GET", "HEAD", "PUT", "DELETE"),
                    openWorldHint=True,
                ),
            )
        )

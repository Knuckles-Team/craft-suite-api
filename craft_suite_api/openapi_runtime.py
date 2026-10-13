"""Native MCP registration for the reviewed operation contract."""

from typing import Any

from agent_connector_sdk.mcp.concurrency import run_blocking
from fastmcp.tools import Tool, ToolResult
from mcp.types import InputRequiredResult, ToolAnnotations
from pydantic import Field

from .openapi_execution import confirm_write
from .openapi_schema import CONTRACT, validate


class OpenApiTool(Tool):
    """One domain, discriminated action inputs, and declared response variants."""

    domain: str = Field(exclude=True)
    client_factory: Any = Field(exclude=True)

    async def run(self, arguments):
        validate(arguments, self.parameters)
        operation = CONTRACT["operations"][arguments["action"]]
        client = self.client_factory()
        confirmation = await confirm_write(operation, arguments, client)
        if isinstance(confirmation, InputRequiredResult):
            return confirmation
        result = await run_blocking(client.execute, self.domain, arguments)
        return ToolResult(structured_content=result)


def register_domain(mcp, domain, client_factory):
    operations = [
        CONTRACT["operations"][action] for action in CONTRACT["domains"][domain]
    ]
    read_only = all(operation["read_only"] for operation in operations)
    inputs, outputs = CONTRACT["schemas"][domain]
    mcp.add_tool(
        OpenApiTool(
            name=f"{domain}_operations",
            domain=domain,
            client_factory=client_factory,
            description="Bound OpenAPI operations: "
            + ", ".join(CONTRACT["domains"][domain]),
            parameters=inputs,
            output_schema=outputs,
            tags={domain},
            annotations=ToolAnnotations(
                readOnlyHint=read_only,
                destructiveHint=not read_only,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
    )

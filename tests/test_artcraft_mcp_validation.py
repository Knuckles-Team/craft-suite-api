import asyncio

import pytest

from craft_suite_api.backend import operation_count, tool_names
from craft_suite_api.mcp_server import get_mcp_instance


def _backend_names() -> set[str]:
    return {f"craft_suite_{name}" for name in tool_names().values()}


@pytest.mark.concept("CRAFT-001")
@pytest.mark.spec("CONN-CRAFT-SUITE-API-R003")
def test_mcp_instance_registration(monkeypatch):
    """MCP server instantiates with its tool domains registered.

    CONCEPT:CRAFT-001
    """
    monkeypatch.setattr("sys.argv", ["craft-suite-mcp"])
    mcp, args, middlewares = get_mcp_instance()
    assert mcp is not None
    tools = asyncio.run(mcp.list_tools())
    names = {tool.name for tool in tools}
    registry = {
        "registry_list_namespaces",
        "registry_activate",
        "registry_deactivate",
        "registry_status",
    }
    assert registry <= names
    backend = _backend_names()
    assert names == registry | backend
    assert len(backend) == operation_count()

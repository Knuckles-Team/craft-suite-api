import pytest

from craft_suite_api.mcp_server import get_mcp_instance


@pytest.mark.concept("CRAFT-001")
def test_mcp_instance_registration(monkeypatch):
    """MCP server instantiates with its tool domains registered.

    CONCEPT:CRAFT-001
    """
    monkeypatch.setattr("sys.argv", ["craft-suite-mcp"])
    mcp, args, middlewares = get_mcp_instance()
    assert mcp is not None

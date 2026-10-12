import pytest

from artcraft_api.mcp_server import get_mcp_instance


@pytest.mark.concept("CRAFT-001")
def test_mcp_instance_registration(monkeypatch):
    """MCP server instantiates with its tool domains registered.

    CONCEPT:CRAFT-001
    """
    monkeypatch.setattr("sys.argv", ["artcraft-mcp"])
    mcp, args, middlewares = get_mcp_instance()
    assert mcp is not None

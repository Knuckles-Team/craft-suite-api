import importlib

import pytest


@pytest.mark.concept("CRAFT-001")
def test_mcp_server_module_importable():
    """MCP server module imports cleanly at startup. CONCEPT:CRAFT-001"""
    assert importlib.import_module("artcraft_api.mcp_server") is not None

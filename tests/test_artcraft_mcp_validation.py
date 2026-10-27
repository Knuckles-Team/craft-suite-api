import asyncio

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
    tools = asyncio.run(mcp.list_tools())
    assert {tool.name for tool in tools} == {
        "craft_suite_get_folder_handler",
        "craft_suite_list_folders_handler",
        "craft_suite_status_alert_handler",
        "craft_suite_omni_gen_audio_models_handler",
        "craft_suite_omni_gen_image_models_handler",
        "craft_suite_omni_gen_mesh_models_handler",
        "craft_suite_omni_gen_splat_models_handler",
        "craft_suite_list_media_file_tags_handler",
        "craft_suite_list_tags_handler",
    }

from ..auth import get_client
from ..openapi_runtime import register_domain


def register_folders_tools(mcp):
    register_domain(mcp, "folders", get_client)


def register_omni_gen_tools(mcp):
    register_domain(mcp, "omni_gen", get_client)


def register_tags_tools(mcp):
    register_domain(mcp, "tags", get_client)

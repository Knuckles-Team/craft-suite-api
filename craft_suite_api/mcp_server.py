from agent_connector_sdk.connector import build_server as _sdk_build_server
from agent_connector_sdk.connector import run

PACKAGE = "craft_suite_api"


def get_mcp_instance(*, command_args=None):
    """Build the server from the declared connector."""
    args, mcp = _sdk_build_server(PACKAGE, command_args=command_args)
    return mcp, args, []


def build_server(*, command_args=None):
    return get_mcp_instance(command_args=command_args)[0]


def mcp_server():
    run(PACKAGE)


if __name__ == "__main__":
    mcp_server()

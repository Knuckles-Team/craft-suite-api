"""The connector's tool registrar: the backend API, one tool per operation."""

from ..auth import backend_settings, build_client
from ..backend import NAMESPACE, Gate, build_backend_server

__all__ = ["register_backend_tools"]


def register_backend_tools(mcp):
    """Mount every backend operation as ``craft_suite_<operationId>``."""
    settings = backend_settings()
    server = build_backend_server(
        build_client(settings),
        Gate(configured=settings.configured, allow_writes=settings.allow_writes),
    )
    mcp.mount(server, namespace=NAMESPACE)

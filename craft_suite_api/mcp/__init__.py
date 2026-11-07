"""The connector's tool registrars.

The backend API is one tool per operation (CONN-CRAFT-SUITE-API-R007); a
backend setting that cannot be used never stops the server: every backend
tool answers the typed refusal ``BACKEND_CONFIG_INVALID`` instead
(CONN-CRAFT-SUITE-API-APPS-R001). Every suite app's engine command is one tool
(CONN-CRAFT-SUITE-API-APPS-R017). Each app's command tools warm independently
(CONN-CRAFT-SUITE-API-APPS-R018).
"""

import logging

from scion_sdk.config import ConfigurationError, csv_values, setting

from ..app_commands import (
    AppCommandProvider,
    ExchangeOutputPaths,
    HideDispatchTools,
    SessionTracker,
    dispatch_tool_names,
)
from ..auth import PLACEHOLDER_ORIGIN, backend_settings, build_client
from ..backend import NAMESPACE, Gate, build_backend_server
from ..error_authority import BACKEND_CONFIG_INVALID
from ..lifecycle import record_backend
from ..upstreams import UPSTREAMS

__all__ = ["register_app_command_tools", "register_backend_tools"]

_logger = logging.getLogger(__name__)


def _backend_gate():
    """The client and gate; unusable settings give a refusing gate, never a raise."""
    import httpx

    try:
        settings = backend_settings()
        client = build_client(settings)
    except (ConfigurationError, ValueError, OSError, RuntimeError, LookupError) as exc:
        # The cause names the bad setting's rule, never a credential value.
        _logger.warning("%s: backend tools refuse: %s", BACKEND_CONFIG_INVALID, exc)
        record_backend(configured=False, invalid_code=BACKEND_CONFIG_INVALID)
        gate = Gate(
            configured=False, allow_writes=False, refusal=BACKEND_CONFIG_INVALID
        )
        return httpx.AsyncClient(base_url=PLACEHOLDER_ORIGIN), gate
    record_backend(configured=settings.configured)
    return client, Gate(
        configured=settings.configured, allow_writes=settings.allow_writes
    )


def register_backend_tools(mcp):
    """Mount every backend operation as ``craft_suite_<operationId>``."""
    client, gate = _backend_gate()
    mcp.mount(build_backend_server(client, gate), namespace=NAMESPACE)


def register_app_command_tools(mcp):
    """Serve each declared app's engine commands as ``<app>_cmd_<id>`` tools."""
    disabled = set(csv_values(setting("SCION_UPSTREAMS_DISABLED", "")))
    apps = {
        decl.name: (decl.command, *decl.args)
        for decl in UPSTREAMS
        if decl.enabled and decl.name not in disabled and decl.command
    }
    if not apps:
        return
    # Each app warms on its own; sessions hear tools/list_changed as each one
    # lands (CONN-CRAFT-SUITE-API-APPS-R018).
    tracker = SessionTracker(mcp)
    mcp.add_middleware(tracker)
    mcp.add_provider(
        AppCommandProvider(
            apps,
            tracker=tracker,
            wait_s=setting("CRAFT_SUITE_WARMUP_WAIT_S", 20.0),
            retry_s=setting("CRAFT_SUITE_REGISTRY_RETRY_S", 15.0),
        )
    )
    mcp.add_transform(HideDispatchTools(dispatch_tool_names(tuple(apps))))
    mcp.add_transform(ExchangeOutputPaths())

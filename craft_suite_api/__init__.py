#!/usr/bin/env python

import importlib
import inspect
import warnings

warnings.filterwarnings("ignore", message=".*urllib3.*or chardet.*")

from scion_sdk.config import ConfigurationError, load_config, setting
from scion_sdk.connector import Connector
from scion_sdk.connector_hooks import Readiness

from .upstreams import UPSTREAMS


async def _tier1_readiness() -> Readiness:
    """The component lifecycle as ``/ready`` serves it.

    Ready once no component is ``warming`` (CONN-CRAFT-SUITE-API-APPS-R018.5):
    a Degraded, Backoff or Unconfigured component never unseats the server, and
    the detail names the backend's and every app's lifecycle state. No request
    is made and no exception escapes: a bad or missing configuration reads
    ``not_configured`` or ``invalid`` (R001.1).
    """
    from . import app_commands
    from .lifecycle import BACKEND, DEGRADED, backend_view, record_backend

    warmup = app_commands.WARMUP
    apps = warmup.readiness_detail() if warmup is not None else {}
    warm = warmup is None or warmup.settled
    if BACKEND.state != DEGRADED:
        # The backend probe: the configuration outcome as a lifecycle event.
        try:
            load_config()
            record_backend(configured=bool(setting("CRAFT_SUITE_API_BASE_URL", "")))
        except ConfigurationError:
            record_backend(configured=False, invalid_code="BACKEND_CONFIG_INVALID")
    detail: dict[str, object] = {
        "backend": backend_view(),
        "state_backend": BACKEND.state,
    }
    if BACKEND.code:
        detail["code"] = BACKEND.code
    return Readiness(ready=warm, detail={**detail, **apps})


connector = Connector(
    instructions=(
        "Craft Suite connector: every backend API operation as one typed tool, "
        "the suite apps as upstreams, and every app engine command as its own "
        "tool (<app>_cmd_<command>)"
    ),
    tools="craft_suite_api.mcp",
    upstreams=UPSTREAMS,
    readiness=_tier1_readiness,
)

__all__: list[str] = ["connector"]

CORE_MODULES = [
    "craft_suite_api.error_authority",
]

OPTIONAL_MODULES = {
    "craft_suite_api.mcp_server": "mcp",
}


def _import_module_safely(module_name: str):
    """Try to import a module and return it, or None if not available."""
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None


def _expose_members(module):
    """Expose public classes and functions from a module into globals and __all__."""
    for name, obj in inspect.getmembers(module):
        if (inspect.isclass(obj) or inspect.isfunction(obj)) and not name.startswith(
            "_"
        ):
            globals()[name] = obj
            __all__.append(name)


for module_name in CORE_MODULES:
    module = importlib.import_module(module_name)
    _expose_members(module)

for module_name, extra_name in OPTIONAL_MODULES.items():
    module = _import_module_safely(module_name)
    if module is not None:
        _expose_members(module)
        globals()[f"_{extra_name.upper()}_AVAILABLE"] = True
    else:
        globals()[f"_{extra_name.upper()}_AVAILABLE"] = False

__all__.extend(["_MCP_AVAILABLE"])

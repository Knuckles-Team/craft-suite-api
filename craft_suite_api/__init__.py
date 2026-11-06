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
    """The Tier 1 backend state; an unconfigured backend never unseats the server.

    ``detail`` reports the configuration only: no request is made and no
    exception escapes, so a bad or missing configuration reads
    ``not_configured`` instead of failing the probe.
    """
    try:
        load_config()
        configured = bool(setting("CRAFT_SUITE_API_BASE_URL", ""))
    except ConfigurationError:
        configured = False
    return Readiness(
        ready=True,
        detail={"backend": "configured" if configured else "not_configured"},
    )


connector = Connector(
    instructions=(
        "Craft Suite connector: every backend API operation as one typed tool, "
        "plus the suite apps as lazily loaded upstreams"
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

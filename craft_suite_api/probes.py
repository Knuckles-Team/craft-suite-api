"""Probes: the backend and each app report a result, never a state.

CONN-CRAFT-SUITE-API-APPS-R018.2. A probe makes no state decision; the
lifecycle machine (``craft_suite_api.lifecycle``) turns each result into an
event and decides the state.
"""

from __future__ import annotations

from dataclasses import dataclass

from scion_sdk.config import ConfigurationError, load_config, setting

from .error_authority import BACKEND_CONFIG_INVALID, BACKEND_NOT_CONFIGURED

__all__ = ["ProbeResult", "app_probe", "backend_probe"]


@dataclass(frozen=True)
class ProbeResult:
    """One probe outcome: success, or a failure with its typed code."""

    ok: bool
    code: str = ""


def backend_probe() -> ProbeResult:
    """The backend configuration check; no request is made."""
    try:
        load_config()
        configured = bool(setting("CRAFT_SUITE_API_BASE_URL", ""))
    except ConfigurationError:
        return ProbeResult(False, BACKEND_CONFIG_INVALID)
    return (
        ProbeResult(True) if configured else ProbeResult(False, BACKEND_NOT_CONFIGURED)
    )


def app_probe(app: str) -> ProbeResult:
    """The registry load of one app (``AppWarmup``), as a result."""
    from . import app_commands
    from .lifecycle import READY, WARMING

    warmup = app_commands.WARMUP
    component = None if warmup is None else warmup.components.get(app)
    if component is None or component.state == WARMING:
        return ProbeResult(False, "APP_WARMING")
    if component.state == READY:
        return ProbeResult(True)
    return ProbeResult(False, app_commands.APP_REGISTRY_UNREADABLE)

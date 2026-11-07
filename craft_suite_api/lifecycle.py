"""One component lifecycle machine for the backend and every app.

CONN-CRAFT-SUITE-API-APPS-R018.1 to R018.5, R001.1. This is the connector-local
form of the SDK connector lifecycle (SCION-CONNECTOR-CONTROL-R917): the same
closed state set, the same edges and the same refusal, so that moving to the SDK
descriptor replaces this module and changes no caller. ``transition`` is the one
function that decides a component's state; nothing else assigns it.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Final

UNCONFIGURED: Final = "Unconfigured"
WARMING: Final = "warming"
READY: Final = "Ready"
DEGRADED: Final = "Degraded"
BACKOFF: Final = "Backoff"
STOPPED: Final = "Stopped"

STATES: Final = frozenset({UNCONFIGURED, WARMING, READY, DEGRADED, BACKOFF, STOPPED})

REGISTRY_LOADED: Final = "registry_loaded"
CYCLE_OK: Final = "cycle_ok"
CYCLE_FAIL: Final = "cycle_fail"
REMOVED: Final = "removed"

#: Failures at which Degraded gives way to Backoff (the three retries of R018).
BACKOFF_AFTER: Final = 3

LIFECYCLE_TRANSITION_REFUSED: Final = "LIFECYCLE_TRANSITION_REFUSED"

#: (from, event, guard) -> to. A guard of None matches any failure count.
EDGES: Final[dict[tuple[str, str, int | None], str]] = {
    (UNCONFIGURED, REGISTRY_LOADED, None): WARMING,  # activate
    (WARMING, CYCLE_OK, None): READY,  # settle
    (WARMING, CYCLE_FAIL, 1): DEGRADED,  # first_failure
    (DEGRADED, CYCLE_FAIL, BACKOFF_AFTER): BACKOFF,  # third_failure
    (DEGRADED, CYCLE_OK, None): READY,  # retry_ok_from_degraded
    (BACKOFF, CYCLE_OK, None): READY,  # retry_ok_from_backoff
}


class LifecycleTransitionRefused(Exception):  # noqa: N818 - the row names the refusal
    """An event that is illegal in the component's state (typed, never silent)."""

    code = LIFECYCLE_TRANSITION_REFUSED

    def __init__(self, component: str, state: str, event: str) -> None:
        super().__init__(
            f"{LIFECYCLE_TRANSITION_REFUSED}: {component} in {state} refuses {event}"
        )
        self.component = component
        self.state = state
        self.event = event

    def as_dict(self) -> dict[str, str]:
        return {
            "refused": "true",
            "code": self.code,
            "component": self.component,
            "state": self.state,
            "event": self.event,
        }


def transition(component: str, state: str, event: str, failures: int = 0) -> str:
    """The next state, or raise :class:`LifecycleTransitionRefused`."""
    if event == REMOVED and state != STOPPED:
        return STOPPED
    for guard in (failures, None):
        target = EDGES.get((state, event, guard))
        if target is not None:
            return target
    raise LifecycleTransitionRefused(component, state, event)


@dataclass
class Component:
    """One component's persisted record: its state and the last failure code."""

    name: str
    state: str = UNCONFIGURED
    code: str = ""
    failures: int = 0
    changed_at: float = field(default_factory=time.monotonic)

    def apply(self, event: str, *, code: str = "", failures: int = 0) -> str:
        """Move by one event through :func:`transition`; the refusal propagates."""
        self.state = transition(self.name, self.state, event, failures)
        self.failures = failures
        self.code = code if self.state in (DEGRADED, BACKOFF) else ""
        self.changed_at = time.monotonic()
        return self.state


#: The backend tier's record, written once by the backend gate (R001.1).
BACKEND = Component("backend")


def record_backend(*, configured: bool, invalid_code: str = "") -> None:
    """Record the configuration outcome of the backend gate as lifecycle events."""
    BACKEND.state, BACKEND.code, BACKEND.failures = UNCONFIGURED, "", 0
    if not configured and not invalid_code:
        BACKEND.code = "BACKEND_NOT_CONFIGURED"
        return
    BACKEND.apply(REGISTRY_LOADED)
    if invalid_code:
        BACKEND.apply(CYCLE_FAIL, code=invalid_code, failures=1)
    else:
        BACKEND.apply(CYCLE_OK)


def backend_view() -> str:
    """The backend field of the readiness detail, rendered from the state."""
    if BACKEND.state == UNCONFIGURED:
        return "not_configured"
    if BACKEND.state in (DEGRADED, BACKOFF):
        return "invalid"
    return "configured"

"""CONN-CRAFT-SUITE-API-APPS-R018.1 to R018.5: the component lifecycle machine."""

from __future__ import annotations

import asyncio

import pytest
from fastmcp import Client

from craft_suite_api import _tier1_readiness, app_commands
from craft_suite_api.lifecycle import (
    BACKEND,
    BACKOFF,
    DEGRADED,
    READY,
    STATES,
    STOPPED,
    UNCONFIGURED,
    WARMING,
    Component,
    LifecycleTransitionRefused,
    transition,
)
from craft_suite_api.probes import ProbeResult, app_probe, backend_probe
from tests.test_app_warmup import FakeRegistries, _server

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R018")

# id -> (from, event, failures, to)
OUTCOMES = {
    "activate": (UNCONFIGURED, "registry_loaded", 0, WARMING),
    "settle": (WARMING, "cycle_ok", 0, READY),
    "first_failure": (WARMING, "cycle_fail", 1, DEGRADED),
    "third_failure": (DEGRADED, "cycle_fail", 3, BACKOFF),
    "retry_ok_from_degraded": (DEGRADED, "cycle_ok", 0, READY),
    "retry_ok_from_backoff": (BACKOFF, "cycle_ok", 0, READY),
    "removed": (READY, "removed", 0, STOPPED),
}


@pytest.fixture(autouse=True)
def _reset(monkeypatch):
    monkeypatch.setattr(app_commands, "WARMUP", None)
    BACKEND.state, BACKEND.code, BACKEND.failures = UNCONFIGURED, "", 0
    yield
    BACKEND.state, BACKEND.code, BACKEND.failures = UNCONFIGURED, "", 0


def test_probes_return_results_not_states(monkeypatch) -> None:
    monkeypatch.delenv("CRAFT_SUITE_API_BASE_URL", raising=False)
    result = backend_probe()
    assert isinstance(result, ProbeResult) and not result.ok
    assert result.code == "BACKEND_NOT_CONFIGURED"
    monkeypatch.setenv("CRAFT_SUITE_API_BASE_URL", "https://service.example.invalid")
    assert backend_probe() == ProbeResult(True)
    assert not hasattr(result, "state")
    assert app_probe("photocraft").code == "APP_WARMING"


def test_failed_app_registry_reports_a_typed_failure(monkeypatch) -> None:
    async def scenario():
        fake = FakeRegistries({}, {"pdfcraft": 9})
        _server_, provider, _ = _server(fake, monkeypatch, retry_s=0.01)
        async with Client(_server_) as client:
            await client.list_tools()
            for _ in range(200):
                if provider.warmup.states["pdfcraft"] == BACKOFF:
                    break
                await asyncio.sleep(0.01)
            assert app_probe("pdfcraft") == ProbeResult(
                False, "APP_REGISTRY_UNREADABLE"
            )
            assert app_probe("photocraft") == ProbeResult(True)

    asyncio.run(scenario())


@pytest.mark.parametrize("outcome", list(OUTCOMES))
def test_every_warmup_and_backend_outcome_maps_to_one_lifecycle_state(outcome) -> None:
    src, event, failures, dst = OUTCOMES[outcome]
    assert dst in STATES
    assert transition("x", src, event, failures) == dst


def test_backend_unconfigured_stays_unconfigured(monkeypatch) -> None:
    monkeypatch.delenv("CRAFT_SUITE_API_BASE_URL", raising=False)
    asyncio.run(_tier1_readiness())
    assert BACKEND.state == UNCONFIGURED and BACKEND.code == "BACKEND_NOT_CONFIGURED"


def test_an_illegal_probe_event_is_refused_with_the_sdk_error_and_the_state_is_kept() -> (
    None
):
    component = Component("photocraft", state=READY)
    with pytest.raises(LifecycleTransitionRefused) as refused:
        component.apply("registry_loaded")
    assert refused.value.code == "LIFECYCLE_TRANSITION_REFUSED"
    assert (refused.value.component, refused.value.state, refused.value.event) == (
        "photocraft",
        READY,
        "registry_loaded",
    )
    assert component.state == READY
    with pytest.raises(LifecycleTransitionRefused):
        transition("x", STOPPED, "cycle_ok")
    with pytest.raises(LifecycleTransitionRefused):
        transition("x", WARMING, "cycle_fail", 3)


def test_ready_is_true_once_no_component_is_warming(monkeypatch) -> None:
    monkeypatch.delenv("CRAFT_SUITE_API_BASE_URL", raising=False)

    async def scenario():
        gate = asyncio.Event()
        fake = FakeRegistries({"filmcraft": gate}, {})
        server, provider, _ = _server(fake, monkeypatch)
        async with Client(server) as client:
            await client.list_tools()
            for _ in range(100):
                if provider.warmup.states["photocraft"] == READY:
                    break
                await asyncio.sleep(0.01)
            held = await _tier1_readiness()
            assert held.ready is False
            assert held.detail["state_filmcraft"] == WARMING
            gate.set()
            for _ in range(100):
                if provider.warmup.settled:
                    break
                await asyncio.sleep(0.01)
            assert (await _tier1_readiness()).ready is True

    asyncio.run(scenario())


def test_broken_components_do_not_hold_ready_and_show_their_state_in_the_detail(
    monkeypatch,
) -> None:
    monkeypatch.setenv("CRAFT_SUITE_API_BASE_URL", "https://craft.example.invalid/x")
    monkeypatch.setenv("CRAFT_SUITE_API_ALLOW_PLAINTEXT", "false")

    async def scenario():
        fake = FakeRegistries({}, {"pdfcraft": 9})
        server, provider, _ = _server(fake, monkeypatch, retry_s=0.01)
        async with Client(server) as client:
            await client.list_tools()
            for _ in range(200):
                if provider.warmup.states["pdfcraft"] == BACKOFF:
                    break
                await asyncio.sleep(0.01)
            probe = await _tier1_readiness()
            assert probe.ready is True
            assert probe.detail["state_pdfcraft"] == BACKOFF
            assert probe.detail["state_photocraft"] == READY
            assert probe.detail["apps_failed"] == "pdfcraft"
            assert probe.detail["state_backend"] in {READY, DEGRADED}

    asyncio.run(scenario())


def test_ready_shows_broken_backend_and_app_as_not_ready_and_recovers(
    monkeypatch,
) -> None:
    from craft_suite_api.lifecycle import record_backend

    monkeypatch.setenv("CRAFT_SUITE_API_BASE_URL", "http://craft.example.invalid")
    # The backend gate records an unusable setting once, as a lifecycle event.
    record_backend(configured=False, invalid_code="BACKEND_CONFIG_INVALID")

    async def scenario():
        fake = FakeRegistries({}, {"pdfcraft": 1})
        server, provider, _ = _server(fake, monkeypatch, retry_s=0.3)
        async with Client(server) as client:
            await client.list_tools()
            for _ in range(100):
                if provider.warmup.states["pdfcraft"] == DEGRADED:
                    break
                await asyncio.sleep(0.01)
            broken = await _tier1_readiness()
            assert broken.detail["state_pdfcraft"] == DEGRADED
            assert broken.detail["state_photocraft"] == READY
            assert broken.detail["backend"] == "invalid"
            assert broken.detail["state_backend"] == DEGRADED
            assert broken.ready is True
            for _ in range(200):
                if provider.warmup.states["pdfcraft"] == READY:
                    break
                await asyncio.sleep(0.01)
            fixed = await _tier1_readiness()
            assert fixed.detail["state_pdfcraft"] == READY
            assert fixed.detail["apps_failed"] == ""

    asyncio.run(scenario())

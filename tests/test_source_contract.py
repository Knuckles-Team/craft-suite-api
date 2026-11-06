"""Packaged content and withheld surfaces (CONN-CRAFT-SUITE-API-R004, R005)."""

import json
from pathlib import Path

import pytest

from craft_suite_api.backend import NAMESPACE, tool_names

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.spec("CONN-CRAFT-SUITE-API-R005")
def test_unscoped_ingestion_is_unavailable():
    import importlib.util

    assert importlib.util.find_spec("craft_suite_api.kg_ingest") is None
    assert importlib.util.find_spec("craft_suite_api.api") is None


def _snapshot_tools(app: str) -> set[str]:
    snapshot = json.loads(
        (ROOT / "content" / "snapshots" / f"{app}.tools.json").read_text(
            encoding="utf-8"
        )
    )
    return {f"{app}_{tool['name']}" for tool in snapshot["tools"]}


def _check_agent_prompt(prompt: dict, declared: set[str]) -> None:
    """An agent definition (CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R009) names
    tools of declared apps: an app's own snapshot tool, or an engine command
    tool ``<app>_cmd_<command>`` read at serve time."""
    for name in prompt["tools"]:
        app = name.split("_", 1)[0]
        assert app in declared, name
        assert name in _snapshot_tools(app) or name.startswith(f"{app}_cmd_"), name


def _check_native_prompt(prompt: dict) -> None:
    """A connector-native prompt lists the connector's own operations."""
    served = {f"{NAMESPACE}_{name}" for name in tool_names().values()}
    assert set(prompt["tools"]) <= served
    assert "graph ingestion is unavailable" in prompt["instructions"]["core_directive"]


def _check_app_prompt(prompt: dict, namespace: str, declared: set[str]) -> None:
    """An app prompt (CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R005) names only
    snapshot tools of one declared app, prefixed with the app namespace."""
    assert namespace in declared
    tools = set(prompt["tools"])
    assert tools
    assert all(name.startswith(f"{namespace}_") for name in tools)
    assert tools <= _snapshot_tools(namespace)


@pytest.mark.spec("CONN-CRAFT-SUITE-API-R004")
def test_served_prompts_match_admitted_capabilities():
    from craft_suite_api.upstreams import APPS

    declared = set(APPS)
    for path in (ROOT / "craft_suite_api/prompts").glob("*.json"):
        text = path.read_text()
        prompt = json.loads(text)
        assert "TODO" not in text
        namespace = prompt.get("requires_namespace")
        if prompt.get("role") == "system" and prompt.get("skills"):
            _check_agent_prompt(prompt, declared)
        elif namespace is None:
            _check_native_prompt(prompt)
        else:
            _check_app_prompt(prompt, namespace, declared)

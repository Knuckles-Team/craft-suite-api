"""CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R005: one prompt per functionality, namespaced tools only."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from craft_suite_api.content_gen.errors import CONTENT_PROMPT_TOOL_UNKNOWN, ContentError
from craft_suite_api.content_gen.prompts import render_prompts
from craft_suite_api.content_gen.sources import (
    AppSource,
    Functionality,
    ToolSnapshot,
    load_app_source,
    load_snapshot,
)

REPO = Path(__file__).resolve().parent.parent
APPS = (
    "photocraft",
    "wordcraft",
    "pdfcraft",
    "solidcraft",
    "vectorcraft",
    "figcraft",
    "effectcraft",
    "filmcraft",
    "soundcraft",
    "deckcraft",
    "cadcraft",
)

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R005")


def _load(app: str) -> tuple[AppSource, ToolSnapshot]:
    return (
        load_app_source(REPO / "content" / "apps" / f"{app}.yml"),
        load_snapshot(REPO / "content" / "snapshots" / f"{app}.tools.json"),
    )


def test_prompt_per_functionality_names_only_snapshot_tools() -> None:
    for app in APPS:
        source, snapshot = _load(app)
        rendered = render_prompts(source, snapshot)

        # One prompt per functionality, named <app>-<functionality>.json.
        assert len(rendered) == len(source.functionalities)
        for func in source.functionalities:
            name = f"{app}-{func.name}.json"
            assert name in rendered
            prompt = json.loads(rendered[name])

            # It names only snapshot tools, all namespaced.
            assert prompt["tools"] == [f"{app}_{t}" for t in func.tools]
            for tool in prompt["tools"]:
                assert tool.split("_", 1)[1] in snapshot.names()

            # It sets requires_namespace to the app and tells the model to
            # activate the namespace first.
            assert prompt["requires_namespace"] == app
            assert "registry_activate" in prompt["instructions"]["core_directive"]
            assert f"`{app}`" in prompt["instructions"]["core_directive"]

    # A functionality naming a tool absent from the snapshot refuses.
    source, snapshot = _load("cadcraft")
    bad_source = AppSource(
        app=source.app,
        summary=source.summary,
        classes=source.classes,
        functionalities=(
            Functionality(
                name="ghost",
                description="names a tool the snapshot lacks",
                tools=("ghost_tool",),
            ),
        ),
    )
    with pytest.raises(ContentError) as excinfo:
        render_prompts(bad_source, snapshot)
    assert excinfo.value.code == CONTENT_PROMPT_TOOL_UNKNOWN

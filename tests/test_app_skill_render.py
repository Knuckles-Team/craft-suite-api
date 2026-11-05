"""CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R004: one skill per app listing every snapshot tool."""

from __future__ import annotations

from pathlib import Path

import pytest

from craft_suite_api.content_gen.errors import CONTENT_SKILL_TOOL_UNKNOWN, ContentError
from craft_suite_api.content_gen.skill import render_skill
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

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R004")


def _load(app: str) -> tuple[AppSource, ToolSnapshot]:
    return (
        load_app_source(REPO / "content" / "apps" / f"{app}.yml"),
        load_snapshot(REPO / "content" / "snapshots" / f"{app}.tools.json"),
    )


def test_skill_lists_every_snapshot_tool_and_refuses_unknown_tool() -> None:
    for app in APPS:
        source, snapshot = _load(app)
        text = render_skill(source, snapshot)

        # Front matter holds name and description.
        assert text.startswith("---\n")
        assert f"name: {app}\n" in text
        assert "description:" in text

        # Every snapshot tool appears exactly once, namespaced.
        for tool in snapshot.tools:
            pattern = f"`{app}_{tool.name}`"
            assert text.count(pattern) == 1, (
                f"{app}: {tool.name} listed {text.count(pattern)} times"
            )

        # The activation step names the registry tool and the namespace.
        assert "registry_activate" in text
        assert f"namespace `{app}`" in text

        # An authored tool missing from the snapshot refuses.
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
            render_skill(bad_source, snapshot)
        assert excinfo.value.code == CONTENT_SKILL_TOOL_UNKNOWN

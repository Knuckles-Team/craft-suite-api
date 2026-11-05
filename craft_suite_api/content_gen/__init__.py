"""Content generation for the ArtCraft suite (CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT).

One renderer per content kind, all pure functions from an app source and its
tool snapshot to file text. The generator script drives them; the refusal
codes below are the only ways a render may fail.
"""

from craft_suite_api.content_gen.errors import (
    CONTENT_DRIFT,
    CONTENT_PARENT_UNKNOWN,
    CONTENT_PROMPT_TOOL_UNKNOWN,
    CONTENT_SKILL_TOOL_UNKNOWN,
    CONTENT_SNAPSHOT_MISSING,
    CONTENT_SNAPSHOT_STALE,
    ContentError,
)

__all__ = [
    "CONTENT_DRIFT",
    "CONTENT_PARENT_UNKNOWN",
    "CONTENT_PROMPT_TOOL_UNKNOWN",
    "CONTENT_SNAPSHOT_MISSING",
    "CONTENT_SKILL_TOOL_UNKNOWN",
    "CONTENT_SNAPSHOT_STALE",
    "ContentError",
]

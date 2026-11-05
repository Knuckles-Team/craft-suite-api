"""Refusal codes and the single error type of the content generator."""

from __future__ import annotations

#: A generated file on disk differs from the render of its sources.
CONTENT_DRIFT = "CONTENT_DRIFT"
#: An authored class names a parent outside the allowed set.
CONTENT_PARENT_UNKNOWN = "CONTENT_PARENT_UNKNOWN"
#: An authored prompt names a tool the snapshot does not list.
CONTENT_PROMPT_TOOL_UNKNOWN = "CONTENT_PROMPT_TOOL_UNKNOWN"
#: An app has a source file but no tool snapshot to render from.
CONTENT_SNAPSHOT_MISSING = "CONTENT_SNAPSHOT_MISSING"
#: An authored skill section names a tool the snapshot does not list.
CONTENT_SKILL_TOOL_UNKNOWN = "CONTENT_SKILL_TOOL_UNKNOWN"
#: A live tool fingerprint differs from the committed snapshot.
CONTENT_SNAPSHOT_STALE = "CONTENT_SNAPSHOT_STALE"


class ContentError(ValueError):
    """A content render or gate refusal.

    ``code`` is one of the module-level refusal tokens; the message names the
    app and the offending item but never a secret or a stack trace.
    """

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        super().__init__(f"{code}: {detail}" if detail else code)

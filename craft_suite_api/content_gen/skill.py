"""Render one app skill file (CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R004).

A pure function from the app source and its tool snapshot to Markdown. The
body holds when to use the app, the activation step, a table listing every
snapshot tool exactly once as ``<app>_<tool>`` with its first description
sentence, and the functionality list linking to the prompt names.
"""

from __future__ import annotations

from craft_suite_api.content_gen.errors import (
    CONTENT_SKILL_TOOL_UNKNOWN,
    ContentError,
)
from craft_suite_api.content_gen.sources import AppSource, ToolSnapshot, first_sentence


def _check_tools(app: str, tools, snapshot: ToolSnapshot) -> None:
    known = snapshot.names()
    for tool in tools:
        if tool not in known:
            raise ContentError(
                CONTENT_SKILL_TOOL_UNKNOWN,
                f"{app}: tool {tool!r} is not in the snapshot",
            )


def render_skill(source: AppSource, snapshot: ToolSnapshot) -> str:
    """The Markdown text of ``skills/<app>/SKILL.md`` for one app."""
    app = source.app
    for func in source.functionalities:
        _check_tools(app, func.tools, snapshot)
    lines = [
        "---",
        f"name: {app}",
        f"description: {source.summary}",
        "---",
        "",
        f"# {app.title()}",
        "",
        "## When to use",
        "",
        source.summary,
        "",
        "## Activation",
        "",
        f"Call `registry_activate` with the namespace `{app}` before using any "
        f"`{app}_*` tool.",
        "",
        "## Files in and out",
        "",
        "Pass an input file as `exchange://<sink>/<key>` (for example "
        "`exchange://files/in/photo.png`) or as an `https` URL; the server "
        "stages it and hands the app a local path. Give an output path as a "
        "relative path such as `out.png`: it lands in this run's folder, and "
        "after the call the result links each output in every configured sink.",
        "",
        "## Tools",
        "",
        "| Tool | What it does |",
        "|---|---|",
    ]
    for tool in snapshot.tools:
        sentence = first_sentence(tool.description) or tool.name
        lines.append(f"| `{app}_{tool.name}` | {sentence} |")
    if source.functionalities:
        lines += ["", "## Functionalities", ""]
        for func in source.functionalities:
            lines.append(
                f"- `{app}-{func.name}` — {func.description}"
                if func.description
                else f"- `{app}-{func.name}`"
            )
    lines.append("")
    return "\n".join(lines)

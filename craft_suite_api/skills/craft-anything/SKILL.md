---
name: craft-anything
description: Craft Anything coding-agent investigation — targets, evidence, findings, hypotheses, unknowns and reports over native code, Android, web, Electron and runtime targets.
---

# Craft-Anything

## When to use

Craft Anything coding-agent investigation — targets, evidence, findings, hypotheses, unknowns and reports over native code, Android, web, Electron and runtime targets.

## Activation

Call `registry_activate` with the namespace `craftanything` before using any `craftanything_*` tool.

## Files in and out

Pass an input file as `exchange://<sink>/<key>` (for example `exchange://files/in/photo.png`) or as an `https` URL; the server stages it and hands the app a local path. Give an output path as a relative path such as `out.png`: it lands in this run's folder, and after the call the result links each output in every configured sink.

## When the app is not ready

An app is `warming` while its command registry loads, `Ready` when it serves, `Degraded` after a failed load and `Backoff` once its retries are used. A call to a `warming` app answers the retryable refusal `APP_WARMING`; a call to a `Degraded` or `Backoff` app answers the retryable refusal `APP_REGISTRY_UNREADABLE`. Retry after `retry_after_s`; a `Backoff` app needs an operator.

## Tools

| Tool | What it does |
|---|---|
| `craftanything_assets_image_generate` | Make a picture with fal. |
| `craftanything_assets_model_generate` | Make a game-ready, low-poly 3D model (GLB) with fal. |
| `craftanything_core_action_approve` | Permission check for a coding agent's action (tool name and input). |
| `craftanything_core_brief_write` | Set the investigation brief: the question, purpose, targets, constraints and what 'done' means. |
| `craftanything_core_evidence_browse` | View part of a stored (or inline) evidence record: the summary, one part, one row of a list, a page of a list's rows (optionally only the rows matching given field values, cut to chosen fields, with the field names listed), or a part of a function dossier (pseudocode, assembly, basic_blocks, callers, callees, flow_*…), with coverage and next_offset. |
| `craftanything_core_evidence_export` | Write every evidence record and unknown to a JSON bundle file. |
| `craftanything_core_evidence_import` | Load a bundle written by core_evidence_export. |
| `craftanything_core_evidence_show` | All evidence recorded in this session (detail=summary for a compact list; filter by operation or evidence_id). |
| `craftanything_core_finding_edit` | Correct a recorded finding without changing its id. |
| `craftanything_core_finding_record` | Record a settled answer. |
| `craftanything_core_handoff_write` | Rewrite the handoff note: where we are, what's next, traps to avoid. |
| `craftanything_core_hypothesis_record` | Record a claim being tested, ideally with the prediction that would confirm or refute it, plus any supporting/contradicting evidence ids. |
| `craftanything_core_hypothesis_update` | Change a hypothesis's status (testing/supported/refuted/abandoned) and attach supporting or contradicting evidence ids and notes. |
| `craftanything_core_investigation_show` | The working memory of this investigation: brief, plan with step status, hypotheses, findings (with evidence ids) and the latest handoff. |
| `craftanything_core_journal_read` | Page through the project's append-only journal (tool calls, model turns, consents, errors), filtered by day, kind or tool. |
| `craftanything_core_person_ask` | Ask the person a question in the app and wait for the answer: a short question, up to six suggested answers shown as buttons, and optionally a typed reply. |
| `craftanything_core_plan_update` | Replace the plan with a numbered list of steps, each todo/doing/done/blocked with a short why. |
| `craftanything_core_report_save` | Save a report a client composed (Markdown, HTML or plain text) to an absolute path the person chose. |
| `craftanything_core_report_write` | Turn the investigation (brief, plan, findings, hypotheses, handoff) and the evidence ledger into a readable report: what we looked at, what we found (each finding with its plain-English summary, confidence and cited evidence), open questions, and how it was done. |
| `craftanything_core_session_show` | What's open, which target is active, Clean room or Deep mode, evidence and unknown counts, version. |
| `craftanything_core_target_close` | Close the active target (or the one named). |
| `craftanything_core_target_select` | Make another open target the active one. |
| `craftanything_core_targets_list` | Every open target with its id, kind and sha256. |
| `craftanything_core_unknown_add` | Record something not yet known, with what would settle it. |
| `craftanything_core_unknown_edit` | Change an unknown's status, evidence or resolution. |
| `craftanything_core_unknown_verify` | Check that a resolved unknown has a resolution and cites evidence that exists and is intact. |
| `craftanything_core_unknowns_show` | Recorded unknowns, filtered by status, severity or domain. |
| `craftanything_enable_toolset` | Add a group of tools to this connection's tool list (the list then changes). |
| `craftanything_list_toolsets` | List the groups of tools (native code, Android, web, Electron, runtime…) with how many tools each has and whether it is enabled in this connection. |
| `craftanything_rebuild_check` | For the builder: test the project's current build against the original now, with the same checks Craft Anything runs after each turn (a website's likeness at each width with the padding, colour, font and layout differences; an app's or game's picture against the original's; whether it builds; the mechanics sheet; credits). |

## Functionalities

- `craft-anything-open_investigation` — Set the investigation brief, plan the steps and manage the open targets.
- `craft-anything-gather_evidence` — Browse and record evidence, track unknowns and record settled findings.
- `craft-anything-write_report` — Turn the investigation into a report, save it and hand off the next session.

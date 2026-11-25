---
name: craft-anything-investigate-target
description: Investigate a target with evidence — write the brief and plan, triage and read the target, ground a finding in the evidence ledger, and publish the investigation report.
---

# Investigate a target

## When to use

A question needs to be answered about a file, a project or a system, and the answer has to stand on recorded evidence: what it is, what it contains, and a report that cites it.

## Inputs

- `${question}`: the question being answered, in one or two sentences.
- `${target}`: the target's absolute path (a file or folder).
- `${done_when}`: what a finished answer looks like.

Every app tool is served by the craft-suite-api connector; call them in this order in one session (the app keeps the investigation — brief, plan, evidence ledger, findings, handoff — between calls). A value written `${name}` is an input above or the value an earlier step returned (its answer names it).

## Steps

| # | Tool | Arguments | Why |
|---|---|---|---|
| 1 | `craftanything_core_brief_write` | `{"question": "${question}", "targets": ["${target}"], "done_when": "${done_when}"}` | Set the investigation brief before the first analysis call; the target is named here. |
| 2 | `craftanything_core_plan_update` | `{"steps": [{"title": "Read the target", "status": "doing", "why": "The brief's answer lives in the target"}, {"title": "Record the finding", "status": "todo", "why": "Grounded in the evidence ledger"}, {"title": "Write and save the report", "status": "todo", "why": "The done-when criteria"}]}` | Replace the plan with the steps; each step carries a title, a status and a short why. |
| 3 | `craftanything_core_target_triage` | `{"path": "${target}"}` | Open the target and take a first look: kind, size, a SHA-256 and the recommended next tools — recorded as the first evidence entry. |
| 4 | `craftanything_core_text_read` | `{"path": "${target}", "limit": 80}` | Read the first lines of the target as text (paged); recorded as a second evidence entry with its location. |
| 5 | `craftanything_core_evidence_show` | `{"detail": "summary"}` | List the evidence ledger; take the evidence ids of the triage and read records — a finding may only cite ids that exist there. |
| 6 | `craftanything_core_finding_record` | `{"statement": "${statement}", "confidence": "observed", "evidence_ids": ["${evidence_id}"]}` | Record the settled answer; every cited evidence id is checked against the ledger, so only step 5's ids are admissible. |
| 7 | `craftanything_core_report_write` | `{"format": "markdown", "include_evidence": true}` | Turn the investigation (brief, plan, findings, handoff) and the evidence ledger into a readable report; the text is returned in the result. |
| 8 | `craftanything_core_report_save` | `{"path": "investigation-report.md", "text": "${report}"}` | Save the report to a relative path (must end in .md, .html, .htm or .txt); the exchange stages it and publishes it to every sink. |
| 9 | `craftanything_core_handoff_write` | `{"text": "${handoff}"}` | Rewrite the handoff note — where we are, what is next, traps to avoid — so the next turn resumes without re-reading. |

## Outputs

Formats: md (the report; `html` works the same way). A relative output path lands in the run folder of the call; after the call the result's `scion/artifacts` lists each file with its link in every configured exchange sink (the object store under `<app>/<date>/<run>/<name>`, and the file share when configured). Pass a published file to another workflow as `exchange://objects/<key>`.

## Verify

Read the saved report: it carries the brief's question and done-when, the finding with its confidence, and an evidence ledger naming both operations (`core_target_triage`, `core_text_read`) with their evidence ids; the file is present in the sink links the save result reports.

## Notes

- Evidence ids come only from the ledger (step 5); a finding that cites an unknown id is refused, and `craftanything_core_evidence_show` is the check that the ids exist before `craftanything_core_finding_record`.
- The target-reading tools (`craftanything_core_target_triage`, `craftanything_core_text_read`) are served by the connector in Deep mode, which is read-only: the target's code, files and page source may be read, nothing runs and `--allow-run` is not granted.
- Investigation state (brief, plan, ledger, findings, handoff) lives in the app's session for the caller; `craftanything_core_investigation_show` reads it back any time.

## Refusals

An app is in one lifecycle state: `warming` while its command registry loads, `Ready`, `Degraded` after a failed load, Backoff once its retries are used. A call to a `warming` app answers `APP_WARMING` (retryable, `retry_after_s`): wait that long and call again. A call to a `Degraded` or `Backoff` app answers `APP_REGISTRY_UNREADABLE` (retryable): retry after `retry_after_s`; a `Backoff` app has used its retries and needs an operator. Report any other refusal verbatim; never retry past it.

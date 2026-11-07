---
name: solidcraft
description: SolidCraft parametric solid modeling — parameters, bodies, exports and measurements.
---

# Solidcraft

## When to use

SolidCraft parametric solid modeling — parameters, bodies, exports and measurements.

## Activation

Call `registry_activate` with the namespace `solidcraft` before using any `solidcraft_*` tool.

## Files in and out

Pass an input file as `exchange://<sink>/<key>` (for example `exchange://files/in/photo.png`) or as an `https` URL; the server stages it and hands the app a local path. Give an output path as a relative path such as `out.png`: it lands in this run's folder, and after the call the result links each output in every configured sink.

## When the app is not ready

An app is `warming` while its command registry loads, `Ready` when it serves, `Degraded` after a failed load and `Backoff` once its retries are used. A call to a `warming` app answers the retryable refusal `APP_WARMING`; a call to a `Degraded` or `Backoff` app answers the retryable refusal `APP_REGISTRY_UNREADABLE`. Retry after `retry_after_s`; a `Backoff` app needs an operator.

## Tools

| Tool | What it does |
|---|---|
| `solidcraft_batch` | Run commands in order, stopping at the first error. |
| `solidcraft_body_topology` | The edges (index, midpoint, length, endpoints) and faces (index, name, area, centroid, plane normal, a `point` that lies on the face, and for a cylindrical face its `cylinder`: origin, axis, radius) of a body. |
| `solidcraft_check_parameters` | Try parameter values without keeping them: set every parameter in `set` with one rebuild, report what `report` asks for, and put the design back exactly as it was (undo history included). |
| `solidcraft_compare_picture` | Compare the model's outline with the part in a reference picture — a concept render, a product photo, one view off a design board. |
| `solidcraft_crash_reports` | SolidCraft's crash reports on this computer (the app's when connected to it). |
| `solidcraft_describe_command` | One command's parameter docs and, for commands with a typed contract (every new command, and more of the older ones as they are converted), the JSON Schemas (2020-12) of its parameters (`input`) and of a successful result (`output`); null for the others. |
| `solidcraft_execute` | Run one command with JSON parameters, exactly as the toolbar, palette and scripts do. |
| `solidcraft_export` | Export bodies to STEP (. |
| `solidcraft_inspect_design` | The whole design: user parameters (expression, value, errors), the timeline (features with type, suppressed, rolled back, error, warning, timing), bodies (volume, area, centre of mass, bounding box, face/edge/vertex counts), sketches (curves with ids and coordinates, points, constraints, profiles, degrees of freedom, solve status), assembly joints (what each origin is attached to: occurrence, the feature, face, edge or sketch curve its face names refer to, whether it resolves and why not; `execute` `joint. |
| `solidcraft_list_commands` | The command catalog: id, label, toolbar tab/panel, shortcut, one-line parameter docs and whether the command is enabled right now. |
| `solidcraft_measure` | Volume (mm³), surface area (mm²), centre of mass, bounding box and face/edge/vertex counts of one body or all bodies, with totals. |
| `solidcraft_new_design` | Start a new, empty design (unsaved changes to the current one are discarded). |
| `solidcraft_open` | Open a . |
| `solidcraft_pending` | Bridged to the app: the result of a request that was still running when its tool call returned (an error starting "still running:"). |
| `solidcraft_redo` | Redo the last undone change. |
| `solidcraft_running` | What the app is running or has queued right now, for every client: each request's connection and id, method, command id (a batch's step count), seconds since it arrived (running_s) and whether it still waits its turn (queued); `self` marks a request sent on the connection that asks. |
| `solidcraft_save` | Save the design to `path` or its current file (a design opened as . |
| `solidcraft_screenshot` | Render the design and return it as a PNG image. |
| `solidcraft_set_parameter` | Create or change a user parameter and re-evaluate the timeline. |
| `solidcraft_skill_reference` | Read a document of SolidCraft's bundled agent skills (solidcraft-modeling, solidcraft-mechanisms, solidcraft-editing, solidcraft-checking) from the copy built into SolidCraft. |
| `solidcraft_undo` | Undo the last change to the design. |

## Functionalities

- `solidcraft-model_body` — Start a design, run modeling commands and look at the result.
- `solidcraft-parameterize_design` — Add parameters to a design and verify their effect.
- `solidcraft-export_model` — Measure a design and export its bodies.

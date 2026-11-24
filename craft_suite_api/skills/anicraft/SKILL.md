---
name: anicraft
description: AniCraft headless animation — timeline documents, keyframed scenes and layers, command scripts and frame renders as PNG.
---

# Anicraft

## When to use

AniCraft headless animation — timeline documents, keyframed scenes and layers, command scripts and frame renders as PNG.

## Activation

Call `registry_activate` with the namespace `anicraft` before using any `anicraft_*` tool.

## Files in and out

Pass an input file as `exchange://<sink>/<key>` (for example `exchange://files/in/photo.png`) or as an `https` URL; the server stages it and hands the app a local path. Give an output path as a relative path such as `out.png`: it lands in this run's folder, and after the call the result links each output in every configured sink.

## When the app is not ready

An app is `warming` while its command registry loads, `Ready` when it serves, `Degraded` after a failed load and `Backoff` once its retries are used. A call to a `warming` app answers the retryable refusal `APP_WARMING`; a call to a `Degraded` or `Backoff` app answers the retryable refusal `APP_REGISTRY_UNREADABLE`. Retry after `retry_after_s`; a `Backoff` app needs an operator.

## Tools

| Tool | What it does |
|---|---|
| `anicraft_anicraft_commands` | Lists the commands anicraft_run accepts: id, label, menu, shortcut, a summary of their params, and whether they change the document. |
| `anicraft_anicraft_document` | The open document: stage size and frame rate, scenes, the current scene's layers and keyframes, library symbols, and the current scene, frame, layer and selection. |
| `anicraft_anicraft_render` | A frame of the current scene as a PNG picture, exactly as exported. |
| `anicraft_anicraft_run` | Runs one command (see anicraft_commands) with its params and returns its result, plus the document revision and current frame. |
| `anicraft_anicraft_run_script` | Runs commands in order and returns each result. |

## Functionalities

- `anicraft-inspect_document` — Read the open document, its stage size, frame rate, scenes, layers, keyframes and the current selection.
- `anicraft-run_command` — Run one engine command with its params and inspect the result.
- `anicraft-run_script` — Run a sequence of commands in order, one result per step.
- `anicraft-render_frame` — Render a frame of the current scene as a PNG, exactly as exported.

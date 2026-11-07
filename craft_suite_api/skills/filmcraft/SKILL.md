---
name: filmcraft
description: FilmCraft video editing — projects, sequences, media imports and frame renders.
---

# Filmcraft

## When to use

FilmCraft video editing — projects, sequences, media imports and frame renders.

## Activation

Call `registry_activate` with the namespace `filmcraft` before using any `filmcraft_*` tool.

## Files in and out

Pass an input file as `exchange://<sink>/<key>` (for example `exchange://files/in/photo.png`) or as an `https` URL; the server stages it and hands the app a local path. Give an output path as a relative path such as `out.png`: it lands in this run's folder, and after the call the result links each output in every configured sink.

## When the app is not ready

An app is `warming` while its command registry loads, `Ready` when it serves, `Degraded` after a failed load and `Backoff` once its retries are used. A call to a `warming` app answers the retryable refusal `APP_WARMING`; a call to a `Degraded` or `Backoff` app answers the retryable refusal `APP_REGISTRY_UNREADABLE`. Retry after `retry_after_s`; a `Backoff` app needs an operator.

## Tools

| Tool | What it does |
|---|---|
| `filmcraft_command_batch` | Run several commands in order: {steps: [{id, params? |
| `filmcraft_command_list` | List every command (id, label, menu path, shortcut, parameter doc, enabled now). |
| `filmcraft_command_run` | Run a command by id with JSON params, e. |
| `filmcraft_doc_inspect` | The project as JSON: the tree (as project_inspect) plus the active sequence (as sequence_inspect; null when there is none). |
| `filmcraft_media_import` | Import media files by absolute path (MP4/MOV, WAV/MP3/FLAC/AIFF/Ogg, PNG/JPEG/…). |
| `filmcraft_project_inspect` | Project tree (bins and items with ids, types, durations), active sequence, source clip. |
| `filmcraft_render_frame` | Render the active sequence's frame (at `seconds` or the playhead) and return it as PNG. |
| `filmcraft_render_preview` | The active sequence's frame at `seconds` (default: the playhead) as PNG, same as render_frame (bridge mode: Program monitor screenshot). |
| `filmcraft_sequence_inspect` | The active sequence as JSON: settings, tracks, clips (ids, start/duration in ticks and frames, effects), transitions, markers, in/out, playhead, selection. |
| `filmcraft_ui_click` | Live app: click an element by id or at x,y (points). |
| `filmcraft_ui_control` | Live app: call any control-channel method directly (ui. |
| `filmcraft_ui_drag` | Live app: press-drag-release from one point/element to another (move clips, trim edges, scrub, resize panels, drop project items onto tracks). |
| `filmcraft_ui_elements` | Live app: every on-screen interactive element with id, label and rect (points). |
| `filmcraft_ui_inspect` | Live app: UI state (tool, workspace, panels, timeline zoom, playback, selection, fps). |
| `filmcraft_ui_key` | Live app: press a key or shortcut (e. |
| `filmcraft_ui_screenshot` | Live app: screenshot of the window or one panel (PNG). |
| `filmcraft_ui_type` | Live app: type text into the focused field. |

## Functionalities

- `filmcraft-import_and_sequence` — Import media and lay it into a sequence.
- `filmcraft-trim_sequence` — Run timeline commands and check the rendered frame.
- `filmcraft-inspect_project` — Read the project, sequence and document state.

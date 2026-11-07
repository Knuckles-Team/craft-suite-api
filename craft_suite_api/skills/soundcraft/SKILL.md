---
name: soundcraft
description: SoundCraft audio mixing — sessions, tracks, imports, edits and bounce renders.
---

# Soundcraft

## When to use

SoundCraft audio mixing — sessions, tracks, imports, edits and bounce renders.

## Activation

Call `registry_activate` with the namespace `soundcraft` before using any `soundcraft_*` tool.

## Files in and out

Pass an input file as `exchange://<sink>/<key>` (for example `exchange://files/in/photo.png`) or as an `https` URL; the server stages it and hands the app a local path. Give an output path as a relative path such as `out.png`: it lands in this run's folder, and after the call the result links each output in every configured sink.

## When the app is not ready

An app is `warming` while its command registry loads, `Ready` when it serves, `Degraded` after a failed load and `Backoff` once its retries are used. A call to a `warming` app answers the retryable refusal `APP_WARMING`; a call to a `Degraded` or `Backoff` app answers the retryable refusal `APP_REGISTRY_UNREADABLE`. Retry after `retry_after_s`; a `Backoff` app needs an operator.

## Tools

| Tool | What it does |
|---|---|
| `soundcraft_batch` | Run up to 1000 commands in order; stops at the first error unless keep_going. |
| `soundcraft_bounce_mix` | Render the mix to an audio file. |
| `soundcraft_click` | APP_ONLY. |
| `soundcraft_drag` | APP_ONLY. |
| `soundcraft_execute` | Run one command by id with JSON params. |
| `soundcraft_import_audio` | Import an audio file (WAV, AIFF, FLAC, MP3, OGG, AAC/M4A, ALAC, CAF) onto a new or existing track. |
| `soundcraft_inspect_session` | The whole session as JSON: tracks (clips, inserts, sends, automation), busses, markers, groups, selection, transport. |
| `soundcraft_key` | APP_ONLY. |
| `soundcraft_list_commands` | List SoundCraft commands (id, label, menu path, shortcut, params doc, enabled). |
| `soundcraft_menu_invoke` | APP_ONLY. |
| `soundcraft_new_session` | Start a new session (optionally the built-in demo). |
| `soundcraft_open_session` | Open a . |
| `soundcraft_parity` | Feature-parity report against the incumbent's menu catalog. |
| `soundcraft_save_session` | Save the session (path required the first time; replace: true to save over another existing file). |
| `soundcraft_screenshot` | APP_ONLY. |
| `soundcraft_ui_inspect` | APP_ONLY. |
| `soundcraft_ui_set` | APP_ONLY. |

## Functionalities

- `soundcraft-mix_session` — Start a session, inspect the tracks and bounce the mix.
- `soundcraft-import_and_save` — Import audio onto the session and save it.
- `soundcraft-edit_session` — Run session commands and review the result.

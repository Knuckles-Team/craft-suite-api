---
name: soundcraft
description: SoundCraft audio mixing — sessions, tracks, imports, edits and bounce renders.
---

# Soundcraft

## When to use

SoundCraft audio mixing — sessions, tracks, imports, edits and bounce renders.

## Activation

Call `registry_activate` with the namespace `soundcraft` before using any `soundcraft_*` tool.

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

---
name: effectcraft
description: EffectCraft motion graphics — projects, compositions, effects, keyframes and rendering.
---

# Effectcraft

## When to use

EffectCraft motion graphics — projects, compositions, effects, keyframes and rendering.

## Activation

Call `registry_activate` with the namespace `effectcraft` before using any `effectcraft_*` tool.

## Files in and out

Pass an input file as `exchange://<sink>/<key>` (for example `exchange://files/in/photo.png`) or as an `https` URL; the server stages it and hands the app a local path. Give an output path as a relative path such as `out.png`: it lands in this run's folder, and after the call the result links each output in every configured sink.

## When the app is not ready

An app is `warming` while its command registry loads, `Ready` when it serves, `Degraded` after a failed load and `Backoff` once its retries are used. A call to a `warming` app answers the retryable refusal `APP_WARMING`; a call to a `Degraded` or `Backoff` app answers the retryable refusal `APP_REGISTRY_UNREADABLE`. Retry after `retry_after_s`; a `Backoff` app needs an operator.

## Tools

| Tool | What it does |
|---|---|
| `effectcraft_add_effect` | Apply an effect to a layer and optionally set its parameters in one undoable call. |
| `effectcraft_add_keyframe` | Add keyframes to a property (turns the stopwatch on): one with `time` (+ optional `value`, default the current value) or many with `keys: [{time, value}]`, then optionally set their `interpolation`: linear, bezier, hold, easyEase, easyEaseIn, easyEaseOut. |
| `effectcraft_batch` | Run several engine commands in one call as ONE undo step (engine. |
| `effectcraft_command_batch` | Run commands in order, returning each result or error. |
| `effectcraft_command_list` | List engine commands: id, label, menu path, shortcut, `params` doc (e. |
| `effectcraft_command_run` | Run any engine command by id with JSON params; edits are undoable. |
| `effectcraft_describe_command` | One command in full: id, label, menu path, shortcut, the `params` doc, a JSON Schema of its parameters (`schema`: properties, required, additionalProperties) and whether it can run now (`why` if not). |
| `effectcraft_doc_inspect` | Inspect the project overview and active composition (null when no composition is active). |
| `effectcraft_execute_command` | Run any engine command by id with JSON params; edits are undoable. |
| `effectcraft_get_comp` | A composition: id, name, size, frame rate, duration, work area, background and its layers top to bottom (id, index, name, type, in/out/start seconds, blend mode, parent, track matte, switches). |
| `effectcraft_get_layer` | A layer's property tree (transform, masks, effects, text, shape contents, . |
| `effectcraft_get_project` | Project overview: file path, dirty flag, bit depth, every item (id, name, type Composition/Footage/Solid/Folder, size, duration, layer count), the active comp id, current time (s), selected layers and the undo stack. |
| `effectcraft_get_property` | Read one property: type, value at `time` (comp seconds; default the current time), whether it is animated, its keyframes (time, value, in/out interpolation) and expression. |
| `effectcraft_get_state` | Where things stand: the editor state (active comp, current time, selected layers/keys/items, open comps, tool, work area) plus what this build can do (`app`: version, command and effect counts, GPU effects, import/export formats, After Effects parity summary). |
| `effectcraft_history` | The branching undo history (History panel): without arguments lists every state {index, id, label, parent, depth (0 = working line, >0 = branch), current, future}; undoing and then editing keeps the undone states as a branch. |
| `effectcraft_list_commands` | List engine commands: id, label, menu path, shortcut, `params` doc (e. |
| `effectcraft_list_effects` | The effect registry: id, After Effects name, category, GPU and 32-bpc support. |
| `effectcraft_list_fonts` | The font families text layers can use, bundled and installed on this machine: family, styles, origin (bundled / system / user), whether it is a variable font and the name in the font's own language. |
| `effectcraft_open_project` | Open a project: `path` to an . |
| `effectcraft_redo` | Redo `steps` undone edits (default 1). |
| `effectcraft_render_frame` | Render a composition frame (default: the active comp at the current time) and return it as a PNG image, longest side `max_side` (default 960, 0 = full size). |
| `effectcraft_render_preview` | Render a composition frame (default: the active comp at the current time) and return it as a PNG image, longest side `max_side` (default 960, 0 = full size). |
| `effectcraft_run_script` | Run JavaScript with an After Effects-style scripting object model (app, app. |
| `effectcraft_save_project` | Save the project to its current file, or to `path` (Save As, . |
| `effectcraft_script_ui` | Drive ScriptUI windows that scripts opened (dialogs, palettes, dockable panels). |
| `effectcraft_set_property` | Set a property. |
| `effectcraft_undo` | Undo the last `steps` edits (default 1). |

## Functionalities

- `effectcraft-build_composition` — Open a project, inspect a composition and add effects.
- `effectcraft-keyframe_property` — Read a property and animate it with keyframes.
- `effectcraft-script_project` — Drive the project through commands and scripts.

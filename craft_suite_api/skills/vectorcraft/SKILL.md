---
name: vectorcraft
description: VectorCraft vector illustration — shapes, paths, paint, text, effects and export.
---

# Vectorcraft

## When to use

VectorCraft vector illustration — shapes, paths, paint, text, effects and export.

## Activation

Call `registry_activate` with the namespace `vectorcraft` before using any `vectorcraft_*` tool.

## Tools

| Tool | What it does |
|---|---|
| `vectorcraft_add_text` | Create point type at (x, y) (the first baseline), area type when width/height are given (`fit` autoHeight grows the frame to the text, shrinkText scales the text down to fit), or type in/on an existing path (`path` id + `mode` area|onPath; `pathEffect` rainbow|skew|3dRibbon|stairStep|gravity). |
| `vectorcraft_answer_dialog` | Set fields of the desktop app's open dialog in order, then confirm (OK) or cancel it, as the control protocol's ui. |
| `vectorcraft_apply_effect` | Append a live effect (Effect menu) to the selection or `ids`. |
| `vectorcraft_command_batch` | Run steps in order; each edit is its own undo step, or with atomic:true the whole batch is one (named `label`, else after its first edit; `atomic` says which documents). |
| `vectorcraft_command_list` | Discover command ids, labels, parameter descriptions and enabled state. |
| `vectorcraft_command_run` | Run an engine command by id with its JSON params. |
| `vectorcraft_create_graph` | Create a graph (graph tools) in the plot rectangle. |
| `vectorcraft_doc_inspect` | Summary of the active document, including artboards, layer tree, selection and history. |
| `vectorcraft_draw_path` | Create a path from points ([[x,y],…] or [{x,y,in? |
| `vectorcraft_draw_shape` | Create a live shape and apply optional paint. |
| `vectorcraft_export` | Export the active document with the engine's document. |
| `vectorcraft_inspect_document` | Summary of the active document: artboards, layer tree (ids, names, kinds, bounds, fill/stroke; `opacity` as a 0–1 fraction and `opacityPct` in the 0–100 % scale the drawing tools take), selection, undo history, current tool and default paint. |
| `vectorcraft_inspect_ui` | UI state of the running desktop app: tool and options, panels, dialogs, view (zoom/center), window, documents, perf. |
| `vectorcraft_invoke_menu` | Invoke a menu item by its command id (same ids as list_commands, including UI-only commands like view. |
| `vectorcraft_list_commands` | List VectorCraft commands (id, label, menu path, shortcut, parameter description, enabled state). |
| `vectorcraft_open_file` | Open a file as a new, active document: . |
| `vectorcraft_open_panel` | Open a panel in the desktop app's dock by id (layers, swatches, stroke, align, pathfinder, transform, …; case-insensitive, display labels like "Layers" work too). |
| `vectorcraft_pathfinder` | Combine the selected (or `ids`) objects destructively, back to front: unite, minusFront, intersect, exclude, divide, trim, merge, crop, outline, minusBack. |
| `vectorcraft_pointer_gesture` | Drive the active tool with mouse events in document coordinates, exactly like the mouse would (e. |
| `vectorcraft_press_key` | Send a key press with modifiers, e. |
| `vectorcraft_redo` | Redo the last undone change (Edit → Redo): the change the last undo took back. |
| `vectorcraft_render_preview` | Render an artboard (default the first) as inline PNG without changing the document. |
| `vectorcraft_run_command` | Execute any VectorCraft command by id with JSON params (see list_commands for ids and params). |
| `vectorcraft_save_file` | Save the active document with the engine's document. |
| `vectorcraft_screenshot` | Render the active artboard to PNG and return it as an image (optionally also saving it to `path`). |
| `vectorcraft_select_tool` | Switch the active tool (as clicking it in the Tools panel). |
| `vectorcraft_set_paint` | Set fill, stroke and/or stroke weight on the selection (or `ids`) and as the default for new art. |
| `vectorcraft_text_wrap` | Make the selected (or `ids`) objects wrap objects: area type below them in the same layer flows around them (offset in pt, invert = flow inside). |
| `vectorcraft_transform` | Move, rotate, scale, reflect or shear the selection (or `ids`); several may be combined and run in that order. |
| `vectorcraft_type_text` | Type text into the focused widget (text tool, dialog field). |
| `vectorcraft_ui_inspect` | Inspect the connected desktop interface; returns a tool error in headless mode. |
| `vectorcraft_ui_screenshot` | Capture the connected desktop window as inline PNG; requires a running desktop app. |
| `vectorcraft_undo` | Undo the last change (Edit → Undo). |

## Functionalities

- `vectorcraft-create_illustration` — Draw shapes and paths, paint them and save the document.
- `vectorcraft-edit_selection` — Combine, transform and undo edits on the selection.
- `vectorcraft-export_artwork` — Export the document and check the rendered result.

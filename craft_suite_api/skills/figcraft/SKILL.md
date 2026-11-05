---
name: figcraft
description: FigCraft figure design — layers, properties, text and document export.
---

# Figcraft

## When to use

FigCraft figure design — layers, properties, text and document export.

## Activation

Call `registry_activate` with the namespace `figcraft` before using any `figcraft_*` tool.

## Files in and out

Pass an input file as `exchange://<sink>/<key>` (for example `exchange://files/in/photo.png`) or as an `https` URL; the server stages it and hands the app a local path. Give an output path as a relative path such as `out.png`: it lands in this run's folder, and after the call the result links each output in every configured sink.

## Tools

| Tool | What it does |
|---|---|
| `figcraft_batch` | Run several commands in order as ONE undo step (engine `command. |
| `figcraft_create_node` | Create a layer (engine `node. |
| `figcraft_export` | Export layers (default: the selection, else every top-level layer of the current page) as png, jpg, svg, webp, pdf or xml (an Android Vector Drawable, with `warnings` for what it changed or left out, per `vdCompat`) at `scale`, or the whole file as `fig` (experimental: written from public format knowledge, with `warnings` for what was left out; other apps may not open every file) (PDF: with `bleed`, `cropMarks`, `bleedMarks` and `cmyk` for print; options `contentsOnly`, `includeBoundingBox`, and for SVG `svgOutlineText`, `svgIdAttribute`, `svgSimplifyStroke`; for XML `svgIdAttribute` and `vdCompat`). |
| `figcraft_get_node` | One layer as JSON (same fields as inspect_document) with its children to `depth`. |
| `figcraft_inspect_document` | The active document as JSON: name, path, dirty flag, current page, selection, the current page's layer tree (id, name, type, x/y relative to the parent frame (groups don't count), width, height, absoluteBounds in page coordinates, fills, strokes, effects, cornerRadius, layout, sizing, text properties, component links, overrides, bound variables), other pages summarised, styles, variable count and the undo history. |
| `figcraft_inspect_ui` | UI state: current tool, view (zoom, centre), status, panels, timings and the app's windows (`windows`: id, title, files) when attached to the app; headless reports the session status. |
| `figcraft_key` | Press a key or shortcut as if typed on the canvas: a menu shortcut (e. |
| `figcraft_list_commands` | List FigCraft commands: id, label, menu path, shortcut, whether it is undoable, and a parameter description. |
| `figcraft_open_file` | Open a . |
| `figcraft_pointer` | Drive the canvas with the mouse in page coordinates, exactly as a user would with the current tool: click to select, drag to move/resize/marquee, or draw with a shape tool (set `tool` first, e. |
| `figcraft_redo` | Redo the last undone change. |
| `figcraft_run_command` | Execute one FigCraft command by id with JSON params (ids and params from list_commands). |
| `figcraft_save_file` | Save the active document as a . |
| `figcraft_screenshot` | Look at the design: renders the given layers (or the whole current page, with its background) to PNG and returns it as image content, plus its size and the scale used. |
| `figcraft_select` | Replace the selection with `ids` (switching to their page). |
| `figcraft_set_properties` | Set properties on one or more layers as one undo step (engine `node. |
| `figcraft_type_text` | Type into a text layer. |
| `figcraft_undo` | Undo the last change (one command, batch or gesture). |
| `figcraft_wait_for_changes` | Wait for new comment events in the attached FigCraft app. |

## Functionalities

- `figcraft-create_figure` — Create layers, set their properties and save the document.
- `figcraft-edit_layers` — Read, select and restyle layers of an open document.
- `figcraft-batch_edits` — Apply several edits as one undo step and review them.

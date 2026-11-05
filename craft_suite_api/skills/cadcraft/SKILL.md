---
name: cadcraft
description: CadCraft 2D drafting — drawings, entities, queries, scripts and renders.
---

# Cadcraft

## When to use

CadCraft 2D drafting — drawings, entities, queries, scripts and renders.

## Activation

Call `registry_activate` with the namespace `cadcraft` before using any `cadcraft_*` tool.

## Files in and out

Pass an input file as `exchange://<sink>/<key>` (for example `exchange://files/in/photo.png`) or as an `https` URL; the server stages it and hands the app a local path. Give an output path as a relative path such as `out.png`: it lands in this run's folder, and after the call the result links each output in every configured sink.

## Tools

| Tool | What it does |
|---|---|
| `cadcraft_cancel` | Press Escape: cancel the running command (or clear the selection). |
| `cadcraft_command_line` | Type one line at the CADCraft command line, exactly as a user would at an AutoCAD-style prompt. |
| `cadcraft_execute` | Run any command with JSON parameters (no prompts or dialogs). |
| `cadcraft_find_text` | Read the drawing's texts: TEXT, MTEXT (formatting removed), block attributes and multileaders, each with its text, insertion point `at`, height, rotation, style, layer and handle. |
| `cadcraft_inspect_drawing` | Summary of the active drawing: entity counts, extents, layers, styles, blocks, layouts, selection, undo history and (optionally) entities with handles and geometry. |
| `cadcraft_list_commands` | List commands with ids, labels, menu paths, aliases and parameter docs. |
| `cadcraft_new_drawing` | Create a new drawing (imperial by default, or metric). |
| `cadcraft_open` | Open a DXF or DWG file. |
| `cadcraft_query_entities` | Entities filtered by type (Line, Circle, Polyline…), layer, current selection (selected:true; active space only) and/or a window [[x0,y0],[x1,y1]] (objects whose geometry is inside or crosses it; crossing:false = entirely inside). |
| `cadcraft_render` | Render the active drawing to a PNG and return it as an image: fitted to the extents by default, or just the area `window` [[x0,y0],[x1,y1]] (drawing units), e. |
| `cadcraft_save` | Save the drawing (DXF or DWG by extension). |
| `cadcraft_script` | Run a multi-line script (like an AutoCAD . |

## Functionalities

- `cadcraft-create_drawing` — Start a drawing, run drafting commands and render it.
- `cadcraft-query_drawing` — Inspect a drawing and query its entities and texts.
- `cadcraft-script_drawing` — Drive the command line with a script and save the result.

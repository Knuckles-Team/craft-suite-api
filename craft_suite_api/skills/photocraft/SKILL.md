---
name: photocraft
description: PhotoCraft raster image editing — documents, layers, data sets and background jobs.
---

# Photocraft

## When to use

PhotoCraft raster image editing — documents, layers, data sets and background jobs.

## Activation

Call `registry_activate` with the namespace `photocraft` before using any `photocraft_*` tool.

## Files in and out

Pass an input file as `exchange://<sink>/<key>` (for example `exchange://files/in/photo.png`) or as an `https` URL; the server stages it and hands the app a local path. Give an output path as a relative path such as `out.png`: it lands in this run's folder, and after the call the result links each output in every configured sink.

## Tools

| Tool | What it does |
|---|---|
| `photocraft_command_batch` | Run several engine commands in one call, in order (fewer round trips). |
| `photocraft_command_list` | List engine commands. |
| `photocraft_command_run` | Run an engine command by id with JSON params (see command_list). |
| `photocraft_control_call` | Bridge mode: call any control-protocol method (docs/control-protocol. |
| `photocraft_doc_close` | Close a document (default: the active one) without saving. |
| `photocraft_doc_export` | Export the document to another format (same as doc_save with an explicit path/format). |
| `photocraft_doc_export_data_sets` | Export every data set of the document as its own flattened file beneath the write root (the capability-scoped Export Data Sets). |
| `photocraft_doc_export_layers` | Export top-level layers as files (groups merged). |
| `photocraft_doc_import_data_sets` | Import a data set CSV from the read root into the document (the capability-scoped Import Variable Data Sets). |
| `photocraft_doc_inspect` | Document state as JSON: layer tree (top to bottom), history, selection, active layer. |
| `photocraft_doc_new` | Create a new document (defaults: 1920x1080 RGB 8-bit white). |
| `photocraft_doc_open` | Open an image or document file and make it active. |
| `photocraft_doc_place` | Place a file into the document as a Smart Object layer (Place Embedded), reading `path` beneath the read root. |
| `photocraft_doc_render_preview` | Render the flattened document and return it as a PNG image (bridge mode: window screenshot). |
| `photocraft_doc_replace_smart_object` | Replace a Smart Object's contents with the file at `path` beneath the read root, keeping its transform and filters (the capability-scoped Replace Contents). |
| `photocraft_doc_save` | Save the document. |
| `photocraft_doc_select` | Make the document at `index` active. |
| `photocraft_jobs_cancel` | Cancel a background job by id (or every running job when `job` is omitted). |
| `photocraft_jobs_list` | List background jobs: running ones with progress (0-1), message and elapsed time, then the last few that ended (state done|failed|cancelled with their result or error). |
| `photocraft_render_preview` | Render a bounded flattened PNG preview (bridge mode: app window screenshot). |
| `photocraft_session_list` | List open documents (index, name, size, dirty) and the active index. |
| `photocraft_ui_inspect` | Bridge mode: full UI state of the live app (tool, panels, views, dialogs, windows). |
| `photocraft_ui_menu_invoke` | Bridge mode: activate a menu item by id. |
| `photocraft_ui_pointer` | Bridge mode: send pointer events (document coordinates) to the active tool; with a Color Picker open they sample the image into it instead. |
| `photocraft_ui_screenshot` | Bridge mode: screenshot of the live app window as PNG. |
| `photocraft_ui_set` | Bridge mode: change UI state (tool, panels, dock, zoom, center, fit, theme, brush settings; see `fields`). |

## Functionalities

- `photocraft-edit_image` — Open an image, inspect it, run engine commands and save the result.
- `photocraft-export_document` — Export the active document or its layers to files.
- `photocraft-inspect_session` — Survey the open documents of the running session.

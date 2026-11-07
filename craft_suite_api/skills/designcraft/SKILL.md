---
name: designcraft
description: DesignCraft page layout — documents, stories, placed images, pages and exports.
---

# Designcraft

## When to use

DesignCraft page layout — documents, stories, placed images, pages and exports.

## Activation

Call `registry_activate` with the namespace `designcraft` before using any `designcraft_*` tool.

## Files in and out

Pass an input file as `exchange://<sink>/<key>` (for example `exchange://files/in/photo.png`) or as an `https` URL; the server stages it and hands the app a local path. Give an output path as a relative path such as `out.png`: it lands in this run's folder, and after the call the result links each output in every configured sink.

## When the app is not ready

An app is `warming` while its command registry loads, `Ready` when it serves, `Degraded` after a failed load and `Backoff` once its retries are used. A call to a `warming` app answers the retryable refusal `APP_WARMING`; a call to a `Degraded` or `Backoff` app answers the retryable refusal `APP_REGISTRY_UNREADABLE`. Retry after `retry_after_s`; a `Backoff` app needs an operator.

## Tools

| Tool | What it does |
|---|---|
| `designcraft_batch` | Run several commands in order, stopping at the first error. |
| `designcraft_click` | Click at a screen point (egui points, top-left of the window = 0,0) through the real pointer path: reaches menus, panels, flyouts and dialogs. |
| `designcraft_dialog_cancel` | Press Cancel in the open dialog. |
| `designcraft_dialog_confirm` | Press OK in the open dialog. |
| `designcraft_dialog_set` | Set a field of the open dialog (see ui_inspect → dialog for its fields). |
| `designcraft_drag` | Press at (x, y), move to (toX, toY) in `steps` moves and release, in screen points through the real pointer path. |
| `designcraft_execute` | Run any DesignCraft command by id with JSON params (ids and params from list_commands). |
| `designcraft_export_png` | Export one page as a PNG (or JPEG if the path ends in . |
| `designcraft_get_story` | Full text of a story plus its length, frames, paragraph count, line count and overset position (length and positions are UTF-8 byte offsets, the unit text. |
| `designcraft_ime` | Input method (IME) events at the Type tool's caret, as a system IME sends them: `preedit` is the marked text (shown in place, no undo step; an empty string cancels the composition), `active` the clause being converted in characters of it, `commit` the text the IME types in its place (one undo step). |
| `designcraft_inspect_document` | Summary of the active document: settings, pages (index, name, bounds, margins, columns), spreads with items (id, kind, bounds, fill, stroke, story), stories (id, frames, length in UTF-8 bytes, overset, preview), layers, paragraph/character styles, swatches, selection, active tool. |
| `designcraft_key` | Press a key with modifiers, e. |
| `designcraft_list_commands` | List DesignCraft commands: id, label, menu path, shortcut, parameter description and whether it can run right now. |
| `designcraft_menu_list` | The menu bar tree (menus, entries as cmd:/ui: command ids, separators, submenus). |
| `designcraft_new_document` | Create a new document and make it active. |
| `designcraft_open_document` | Open a . |
| `designcraft_place_image` | Place an image (PNG, JPEG, WebP, GIF, TIFF) from a file `path` or `base64` data. |
| `designcraft_pointer` | Drive the active tool with mouse events, exactly like the mouse would. |
| `designcraft_render_page` | Render one page of the active document (printing items only, like Preview) and return it as a PNG image. |
| `designcraft_save_document` | Save the active document in the native . |
| `designcraft_screenshot` | Capture the whole app window (menus, panels, canvas) and return it as a PNG image. |
| `designcraft_select_tool` | Switch the active tool (as clicking it in the Tools panel). |
| `designcraft_set_story_text` | Replace the whole text of a story (keeps the first paragraph's and character's formatting). |
| `designcraft_type_text` | Type text at the text insertion point, independently of the active tool, or into the focused dialog field in the desktop app. |
| `designcraft_ui_inspect` | UI state: active tool, panels, view (zoom, origin), canvas rect in screen points, window size, documents, open dialog, perf. |
| `designcraft_ui_set` | Change UI state: panel to open or close, brightness, status text, rulers/guides/frameEdges/baselineGrid/documentGrid/textThreads, Control bar, dock expanded, screenMode, zoom, page (1-based), fit (page|spread). |

## Functionalities

- `designcraft-lay_out_document` — Start a document, place images and set story text.
- `designcraft-inspect_document` — Open a document and read its pages and stories.
- `designcraft-run_commands` — Look up engine commands and run them, alone or in a batch.

---
name: deckcraft
description: DeckCraft presentation editing — slides, shapes, charts, tables and export.
---

# Deckcraft

## When to use

DeckCraft presentation editing — slides, shapes, charts, tables and export.

## Activation

Call `registry_activate` with the namespace `deckcraft` before using any `deckcraft_*` tool.

## Files in and out

Pass an input file as `exchange://<sink>/<key>` (for example `exchange://files/in/photo.png`) or as an `https` URL; the server stages it and hands the app a local path. Give an output path as a relative path such as `out.png`: it lands in this run's folder, and after the call the result links each output in every configured sink.

## Tools

| Tool | What it does |
|---|---|
| `deckcraft_add_shape` | Insert a preset shape (rect, roundRect, ellipse, triangle, diamond, rightArrow, chevron, star5, heart, cloud, wedgeRectCallout, line, straightConnector1… see shape. |
| `deckcraft_add_slide` | Insert a slide after the current one with a layout (title, titleAndContent, sectionHeader, twoContent, comparison, titleOnly, blank, contentWithCaption, pictureWithCaption) and optional title/body text (body: one paragraph per line, leading tabs indent). |
| `deckcraft_add_text_box` | Insert a text box. |
| `deckcraft_batch` | Run commands in order; stops at the first error unless keepGoing. |
| `deckcraft_call_app` | Call any control-channel method (ui. |
| `deckcraft_export` | Export slides: png/jpeg (one slide, or all with all:true), pptx, deckcraft, outline text, pdf (slides, notes pages or handouts), or an animated gif of the deck (one frame per slide). |
| `deckcraft_go_to_slide` | Make a slide current (shape commands act on the current slide). |
| `deckcraft_insert_chart` | Insert a chart (column, bar, line, pie, doughnut, area, scatter, stackedColumn…) with categories and series, optionally at a box. |
| `deckcraft_insert_picture` | Insert a picture from a file path or base64 data, optionally at a box. |
| `deckcraft_insert_table` | Insert a table with rows×cols and optional cell text (data: rows of strings). |
| `deckcraft_inspect_document` | Slides (index, id, title, layout, shape count, transition, animations, notes), sections, theme, layouts, media and the selection. |
| `deckcraft_inspect_slide` | One slide's shapes with ids, kinds, boxes [x,y,w,h], placeholder types, text, fills, tables, charts; plus background, transition, animations, notes. |
| `deckcraft_key` | Press a key as on the keyboard: text editing keys (arrows, Backspace, Enter, Tab), nudges, and shortcuts (cmd+B…). |
| `deckcraft_list_commands` | Every command (id, label, ribbon/menu place, shortcut, parameter summary, whether it is enabled now). |
| `deckcraft_new_presentation` | Start a new presentation (one title slide). |
| `deckcraft_open_presentation` | Open a . |
| `deckcraft_pointer` | Drive the active tool with pointer events in slide points: down/drag/up/move/doubleclick/contextclick, exactly like the mouse (draws, moves, resizes, rotates, places the caret; contextclick selects like a right click). |
| `deckcraft_render_slide` | Render a slide to a PNG image and return it, to check your work visually. |
| `deckcraft_run_command` | Run any command by id with JSON parameters. |
| `deckcraft_save_presentation` | Save the active presentation (. |
| `deckcraft_screenshot` | Screenshot of the whole DeckCraft window (UI included). |
| `deckcraft_select` | Select shapes by id (formatting commands then act on them). |
| `deckcraft_select_tool` | Pick the pointer tool: select, textBox, shape (with preset), pen, highlighter, eraser — or a preset name. |
| `deckcraft_set_text` | Replace a shape's text (keeps its first run's formatting). |
| `deckcraft_type_text` | Type text into the text being edited (or into the selected shape). |

## Functionalities

- `deckcraft-build_deck` — Start a presentation, add slides and text, then save.
- `deckcraft-insert_content` — Add shapes, charts and tables to the current slide.
- `deckcraft-export_deck` — Render a slide, check it, and export the deck.

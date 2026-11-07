---
name: wordcraft
description: WordCraft word processing — documents, formatting, tracked edits and page renders.
---

# Wordcraft

## When to use

WordCraft word processing — documents, formatting, tracked edits and page renders.

## Activation

Call `registry_activate` with the namespace `wordcraft` before using any `wordcraft_*` tool.

## Files in and out

Pass an input file as `exchange://<sink>/<key>` (for example `exchange://files/in/photo.png`) or as an `https` URL; the server stages it and hands the app a local path. Give an output path as a relative path such as `out.png`: it lands in this run's folder, and after the call the result links each output in every configured sink.

## When the app is not ready

An app is `warming` while its command registry loads, `Ready` when it serves, `Degraded` after a failed load and `Backoff` once its retries are used. A call to a `warming` app answers the retryable refusal `APP_WARMING`; a call to a `Degraded` or `Backoff` app answers the retryable refusal `APP_REGISTRY_UNREADABLE`. Retry after `retry_after_s`; a `Backoff` app needs an operator.

## Tools

| Tool | What it does |
|---|---|
| `wordcraft_batch` | Run commands in order; stops at the first error unless keepGoing. |
| `wordcraft_click` | Click at window coordinates (desktop app only). |
| `wordcraft_execute` | Run one command by id with params, e. |
| `wordcraft_get_text` | Body text with tracked deletions omitted. |
| `wordcraft_inspect_document` | Structure: blocks with text, styles, formatting runs, lists, tables, sections, parts, selection, pages. |
| `wordcraft_key` | Press a key with modifiers (desktop app only), e. |
| `wordcraft_list_commands` | Every WordCraft command: id, label, ribbon location, shortcut and params. |
| `wordcraft_list_documents` | The open documents in the order they were opened: id, title, path, dirty (unsaved changes) and active (the one commands work on by default). |
| `wordcraft_new_document` | Start a document: blank, sample, letter, resume or report. |
| `wordcraft_open_document` | Open a . |
| `wordcraft_parity` | WordCraft's command coverage of the word-processor feature catalog. |
| `wordcraft_render_page` | Render a page to PNG to look at the result. |
| `wordcraft_save_document` | Save (format from the extension: docx, pdf, odt, rtf, html, md, tex, txt, png). |
| `wordcraft_screenshot` | Screenshot of the whole WordCraft window (desktop app only). |
| `wordcraft_select_text` | Select the n-th occurrence of some text. |
| `wordcraft_type_text` | Type at the caret (replacing the selection). |
| `wordcraft_ui_inspect` | UI state: tab, panes, dialog, page rectangles on screen, caret (desktop app only). |

## Functionalities

- `wordcraft-write_document` — Start a document, type content and save it.
- `wordcraft-format_document` — Inspect the document structure and apply formatting commands.
- `wordcraft-open_and_review` — Open an existing document, read its text and save changes.

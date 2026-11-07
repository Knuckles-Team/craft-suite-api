---
name: gridcraft
description: GridCraft spreadsheets — workbooks, ranges, formulas, tables and charts.
---

# Gridcraft

## When to use

GridCraft spreadsheets — workbooks, ranges, formulas, tables and charts.

## Activation

Call `registry_activate` with the namespace `gridcraft` before using any `gridcraft_*` tool.

## Files in and out

Pass an input file as `exchange://<sink>/<key>` (for example `exchange://files/in/photo.png`) or as an `https` URL; the server stages it and hands the app a local path. Give an output path as a relative path such as `out.png`: it lands in this run's folder, and after the call the result links each output in every configured sink.

## When the app is not ready

An app is `warming` while its command registry loads, `Ready` when it serves, `Degraded` after a failed load and `Backoff` once its retries are used. A call to a `warming` app answers the retryable refusal `APP_WARMING`; a call to a `Degraded` or `Backoff` app answers the retryable refusal `APP_REGISTRY_UNREADABLE`. Retry after `retry_after_s`; a `Backoff` app needs an operator.

## Tools

| Tool | What it does |
|---|---|
| `gridcraft_create_table` | Format a range as an Excel table (structured references, banded rows, filter buttons). |
| `gridcraft_evaluate_formula` | Evaluate a formula against the active sheet WITHOUT changing any cell, e. |
| `gridcraft_execute_command` | Run ANY GridCraft command by id with JSON params — every ribbon/menu action is a command. |
| `gridcraft_filter` | Filter rows by a column (turns on AutoFilter on the current region, or `range`, when needed). |
| `gridcraft_format_range` | Apply several formats to a range in one call: bold, italic, underline, font name/size, font color, fill color, number format, horizontal alignment, wrap, borders. |
| `gridcraft_get_cell` | Details of one cell: computed value and type, formula, display text, raw input, spill range, style, merge, comment and hyperlink. |
| `gridcraft_insert_chart` | Insert a chart from a data range (first row/column used as series names and categories, like Excel). |
| `gridcraft_inspect_workbook` | Summary of the active workbook: title, path, dirty flag, sheets (name, used range, cell count, tables, charts, merges, filters, freeze panes), defined names, current selection and active cell, calculation mode and undo/redo history. |
| `gridcraft_list_commands` | List GridCraft commands: id, label, ribbon path, shortcut, a parameter description (`params`) and whether it can run right now. |
| `gridcraft_list_functions` | List worksheet functions: name, category, signature and description. |
| `gridcraft_list_windows` | List the open windows: window id, workbook (`doc`) id, title ("Book1", or "Book1:2" for a workbook's second window), unsaved changes, active and hidden. |
| `gridcraft_new_workbook` | Create a new workbook and make it active: blank, or a built-in sample ("budget", "sales", "grades"). |
| `gridcraft_open_workbook` | Open a workbook file (. |
| `gridcraft_read_range` | Read cell values from a range as rows (2-D array). |
| `gridcraft_redo` | Redo the last undone change(s). |
| `gridcraft_save_workbook` | Save the active workbook. |
| `gridcraft_screenshot` | Save a PNG screenshot of the GridCraft window to `path`. |
| `gridcraft_select` | Set the selection (what commands without a `range` param act on). |
| `gridcraft_set_cell` | Enter one cell exactly as if typed: a number, text, or a formula starting with = ("=AVERAGE(B2:B9)"). |
| `gridcraft_sort_range` | Sort a range by one or more columns. |
| `gridcraft_undo` | Undo the last change(s) to the active workbook. |
| `gridcraft_write_range` | Write a 2-D array of values starting at the top-left cell of `range` (rows of cells). |

## Functionalities

- `gridcraft-edit_workbook` — Open or start a workbook, write ranges and save it.
- `gridcraft-analyse_data` — Read ranges, evaluate formulas and add tables and charts.
- `gridcraft-run_commands` — Look up engine commands and spreadsheet functions and run commands.

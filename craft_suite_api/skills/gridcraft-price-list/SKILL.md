---
name: gridcraft-price-list
description: Build a product price list with formula columns, currency formats and a chart, and save it as XLSX and CSV.
---

# Build a price list

## When to use

A price list, stock sheet, quote or simple budget is needed as a spreadsheet with live formulas and a chart.

## Inputs

- `${name}`: the file name stem.

Every app tool is served by the craft-suite-api connector; call them in this order in one session (the app keeps the open document between calls). A value written `${name}` is an input above or the value an earlier step returned (its answer names it).

## Steps

| # | Tool | Arguments | Why |
|---|---|---|---|
| 1 | `gridcraft_new_workbook` | `{}` | New workbook. |
| 2 | `gridcraft_write_range` | `{"range": "A1", "values": [["SKU", "Product", "Unit Cost", "Markup %", "Price", "Stock", "Stock Value"], ["EL-001", "Ember Lamp", 22, 0.5, "=C2*(1+D2)", 40, "=E2*F2"], ["EL-002", "Ember Lamp Mini", 14, 0.5, "=C3*(1+D3)", 75, "=E3*F3"], ["EL-003", "Ember Shade", 6, 0.8, "=C4*(1+D4)", 120, "=E4*F4"], ["EL-004", "Ember Stand", 9, 0.6, "=C5*(1+D5)", 60, "=E5*F5"], ["", "Total", "", "", "", "=SUM(F2:F5)", "=SUM(G2:G5)"]]}` | Write the table from A1; strings that start with = are formulas. |
| 3 | `gridcraft_format_range` | `{"range": "A1:G1", "bold": true, "fillColor": "#DDEEFF"}` | Bold and shade the header row. |
| 4 | `gridcraft_format_range` | `{"range": "C2:C5", "numberFormat": "Currency"}` | Currency format for unit cost. |
| 5 | `gridcraft_format_range` | `{"range": "E2:E5", "numberFormat": "Currency"}` | Currency format for price. |
| 6 | `gridcraft_format_range` | `{"range": "G2:G6", "numberFormat": "Currency"}` | Currency format for stock value and total. |
| 7 | `gridcraft_format_range` | `{"range": "D2:D5", "numberFormat": "0%"}` | Percent format for markup. |
| 8 | `gridcraft_insert_chart` | `{"range": "B1:B5,E1:E5", "type": "column", "title": "Retail price by product", "at": "I2"}` | Insert a column chart (a range list like B1:B5,E1:E5 picks non-adjacent columns; at is the anchor cell). |
| 9 | `gridcraft_read_range` | `{"range": "A1:G6", "formulas": true}` | Read back the formulas. |
| 10 | `gridcraft_read_range` | `{"range": "A1:G6"}` | Read back the values. |
| 11 | `gridcraft_save_workbook` | `{"path": "${name}.xlsx"}` | Save as XLSX (formulas and chart kept). |
| 12 | `gridcraft_save_workbook` | `{"path": "${name}.csv"}` | Save as CSV (the shown values). |

## Outputs

Formats: xlsx, csv. A relative output path lands in the run folder of the call; after the call the result's `scion/artifacts` lists each file with its link in every configured exchange sink (the object store under `<app>/<date>/<run>/<name>`, and the file share when configured). Pass a published file to another workflow as `exchange://objects/<key>`.

## Verify

The XLSX keeps the formulas and their computed values and holds one chart; the CSV holds the formatted values.

## Notes

- Saving can take a minute even for a small workbook.
- Replace the table in step 2 with the business's own products; keep formulas as = strings.

## Refusals

An app is in one lifecycle state: `warming` while its command registry loads, `Ready`, `Degraded` after a failed load, `Backoff` once its retries are used. A call to a `warming` app answers `APP_WARMING` (retryable, `retry_after_s`): wait that long and call again. A call to a `Degraded` or `Backoff` app answers `APP_REGISTRY_UNREADABLE` (retryable): retry after `retry_after_s`; a `Backoff` app has used its retries and needs an operator. Report any other refusal verbatim; never retry past it.

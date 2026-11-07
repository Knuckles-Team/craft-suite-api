---
name: pdfcraft-stamp-and-brand
description: Open a PDF, add a watermark, a header and page-numbered footer, set its title and author, and save a new PDF.
---

# Stamp and brand a PDF

## When to use

A PDF (release, brochure, price sheet, proposal) needs a draft or confidential watermark, branded header and footer, page numbers or document metadata.

## Inputs

- `${src}`: the PDF, as exchange://<sink>/<key>.
- `${watermark}`: the watermark text.
- `${company}`: the header text.
- `${title}`: the document title.
- `${name}`: the file name stem.

Every app tool is served by the craft-suite-api connector; call them in this order in one session (the app keeps the open document between calls). A value written `${name}` is an input above or the value an earlier step returned (its answer names it).

## Steps

| # | Tool | Arguments | Why |
|---|---|---|---|
| 1 | `pdfcraft_doc_open` | `{"path": "${src}"}` | Open the PDF; the answer gives its doc id. Returns `doc` as `${doc}`. |
| 2 | `pdfcraft_doc_watermark` | `{"doc": "${doc}", "text": "${watermark}", "opacity": 0.25, "rotation": 45, "color": "#cc0000"}` | Add the watermark (opacity 0..1, rotation in degrees, colour #rrggbb). |
| 3 | `pdfcraft_doc_header_footer` | `{"doc": "${doc}", "header_left": "${company}", "footer_center": "Page <<1 of n>>", "footer_right": "<<yyyy-mm-dd>>", "font": "Helvetica", "font_size": 9}` | Add the header and footer; <<1 of n>> numbers pages and <<yyyy-mm-dd>> stamps the date. |
| 4 | `pdfcraft_doc_set_info` | `{"doc": "${doc}", "key": "Title", "value": "${title}"}` | Set the Title metadata. |
| 5 | `pdfcraft_doc_set_info` | `{"doc": "${doc}", "key": "Author", "value": "${company}"}` | Set the Author metadata. |
| 6 | `pdfcraft_doc_info` | `{"doc": "${doc}"}` | Read the document info to check it. |
| 7 | `pdfcraft_doc_save` | `{"doc": "${doc}", "path": "${name}.pdf"}` | Save as a new PDF. |

## Outputs

Formats: pdf. A relative output path lands in the run folder of the call; after the call the result's `scion/artifacts` lists each file with its link in every configured exchange sink (the object store under `<app>/<date>/<run>/<name>`, and the file share when configured). Pass a published file to another workflow as `exchange://objects/<key>`.

## Verify

The saved PDF's text holds the watermark, the header and 'Page 1 of n'; its metadata holds the title and author.

## Notes

- `pdfcraft_doc_watermark` and `pdfcraft_doc_header_footer` take colours as #rrggbb strings.

## Refusals

An app is in one lifecycle state: `warming` while its command registry loads, `Ready`, `Degraded` after a failed load, `Backoff` once its retries are used. A call to a `warming` app answers `APP_WARMING` (retryable, `retry_after_s`): wait that long and call again. A call to a `Degraded` or `Backoff` app answers `APP_REGISTRY_UNREADABLE` (retryable): retry after `retry_after_s`; a `Backoff` app has used its retries and needs an operator. Report any other refusal verbatim; never retry past it.

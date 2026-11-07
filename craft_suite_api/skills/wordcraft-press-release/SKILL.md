---
name: wordcraft-press-release
description: Write a one-page press release with a heading, body paragraphs and the product photo, and save it as DOCX and PDF.
---

# Write a press release

## When to use

An announcement, press release, product sheet or letter is needed as an editable document and a PDF.

## Inputs

- `${photo}`: the product photo, as exchange://<sink>/<key>.
- `${headline}`: the release headline.
- `${body}`: the body text, one paragraph per line.
- `${name}`: the file name stem.

Every app tool is served by the craft-suite-api connector; call them in this order in one session (the app keeps the open document between calls). A value written `${name}` is an input above or the value an earlier step returned (its answer names it).

## Steps

| # | Tool | Arguments | Why |
|---|---|---|---|
| 1 | `wordcraft_new_document` | `{"template": "blank"}` | New blank document; the answer gives its id. Returns `id` as `${doc}`. |
| 2 | `wordcraft_cmd_para_heading1` | `{}` | Make the first paragraph a Heading 1. |
| 3 | `wordcraft_type_text` | `{"text": "${headline}"}` | Type the headline. |
| 4 | `wordcraft_cmd_text_newParagraph` | `{}` | Start a new paragraph. |
| 5 | `wordcraft_cmd_para_style` | `{"style": "Normal"}` | Set it to the Normal style. |
| 6 | `wordcraft_type_text` | `{"text": "${body}", "paragraphs": true}` | Type the body; paragraphs:true turns each line into a paragraph. |
| 7 | `wordcraft_cmd_insert_picture` | `{"path": "${photo}", "width": 300, "alt": "Ember Lamp product photo"}` | Insert the product photo inline (width in pt) with alt text. |
| 8 | `wordcraft_get_text` | `{}` | Read the text back to check it. |
| 9 | `wordcraft_save_document` | `{"path": "${name}.docx"}` | Save as DOCX (the extension picks the format). |
| 10 | `wordcraft_save_document` | `{"path": "${name}.pdf"}` | Save as PDF. |

## Outputs

Formats: docx, pdf. A relative output path lands in the run folder of the call; after the call the result's `scion/artifacts` lists each file with its link in every configured exchange sink (the object store under `<app>/<date>/<run>/<name>`, and the file share when configured). Pass a published file to another workflow as `exchange://objects/<key>`.

## Verify

The DOCX has the Heading 1 title, the body paragraphs and one inline picture; the PDF has one page with the text and the image.

## Notes

- Formats follow the save path's extension (.docx, .pdf, .odt, .rtf).

## Refusals

An app is in one lifecycle state: `warming` while its command registry loads, `Ready`, `Degraded` after a failed load, `Backoff` once its retries are used. A call to a `warming` app answers `APP_WARMING` (retryable, `retry_after_s`): wait that long and call again. A call to a `Degraded` or `Backoff` app answers `APP_REGISTRY_UNREADABLE` (retryable): retry after `retry_after_s`; a `Backoff` app has used its retries and needs an operator. Report any other refusal verbatim; never retry past it.

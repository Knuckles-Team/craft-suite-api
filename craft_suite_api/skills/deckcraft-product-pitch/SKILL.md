---
name: deckcraft-product-pitch
description: Build a two-slide product pitch with a title slide, bullet points and the product photo, and export PDF and PPTX.
---

# Build a product pitch deck

## When to use

A pitch, sales or product deck is needed for a meeting, email or print.

## Inputs

- `${photo}`: the product image, as exchange://<sink>/<key>.
- `${title}`: the deck title.
- `${subtitle}`: the title slide subtitle.
- `${slide2_title}`: the second slide title.
- `${bullets}`: the bullet points, one per line.
- `${name}`: the file name stem.

Every app tool is served by the craft-suite-api connector; call them in this order in one session (the app keeps the open document between calls). A value written `${name}` is an input above or the value an earlier step returned (its answer names it).

## Steps

| # | Tool | Arguments | Why |
|---|---|---|---|
| 1 | `deckcraft_new_presentation` | `{"theme": "Ember"}` | New presentation with a theme. |
| 2 | `deckcraft_inspect_slide` | `{"index": 0}` | Read the title slide's placeholder ids. Returns `shapes.0.id` as `${t0}`, `shapes.1.id` as `${s0}`. |
| 3 | `deckcraft_set_text` | `{"id": "${t0}", "text": "${title}"}` | Set the title. |
| 4 | `deckcraft_set_text` | `{"id": "${s0}", "text": "${subtitle}"}` | Set the subtitle. |
| 5 | `deckcraft_add_slide` | `{"layout": "titleOnly", "title": "${slide2_title}"}` | Add a title-only slide. |
| 6 | `deckcraft_add_text_box` | `{"x": 60, "y": 150, "w": 400, "text": "${bullets}", "size": 24}` | Add the bullets as a text box (x, y, width in pt). |
| 7 | `deckcraft_insert_picture` | `{"path": "${photo}", "x": 500, "y": 130, "w": 400, "h": 300}` | Insert the product photo (x, y, w, h in pt). |
| 8 | `deckcraft_inspect_document` | `{}` | Check the deck. |
| 9 | `deckcraft_export` | `{"path": "${name}.pdf"}` | Export PDF. |
| 10 | `deckcraft_export` | `{"path": "${name}.pptx"}` | Export PPTX. |

## Outputs

Formats: pdf, pptx. A relative output path lands in the run folder of the call; after the call the result's `scion/artifacts` lists each file with its link in every configured exchange sink (the object store under `<app>/<date>/<run>/<name>`, and the file share when configured). Pass a published file to another workflow as `exchange://objects/<key>`.

## Verify

The PDF has the slides with their text; the PPTX has the same slides and the embedded image.

## Notes

- Shape ids come from `deckcraft_inspect_slide`.

## Refusals

`APP_WARMING` (retryable, `retry_after_s`): the app's command registry is still loading after a restart; wait and call again. `APP_REGISTRY_UNREADABLE` (retryable): the app's registry could not be read; it is retried in the background. Report any other refusal verbatim; never retry past it.

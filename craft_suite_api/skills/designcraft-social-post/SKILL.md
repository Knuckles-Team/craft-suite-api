---
name: designcraft-social-post
description: Lay out a square social post with a brand background, the product photo and a headline, and export a 1080 x 1080 PNG.
---

# Design a social post

## When to use

A marketing graphic, social post or ad tile is needed from a product photo and a line of copy.

## Inputs

- `${photo}`: the product image, as exchange://<sink>/<key>.
- `${headline}`: the headline text.
- `${brand_color}`: the background colour, #rrggbb.
- `${accent_color}`: the headline colour, #rrggbb.

Every app tool is served by the craft-suite-api connector; call them in this order in one session (the app keeps the open document between calls). A value written `${name}` is an input above or the value an earlier step returned (its answer names it).

## Steps

| # | Tool | Arguments | Why |
|---|---|---|---|
| 1 | `designcraft_new_document` | `{"width": 540, "height": 540, "intent": "web", "margins": 0}` | New web document, 540 x 540 pt (1080 px at scale 2), no margins. |
| 2 | `designcraft_cmd_frame_create` | `{"rect": [0, 0, 540, 540], "shape": "rectangle", "content": "unassigned"}` | Draw the background frame over the whole page; the answer gives its id. Returns `id` as `${bg}`. |
| 3 | `designcraft_cmd_object_color` | `{"color": "${brand_color}", "target": "fill", "ids": ["${bg}"]}` | Fill it with the brand colour. |
| 4 | `designcraft_place_image` | `{"path": "${photo}", "x": 90, "y": 36, "width": 360}` | Place the product photo (x, y and width in pt). |
| 5 | `designcraft_cmd_frame_create` | `{"rect": [40, 330, 500, 420], "content": "text", "text": "${headline}"}` | Create the headline text frame (rect in pt). Returns `id` as `${headline}`. |
| 6 | `designcraft_cmd_text_selectStory` | `{"frame": "${headline}", "point": [60, 345]}` | Select the headline's story so formatting reaches the text. |
| 7 | `designcraft_cmd_type_char` | `{"attrs": {"size": 40, "fontFamily": "DejaVu Sans", "fontStyle": "Bold"}}` | Set the headline's font, style and size. |
| 8 | `designcraft_cmd_object_color` | `{"color": "${accent_color}", "text": true}` | Colour the selected text. |
| 9 | `designcraft_cmd_text_exitToFrame` | `{}` | Leave the text so the export shows the page, not a caret. |
| 10 | `designcraft_export_png` | `{"path": "social-post.png", "scale": 2}` | Export the page as PNG (scale = pixels per point). |

## Outputs

Formats: png. A relative output path lands in the run folder of the call; after the call the result's `scion/artifacts` lists each file with its link in every configured exchange sink (the object store under `<app>/<date>/<run>/<name>`, and the file share when configured). Pass a published file to another workflow as `exchange://objects/<key>`.

## Verify

The PNG is 1080 x 1080, the corner pixel has the background colour, and the photo and headline are visible.

## Notes

- `designcraft_cmd_object_color` with `ids` colours the frame, not its text: select the story first and pass `text: true` without ids.
- Sizes are points; export_png's scale is pixels per point.

## Refusals

An app is in one lifecycle state: `warming` while its command registry loads, `Ready`, `Degraded` after a failed load, `Backoff` once its retries are used. A call to a `warming` app answers `APP_WARMING` (retryable, `retry_after_s`): wait that long and call again. A call to a `Degraded` or `Backoff` app answers `APP_REGISTRY_UNREADABLE` (retryable): retry after `retry_after_s`; a `Backoff` app has used its retries and needs an operator. Report any other refusal verbatim; never retry past it.

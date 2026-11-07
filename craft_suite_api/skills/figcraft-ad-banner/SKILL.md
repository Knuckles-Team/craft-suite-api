---
name: figcraft-ad-banner
description: Build a 1200 x 628 ad banner frame with the product photo, headline, subhead and a call-to-action button, and export it as PNG.
---

# Design an ad banner

## When to use

A display ad, link preview image, landing-page hero or UI mock-up is needed from a product photo and copy.

## Inputs

- `${photo}`: the product image, as exchange://<sink>/<key>.
- `${headline}`: the headline.
- `${subhead}`: the supporting line.
- `${cta}`: the button label.
- `${name}`: the file name stem.

Every app tool is served by the craft-suite-api connector; call them in this order in one session (the app keeps the open document between calls). A value written `${name}` is an input above or the value an earlier step returned (its answer names it).

## Steps

| # | Tool | Arguments | Why |
|---|---|---|---|
| 1 | `figcraft_cmd_file_new` | `{"name": "${name}"}` | New file. |
| 2 | `figcraft_create_node` | `{"type": "frame", "name": "Ad 1200x628", "x": 0, "y": 0, "width": 1200, "height": 628, "props": {"fill": "#1d1b3a", "clip": true}}` | Create the 1200 x 628 frame filled with the brand colour; the answer gives its id. Returns `id` as `${fr}`. |
| 3 | `figcraft_cmd_image_place` | `{"path": "${photo}", "x": 700, "y": 90, "width": 440, "height": 330, "parent": "${fr}", "name": "Product"}` | Place the product photo inside the frame. |
| 4 | `figcraft_create_node` | `{"type": "text", "parent": "${fr}", "x": 60, "y": 150, "width": 600, "text": "${headline}", "name": "Headline", "props": {"fontSize": 88, "fill": "#ffb347"}}` | Headline text node (fontSize, fill). |
| 5 | `figcraft_create_node` | `{"type": "text", "parent": "${fr}", "x": 60, "y": 290, "width": 600, "text": "${subhead}", "name": "Subhead", "props": {"fontSize": 34, "fill": "#ffffff"}}` | Subhead text node. |
| 6 | `figcraft_create_node` | `{"type": "rectangle", "parent": "${fr}", "x": 60, "y": 440, "width": 280, "height": 76, "name": "CTA", "props": {"fill": "#ff7a2f", "cornerRadius": 38}}` | CTA button: a rounded rectangle. |
| 7 | `figcraft_create_node` | `{"type": "text", "parent": "${fr}", "x": 100, "y": 458, "text": "${cta}", "name": "CTA label", "props": {"fontSize": 34, "fill": "#1d1b3a"}}` | CTA label text. |
| 8 | `figcraft_export` | `{"ids": ["${fr}"], "path": "${name}.png", "scale": 1}` | Export the frame as PNG at scale 1. |

## Outputs

Formats: png. A relative output path lands in the run folder of the call; after the call the result's `scion/artifacts` lists each file with its link in every configured exchange sink (the object store under `<app>/<date>/<run>/<name>`, and the file share when configured). Pass a published file to another workflow as `exchange://objects/<key>`.

## Verify

The PNG is 1200 x 628 and shows the photo, headline, subhead and button.

## Notes

- Give every node `parent` = the frame id so it exports with the frame.

## Refusals

An app is in one lifecycle state: `warming` while its command registry loads, `Ready`, `Degraded` after a failed load, `Backoff` once its retries are used. A call to a `warming` app answers `APP_WARMING` (retryable, `retry_after_s`): wait that long and call again. A call to a `Degraded` or `Backoff` app answers `APP_REGISTRY_UNREADABLE` (retryable): retry after `retry_after_s`; a `Backoff` app has used its retries and needs an operator. Report any other refusal verbatim; never retry past it.

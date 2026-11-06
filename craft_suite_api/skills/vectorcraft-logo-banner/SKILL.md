---
name: vectorcraft-logo-banner
description: Draw a brand banner with a simple logo mark, the brand name and a tagline, and export it as SVG and PNG.
---

# Make a logo banner

## When to use

A logo lock-up, header banner, sign or other vector brand art is needed, as scalable SVG and a raster PNG.

## Inputs

- `${brand}`: the brand name.
- `${tagline}`: the tagline.
- `${brand_color}`: the background colour, #rrggbb.
- `${name}`: the file name stem.

Every app tool is served by the craft-suite-api connector; call them in this order in one session (the app keeps the open document between calls). A value written `${name}` is an input above or the value an earlier step returned (its answer names it).

## Steps

| # | Tool | Arguments | Why |
|---|---|---|---|
| 1 | `vectorcraft_cmd_file_new` | `{"name": "${name}", "width": 1200, "height": 400, "units": "Pixels"}` | New document in pixels (1200 x 400). |
| 2 | `vectorcraft_draw_shape` | `{"shape": "rectangle", "x": 0, "y": 0, "width": 1200, "height": 400, "fill": "${brand_color}", "stroke": "none", "name": "background"}` | Background rectangle in the brand colour. |
| 3 | `vectorcraft_draw_shape` | `{"shape": "ellipse", "x": 60, "y": 90, "width": 220, "height": 220, "fill": "#ff7a2f", "stroke": "none", "name": "logo-flame"}` | Logo mark: a filled circle. |
| 4 | `vectorcraft_draw_shape` | `{"shape": "star", "cx": 170, "cy": 200, "radius1": 70, "radius2": 30, "points": 5, "fill": "#ffe9b8", "stroke": "none", "name": "logo-star"}` | Logo mark: a star over it (points, inner and outer radius). |
| 5 | `vectorcraft_add_text` | `{"text": "${brand}", "x": 330, "y": 210, "size": 96, "font": "DejaVu Sans", "color": "#ffb347"}` | Brand name as live text (x, y is the baseline start; size in px). |
| 6 | `vectorcraft_add_text` | `{"text": "${tagline}", "x": 334, "y": 290, "size": 34, "font": "DejaVu Sans", "color": "#ffffff"}` | Tagline as live text. |
| 7 | `vectorcraft_export` | `{"path": "${name}.svg"}` | Export SVG (the extension picks the format). |
| 8 | `vectorcraft_export` | `{"path": "${name}.png", "scale": 2}` | Export PNG at scale 2 (2400 x 800). |

## Outputs

Formats: svg, png. A relative output path lands in the run folder of the call; after the call the result's `scion/artifacts` lists each file with its link in every configured exchange sink (the object store under `<app>/<date>/<run>/<name>`, and the file share when configured). Pass a published file to another workflow as `exchange://objects/<key>`.

## Verify

The SVG has the 1200 x 400 viewBox, the brand colours and the live text; the PNG is 2400 x 800.

## Notes

- `vectorcraft_export` can take 10-40 s; `outlineText: true` on SVG can pass the call timeout, so keep text live unless outlines are required.

## Refusals

`APP_WARMING` (retryable, `retry_after_s`): the app's command registry is still loading after a restart; wait and call again. `APP_REGISTRY_UNREADABLE` (retryable): the app's registry could not be read; it is retried in the background. Report any other refusal verbatim; never retry past it.

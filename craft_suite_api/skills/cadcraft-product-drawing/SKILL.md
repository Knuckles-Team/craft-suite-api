---
name: cadcraft-product-drawing
description: Draw a product outline with linear dimensions and a title block on layers, and save DXF and PDF plus a PNG render.
---

# Draw a dimensioned product drawing

## When to use

A spec sheet, manufacturer brief or packaging drawing needs a dimensioned 2-D drawing.

## Inputs

- `${title}`: the drawing title.
- `${notes}`: the notes line (units, scale, material).
- `${name}`: the file name stem.

Every app tool is served by the craft-suite-api connector; call them in this order in one session (the app keeps the open document between calls). A value written `${name}` is an input above or the value an earlier step returned (its answer names it).

## Steps

| # | Tool | Arguments | Why |
|---|---|---|---|
| 1 | `cadcraft_new_drawing` | `{"metric": true}` | New metric drawing. |
| 2 | `cadcraft_cmd_layer_new` | `{"name": "OUTLINE", "color": "white", "current": true}` | Outline layer. |
| 3 | `cadcraft_cmd_pline` | `{"vertices": [[0, 0], [120, 0], [100, 90], [20, 90]], "closed": true}` | The outline as a closed polyline (mm). |
| 4 | `cadcraft_cmd_layer_new` | `{"name": "DIMS", "color": "red", "current": true}` | Dimensions layer. |
| 5 | `cadcraft_cmd_dimlinear` | `{"p1": [0, 0], "p2": [120, 0], "at": [60, -20]}` | Bottom width dimension. |
| 6 | `cadcraft_cmd_dimlinear` | `{"p1": [20, 90], "p2": [100, 90], "at": [60, 105]}` | Top width dimension. |
| 7 | `cadcraft_cmd_dimlinear` | `{"p1": [120, 0], "p2": [100, 90], "at": [140, 45], "rotation": 90}` | Height dimension (rotated 90). |
| 8 | `cadcraft_cmd_layer_new` | `{"name": "TITLE", "color": "cyan", "current": true}` | Title layer. |
| 9 | `cadcraft_cmd_text` | `{"at": [0, -50], "text": "${title}", "height": 6}` | Title text (height in mm). |
| 10 | `cadcraft_cmd_text` | `{"at": [0, -60], "text": "${notes}", "height": 4}` | Notes text. |
| 11 | `cadcraft_cmd_zoom_extents` | `{}` | Zoom to the drawing. |
| 12 | `cadcraft_inspect_drawing` | `{"entities": true, "limit": 50}` | List the entities to check. |
| 13 | `cadcraft_save` | `{"path": "${name}.dxf"}` | Save DXF. |
| 14 | `cadcraft_save` | `{"path": "${name}.pdf"}` | Save PDF. |
| 15 | `cadcraft_render` | `{"path": "${name}.png", "width": 1200, "height": 800}` | Render a PNG. |

## Outputs

Formats: dxf, pdf, png. A relative output path lands in the run folder of the call; after the call the result's `scion/artifacts` lists each file with its link in every configured exchange sink (the object store under `<app>/<date>/<run>/<name>`, and the file share when configured). Pass a published file to another workflow as `exchange://objects/<key>`.

## Verify

The DXF holds the polyline, three dimensions and the two texts; the PDF has one page; the PNG shows the drawing.

## Refusals

An app is in one lifecycle state: `warming` while its command registry loads, `Ready`, `Degraded` after a failed load, `Backoff` once its retries are used. A call to a `warming` app answers `APP_WARMING` (retryable, `retry_after_s`): wait that long and call again. A call to a `Degraded` or `Backoff` app answers `APP_REGISTRY_UNREADABLE` (retryable): retry after `retry_after_s`; a `Backoff` app has used its retries and needs an operator. Report any other refusal verbatim; never retry past it.

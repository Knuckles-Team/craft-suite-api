---
name: lightcraft-develop-product-photo
description: Import a photo into the library, develop it (exposure, contrast, shadows, vibrance, white balance), crop it and export a JPEG.
---

# Develop a product photo

## When to use

Photos from a shoot need consistent, non-destructive development and a crop before they are used in listings or posts.

## Inputs

- `${photo}`: the photo, as exchange://<sink>/<key>.
- `${name}`: the file name stem.

Every app tool is served by the craft-suite-api connector; call them in this order in one session (the app keeps the open document between calls). A value written `${name}` is an input above or the value an earlier step returned (its answer names it).

## Steps

| # | Tool | Arguments | Why |
|---|---|---|---|
| 1 | `lightcraft_import` | `{"paths": ["${photo}"]}` | Import the photo; a photo already in the library is reported as a duplicate instead. Returns `imported.0` as `${pid}`. |
| 2 | `lightcraft_query_photos` | `{"limit": 1}` | Find the photo's id (newest first). Returns `photos.0.id` as `${pid}`. |
| 3 | `lightcraft_select_photos` | `{"ids": ["${pid}"], "active": "${pid}"}` | Select it and make it active. |
| 4 | `lightcraft_set_develop` | `{"id": "${pid}", "values": {"light.exposure": 0.5, "light.contrast": 15, "light.shadows": 20, "color.vibrance": 20}}` | Set the develop values (exposure in EV, contrast, shadows, vibrance). |
| 5 | `lightcraft_cmd_develop_wb` | `{"mode": "custom", "temp": 5800, "tint": 5}` | Set a custom white balance (temperature in K, tint). |
| 6 | `lightcraft_crop` | `{"id": "${pid}", "rect": [0.1, 0.1, 0.9, 0.9]}` | Crop with a normalised rect [left, top, right, bottom] in 0..1. |
| 7 | `lightcraft_export` | `{"id": "${pid}", "path": "${name}.jpg", "format": "jpeg"}` | Export a JPEG. |

## Outputs

Formats: jpg. A relative output path lands in the run folder of the call; after the call the result's `scion/artifacts` lists each file with its link in every configured exchange sink (the object store under `<app>/<date>/<run>/<name>`, and the file share when configured). Pass a published file to another workflow as `exchange://objects/<key>`.

## Verify

The JPEG has the cropped size (80% of each side here) and its colours differ from the same region of the source.

## Notes

- `lightcraft_import` takes `paths` (a list) although its schema does not name it.
- lightcraft's own `cmd_*` tools publish no argument schema; their parameters are only in the description.

## Refusals

`APP_WARMING` (retryable, `retry_after_s`): the app's command registry is still loading after a restart; wait and call again. `APP_REGISTRY_UNREADABLE` (retryable): the app's registry could not be read; it is retried in the background. Report any other refusal verbatim; never retry past it.

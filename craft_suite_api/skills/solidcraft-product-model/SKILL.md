---
name: solidcraft-product-model
description: Sketch a profile and revolve it into a solid product model, check its size, and export STL, STEP, a PNG render and the design file.
---

# Model a product in 3-D

## When to use

A simple product part or prototype needs a 3-D model for printing, manufacturing quotes or product renders.

## Inputs

- `${name}`: the design and file name stem.

Every app tool is served by the craft-suite-api connector; call them in this order in one session (the app keeps the open document between calls). A value written `${name}` is an input above or the value an earlier step returned (its answer names it).

## Steps

| # | Tool | Arguments | Why |
|---|---|---|---|
| 1 | `solidcraft_new_design` | `{"name": "${name}"}` | New design. |
| 2 | `solidcraft_batch` | `{"commands": [{"command": "sketch.create", "params": {"plane": "XZ"}}, {"command": "sketch.line", "params": {"points": [[60, 0], [57, 0], [37, -87], [15, -87], [15, -90], [40, -90]], "closed": true}}, {"command": "solid.revolve", "params": {"axis": "Z", "angle": "360 deg", "body_name": "LampShade"}}], "expect": {"bodies": 1, "bbox": {"min": [-60, -60, 0], "max": [60, 60, 90]}}}` | Sketch the half profile on XZ and revolve it 360 deg around Z in one batch (with an expected bounding box check). |
| 3 | `solidcraft_measure` | `{"summary": true}` | Measure the body: bounding box, volume, faces. |
| 4 | `solidcraft_export` | `{"path": "${name}.stl"}` | Export STL for printing or texturing. |
| 5 | `solidcraft_export` | `{"path": "${name}.step"}` | Export STEP for CAD exchange. |
| 6 | `solidcraft_screenshot` | `{"path": "${name}.png", "width": 1000, "height": 800}` | Render a PNG (width and height in px). |
| 7 | `solidcraft_save` | `{"path": "${name}.sc"}` | Save the design. |

## Outputs

Formats: stl, step, png, sc. A relative output path lands in the run folder of the call; after the call the result's `scion/artifacts` lists each file with its link in every configured exchange sink (the object store under `<app>/<date>/<run>/<name>`, and the file share when configured). Pass a published file to another workflow as `exchange://objects/<key>`.

## Verify

The measure shows one closed body with the expected size; the STL and STEP are written and the PNG is not blank.

## Notes

- Replies carry a headless-session note after the JSON; read the JSON part.
- Use `sketch.line` with `closed: true` for a polygon.

## Refusals

An app is in one lifecycle state: `warming` while its command registry loads, `Ready`, `Degraded` after a failed load, `Backoff` once its retries are used. A call to a `warming` app answers `APP_WARMING` (retryable, `retry_after_s`): wait that long and call again. A call to a `Degraded` or `Backoff` app answers `APP_REGISTRY_UNREADABLE` (retryable): retry after `retry_after_s`; a `Backoff` app has used its retries and needs an operator. Report any other refusal verbatim; never retry past it.

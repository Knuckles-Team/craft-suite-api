---
name: anicraft-compose-frame
description: Compose an animation frame — set a stage, draw a rounded rectangle and an ellipse on it, verify the document, preview the frame, and export it as a published PNG.
---

# Compose an animation frame

## When to use

A frame of an animation is needed as a file: a title card, a product loop frame or a still from a motion piece. The frame is composed from shapes on a stage and exported as PNG.

## Inputs

None — the stage and shapes below are the proven composition; adjust the geometry and colours to the request.

Every app tool is served by the craft-suite-api connector; call them in this order in one session (the app keeps the open document between calls). A value written `${name}` is an input above or the value an earlier step returned (its answer names it).

## Steps

| # | Tool | Arguments | Why |
|---|---|---|---|
| 1 | `anicraft_cmd_doc_set_stage` | `{"width": 1280, "height": 720, "fps": 24, "background": "#101418"}` | Set the stage size and frame rate; the dark background is the frame's base. |
| 2 | `anicraft_cmd_draw_rect` | `{"x": 140, "y": 180, "w": 420, "h": 260, "radius": 36, "fill": "#3dd6c3", "stroke": "#0b1f24", "stroke_width": 6}` | Draw the first shape: a teal rounded rectangle (x,y is the top-left corner; radius in px; fill/stroke as #rrggbb). |
| 3 | `anicraft_cmd_draw_ellipse` | `{"x": 760, "y": 300, "w": 300, "h": 300, "fill": "#f4b942", "stroke": "#3a2a08", "stroke_width": 6}` | Draw the second shape: a gold circle beside the rectangle. |
| 4 | `anicraft_anicraft_document` | `{}` | Read the open document: stage size, scenes, layers and keyframes — confirm the shapes are present before rendering. |
| 5 | `anicraft_anicraft_render` | `{"frame": 0, "scale": 1.0}` | Render frame 0 as a PNG picture in the result, exactly as exported — the quick preview before publishing. |
| 6 | `anicraft_cmd_file_export_png` | `{"frame": 0, "path": "animation-frame-0.png", "scale": 1.0}` | Export the same frame to a file; a relative path lands in the run folder and is published. |

## Outputs

Formats: png. A relative output path lands in the run folder of the call; after the call the result's `scion/artifacts` lists each file with its link in every configured exchange sink (the object store under `<app>/<date>/<run>/<name>`, and the file share when configured). Pass a published file to another workflow as `exchange://objects/<key>`.

## Verify

Open the exported PNG: the image size equals the stage (1280 x 720 at scale 1.0), the background pixels read as the stage colour, and the shape pixels read as the fills — the rectangle's fill at its centre, the ellipse's fill at its centre. The preview frame from the render call and the exported file agree.

## Notes

- The document stays open in the session between calls; `anicraft_anicraft_document` is the check that the commands landed before anything is rendered or exported.
- `anicraft_anicraft_render` returns the frame as picture content in the result; `anicraft_cmd_file_export_png` is the call that writes the published file — use both: preview, then export.
- The generated `anicraft_cmd_<command>` tools are the served command interface; their parameter names are the engine command's own (verify against `anicraft_anicraft_commands` when the request needs a command this skill does not walk).

## Refusals

An app is in one lifecycle state: `warming` while its command registry loads, `Ready`, `Degraded` after a failed load, Backoff once its retries are used. A call to a `warming` app answers `APP_WARMING` (retryable, `retry_after_s`): wait that long and call again. A call to a `Degraded` or `Backoff` app answers `APP_REGISTRY_UNREADABLE` (retryable): retry after `retry_after_s`; a `Backoff` app has used its retries and needs an operator. Report any other refusal verbatim; never retry past it.

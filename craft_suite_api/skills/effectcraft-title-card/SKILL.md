---
name: effectcraft-title-card
description: Build a 5 s animated title card (title slides and fades in, subtitle fades in) and render it to MP4, with stills and a Lottie file.
---

# Animate a title card

## When to use

A promo needs an animated title, lower third or end card, as video or as a Lottie animation for the web.

## Inputs

- `${title}`: the title.
- `${subtitle}`: the subtitle.
- `${name}`: the composition name.
- `${run}`: an exchange run id you choose for the render steps, e.g. title-card-1.

Every app tool is served by the craft-suite-api connector; call them in this order in one session (the app keeps the open document between calls). A value written `${name}` is an input above or the value an earlier step returned (its answer names it).

## Steps

| # | Tool | Arguments | Why |
|---|---|---|---|
| 1 | `effectcraft_cmd_file_newProject` | `{}` | New project. |
| 2 | `effectcraft_cmd_comp_new` | `{"name": "${name}", "width": 1280, "height": 720, "frameRate": 24, "duration": 5, "background": "#1d1b3a"}` | New composition: size, frame rate, duration in seconds, background colour. |
| 3 | `effectcraft_cmd_layer_newSolid` | `{"name": "Backdrop", "color": "#2a2760", "width": 1280, "height": 720}` | A backdrop solid. |
| 4 | `effectcraft_cmd_layer_newText` | `{"text": "${title}", "position": [640, 330], "size": 120, "fill": "#ffb347", "justify": "center"}` | The title text layer (position in px, size, fill). |
| 5 | `effectcraft_cmd_layer_newText` | `{"text": "${subtitle}", "position": [640, 440], "size": 44, "fill": "#ffffff", "justify": "center"}` | The subtitle text layer. |
| 6 | `effectcraft_add_keyframe` | `{"layer": "#2", "path": "transform/opacity", "keys": [{"time": 0, "value": 0}, {"time": 1, "value": 100}], "interpolation": "easyEase"}` | Fade the title in: opacity keys (0 to 100 over 1 s). |
| 7 | `effectcraft_add_keyframe` | `{"layer": "#2", "path": "transform/position", "keys": [{"time": 0, "value": [440, 330]}, {"time": 1.2, "value": [640, 330]}], "interpolation": "easyEase"}` | Slide the title in: position keys. |
| 8 | `effectcraft_add_keyframe` | `{"layer": "#1", "path": "transform/opacity", "keys": [{"time": 0.8, "value": 0}, {"time": 1.8, "value": 100}], "interpolation": "easyEase"}` | Fade the subtitle in after the title. |
| 9 | `effectcraft_cmd_renderQueue_add` | `{"format": "h264", "output": "title-card.mp4"}` | Queue the render: format and relative output file. Send `_meta: {"scion/run": "${run}"}` (one run id for these steps). |
| 10 | `effectcraft_cmd_renderQueue_render` | `{"wait": true}` | Render the queue and wait. The output is written during this call, so steps 9 and 10 share one exchange run. Send `_meta: {"scion/run": "${run}"}` (one run id for these steps). |
| 11 | `effectcraft_cmd_comp_saveFrameAs` | `{"path": "title-t0.3.png", "time": 0.3}` | Save a still early in the animation. |
| 12 | `effectcraft_cmd_comp_saveFrameAs` | `{"path": "title-t2.5.png", "time": 2.5}` | Save a still once everything is in. |
| 13 | `effectcraft_cmd_file_exportLottie` | `{"path": "title-card.json"}` | Export the animation as Lottie JSON. |

## Outputs

Formats: mp4, png, json. A relative output path lands in the run folder of the call; after the call the result's `scion/artifacts` lists each file with its link in every configured exchange sink (the object store under `<app>/<date>/<run>/<name>`, and the file share when configured). Pass a published file to another workflow as `exchange://objects/<key>`.

## Verify

ffprobe the MP4: 5 s, h264, 1280 x 720 at 24 fps; the early still shows the title faded, the late one shows title and subtitle.

## Notes

- Layer `#1` is the topmost (the last text added).
- Property paths: `transform/opacity`, `transform/position`, `transform/scale`, `transform/rotation`.
- Pass the same `scion/run` in the call `_meta` for the queue and render steps (any value matching [A-Za-z0-9][A-Za-z0-9._-]*), so the file the render writes is published.
- Script running (`run_script`) is refused while file access is confined.

## Refusals

An app is in one lifecycle state: `warming` while its command registry loads, `Ready`, `Degraded` after a failed load, `Backoff` once its retries are used. A call to a `warming` app answers `APP_WARMING` (retryable, `retry_after_s`): wait that long and call again. A call to a `Degraded` or `Backoff` app answers `APP_REGISTRY_UNREADABLE` (retryable): retry after `retry_after_s`; a `Backoff` app has used its retries and needs an operator. Report any other refusal verbatim; never retry past it.

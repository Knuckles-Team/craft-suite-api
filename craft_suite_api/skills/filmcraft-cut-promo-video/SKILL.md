---
name: filmcraft-cut-promo-video
description: Import a clip, make a sequence from it, trim the head and tail, lay a title over it and export an H.264 MP4.
---

# Cut a promo video

## When to use

A raw clip needs to become a short promo: keep the best seconds, add a title card or text overlay, and deliver an MP4.

## Inputs

- `${clip}`: the source clip, as exchange://<sink>/<key> or an https URL.
- `${tps}`: ticks per second of the timeline (254016000000); trims are in ticks.
- `${title}`: the title text.
- `${project}`: a project name.

Every app tool is served by the craft-suite-api connector; call them in this order in one session (the app keeps the open document between calls). A value written `${name}` is an input above or the value an earlier step returned (its answer names it).

## Steps

| # | Tool | Arguments | Why |
|---|---|---|---|
| 1 | `filmcraft_cmd_file_newProject` | `{"name": "${project}"}` | Start a project. |
| 2 | `filmcraft_cmd_file_import` | `{"paths": ["${clip}"]}` | Import the clip; the answer names the project item. Returns `items.0` as `${item}`. |
| 3 | `filmcraft_cmd_file_newSequenceFromClip` | `{"items": ["${item}"]}` | Make a sequence from the clip; the answer gives the video and audio clip ids. Returns `clips.0` as `${vclip}`. |
| 4 | `filmcraft_cmd_timeline_trim` | `{"clip": "${vclip}", "edge": "in", "mode": "ripple", "delta": 508032000000, "linked": true}` | Trim the head: ripple the in edge forward (delta in ticks; here 2 s), audio follows when linked. |
| 5 | `filmcraft_cmd_timeline_trim` | `{"clip": "${vclip}", "edge": "out", "mode": "ripple", "delta": -1016064000000, "linked": true}` | Trim the tail: ripple the out edge back (here 4 s), leaving 6 s. |
| 6 | `filmcraft_cmd_graphics_newText` | `{"text": "${title}", "position": [120, 620], "size": 72, "seconds": 6, "time": 0}` | Add the title on the track above (position in pixels, size in px, seconds on screen, time in ticks). |
| 7 | `filmcraft_sequence_inspect` | `{}` | Check the sequence: duration, clip in/out and the title clip. |
| 8 | `filmcraft_cmd_file_exportMedia` | `{"path": "promo.mp4", "format": "h264", "audioCodec": "aac"}` | Export the MP4. The export runs as a background job; the tool waits for it and then publishes the file. |

## Outputs

Formats: mp4. A relative output path lands in the run folder of the call; after the call the result's `scion/artifacts` lists each file with its link in every configured exchange sink (the object store under `<app>/<date>/<run>/<name>`, and the file share when configured). Pass a published file to another workflow as `exchange://objects/<key>`.

## Verify

ffprobe the published MP4: duration equals the trimmed length, the streams are h264 video and aac audio, and a frame grab shows the title.

## Notes

- Times are in ticks: 254016000000 per second.
- `filmcraft_cmd_file_exportMedia` answers `finished: true` and the file links only after the job ends; a failed job answers an error with the job's message.

## Refusals

An app is in one lifecycle state: `warming` while its command registry loads, `Ready`, `Degraded` after a failed load, `Backoff` once its retries are used. A call to a `warming` app answers `APP_WARMING` (retryable, `retry_after_s`): wait that long and call again. A call to a `Degraded` or `Backoff` app answers `APP_REGISTRY_UNREADABLE` (retryable): retry after `retry_after_s`; a `Backoff` app has used its retries and needs an operator. Report any other refusal verbatim; never retry past it.

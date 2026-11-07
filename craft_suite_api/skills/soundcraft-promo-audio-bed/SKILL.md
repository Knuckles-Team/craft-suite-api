---
name: soundcraft-promo-audio-bed
description: Import audio (or a clip's soundtrack), raise its gain, fade it in and out, and bounce the mix to WAV.
---

# Make a promo audio bed

## When to use

A promo, video or ad needs its music or voice bed levelled and faded, delivered as a WAV.

## Inputs

- `${clip}`: the audio or video file, as exchange://<sink>/<key>.
- `${name}`: the session name.

Every app tool is served by the craft-suite-api connector; call them in this order in one session (the app keeps the open document between calls). A value written `${name}` is an input above or the value an earlier step returned (its answer names it).

## Steps

| # | Tool | Arguments | Why |
|---|---|---|---|
| 1 | `soundcraft_new_session` | `{"name": "${name}"}` | New session. |
| 2 | `soundcraft_import_audio` | `{"path": "${clip}"}` | Import the audio (a video file's soundtrack works); the answer gives the clip id. Returns `imported.0.clip` as `${c}`. |
| 3 | `soundcraft_cmd_clip_gain` | `{"clips": ["${c}"], "db": 6}` | Raise the clip gain (dB). |
| 4 | `soundcraft_cmd_edit_fades_create` | `{"clip": "${c}", "side": "in", "length": 48000, "shape": "equal power"}` | Fade in (length in samples; 48000 = 1 s at 48 kHz). |
| 5 | `soundcraft_cmd_edit_fades_create` | `{"clip": "${c}", "side": "out", "length": 96000, "shape": "s-curve"}` | Fade out (here 2 s). |
| 6 | `soundcraft_bounce_mix` | `{"path": "promo-bed.wav", "format": "wav"}` | Bounce the mix to WAV; the answer gives seconds, peak and loudness. |

## Outputs

Formats: wav. A relative output path lands in the run folder of the call; after the call the result's `scion/artifacts` lists each file with its link in every configured exchange sink (the object store under `<app>/<date>/<run>/<name>`, and the file share when configured). Pass a published file to another workflow as `exchange://objects/<key>`.

## Verify

The WAV's duration matches the source; the peak rose by the gain; the first and last seconds ramp.

## Notes

- Fade lengths are in samples.
- Use the command tools (`soundcraft_cmd_*`); the dispatch tool `soundcraft_execute` is not listed.

## Refusals

An app is in one lifecycle state: `warming` while its command registry loads, `Ready`, `Degraded` after a failed load, `Backoff` once its retries are used. A call to a `warming` app answers `APP_WARMING` (retryable, `retry_after_s`): wait that long and call again. A call to a `Degraded` or `Backoff` app answers `APP_REGISTRY_UNREADABLE` (retryable): retry after `retry_after_s`; a `Backoff` app has used its retries and needs an operator. Report any other refusal verbatim; never retry past it.

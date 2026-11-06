---
name: texturecraft-texture-product
description: Import a product mesh, paint colour and material strokes on it, render the viewport, and export PBR textures, a GLB and the project.
---

# Texture a product model

## When to use

A 3-D product model needs colour and material for renders, AR or a web viewer.

## Inputs

- `${mesh}`: the mesh (glb, gltf, fbx, obj, stl, ...), as exchange://<sink>/<key>, e.g. a solidcraft export.
- `${name}`: the file name stem.

Every app tool is served by the craft-suite-api connector; call them in this order in one session (the app keeps the open document between calls). A value written `${name}` is an input above or the value an earlier step returned (its answer names it).

## Steps

| # | Tool | Arguments | Why |
|---|---|---|---|
| 1 | `texturecraft_mesh_import` | `{"path": "${mesh}", "resolution": 1024}` | New project from the mesh (texture resolution in px). |
| 2 | `texturecraft_paint_stroke` | `{"points": [[300, 200], [500, 300], [400, 420]], "color": "#c0392b", "roughness": 0.4, "metallic": 0.2, "size": 30}` | Paint a stroke: points in viewport pixels, base colour, roughness, metallic, brush size. |
| 3 | `texturecraft_paint_stroke` | `{"points": [[420, 180], [480, 250], [560, 330]], "color": "#f1c40f", "roughness": 0.3, "metallic": 0.8, "size": 25}` | Paint a second stroke. |
| 4 | `texturecraft_viewport_render` | `{"width": 800, "height": 600, "yaw": 30, "pitch": 15}` | Render the viewport to check where the paint landed. |
| 5 | `texturecraft_textures_export` | `{"dir": "${name}-textures", "preset": "glTF PBR Metal Roughness"}` | Export the textures with a preset (glTF PBR Metal Roughness). |
| 6 | `texturecraft_mesh_export` | `{"path": "${name}.glb", "format": "glb"}` | Export the mesh as GLB with its textures embedded. |
| 7 | `texturecraft_project_save` | `{"path": "${name}.tcraft"}` | Save the project. |

## Outputs

Formats: png, glb, tcraft. A relative output path lands in the run folder of the call; after the call the result's `scion/artifacts` lists each file with its link in every configured exchange sink (the object store under `<app>/<date>/<run>/<name>`, and the file share when configured). Pass a published file to another workflow as `exchange://objects/<key>`.

## Verify

The base colour texture holds the painted colours; the GLB and project are written.

## Notes

- Stroke points are viewport pixels: render the viewport first to see where the mesh is.
- Paths are relative to the app's roots; the connector converts the exchange's paths.

## Refusals

`APP_WARMING` (retryable, `retry_after_s`): the app's command registry is still loading after a restart; wait and call again. `APP_REGISTRY_UNREADABLE` (retryable): the app's registry could not be read; it is retried in the background. Report any other refusal verbatim; never retry past it.

---
name: texturecraft
description: TextureCraft 3D texture painting — projects, meshes, bakes, paint strokes and texture exports.
---

# Texturecraft

## When to use

TextureCraft 3D texture painting — projects, meshes, bakes, paint strokes and texture exports.

## Activation

Call `registry_activate` with the namespace `texturecraft` before using any `texturecraft_*` tool.

## Files in and out

Pass an input file as `exchange://<sink>/<key>` (for example `exchange://files/in/photo.png`) or as an `https` URL; the server stages it and hands the app a local path. Give an output path as a relative path such as `out.png`: it lands in this run's folder, and after the call the result links each output in every configured sink.

## Tools

| Tool | What it does |
|---|---|
| `texturecraft_bake` | Bake mesh maps (ambient occlusion, curvature, thickness, …) for generators and smart materials. |
| `texturecraft_bake_mesh_add` | Add a high-definition mesh for baking (path relative to the read root), or with `cage: true` set the bake cage. |
| `texturecraft_command_batch` | Run several commands in order: steps [{id, params}]. |
| `texturecraft_command_list` | List engine commands: id, label, menu path, shortcut, params doc and whether it can run now. |
| `texturecraft_command_run` | Run an engine command by id with JSON params (see command_list). |
| `texturecraft_material_load` | Add a smart material from a . |
| `texturecraft_material_save` | Save a layer or folder (default: the selected one) as a smart material file (. |
| `texturecraft_mesh_export` | Export the mesh with its textures (obj, glb, usda, usdc or usdz; path relative to the write root). |
| `texturecraft_mesh_import` | New project from a mesh file (path relative to the read root): one texture set per material. |
| `texturecraft_mesh_reimport` | Reimport the project's mesh from a file (path relative to the read root) or, without a path, from the project's own copy. |
| `texturecraft_paint_stroke` | Paint a stroke with the paint tool on the selected layer (or its mask target): sets the brush material (color, roughness, metallic, height) and size/hardness, then strokes through `points` in viewport pixels. |
| `texturecraft_project_new` | Start a new project on a built-in mesh (one texture set per material, each with an empty paint layer). |
| `texturecraft_project_open` | Open a . |
| `texturecraft_project_save` | Save the project as . |
| `texturecraft_resource_import` | Import an image (png, jpg, tga, tif, bmp, webp, exr, hdr; path relative to the read root) as a project resource. |
| `texturecraft_session_inspect` | The whole session as JSON: project, mesh, texture sets (resolution, channels, baked maps), the layer stack top to bottom (fill sources, masks, effects, painted tile counts), tool, camera, display and history. |
| `texturecraft_textures_export` | Export textures with a preset into a folder relative to the write root. |
| `texturecraft_ui_inspect` | Bridge mode: the app's UI state (panels, windows, mode, layout, viewport rect, toasts). |
| `texturecraft_ui_menu_invoke` | Bridge mode: activate a menu item by id like a click (may open a window). |
| `texturecraft_ui_screenshot` | Bridge mode: PNG of the whole app window (downscaled to 2048 px a side at most). |
| `texturecraft_viewport_render` | Headless: render the 3D view (or the 2D UV view) as a PNG image, up to 2048 px a side. |
| `texturecraft_viewport_screenshot` | Bridge mode: PNG of the live app's 3D or 2D viewport. |

## Functionalities

- `texturecraft-paint_mesh` — Start a project from a mesh, bake its maps and paint it.
- `texturecraft-export_textures` — Open a project, render the viewport and export the textures.
- `texturecraft-run_commands` — Look up engine commands and run them, alone or in a batch.

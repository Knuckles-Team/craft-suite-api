---
name: materialcraft
description: MaterialCraft node-based materials — packages, graphs, nodes, renders and output exports.
---

# Materialcraft

## When to use

MaterialCraft node-based materials — packages, graphs, nodes, renders and output exports.

## Activation

Call `registry_activate` with the namespace `materialcraft` before using any `materialcraft_*` tool.

## Files in and out

Pass an input file as `exchange://<sink>/<key>` (for example `exchange://files/in/photo.png`) or as an `https` URL; the server stages it and hands the app a local path. Give an output path as a relative path such as `out.png`: it lands in this run's folder, and after the call the result links each output in every configured sink.

## Tools

| Tool | What it does |
|---|---|
| `materialcraft_bitmap_import` | Embed an image (path relative to the read root) as a bitmap resource. |
| `materialcraft_command_batch` | Run several commands in order: steps [{id, params}]. |
| `materialcraft_command_list` | List engine commands: id, label, menu path, shortcut, params doc and whether it can run now. |
| `materialcraft_command_run` | Run an engine command by id with JSON params (see command_list). |
| `materialcraft_graph_new` | Add a new graph to the package from a template and open it. |
| `materialcraft_library_list` | The node library: every node's id, label, category, input and output ports and parameters (id, default, range, enum options). |
| `materialcraft_node_add` | Add a node to the open graph (optionally wired from another node's output). |
| `materialcraft_node_connect` | Wire an output port of one node into an input port of another (replacing what fed that input). |
| `materialcraft_node_param` | Set one parameter of a node. |
| `materialcraft_outputs_export` | Cook a graph at full size and write every output (base color, normal, roughness, …) into a folder relative to the write root. |
| `materialcraft_package_open` | Open an . |
| `materialcraft_package_save` | Save the package (path relative to the write root; omit to save to its own file). |
| `materialcraft_session_inspect` | The whole session as JSON: package, graphs, the open graph's nodes (definition, parameters, base parameters, ports, cook errors, timings, mean values), connections, frames, comments, pins, exposed inputs, views and history. |
| `materialcraft_ui_input` | Bridge mode: synthesize mouse, keyboard and text input in the app window (clicks, drags between node ports, scrolling, shortcuts, typing). |
| `materialcraft_ui_inspect` | Bridge mode: the app's UI state (panels, windows, graph view camera, node rectangles on screen, toasts). |
| `materialcraft_ui_menu_invoke` | Bridge mode: activate a menu item by id like a click (may open a window). |
| `materialcraft_ui_screenshot` | Bridge mode: PNG of the whole app window (downscaled to 2048 px a side at most). |
| `materialcraft_view_render` | Headless: render the material on the 3D view's scene, or a node's output (view 2d), as a PNG up to 2048 px a side. |
| `materialcraft_view_screenshot` | Bridge mode: PNG of the live app's 3D or 2D view. |

## Functionalities

- `materialcraft-build_material` — Start a graph, add and connect nodes and set parameters.
- `materialcraft-export_material` — Open a package, render the material and export its outputs.
- `materialcraft-run_commands` — Look up engine commands and run them, alone or in a batch.

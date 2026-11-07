---
name: materialcraft-product-material
description: Build a brushed-metal PBR material graph from noise, levels, a gradient map and a normal/AO node, and export its texture maps.
---

# Build a product material

## When to use

A product render, 3-D model or texture project needs a material (metal, fabric, wood) as PBR texture maps.

## Inputs

- `${name}`: the graph and folder name.

Every app tool is served by the craft-suite-api connector; call them in this order in one session (the app keeps the open document between calls). A value written `${name}` is an input above or the value an earlier step returned (its answer names it).

## Steps

| # | Tool | Arguments | Why |
|---|---|---|---|
| 1 | `materialcraft_graph_new` | `{"name": "${name}", "template": "pbr", "size": 512}` | New PBR graph (size in px); the answer gives its index. Returns `graph` as `${g}`. |
| 2 | `materialcraft_command_batch` | `{"steps": [{"id": "graph.select", "params": {"ids": [1]}}, {"id": "graph.node.param", "params": {"id": 1, "param": "metallic", "value": 1.0}}]}` | Set the metallic output to 1 (select the node first, then set its parameter). |
| 3 | `materialcraft_node_add` | `{"def": "anisotropic_noise", "params": {"scale": 2, "scale_y": 300, "smoothness": 0.4}, "at": [-400, 0]}` | Anisotropic noise: the brushed streaks. Returns `id` as `${noise}`. |
| 4 | `materialcraft_node_add` | `{"def": "levels", "params": {"in_low": 0.25, "in_high": 0.85, "out_low": 0.25, "out_high": 0.6}, "connectFrom": {"node": "${noise}"}}` | Levels: the roughness range. Returns `id` as `${lv}`. |
| 5 | `materialcraft_node_add` | `{"def": "gradient_map", "params": {"gradient": [[0.0, "#7d8189"], [1.0, "#d8dbe0"]]}, "connectFrom": {"node": "${noise}"}}` | Gradient map: the metal's base colour. Returns `id` as `${gm}`. |
| 6 | `materialcraft_node_add` | `{"def": "height_normal_ao", "params": {"normal_intensity": 0.6}, "connectFrom": {"node": "${noise}"}}` | Height to normal and ambient occlusion. Returns `id` as `${hn}`. |
| 7 | `materialcraft_node_connect` | `{"from": "${gm}", "to": 2}` | Base colour output from the gradient map. |
| 8 | `materialcraft_node_connect` | `{"from": "${hn}", "fromPort": "normal", "to": 3}` | Normal output. |
| 9 | `materialcraft_node_connect` | `{"from": "${lv}", "to": 4}` | Roughness output from the levels. |
| 10 | `materialcraft_node_connect` | `{"from": "${hn}", "fromPort": "ambient_occlusion", "to": 7}` | Ambient occlusion output. |
| 11 | `materialcraft_node_connect` | `{"from": "${noise}", "to": 6}` | Height output from the noise. |
| 12 | `materialcraft_outputs_export` | `{"dir": "${name}"}` | Export every output into a folder (relative to the run). |
| 13 | `materialcraft_view_render` | `{}` | Render a preview. |

## Outputs

Formats: png. A relative output path lands in the run folder of the call; after the call the result's `scion/artifacts` lists each file with its link in every configured exchange sink (the object store under `<app>/<date>/<run>/<name>`, and the file share when configured). Pass a published file to another workflow as `exchange://objects/<key>`.

## Verify

The export lists the base colour, normal, roughness, metallic, height and AO maps; they are full-size and not flat.

## Notes

- `materialcraft_node_param` needs the node selected first (`graph.select`).
- Paths are relative to the app's roots; the connector converts the exchange's paths.

## Refusals

An app is in one lifecycle state: `warming` while its command registry loads, `Ready`, `Degraded` after a failed load, `Backoff` once its retries are used. A call to a `warming` app answers `APP_WARMING` (retryable, `retry_after_s`): wait that long and call again. A call to a `Degraded` or `Backoff` app answers `APP_REGISTRY_UNREADABLE` (retryable): retry after `retry_after_s`; a `Backoff` app has used its retries and needs an operator. Report any other refusal verbatim; never retry past it.

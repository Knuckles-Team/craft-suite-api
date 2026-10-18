---
name: artcraft-starter
description: >-
  Browse ArtCraft audio, image, mesh, and splat model catalogs through this
  connector's public MCP operations. Use for model availability and returned
  capabilities; generation and video catalog discovery are unavailable.
license: MIT
tags: [artcraft, model-catalog, mcp]
metadata:
  version: '0.2.0'
---

# Browse ArtCraft model catalogs

Use one of these per-operation tools (each action is its own `craft_suite_<action>` tool):

- `craft_suite_omni_gen_audio_models_handler`
- `craft_suite_omni_gen_image_models_handler`
- `craft_suite_omni_gen_mesh_models_handler`
- `craft_suite_omni_gen_splat_models_handler`

The approved provider origin and TLS configuration come from the operator.
These four static catalog reads require no signed session or write enablement.
Report capabilities returned by the selected action. The pinned image handler
ignores its provider filter, so do not describe its response as provider-filtered.

Do not invoke generation, uploads, job polling, video discovery, arbitrary routes,
or graph ingestion: this connector does not support them. Source validation does
not prove a live backend, full enum/serializer parity or deployed availability.

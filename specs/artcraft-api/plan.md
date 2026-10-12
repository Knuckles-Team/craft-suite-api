# CONN-ARTCRAFT-API — Design and implementation plan

Governing specification: [spec.md](spec.md).

## Existing system and reuse

The connector reuses the SDK server factory, credential resolver, and HTTP client. Ingestion is unavailable in this version.
The connector owns operation arguments, external-system mappings, and package content.

The governing [specification](spec.md) records component ownership and source bindings.
The [architecture page](../../docs/architecture.md) shows the active request path.
No graph-ingestion path is enabled.

## Implementation units

- `artcraft_api/openapi_schema.py`: captured contract and bounded validation.
- `artcraft_api/openapi_parameters.py`: declared path/query/header serialization.
- `artcraft_api/openapi_client.py`: origin, permission and HTTP dispatch policy.
- `artcraft_api/openapi_responses.py`: bounded response reading and decoding.
- `artcraft_api/openapi_runtime.py`: native MCP routing and confirmation.

## Interfaces and live integration path

`artcraft_api/mcp_server.py` exposes `build_server` and the console entry point.
`get_mcp_instance` calls `create_mcp_server`, `register_tool_surface`, and the package tool registrars.
`artcraft_api/mcp/__init__.py` routes selected operations through `get_client` and the API client.
`artcraft_api/auth.py` resolves references only when a caller requests a client.
`artcraft_api/openapi_client.py` enforces transport and response limits before returning external data.
Graph ingestion is withheld until a tenant/source-scoped mapping and complete receipt contract have been reviewed.
The SDK owns engine transport and durable checkpoints.

## Content and contracts

The server serves package prompts, skills, ontology, and `connector_manifest.yml` through native MCP primitives.
The schema generator reads `tools/list` without invoking vendor operations.
It records both input and output schemas. Empty source presets declare no extraction integration.
Native content listing acceptance remains pending until a connector-owned test exercises the production server.

## Dependencies and decisions

No additional capability prerequisite has been established in this starter repository.
The SDK reference records a source dependency; it does not create a cross-repository delivery prerequisite.
Reviewers must add `Depends-on:` declarations only for confirmed prerequisite requirements.
Each source mapping must match the connector's actual external data before ingestion is enabled.

## Quality and release gates

Run `python scripts/check_connector_contract.py . --package artcraft_api`.
Run `python scripts/generate_tool_schemas.py --check` and `python -m pytest tests -q`.
Run the pinned pre-commit and pre-push gates with the approved scanner toolchain.
The published site must pass the shared readiness checks and render canonical spec records.
Source tests do not authorize release, deployment, or external effects.

## Risks and alternatives

Starter operations and mappings require external-system validation before production use.
Missing credentials, rejected source observations, and failed transport checks must propagate as explicit failures.
Duplicating shared SDK or pipeline logic would create conflicting owners.

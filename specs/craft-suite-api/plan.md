# CONN-CRAFT-SUITE-API — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

The connector reuses the SDK server factory, credential resolver, and HTTP client. Ingestion is unavailable in this version. The connector owns operation arguments, external-system mappings, and package content. The governing [specification](spec.md) records component ownership and source bindings. The [architecture page](../../docs/architecture.md) shows the active request path. No graph-ingestion path is enabled.

## Technical Context

- **Language/Version**: Python 3.14 (floor 3.12)
- **Primary Dependencies**: scion-sdk, fastmcp
- **Storage**: N/A; the connector stores nothing
- **Testing**: pytest; the proof level each row names
- **Target Platform**: Linux containers
- **Project Type**: connector (MCP server)
- **Performance Goals**: N/A
- **Constraints**: one tool per API operation; shared capabilities come from the SDK
- **Scale/Scope**: 6 rows

## Constitution Check

- One owner per concept: pass. The connector owns one external system's calls, mappings and tools only.
- Connectors depend on the SDK and are called through arbora: pass.
- No ratchets: pass. The rows add no suppression.

## Project Structure

```text
craft_suite_api/auth.py  existing
craft_suite_api/openapi_client.py  existing
craft_suite_api/openapi_responses.py  existing
craft_suite_api/mcp_server.py  existing
craft_suite_api/mcp/__init__.py  existing
craft_suite_api/openapi_runtime.py  existing
pyproject.toml  existing
craft_suite_api/openapi_execution.py  existing
```

## Phase 0: Research

No unknowns. Each row names the code it touches.

## Phase 1: Design

### Implementation units

- `craft_suite_api/openapi_schema.py`: captured contract and bounded validation.
- `craft_suite_api/openapi_parameters.py`: declared path/query/header serialization.
- `craft_suite_api/openapi_client.py`: origin, permission and HTTP dispatch policy.
- `craft_suite_api/openapi_responses.py`: bounded response reading and decoding.
- `craft_suite_api/openapi_runtime.py`: native MCP routing and confirmation.

### Interfaces and live integration path

`craft_suite_api/mcp_server.py` exposes `build_server` and the console entry point.
`get_mcp_instance` calls `create_mcp_server`, `register_tool_surface`, and the package tool registrars.
`craft_suite_api/mcp/__init__.py` routes selected operations through `get_client` and the API client.
`craft_suite_api/auth.py` resolves references only when a caller requests a client.
`craft_suite_api/openapi_client.py` enforces transport and response limits before returning external data.
Graph ingestion is withheld until a tenant/source-scoped mapping and complete receipt contract have been reviewed.
The SDK owns engine transport and durable checkpoints.

### Content and contracts

The server serves package prompts, skills, ontology, and `connector_manifest.yml` through native MCP primitives.
The schema generator reads `tools/list` without invoking vendor operations.
It records both input and output schemas. Empty source presets declare no extraction integration.
Native content listing acceptance remains pending until a connector-owned test exercises the production server.

### Dependencies and decisions

No additional capability prerequisite has been established in this starter repository.
The SDK reference records a source dependency; it does not create a cross-repository delivery prerequisite.
Reviewers must add `Depends-on:` declarations only for confirmed prerequisite requirements.
Each source mapping must match the connector's actual external data before ingestion is enabled.

### Quality and release gates

Run `python scripts/check_connector_contract.py . --package craft_suite_api`.
Run `python scripts/generate_tool_schemas.py --check` and `python -m pytest tests -q`.
Run the pinned pre-commit and pre-push gates with the approved scanner toolchain.
The published site must pass the shared readiness checks and render canonical spec records.
Source tests do not authorize release, deployment, or external effects.

### Risks and alternatives

Starter operations and mappings require external-system validation before production use.
Missing credentials, rejected source observations, and failed transport checks must propagate as explicit failures.
Duplicating shared SDK or pipeline logic would create conflicting owners.

## Phase 2: Task approach

`tasks.md` holds one task line per row, producer first.

## Complexity Tracking

None. The constitution check passed.

## Build contract

The repository pre-commit hooks apply: `spec-standard`, `spec-status`, `ruff-format`. Each row names its proving test. No suppression and no duplicate implementation.

## Production caller chain

1. `CONN-CRAFT-SUITE-API-R001`: an MCP tool call reaches `get_client` in `craft_suite_api/auth.py`, which calls `_build_client` and then `_reference_auth` to turn the configured credential reference into SDK auth before the first request.
2. `CONN-CRAFT-SUITE-API-R002`: a write or read tool calls `OpenApiClient.execute` in `craft_suite_api/openapi_client.py`, which calls `_authorize` and then `_send`.
3. `CONN-CRAFT-SUITE-API-R003`: the `scion_sdk.connector` entry point calls `get_mcp_instance` in `craft_suite_api/mcp_server.py`, which calls the SDK `build_server`, which calls each `register_<domain>_tools` registrar in `craft_suite_api/mcp/__init__.py`.
4. `CONN-CRAFT-SUITE-API-R004`: the SDK `build_server` called from `get_mcp_instance` in `craft_suite_api/mcp_server.py` serves the packaged `skills/`, `ontology/` and `prompts/` directories with no content argument.
5. `CONN-CRAFT-SUITE-API-R005`: no tool or entry point reaches an ingestion path, because `craft_suite_api.kg_ingest` and `craft_suite_api.api.api_client_base` are absent from the package.
6. `CONN-CRAFT-SUITE-API-R006`: an MCP client calls a write tool, `OpenApiTool.run` in `craft_suite_api/openapi_runtime.py` calls `confirm_write` in `craft_suite_api/openapi_execution.py`, which calls the SDK `ctx_confirm_destructive` before any outbound request.

## Cross-repo seams

none

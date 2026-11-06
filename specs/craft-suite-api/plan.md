# CONN-CRAFT-SUITE-API — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

The connector serves every backend API operation as one typed tool. The backend publishes an API description and no MCP server, so the framework's OpenAPI provider generates the tools from a pinned, normalized copy of that description: no operation is written by hand. A governance middleware on the mounted sub-server refuses calls with typed results, confirms writes and audits them. The SDK owns HTTP, credential references, TLS and confirmation. Ingestion is unavailable in this version. The [architecture page](../../docs/architecture.md) shows the active request path. Research: [research.md](research.md).

## Technical Context

- **Language/Version**: Python 3.14 (floor 3.12)
- **Primary Dependencies**: scion-sdk, fastmcp
- **Storage**: N/A; the connector stores nothing
- **Testing**: pytest; the proof level each row names
- **Target Platform**: Linux containers
- **Project Type**: connector (MCP server)
- **Performance Goals**: one read in under one second, excluding backend latency (R009)
- **Constraints**: one tool per API operation; shared capabilities come from the SDK
- **Scale/Scope**: 9 rows; 268 backend operations

## Constitution Check

- One owner per concept: pass. The connector owns one external system's calls, mappings and tools only.
- Connectors depend on the SDK and are called through arbora: pass.
- No ratchets: pass. The rows add no suppression.
- Hard cutover: pass. The hand-reviewed nine-operation contract and its runtime are removed in the same change.

## Project Structure

```text
api-spec/backend.openapi.json  new (pinned published description)
api-spec/backend.source.json  new (url, sha256, licence note)
scripts/generate_backend_tools.py  new
craft_suite_api/backend_openapi.json  new (generated)
craft_suite_api/backend.py  new
craft_suite_api/auth.py  existing
craft_suite_api/mcp/__init__.py  existing
craft_suite_api/mcp_server.py  existing
pyproject.toml  existing
```

## Phase 0: Research

See [research.md](research.md): the operation counts, the licences, the absence of a backend MCP server and the defects in the published description.

## Phase 1: Design

### Implementation units

- `scripts/generate_backend_tools.py`: sha256 check and deterministic repair of the description.
- `craft_suite_api/backend.py`: the provider, the name map, the governance middleware and the audit log.
- `craft_suite_api/auth.py`: the governed async client, the credential reference and the response bound.
- `craft_suite_api/mcp/__init__.py`: the one registrar that mounts the backend sub-server.

### Interfaces and live integration path

`craft_suite_api/mcp_server.py` exposes `build_server` and the console entry point.
`register_backend_tools` builds the client and mounts `build_backend_server` under the `craft_suite` namespace.
`BackendGovernance.on_call_tool` decides every call before the provider sends it.
Graph ingestion is withheld until a tenant/source-scoped mapping and complete receipt contract have been reviewed.

### Content and contracts

The server serves package prompts, skills, ontology, and `connector_manifest.yml` through native MCP primitives.
`backend_openapi.json` ships as package data. `scripts/generate_backend_tools.py --check` fails on a stale copy.

### Dependencies and decisions

- Decision: generate from the description with the framework's OpenAPI provider. The backend has no MCP server to mount. Hand-written tools would duplicate the description.
- Decision: repair the description at build time, deterministically, and keep the pinned original byte for byte. A new upstream copy is a new sha256 and a regenerated file.
- Decision: govern on a mounted sub-server, so the middleware never sees app upstream calls.
- Decision: every non-GET operation is a write. Generation, upload, account and moderation are classes of write that the refusal and the audit record name.
- Decision: the former nine reviewed reads remain as generated tools with the same names, and nothing else of the reviewed contract is kept.

### Quality and release gates

Run `python scripts/check_connector_contract.py . --package craft_suite_api`.
Run `python scripts/generate_backend_tools.py --check` and `python -m pytest tests -q`.
Run the pinned pre-commit and pre-push gates with the approved scanner toolchain.
Source tests do not authorize release, deployment, or external effects.

### Risks and alternatives

- Writes are proven against a fake transport. Live writes need the operator switch and a credential.
- A future upstream description can add or rename operations. The coverage test counts against the generated document, so a regeneration moves both.

## Phase 2: Task approach

`tasks.md` holds one task line per row, producer first.

## Complexity Tracking

None. The constitution check passed.

## Build contract

The repository pre-commit hooks apply: `spec-standard`, `spec-status`, `ruff-format`, `content-drift`, `backend-tools-drift`. Each row names its proving test. No suppression and no duplicate implementation.

## Production caller chain

1. `CONN-CRAFT-SUITE-API-R001`: `register_backend_tools` calls `build_client` in `craft_suite_api/auth.py`, which calls `_auth` to turn the credential reference into SDK auth.
2. `CONN-CRAFT-SUITE-API-R002`: every backend request goes through the client from `build_client`, bounded by `_check_origin`, the SDK transport and `bound_response`.
3. `CONN-CRAFT-SUITE-API-R003`: the `scion_sdk.connector` entry point calls `get_mcp_instance`, the SDK `build_server` and `register_backend_tools`, which mounts `build_backend_server`.
4. `CONN-CRAFT-SUITE-API-R004`: the SDK `build_server` serves the packaged `skills/`, `ontology/` and `prompts/` directories with no content argument.
5. `CONN-CRAFT-SUITE-API-R005`: no tool or entry point reaches an ingestion path, because `craft_suite_api.kg_ingest` and `craft_suite_api.api` are absent from the package.
6. `CONN-CRAFT-SUITE-API-R006`: a write call reaches `BackendGovernance._write`, which calls the SDK `ctx_confirm_destructive` before the request is sent.
7. `CONN-CRAFT-SUITE-API-R007`: `build_backend_server` passes `backend_openapi.json` and `tool_names` to the OpenAPI provider.
8. `CONN-CRAFT-SUITE-API-R008`: `BackendGovernance.on_call_tool` refuses, confirms, decodes upload parts and audits.
9. `CONN-CRAFT-SUITE-API-R009`: a read passes `on_call_tool` untouched and the provider sends it once.

## Cross-repo seams

none

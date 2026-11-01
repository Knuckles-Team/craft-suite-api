# CONN-CRAFT-SUITE-API — ArtCraft connector

## Outcome

The connector must expose reviewed external-system operations through one governed integration boundary.
The connector must preserve credential, transport, source, and content contracts.

## Scope and owner

The `craft-suite-api` repository owns external-system operations and source mappings.
The shared connector SDK owns reusable transport, authentication, MCP, and ingest contracts.
The shared pipelines repository owns quality gates and delivery rendering.

Component: Connector integration
References: [Connector SDK](https://github.com/Knuckles-Team/scion-sdk/blob/5babc4cc48ad73928468b243842f219f51e2cca1/README.md)
Code: ../../craft_suite_api/auth.py ../../craft_suite_api/openapi_client.py ../../craft_suite_api/openapi_runtime.py ../../craft_suite_api/mcp_server.py ../../craft_suite_api/mcp/__init__.py ../../tests/test_auth.py ../../tests/test_api_wrapper.py ../../tests/test_artcraft_mcp_validation.py ../../scripts/generate_tool_schemas.py

## Non-goals

This specification grants no service access, credential creation, deployment, or approval exception.
The connector must not implement a graph engine, independent policy authority, or duplicate SDK runtime.

## Why a new spec

The scaffold emits the repository's first capability specification.
No existing specification occurs in this newly generated source tree.
An existing repository must reconcile this capability with its current owner before adopting the generated files.

## Requirements

See [requirements.md](requirements.md), [plan.md](plan.md), and [test-spec.md](test-spec.md).
Existing test references identify verification targets. They do not establish delivery.

## Scope and interfaces

In scope: the rows of [requirements.md](requirements.md). Out of scope: the SDK modules and the engine, which own the shared capabilities.

## User Scenarios & Testing

### User Story 1 - ArtCraft connector (Priority: P1)

The connector must expose reviewed external-system operations through one governed integration boundary.

**Acceptance Scenarios**:

1. **Given** the connector is configured, **When** the behaviour of row `CONN-CRAFT-SUITE-API-R001` (credential references) is exercised, **Then** `tests/test_auth.py::test_client_resolves_reference_and_cleans_up` must observe reference resolution and resource cleanup.
2. **Given** the connector is configured, **When** the behaviour of row `CONN-CRAFT-SUITE-API-R002` (bounded api requests) is exercised, **Then** `tests/test_api_wrapper.py::test_oversized_response_rejected`, `::test_redirect_not_followed`, `::test_response_deadline_enforced` and `::test_invalid_provider_origin_rejected` must exercise oversized responses, redirects, deadlines and rejected origins through the real client.
3. **Given** the connector is configured, **When** the behaviour of row `CONN-CRAFT-SUITE-API-R003` (mcp registration) is exercised, **Then** `tests/test_artcraft_mcp_validation.py::test_mcp_instance_registration` must construct the production server without vendor requests.

### Edge Cases

- If `CONN-CRAFT-SUITE-API-R001` is not met, its proving test fails: credential references.
- If `CONN-CRAFT-SUITE-API-R002` is not met, its proving test fails: bounded api requests.
- If `CONN-CRAFT-SUITE-API-R003` is not met, its proving test fails: mcp registration.

## Requirements

- **FR-001**: Credential references. Rows: `CONN-CRAFT-SUITE-API-R001`.
- **FR-002**: Bounded API requests. Rows: `CONN-CRAFT-SUITE-API-R002`.
- **FR-003**: MCP registration. Rows: `CONN-CRAFT-SUITE-API-R003`.
- **FR-004**: Native content contracts. Rows: `CONN-CRAFT-SUITE-API-R004`.
- **FR-005**: Withhold unscoped ingestion. Rows: `CONN-CRAFT-SUITE-API-R005`.
- **FR-006**: Destructive-write confirmation. Rows: `CONN-CRAFT-SUITE-API-R006`.

## Success Criteria

- **SC-001**: `tests/test_auth.py::test_client_resolves_reference_and_cleans_up` must observe reference resolution and resource cleanup. Rows: `CONN-CRAFT-SUITE-API-R001`.
- **SC-002**: `tests/test_api_wrapper.py::test_oversized_response_rejected`, `::test_redirect_not_followed`, `::test_response_deadline_enforced` and `::test_invalid_provider_origin_rejected` must exercise oversized responses, redirects, deadlines and rejected origins through the real client. Rows: `CONN-CRAFT-SUITE-API-R002`.
- **SC-003**: `tests/test_artcraft_mcp_validation.py::test_mcp_instance_registration` must construct the production server without vendor requests. Rows: `CONN-CRAFT-SUITE-API-R003`.
- **SC-004**: `tests/test_default_content_surfaces.py::test_default_content_surfaces` and `tests/test_source_contract.py::test_served_prompts_match_admitted_capabilities` must list the packaged skills, ontology and prompts through the production server. Rows: `CONN-CRAFT-SUITE-API-R004`.
- **SC-005**: `tests/test_source_contract.py::test_unscoped_ingestion_is_unavailable` must reject import of the removed ingestion starter. Rows: `CONN-CRAFT-SUITE-API-R005`.
- **SC-006**: `tests/test_destructive_confirmation_transports.py::test_stdio_no_auth_destructive_call`, `::test_http_no_auth_localhost_destructive_call` and `::test_http_jwt_destructive_call` must show that a client without elicitation is refused with no upstream write until `confirm=true`, and that an eliciting client is asked and then writes. Rows: `CONN-CRAFT-SUITE-API-R006`.

## Assumptions

- The external system is reachable with operator-supplied credentials.
- The SDK and engine contracts the rows cite are at the floors declared in `pyproject.toml`.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-CRAFT-SUITE-API-R001` | [plan.md](plan.md) | T-001 | [test-spec.md](test-spec.md) |
| FR-002 | `CONN-CRAFT-SUITE-API-R002` | [plan.md](plan.md) | T-002 | [test-spec.md](test-spec.md) |
| FR-003 | `CONN-CRAFT-SUITE-API-R003` | [plan.md](plan.md) | T-003 | [test-spec.md](test-spec.md) |
| FR-004 | `CONN-CRAFT-SUITE-API-R004` | [plan.md](plan.md) | T-004 | [test-spec.md](test-spec.md) |
| FR-005 | `CONN-CRAFT-SUITE-API-R005` | [plan.md](plan.md) | T-005 | [test-spec.md](test-spec.md) |
| FR-006 | `CONN-CRAFT-SUITE-API-R006` | [plan.md](plan.md) | T-006 | [test-spec.md](test-spec.md) |

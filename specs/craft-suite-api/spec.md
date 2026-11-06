# CONN-CRAFT-SUITE-API — ArtCraft connector

## Outcome

The connector must expose every backend API operation as one typed tool through one governed integration boundary.
The connector must preserve credential, transport, source, and content contracts.

## Scope and owner

The `craft-suite-api` repository owns external-system operations and source mappings.
The shared connector SDK owns reusable transport, authentication, MCP, and ingest contracts.
The shared pipelines repository owns quality gates and delivery rendering.

Component: Connector integration
References: [Connector SDK](https://github.com/Knuckles-Team/scion-sdk/blob/5babc4cc48ad73928468b243842f219f51e2cca1/README.md)
Code: ../../craft_suite_api/auth.py ../../craft_suite_api/backend.py ../../craft_suite_api/backend_openapi.json ../../craft_suite_api/mcp_server.py ../../craft_suite_api/mcp/__init__.py ../../scripts/generate_backend_tools.py ../../api-spec/backend.source.json ../../tests/test_auth.py ../../tests/test_api_wrapper.py ../../tests/test_artcraft_mcp_validation.py ../../tests/test_backend_tools.py

## Non-goals

This specification grants no service access, credential creation, deployment, or approval exception.
The connector must not implement a graph engine, independent policy authority, or duplicate SDK runtime.

## Why a new spec

The scaffold emits the repository's first capability specification.
No existing specification occurs in this newly generated source tree.
An existing repository must reconcile this capability with its current owner before adopting the generated files.

## Requirements

See [requirements.md](requirements.md), [plan.md](plan.md), [research.md](research.md), and [test-spec.md](test-spec.md).
Existing test references identify verification targets. They do not establish delivery.

## Scope and interfaces

In scope: the rows of [requirements.md](requirements.md). Out of scope: the SDK modules and the engine, which own the shared capabilities.

## User Scenarios & Testing

### User Story 1 - ArtCraft connector (Priority: P1)

The connector must expose every backend API operation as one typed tool through one governed integration boundary.

**Acceptance Scenarios**:

1. **Given** the connector is configured, **When** the behaviour of row `CONN-CRAFT-SUITE-API-R001` (credential references) is exercised, **Then** `tests/test_auth.py::test_client_resolves_reference_and_cleans_up` must observe reference resolution and resource cleanup.
2. **Given** the connector is configured, **When** the behaviour of row `CONN-CRAFT-SUITE-API-R002` (bounded api requests) is exercised, **Then** `tests/test_api_wrapper.py::test_oversized_response_rejected`, `::test_redirect_not_followed`, `::test_response_deadline_enforced` and `::test_invalid_provider_origin_rejected` must exercise oversized responses, redirects, deadlines and rejected origins through the real client.
3. **Given** the connector is configured, **When** the behaviour of row `CONN-CRAFT-SUITE-API-R003` (mcp registration) is exercised, **Then** `tests/test_artcraft_mcp_validation.py::test_mcp_instance_registration` must construct the production server without vendor requests and list one `craft_suite_` tool per backend operation plus the registry tools.
4. **Given** the pinned backend description, **When** the behaviour of row `CONN-CRAFT-SUITE-API-R007` (every backend operation as one typed tool) is exercised, **Then** `tests/test_backend_tools.py::test_every_operation_is_one_typed_tool` must list at least one typed tool per operation.
5. **Given** a write tool, **When** the behaviour of row `CONN-CRAFT-SUITE-API-R008` (governed writes) is exercised, **Then** `tests/test_backend_tools.py::test_writes_disabled_refuse_typed_and_audit` must see a typed refusal and an audit record, with no request sent.
6. **Given** a configured backend, **When** the behaviour of row `CONN-CRAFT-SUITE-API-R009` (hot-path proof) is exercised, **Then** `tests/test_backend_tools.py::test_hot_path_read_reaches_the_exact_route_with_the_session` must observe one request to the exact route in under one second.

### Edge Cases

- If `CONN-CRAFT-SUITE-API-R001` is not met, its proving test fails: credential references.
- If `CONN-CRAFT-SUITE-API-R002` is not met, its proving test fails: bounded api requests.
- If `CONN-CRAFT-SUITE-API-R003` is not met, its proving test fails: mcp registration.
- If `CONN-CRAFT-SUITE-API-R007` is not met, its proving test fails: an operation without a typed tool.
- If `CONN-CRAFT-SUITE-API-R008` is not met, its proving test fails: an ungoverned write.
- If `CONN-CRAFT-SUITE-API-R009` is not met, its proving test fails: a slow or misrouted read.

## Requirements

- **FR-001**: Credential references. Rows: `CONN-CRAFT-SUITE-API-R001`.
- **FR-002**: Bounded API requests. Rows: `CONN-CRAFT-SUITE-API-R002`.
- **FR-003**: MCP registration. Rows: `CONN-CRAFT-SUITE-API-R003`.
- **FR-004**: Native content contracts. Rows: `CONN-CRAFT-SUITE-API-R004`.
- **FR-005**: Withhold unscoped ingestion. Rows: `CONN-CRAFT-SUITE-API-R005`.
- **FR-006**: Destructive-write confirmation. Rows: `CONN-CRAFT-SUITE-API-R006`.
- **FR-007**: Every backend operation as one typed tool. Rows: `CONN-CRAFT-SUITE-API-R007`.
- **FR-008**: Governed writes with typed refusals and audit. Rows: `CONN-CRAFT-SUITE-API-R008`.
- **FR-009**: Hot-path proof. Rows: `CONN-CRAFT-SUITE-API-R009`.

## Success Criteria

- **SC-001**: `tests/test_auth.py::test_client_resolves_reference_and_cleans_up` must observe reference resolution and resource cleanup. Rows: `CONN-CRAFT-SUITE-API-R001`.
- **SC-002**: `tests/test_api_wrapper.py::test_oversized_response_rejected`, `::test_redirect_not_followed`, `::test_response_deadline_enforced` and `::test_invalid_provider_origin_rejected` must exercise oversized responses, redirects, deadlines and rejected origins through the real client. Rows: `CONN-CRAFT-SUITE-API-R002`.
- **SC-003**: `tests/test_artcraft_mcp_validation.py::test_mcp_instance_registration` must construct the production server without vendor requests and list one `craft_suite_` tool per backend operation plus the registry tools. Rows: `CONN-CRAFT-SUITE-API-R003`.
- **SC-004**: `tests/test_default_content_surfaces.py::test_default_content_surfaces` and `tests/test_source_contract.py::test_served_prompts_match_admitted_capabilities` must list the packaged skills, ontology and prompts through the production server. Rows: `CONN-CRAFT-SUITE-API-R004`.
- **SC-005**: `tests/test_source_contract.py::test_unscoped_ingestion_is_unavailable` must reject import of the removed ingestion starter. Rows: `CONN-CRAFT-SUITE-API-R005`.
- **SC-006**: `tests/test_destructive_confirmation_transports.py::test_stdio_no_auth_destructive_call`, `::test_http_no_auth_localhost_destructive_call` and `::test_http_jwt_destructive_call` must show that a client without elicitation is refused with no upstream write until `confirm=true`, and that an eliciting client is asked and then writes. Rows: `CONN-CRAFT-SUITE-API-R006`.
- **SC-007**: `tests/test_backend_tools.py::test_every_operation_is_one_typed_tool` must list at least 268 typed tools, one per operation. Rows: `CONN-CRAFT-SUITE-API-R007`.
- **SC-008**: `tests/test_backend_tools.py::test_writes_disabled_refuse_typed_and_audit` and `::test_unconfirmed_write_is_refused_then_confirm_sends` must show typed refusals, audit records and no request before confirmation. Rows: `CONN-CRAFT-SUITE-API-R008`.
- **SC-009**: `tests/test_backend_tools.py::test_hot_path_read_reaches_the_exact_route_with_the_session` must finish one read in under one second. Rows: `CONN-CRAFT-SUITE-API-R009`.

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
| FR-007 | `CONN-CRAFT-SUITE-API-R007` | [plan.md](plan.md) | T-007 | [test-spec.md](test-spec.md) |
| FR-008 | `CONN-CRAFT-SUITE-API-R008` | [plan.md](plan.md) | T-008 | [test-spec.md](test-spec.md) |
| FR-009 | `CONN-CRAFT-SUITE-API-R009` | [plan.md](plan.md) | T-009 | [test-spec.md](test-spec.md) |

# CONN-CRAFT-SUITE-API — Verification plan

Governing specification: [spec.md](spec.md).

These acceptance targets require connector-specific execution and review.
Test names describe source mappings, not successful runs or delivery receipts.
Native content listing needs a connector-owned integration test before the content requirement is delivered.

| Requirement | Verification target |
|---|---|
| `CONN-CRAFT-SUITE-API-R001` | `tests/test_auth.py::test_client_resolves_reference_and_cleans_up` must observe reference resolution and resource cleanup. |
| `CONN-CRAFT-SUITE-API-R002` | `tests/test_api_wrapper.py::test_oversized_response_rejected`, `::test_redirect_not_followed`, `::test_response_deadline_enforced` and `::test_invalid_provider_origin_rejected` must exercise oversized responses, redirects, deadlines and rejected origins through the real client. |
| `CONN-CRAFT-SUITE-API-R003` | `tests/test_artcraft_mcp_validation.py::test_mcp_instance_registration` must construct the production server without vendor requests. |
| `CONN-CRAFT-SUITE-API-R004` | `tests/test_default_content_surfaces.py::test_default_content_surfaces` and `tests/test_source_contract.py::test_served_prompts_match_admitted_capabilities` must list the packaged skills, ontology and prompts through the production server. |
| `CONN-CRAFT-SUITE-API-R005` | `tests/test_source_contract.py::test_unscoped_ingestion_is_unavailable` must reject import of the removed ingestion starter. |
| `CONN-CRAFT-SUITE-API-R006` | `tests/test_destructive_confirmation_transports.py::test_stdio_no_auth_destructive_call`, `::test_http_no_auth_localhost_destructive_call` and `::test_http_jwt_destructive_call` must show that a client without elicitation is refused with no upstream write until `confirm=true`, and that an eliciting client is asked and then writes. |
| `CONN-CRAFT-SUITE-API-R007` | `tests/test_generated_routes.py::test_one_tool_per_reviewed_operation` must compare the served `tools/list` with the operation list of the description. |
| `CONN-CRAFT-SUITE-API-R008` | `tests/test_generated_routes.py::test_generation_upload_and_asset_routes_are_tools` must find a tool for each named route group. |
| `CONN-CRAFT-SUITE-API-R009` | `tests/test_generated_routes.py::test_generated_writes_require_confirmation_and_refuse_typed` must call one generated write unconfirmed and one with an unset provider. |
| `CONN-CRAFT-SUITE-API-R010` | `tests/test_generated_routes.py::test_coverage_gate_reports_missing_and_extra_operations` must run the gate against a description with one operation removed. |
| `CONN-CRAFT-SUITE-API-R011` | `tests/test_generated_routes.py::test_first_tools_list_is_registry_only_and_domains_activate_alone` must observe the initial list and one domain activation. |
| `CONN-CRAFT-SUITE-API-R012` | `tests/test_generated_routes.py::test_generate_list_and_retrieve_asset_over_the_served_connector` must pass against the fixture backend. |

The owner must retain failure evidence and use canonical lifecycle tooling to regenerate `status.json`.

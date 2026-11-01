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

The owner must retain failure evidence and use canonical lifecycle tooling to regenerate `status.json`.

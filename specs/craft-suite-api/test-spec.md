# CONN-CRAFT-SUITE-API — Verification plan

Governing specification: [spec.md](spec.md).

These acceptance targets require connector-specific execution and review.
Test names describe source mappings, not successful runs or delivery receipts.
Native content listing needs a connector-owned integration test before the content requirement is delivered.

| Requirement | Verification target |
|---|---|
| `CONN-CRAFT-SUITE-API-R001` | `tests/test_auth.py::test_client_resolves_reference_and_cleans_up` must observe the resolved `session` header, a redacted auth repr and the cleanup on close. |
| `CONN-CRAFT-SUITE-API-R002` | `tests/test_api_wrapper.py::test_oversized_response_rejected`, `::test_redirect_not_followed`, `::test_response_deadline_enforced` and `::test_invalid_provider_origin_rejected` must exercise oversized responses, redirects, deadlines and rejected origins through the real client. |
| `CONN-CRAFT-SUITE-API-R003` | `tests/test_artcraft_mcp_validation.py::test_mcp_instance_registration` must construct the production server without vendor requests and list one `craft_suite_` tool per backend operation plus the registry tools. |
| `CONN-CRAFT-SUITE-API-R004` | `tests/test_default_content_surfaces.py::test_default_content_surfaces` and `tests/test_source_contract.py::test_served_prompts_match_admitted_capabilities` must list the packaged skills, ontology and prompts through the production server. |
| `CONN-CRAFT-SUITE-API-R005` | `tests/test_source_contract.py::test_unscoped_ingestion_is_unavailable` must reject import of the removed ingestion starter. |
| `CONN-CRAFT-SUITE-API-R006` | `tests/test_destructive_confirmation_transports.py::test_stdio_no_auth_destructive_call`, `::test_http_no_auth_localhost_destructive_call` and `::test_http_jwt_destructive_call` must show that a client without elicitation is refused with no upstream write until `confirm=true`, and that an eliciting client is asked and then writes. |
| `CONN-CRAFT-SUITE-API-R007` | `tests/test_backend_tools.py::test_every_operation_is_one_typed_tool` must list at least `operation_count()` tools (268 or more) with unique names of 64 characters or fewer, a typed schema for every property, an output schema, and a `confirm` input on writes only; `::test_generated_document_is_current_and_pinned` must pass the generator check. |
| `CONN-CRAFT-SUITE-API-R008` | `tests/test_backend_tools.py::test_unconfigured_backend_refuses_typed`, `::test_writes_disabled_refuse_typed_and_audit`, `::test_unconfirmed_write_is_refused_then_confirm_sends` and `::test_upload_sends_the_decoded_file_as_a_binary_part` must show typed refusals for generation, upload and account writes, audit records, no request before confirmation, and the decoded file bytes in the multipart request. |
| `CONN-CRAFT-SUITE-API-R009` | `tests/test_backend_tools.py::test_hot_path_read_reaches_the_exact_route_with_the_session` must observe one request to `/v1/tags/list` with the `session` header and a structured result equal to the response, in under one second. |

The owner must retain failure evidence and use canonical lifecycle tooling to regenerate `status.json`.

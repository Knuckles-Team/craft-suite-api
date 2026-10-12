# CONN-ARTCRAFT-API — Verification plan

Governing specification: [spec.md](spec.md).

These acceptance targets require connector-specific execution and review.
Test names describe source mappings, not successful runs or delivery receipts.
Native content listing needs a connector-owned integration test before the content requirement is delivered.

| Requirement | Verification target |
|---|---|
| `CONN-ARTCRAFT-API-R001` | `tests/test_auth.py::test_client_resolves_reference_and_cleans_up` must observe reference resolution and resource cleanup. |
| `CONN-ARTCRAFT-API-R002` | `tests/test_api_wrapper.py` must exercise rejected origins, redirects, deadlines, and oversized responses through the real client. |
| `CONN-ARTCRAFT-API-R003` | `tests/test_artcraft_mcp_validation.py::test_mcp_instance_registration` must construct the production server without vendor requests. |
| `CONN-ARTCRAFT-API-R004` | `scripts/generate_tool_schemas.py --check` must validate live tool contracts. Native content listing verification remains required before delivery. |
| `CONN-ARTCRAFT-API-R005` | `tests/test_source_contract.py::test_unscoped_ingestion_is_unavailable` must reject import of the removed ingestion starter. |

The owner must retain failure evidence and use canonical lifecycle tooling to regenerate `status.json`.

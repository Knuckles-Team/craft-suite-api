# CONN-ARTCRAFT-API — Implementation tasks

Governing specification: [spec.md](spec.md).

The owner must reconcile starter behavior with the external system before completing these tasks.

- [ ] `CONN-ARTCRAFT-API-R001` — Implement credential references. `tests/test_auth.py::test_client_resolves_reference_and_cleans_up` must observe reference resolution and resource cleanup.
- [ ] `CONN-ARTCRAFT-API-R002` — Implement bounded api requests. `tests/test_api_wrapper.py` must exercise rejected origins, redirects, deadlines, and oversized responses through the real client.
- [ ] `CONN-ARTCRAFT-API-R003` — Implement mcp registration. `tests/test_artcraft_mcp_validation.py::test_mcp_instance_registration` must construct the production server without vendor requests.
- [ ] `CONN-ARTCRAFT-API-R004` — Implement native content contracts. `scripts/generate_tool_schemas.py --check` must validate live tool contracts. Native content listing verification remains required before delivery.
- [ ] `CONN-ARTCRAFT-API-R005` — Keep unscoped ingestion unavailable until a separate scoped design is accepted. `tests/test_source_contract.py::test_unscoped_ingestion_is_unavailable` must reject import of the removed ingestion starter.

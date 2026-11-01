# CONN-CRAFT-SUITE-API — Implementation tasks

Governing specification: [spec.md](spec.md).

The owner must reconcile starter behavior with the external system before completing these tasks.

- [ ] T001 [P] [US1] CONN-CRAFT-SUITE-API-R001 Implement credential references. `tests/test_auth.py::test_client_resolves_reference_and_cleans_up` must observe reference resolution and resource cleanup.
- [ ] T002 [P] [US1] CONN-CRAFT-SUITE-API-R002 Implement bounded api requests. `tests/test_api_wrapper.py` must exercise rejected origins, redirects, deadlines, and oversized responses through the real client.
- [ ] T003 [P] [US1] CONN-CRAFT-SUITE-API-R003 Implement mcp registration. `tests/test_artcraft_mcp_validation.py::test_mcp_instance_registration` must construct the production server without vendor requests.
- [ ] T004 [P] [US1] CONN-CRAFT-SUITE-API-R004 Implement native content contracts. `scripts/generate_tool_schemas.py --check` must validate live tool contracts. Native content listing verification remains required before delivery.
- [ ] T005 [P] [US1] CONN-CRAFT-SUITE-API-R005 Keep unscoped ingestion unavailable until a separate scoped design is accepted. `tests/test_source_contract.py::test_unscoped_ingestion_is_unavailable` must reject import of the removed ingestion starter.
- [ ] T006 [P] [US1] CONN-CRAFT-SUITE-API-R006 Implement destructive-write confirmation. `tests/test_destructive_confirmation_transports.py` must show, over stdio, unauthenticated HTTP, and JWT HTTP, that a client without elicitation is refused with no upstream write until `confirm=true`, and that an eliciting client is asked and then writes.

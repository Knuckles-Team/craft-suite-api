# CONN-CRAFT-SUITE-API — Requirements

Governing specification: [spec.md](spec.md).

Each row identifies one connector behavior and its verification target.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-CRAFT-SUITE-API-R001` | **Credential references.** The connector must resolve authorized credential references in `craft_suite_api/auth.py` when a client is requested. | `tests/test_auth.py::test_client_resolves_reference_and_cleans_up` must observe reference resolution and resource cleanup. |
| `CONN-CRAFT-SUITE-API-R002` | **Bounded API requests.** The connector must enforce origin, TLS, timeout, and response-size limits in `craft_suite_api/openapi_client.py`. | `tests/test_api_wrapper.py` must exercise rejected origins, redirects, deadlines, and oversized responses through the real client. |
| `CONN-CRAFT-SUITE-API-R003` | **MCP registration.** The connector must register its operation router through `craft_suite_api/mcp_server.py` and `craft_suite_api/mcp/__init__.py`. | `tests/test_artcraft_mcp_validation.py::test_mcp_instance_registration` must construct the production server without vendor requests. |
| `CONN-CRAFT-SUITE-API-R004` | **Native content contracts.** The connector must publish packaged prompts, skills, ontology, and its manifest through `craft_suite_api/mcp_server.py`. | `scripts/generate_tool_schemas.py --check` must validate live tool contracts. Native content listing verification remains required before delivery. |
| `CONN-CRAFT-SUITE-API-R005` | **Withhold unscoped ingestion.** The connector must not expose generic ingestion before a tenant/source-scoped ArtCraft mapping and complete receipt contract exist. | `tests/test_source_contract.py::test_unscoped_ingestion_is_unavailable` must reject import of the removed ingestion starter. |

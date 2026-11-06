# CONN-CRAFT-SUITE-API quickstart

Run the proof of each row from a fresh checkout after `uv sync`.

- CONN-CRAFT-SUITE-API-R001: `uv run pytest tests/test_auth.py::test_client_resolves_reference_and_cleans_up -q`
- CONN-CRAFT-SUITE-API-R002: `uv run pytest tests/test_api_wrapper.py -q`
- CONN-CRAFT-SUITE-API-R003: `uv run pytest tests/test_artcraft_mcp_validation.py::test_mcp_instance_registration -q`
- CONN-CRAFT-SUITE-API-R004: `uv run pytest tests/test_default_content_surfaces.py::test_default_content_surfaces -q`
- CONN-CRAFT-SUITE-API-R005: `uv run pytest tests/test_source_contract.py::test_unscoped_ingestion_is_unavailable -q`
- CONN-CRAFT-SUITE-API-R006: `uv run pytest tests/test_destructive_confirmation_transports.py -q`
- CONN-CRAFT-SUITE-API-R007: `uv run pytest tests/test_backend_tools.py::test_every_operation_is_one_typed_tool -q`
- CONN-CRAFT-SUITE-API-R008: `uv run pytest tests/test_backend_tools.py -k "refuse or unconfirmed or upload" -q`
- CONN-CRAFT-SUITE-API-R009: `uv run pytest tests/test_backend_tools.py::test_hot_path_read_reaches_the_exact_route_with_the_session -q`

Scenario: with `CRAFT_SUITE_API_BASE_URL` set, call `craft_suite_list_tags_handler` with no arguments; it returns the backend's tag page.

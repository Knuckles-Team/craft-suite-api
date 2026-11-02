# CONN-CRAFT-SUITE-API-APPS quickstart

Run the proof of each row from a fresh checkout after `uv sync`. Each command exercises the row through the production server.

- CONN-CRAFT-SUITE-API-APPS-R001: `uv run pytest tests/test_tier1_degrade.py::test_unconfigured_backend_lists_tools_and_refuses_typed -q`
- CONN-CRAFT-SUITE-API-APPS-R002: `uv run pytest tests/test_upstream_declarations.py::test_eleven_apps_declared_with_roots_fail_closed -q`
- CONN-CRAFT-SUITE-API-APPS-R003: `uv run pytest tests/test_probe_apps.py::test_probe_reports_declared_undeclared_and_missing -q`
- CONN-CRAFT-SUITE-API-APPS-R004: `uv run pytest tests/test_local_mode.py::test_missing_cli_marks_one_upstream_unavailable -q`
- CONN-CRAFT-SUITE-API-APPS-R005: `uv run pytest tests/test_remote_overlay.py::test_example_overlay_validates_and_switches_one_app_to_http -q`
- CONN-CRAFT-SUITE-API-APPS-R006: `uv run pytest tests/test_bridge_overlay.py::test_example_bridge_overlay_validates_and_remote_address_refuses -q`
- CONN-CRAFT-SUITE-API-APPS-R007: `uv run pytest tests/test_tool_budget.py::test_initial_list_is_tier1_plus_registry_only -q`
- CONN-CRAFT-SUITE-API-APPS-R008: `uv run pytest tests/test_phase4_gate.py::test_arbora_loads_and_unloads_one_app_group -q`
- CONN-CRAFT-SUITE-API-APPS-R009: `uv run pytest tests/test_phase1_gate.py::test_three_app_mvp_with_fixture_clis -q`
- CONN-CRAFT-SUITE-API-APPS-R010: `uv run pytest tests/test_phase2_gate.py::test_eleven_upstreams_isolated_failure_and_overlays -q`
- CONN-CRAFT-SUITE-API-APPS-R011: `uv run pytest tests/test_phase3_gate.py::test_all_apps_have_content_and_pack_imports_clean -q`
- CONN-CRAFT-SUITE-API-APPS-R012: `uv run pytest tests/test_phase4_gate.py::test_coverage_passes_and_pin_survives_restart -q`

The opt-in live smoke runs only on a host that has the app command-line programs: `CRAFT_SUITE_LIVE=1 uv run pytest tests/live -q`.

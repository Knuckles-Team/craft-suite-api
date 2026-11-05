# CONN-CRAFT-SUITE-API-APPS — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Proving test | Expected observation |
|---|---|---|---|
| T-001 | `CONN-CRAFT-SUITE-API-APPS-R001` | `tests/test_tier1_degrade.py::test_unconfigured_backend_lists_tools_and_refuses_typed` | With no base URL, `tools/list` holds the nine Tier 1 tools and a call returns `BACKEND_NOT_CONFIGURED`. |
| T-002 | `CONN-CRAFT-SUITE-API-APPS-R002` | `tests/test_upstream_declarations.py::test_eleven_apps_declared_with_roots_fail_closed` | Eleven declarations exist with unique namespaces. With both settings unset, each command line holds no root flag. With one read root set, each holds one read flag pair and no write flag, except `filmcraft` and `cadcraft`, whose command line is `<app>-cli mcp` with no root flag whatever the settings. |
| T-003 | `CONN-CRAFT-SUITE-API-APPS-R003` | `tests/test_probe_apps.py::test_probe_reports_declared_undeclared_and_missing` | A fixture CLI with `mcp` reports `exposes_mcp` true. A fixture without it reports `APP_NO_MCP`. An undeclared app that exposes `mcp` makes the exit code non-zero. |
| T-004 | `CONN-CRAFT-SUITE-API-APPS-R004` | `tests/test_local_mode.py::test_missing_cli_marks_one_upstream_unavailable` | With one app absent from `PATH`, activation of another app succeeds and `registry_status` shows the absent app as `unavailable` with `UPSTREAM_SPAWN_FAILED`. |
| T-005 | `CONN-CRAFT-SUITE-API-APPS-R005` | `tests/test_remote_overlay.py::test_example_overlay_validates_and_switches_one_app_to_http` | The example overlay validates. After the merge, one app is `http` and ten stay `stdio`. A literal credential in the overlay refuses with `UPSTREAM_SECRET_LITERAL`. |
| T-006 | `CONN-CRAFT-SUITE-API-APPS-R006` | `tests/test_bridge_overlay.py::test_example_bridge_overlay_validates_and_remote_address_refuses` | The example overlay validates. A non-loopback address refuses with `UPSTREAM_BRIDGE_NOT_LOOPBACK`. |
| T-007 | `CONN-CRAFT-SUITE-API-APPS-R007` | `tests/test_tool_budget.py::test_initial_list_is_tier1_plus_registry_only` | A fresh session lists exactly thirteen tools and starts no app process. After one activation it lists the thirteen plus that app's tools. |
| T-008 | `CONN-CRAFT-SUITE-API-APPS-R008` | `tests/test_phase4_gate.py::test_arbora_loads_and_unloads_one_app_group` | Against a loopback gateway, the catalog holds the facade's tools. Loading the group `photocraft` loads only photocraft tools. Unloading it leaves wordcraft loaded. |
| T-009 | `CONN-CRAFT-SUITE-API-APPS-R009` | `tests/test_phase1_gate.py::test_three_app_mvp_with_fixture_clis` | All five checks pass. The elicitation count equals one. |
| T-010 | `CONN-CRAFT-SUITE-API-APPS-R010` | `tests/test_phase2_gate.py::test_eleven_upstreams_isolated_failure_and_overlays` | A killed fixture app shows `unavailable` while ten stay callable. Both overlays validate. The drifted app shows `drifted`. |
| T-011 | `CONN-CRAFT-SUITE-API-APPS-R011` | `tests/test_phase3_gate.py::test_all_apps_have_content_and_pack_imports_clean` | Eleven ontologies, eleven skills and at least one prompt per app exist. The drift check passes. The pack import reports no orphan class. |
| T-012 | `CONN-CRAFT-SUITE-API-APPS-R012` | `tests/test_phase4_gate.py::test_coverage_passes_and_pin_survives_restart` | Strict status succeeds with the facade registered. After a gateway restart the pinned tool is still loaded. |
| T-013 | `CONN-CRAFT-SUITE-API-APPS-R013` | `tests/test_artifact_exchange.py::test_every_app_declares_the_exchange_binding` | All eleven declarations carry the binding with the four path arguments. |
| T-014 | `CONN-CRAFT-SUITE-API-APPS-R014` | `tests/test_artifact_exchange.py::test_example_exchange_file_validates_and_renders_app_folders` | The SDK parser accepts the example, and the `files` sink renders the app folder path. |
| T-015 | `CONN-CRAFT-SUITE-API-APPS-R015` | `tests/test_artifact_exchange.py::test_fixture_app_reads_exchange_input_and_publishes_output` | Both sinks hold the output, and the result holds one link. |
| T-016 | `CONN-CRAFT-SUITE-API-APPS-R016` | `tests/test_artifact_exchange.py::test_every_app_skill_states_input_forms_and_output_links` | Each skill states the input forms and the output rule. |

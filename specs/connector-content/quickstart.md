# CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT quickstart

Run the proof of each row from a fresh checkout after `uv sync`.

- CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R001: `uv run pytest tests/test_default_content_surfaces.py -q`
- CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R002: `uv run pytest tests/test_artcraft_ontology.py::test_pack_classes_extend_core_and_import_nothing -q`
- CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R003: `uv run pytest tests/test_app_ontology_render.py::test_each_app_file_extends_core_and_unknown_parent_refuses -q`
- CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R004: `uv run pytest tests/test_app_skill_render.py::test_skill_lists_every_snapshot_tool_and_refuses_unknown_tool -q`
- CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R005: `uv run pytest tests/test_app_prompt_render.py::test_prompt_per_functionality_names_only_snapshot_tools -q`
- CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R006: `uv run pytest tests/test_generate_app_content.py::test_write_is_deterministic_and_missing_snapshot_refuses -q`
- CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R007: `uv run pytest tests/test_content_drift_gate.py::test_offline_gate_flags_edited_file_and_live_gate_flags_stale_snapshot -q`
- CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R008: `uv run pytest tests/test_pack_import_served.py::test_pack_imports_without_orphans_and_class_query_reaches_subclasses -q`

Regenerate content with `uv run python scripts/generate_app_content.py --write`. Check it with `--check`.

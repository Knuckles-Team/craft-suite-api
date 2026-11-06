# CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Proving test | Expected observation |
|---|---|---|---|
| T-001 | `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R001` | `tests/test_default_content_surfaces.py` | The listings include the packaged skills, ontology and prompts. |
| T-002 | `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R002` | `tests/test_artcraft_ontology.py::test_pack_classes_extend_core_and_import_nothing` | Three classes exist. Each reaches a core class. The file holds no `owl:imports` line and no stub class. |
| T-003 | `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R003` | `tests/test_app_ontology_render.py::test_each_app_file_extends_core_and_unknown_parent_refuses` | Eleven files are produced. Every class reaches a core class. A class with another parent fails with `CONTENT_PARENT_UNKNOWN`. |
| T-004 | `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R004` | `tests/test_app_skill_render.py::test_skill_lists_every_snapshot_tool_and_refuses_unknown_tool` | Each skill table holds every snapshot tool once. A tool name missing from the snapshot fails with `CONTENT_SKILL_TOOL_UNKNOWN`. |
| T-005 | `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R005` | `tests/test_app_prompt_render.py::test_prompt_per_functionality_names_only_snapshot_tools` | One prompt exists for each functionality. Each prompt holds `requires_namespace`. An unknown tool fails with `CONTENT_PROMPT_TOOL_UNKNOWN`. |
| T-006 | `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R006` | `tests/test_generate_app_content.py::test_write_is_deterministic_and_missing_snapshot_refuses` | Two `--write` runs give identical bytes. An app without a snapshot fails with `CONTENT_SNAPSHOT_MISSING`. |
| T-007 | `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R007` | `tests/test_content_drift_gate.py::test_offline_gate_flags_edited_file_and_live_gate_flags_stale_snapshot` | An edited generated file fails with `CONTENT_DRIFT`. A fixture CLI with one changed schema fails the live gate with `CONTENT_SNAPSHOT_STALE`. |
| T-008 | `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R008` | `tests/test_pack_import_served.py::test_pack_imports_without_orphans_and_class_query_reaches_subclasses` | The receipt holds no ontology warning. The two class queries return the new subclasses. |
| T-009 | `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R009` | `tests/test_workflow_content.py::test_every_packaged_class_rolls_up_to_core_without_importing_it` | No packaged module imports the core; every packaged class reaches `bfo:Entity` through the installed core modules; each workflow has an ordered contract, one skill walking its tools in order and a data location; each agent prompt is a system prompt with all seven sections and lists exactly the skills and tools the ontology links. |
| T-010 | `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R010` | `tests/test_workflow_content.py::test_every_packaged_class_rolls_up_to_core_without_importing_it` (planned) | Every packaged class rolls up and the pack declares no lifecycle class. |
| T-011 | `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R010.1` | `tests/test_workflow_content.py::test_pack_declares_no_lifecycle_state_classes_of_its_own` (planned) | The pack reuses the SDK classes. |
| T-012 | `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R010.2` | `tests/test_workflow_content.py::test_every_app_skill_states_the_not_ready_refusals_and_retry` (planned) | Every skill names the refusals and the retry. |

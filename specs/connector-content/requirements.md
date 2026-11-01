# CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R001` | **Default content.** `pyproject.toml` declares `craft-suite-api` as the single `scion_sdk.connector` entry point. The server lists the packaged `skill://` and `ontology://` resources and the packaged prompts with no `content=` argument. Proving test: `tests/test_default_content_surfaces.py`. Caller chain: the `craft-suite-mcp` console script (pyproject.toml) loads the `scion_sdk.connector` entry point `craft_suite_api:connector` -> craft_suite_api/__init__.py::connector (a Connector with no content= argument) -> the SDK default content registration serves skill://, ontology:// and prompts. Shape: tests build the server from craft_suite_api and list resources and prompts over the packaged craft_suite_api/skills, craft_suite_api/ontology and craft_suite_api/prompts directories. | `resources/list` includes `skill://` and `ontology://`; `prompts/list` includes each packaged prompt. Test: `tests/test_default_content_surfaces.py::test_default_content_surfaces`. |

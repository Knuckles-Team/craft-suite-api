# CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Architecture

`pyproject.toml` declares `craft-suite-api` as the connector identity. `create_mcp_server` resolves the packaged content of `craft_suite_api` from it.

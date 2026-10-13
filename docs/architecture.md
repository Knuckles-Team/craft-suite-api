# Connector architecture

The `craft-suite-api` package owns the nine reviewed external-system operations. Graph ingestion is unavailable until a scoped source mapping is implemented.
The [shared connector SDK](https://github.com/Knuckles-Team/agent-connector-sdk/blob/5babc4cc48ad73928468b243842f219f51e2cca1/README.md) owns reusable runtime contracts.

```mermaid
flowchart LR
    Caller[Authorized caller] --> Server[MCP server]
    Server --> Router[Operation router]
    Router --> Client[Connector API client]
    Client --> Vendor[Configured external system]
    Resolver[Credential references and TLS policy] --> Client
    Content[Packaged skills prompts ontology manifest] --> Server
```

## Source and verification map

| Boundary | Source | Verification target |
|---|---|---|
| MCP entry and routing | `craft_suite_api/mcp_server.py`, `craft_suite_api/mcp/__init__.py` | `tests/test_artcraft_mcp_validation.py` |
| Credentials and TLS | `craft_suite_api/auth.py` | `tests/test_auth.py` |
| External requests | `craft_suite_api/api/api_client_system.py`, `craft_suite_api/openapi_client.py` | `tests/test_api_wrapper.py` |
| Native content and tool schemas | Package content and `scripts/generate_tool_schemas.py` | Live schema check; native content verification remains pending |
| Withheld ingestion | No callable ingestion module | `tests/test_source_contract.py` verifies the starter cannot be imported |

The [capability specification](https://github.com/Knuckles-Team/craft-suite-api/blob/main/specs/craft-suite-api/spec.md)
defines the planned behavior and acceptance targets.
The [delivery dashboard](https://knuckles-team.github.io/craft-suite-api/spec-delivery/)
shows source-backed records, code mappings, and declared relationships.
Its architecture download preserves the declared spec graph without inferring dependencies from shared code.

The generated source does not prove live service behavior, published artifacts, or deployed operation.

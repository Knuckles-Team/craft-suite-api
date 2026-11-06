# CONN-CRAFT-SUITE-API-APPS data model

This spec adds no persisted type. It uses the SDK types `UpstreamDecl`, `SandboxRoots` and `BridgeDecl` (`SCION-CONNECTOR-CONTROL-R914.1`).

- Declaration tuple (`craft_suite_api/upstreams.py`, CONN-CRAFT-SUITE-API-APPS-R002): sixteen `UpstreamDecl` values built from one app tuple.
- Command registry tools (`craft_suite_api/app_commands.py`, CONN-CRAFT-SUITE-API-APPS-R017): per app a `Dispatch` (list tool, run tool, id and params argument names, hidden dispatch tools) and one `CommandTool` per registry entry (`command_id`, `dispatch_name`, `context_args`).
- Probe result (`scripts/probe_app_clis.py`, CONN-CRAFT-SUITE-API-APPS-R003): `ProbeResult{app, exposes_mcp, version, tool_count}`, printed and never stored.
- Operator overlay (`docs/*.example.toml`, CONN-CRAFT-SUITE-API-APPS-R005 and CONN-CRAFT-SUITE-API-APPS-R006): TOML files that the SDK merges by upstream name.
- Exchange settings example (`docs/exchange.example.json`, CONN-CRAFT-SUITE-API-APPS-R014): the SDK `ExchangeSettings` document with two sinks, `objects` and `files`.

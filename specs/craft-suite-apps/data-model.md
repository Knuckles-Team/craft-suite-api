# CONN-CRAFT-SUITE-API-APPS data model

This spec adds no persisted type. It uses the SDK types `UpstreamDecl`, `SandboxRoots` and `BridgeDecl` (`SCION-CONNECTOR-CONTROL-R914.1`).

- Declaration tuple (`craft_suite_api/upstreams.py`, CONN-CRAFT-SUITE-API-APPS-R002): eleven `UpstreamDecl` values built from one app tuple.
- Probe result (`scripts/probe_app_clis.py`, CONN-CRAFT-SUITE-API-APPS-R003): `ProbeResult{app, exposes_mcp, version, tool_count}`, printed and never stored.
- Operator overlay (`docs/*.example.toml`, CONN-CRAFT-SUITE-API-APPS-R005 and CONN-CRAFT-SUITE-API-APPS-R006): TOML files that the SDK merges by upstream name.

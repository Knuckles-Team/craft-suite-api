# Upstream registry seam contract

Provider: scion-sdk SCION-CONNECTOR-CONTROL-R914
Consumer: craft-suite-api CONN-CRAFT-SUITE-API-APPS-R002

Counterpart: scion-sdk `specs/scion-connector-control/contracts/upstream-registry.md`.

## Wire shape

The connector sets `Connector.upstreams` to eleven `UpstreamDecl` values. Each value has `kind` `stdio`, `command` `<app>-cli`, `args` `("mcp",)` and a `sandbox` with the flags `--automation-read-root` and `--automation-write-root`. The roots come from the settings `CRAFT_SUITE_READ_ROOTS` and `CRAFT_SUITE_WRITE_ROOTS`. An operator overlay named by `SCION_UPSTREAMS_FILE` switches an app to `http` or `bridge`.

The SDK serves proxied tools as `<app>_<tool>` with the tag `ns:<app>` and the metadata key `scion/upstream`.

## Refusal codes

The connector adds no refusal code at this seam. It passes through `UPSTREAM_ROOTS_REQUIRED`, `UPSTREAM_ROOT_UNSAFE`, `UPSTREAM_SECRET_LITERAL`, `UPSTREAM_EGRESS_REFUSED`, `UPSTREAM_BRIDGE_NOT_LOOPBACK`, `UPSTREAM_BRIDGE_TOKEN_MISSING` and `UPSTREAM_SPAWN_FAILED` from the SDK.

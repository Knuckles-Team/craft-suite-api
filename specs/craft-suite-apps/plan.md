# CONN-CRAFT-SUITE-API-APPS — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

The connector declares eleven upstreams and the SDK registry serves them. This plan covers the ArtCraft declarations, the root settings, the deployment overlays, the probe and the four acceptance gates. The registry, the pool, the health report and the drift check are SDK rows (`SCION-CONNECTOR-CONTROL-R914`). The gateway group load is an Arbora row (`ARBORA-FLEET-R061`).

## Technical Context

- **Language/Version**: Python 3.14 (floor 3.12)
- **Primary Dependencies**: scion-sdk with the `mcp` extra, which pins the MCP framework
- **Storage**: N/A; the connector stores nothing, and generated content is committed files
- **Testing**: pytest with fixture app command-line programs; a live smoke is opt-in
- **Target Platform**: Linux containers and developer hosts that carry the app command-line programs
- **Project Type**: connector (MCP server)
- **Performance Goals**: N/A
- **Constraints**: the SDK owns the registry, the lifecycle and the drift check; the connector reimplements none of them
- **Scale/Scope**: 12 rows, 11 upstream declarations

## Constitution Check

- One owner per concept: pass. The SDK owns the registry. This connector owns the ArtCraft declarations only.
- Extend before you create: pass. The Tier 1 rows and the content rows stay in their specs; this spec holds the upstream rows no spec owns.
- Connectors depend on the SDK and are called through the gateway: pass.
- No ratchets: pass. The rows add no suppression and no baseline.
- Complete rows: pass. Every row holds a caller chain, a shape and a test reference.

## Project Structure

```text
craft_suite_api/upstreams.py          new       eleven UpstreamDecl values
craft_suite_api/__init__.py           existing  Connector(upstreams=UPSTREAMS)
craft_suite_api/error_authority.py    existing  gains BackendNotConfigured
craft_suite_api/auth.py               existing  get_client raises it
scripts/probe_app_clis.py             new       craft-suite-probe
docs/remote-upstreams.example.toml    new       remote overlay example
docs/bridge-upstreams.example.toml    new       bridge overlay example
docs/tool-budget.md                   new       activation steps
docs/fleet-deployment.md              new       gateway settings
tests/fixtures/fake_app_cli.py        new       fixture app command-line program
```

## Phase 0: Research

Unknowns settled in [research.md](research.md):

- Which apps expose `mcp`, and how a tool list of about 400 tools reaches a model.
- How a destructive app call asks for confirmation.
- How a desktop session is reached.

## Phase 1: Design

### Existing system and reuse

Tier 1 is the generated backend connector. The SDK registry owns the proxy, the namespace, the activation tools, the stdio pool, the health report, the elicitation pass-through and the drift check. This connector adds data, not mechanisms.

### Decisions

Namespacing: `<app>_<tool>`, one lowercase alphanumeric word for the app. The names `execute`, `save`, `export` and `screenshot` occur in several apps, so the prefix is required.

Activation default: `lazy` for a direct client, so the first list holds thirteen tools. A deployment behind the gateway sets `SCION_UPSTREAM_ACTIVATION=active`, and the gateway load controls exposure.

Roots: unset means deny. The read and write settings are separate, and the write roots never default to the read roots.

Lifecycle: pooled stdio children, owned by the SDK (`SCION-CONNECTOR-CONTROL-R914.8`). The connector sets no lifecycle knob.

Remote and bridge modes: operator overlays only. The repository ships examples with placeholder values.

### Acceptance phases

| Phase | Scope | Row |
|---|---|---|
| 1 | Facade MVP with photocraft, wordcraft and solidcraft over stdio | `CONN-CRAFT-SUITE-API-APPS-R009` |
| 2 | All eleven apps, remote mode, bridge mode, failure isolation | `CONN-CRAFT-SUITE-API-APPS-R010` |
| 3 | Content tier with the drift gate | `CONN-CRAFT-SUITE-API-APPS-R011` |
| 4 | Gateway integration: coverage, group load, pins | `CONN-CRAFT-SUITE-API-APPS-R012` |

### Quality and release gates

Run `pipelines-hook spec-standard`, `pipelines-hook spec-status` and `ste-staged` on the spec directory. Phase gates run offline against fixture programs.

## Phase 2: Task approach

Order the work producer first. The SDK rows `SCION-CONNECTOR-CONTROL-R914.1` to `SCION-CONNECTOR-CONTROL-R914.5` land before `CONN-CRAFT-SUITE-API-APPS-R002`. The gateway row `ARBORA-FLEET-R061` lands before `CONN-CRAFT-SUITE-API-APPS-R008`. The phase gates land last, one after each group of rows.

## Complexity Tracking

none. The constitution check passed.

## Build contract

The change must meet these gate thresholds from the organization constitution table.

- Cyclomatic complexity 10 and cognitive complexity 15 per function (`pipelines_hooks/complexity`).
- Words per sentence 20 (`ste`).
- Clone similarity 0.85 blocking at 40 tokens (`dupehound`).
- KISS limits from `.config/kiss.toml`: 35 statements, 15 locals, 20 calls, 3 positional arguments, 4 indentation levels, 300 lines and 10 functions per file.
- Pre-land fast set: `format`, `hygiene`, `secrets`, `types`, `tests-fast`; post-land set: `spec`, `tests`, `supply-chain`.

Repository commands: `pre-commit run --all-files`, then `uv run pytest tests`. No scanner gaming, no suppression and no duplicate implementation: a row reuses the helper named in its `Shape:` sentence.

## Production caller chain

Entry point: the `scion_sdk.connector` entry point calls `run` and `build_server`, which call `_serve_hooks` (`scion_sdk/_connector_serve.py:97`). `_serve_hooks` calls `attach_upstreams` with `connector.upstreams` from `craft_suite_api/__init__.py`. Tier 1 reaches the backend through `get_client` (`craft_suite_api/auth.py:70`). Obsolete paths to delete: none.

## Cross-repo seams

- Upstream registry: provider `SCION-CONNECTOR-CONTROL-R914`, consumer `CONN-CRAFT-SUITE-API-APPS-R002`; see [contracts/upstream-registry.md](contracts/upstream-registry.md).
- Gateway fleet: provider `ARBORA-FLEET-R061`, consumer `CONN-CRAFT-SUITE-API-APPS-R008`; see [contracts/arbora-fleet.md](contracts/arbora-fleet.md).

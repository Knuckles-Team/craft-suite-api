# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0] - 2026-11-06

### Added
- Graceful startup: each app's command registry loads on its own; a listing
  answers at once and every app that lands publishes `ToolsListChanged`. A call
  to a warming app waits up to `CRAFT_SUITE_WARMUP_WAIT_S` for that app, then
  answers the retryable refusal `APP_WARMING`; a failed registry answers
  `APP_REGISTRY_UNREADABLE` and is retried in the background. `/ready` is 503
  until every app has settled and reports the per-app state
  (CONN-CRAFT-SUITE-API-APPS-R018).
- Command tool parameters are typed from the apps' own documentation (types,
  ranges, enums, defaults; pdfcraft's JSON schemas as is); unions and prose
  stay open (CONN-CRAFT-SUITE-API-APPS-R019).
- Sixteen proven business workflows as skills, six agent definitions
  (operator plus five business roles) as system prompts, and the workflow
  ontology: tool-use contracts, data locations, and the skill, prompt and role
  links, rolled up to the core by subclassing
  (CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R009).

### Fixed
- Command tools ran their arguments outside the artifact exchange, so no
  command output was published and filmcraft could not write an export. They
  now stage inputs, place relative outputs in the run, publish them, and await
  background export jobs (CONN-CRAFT-SUITE-API-APPS-R020).
- Only real output paths move into the run: effectcraft's property paths
  (`transform/opacity`) and photocraft's vector path names pass through.
- materialcraft and texturecraft get root-relative paths (they refuse absolute
  ones); solidcraft gets its folders through `--allow-path` (it ignored the
  automation root flags) (CONN-CRAFT-SUITE-API-APPS-R002, R020).
- The backend description keeps the JSON body of operations with a bogus
  `request` parameter (flux schnell asked for a file) and opens response-only
  enums the live backend exceeds (CONN-CRAFT-SUITE-API-R007).

### Changed
- The served backend description is built from the pinned published document
  at first use; the committed generated copy and its drift hook are gone
  (CONN-CRAFT-SUITE-API-R007).

## [0.7.1] - 2026-11-06

### Fixed
- The full listing (about 9,000 tools) was 9.1 MB and exceeded the fleet
  gateway's 8 MiB single-response limit, so the gateway could not read it.
  Command tools now name their parameters once (the documentation stays in the
  description, cut at 1000 characters), carry the SDK `scion/upstream` group
  metadata, and set a read-only hint only where the app marks a command as not
  mutating: the listing is about 6 MB (CONN-CRAFT-SUITE-API-APPS-R017).

## [0.7.0] - 2026-11-06

### Added
- Every app engine command is its own tool, `<app>_cmd_<command id>`: the
  apps' command registries (7,866 commands across fifteen apps; lightcraft
  already serves one tool per command) are read from the installed binaries at
  serve time. Each tool documents the app's own parameters and forwards to the
  app's dispatch tool, which is no longer listed (CONN-CRAFT-SUITE-API-APPS-R017).
- Five more apps are declared as upstreams: designcraft, gridcraft, lightcraft,
  materialcraft and texturecraft, with their content tier (skills, ontologies,
  prompts) (CONN-CRAFT-SUITE-API-APPS-R002).

### Fixed
- An unusable backend setting (a path in the origin, plaintext without the
  opt-in, an unresolvable credential or TLS profile) no longer stops the server:
  every backend tool answers the typed refusal `BACKEND_CONFIG_INVALID` and
  readiness reports `invalid` (CONN-CRAFT-SUITE-API-APPS-R001).

## [0.6.0] - 2026-11-05

### Changed (breaking)
- The backend tier now serves every operation of the backend's published API
  description as one typed tool, `craft_suite_<operationId>`: 268 tools instead
  of 9, including generation, upload and account operations
  (CONN-CRAFT-SUITE-API-R007). The tools are generated with fastmcp's OpenAPI
  provider from `api-spec/backend.openapi.json`, pinned by sha256 and repaired
  deterministically by `scripts/generate_backend_tools.py`.
- Every write needs `CRAFT_SUITE_API_ALLOW_WRITES` and a confirmation. Refusals
  are typed (`BACKEND_NOT_CONFIGURED`, `WRITES_DISABLED`, unconfirmed), and every
  write decision is audited on the `craft_suite_api.audit` logger
  (CONN-CRAFT-SUITE-API-R008).
- Reads no longer need write enablement or confirmation.

### Removed
- The hand-reviewed nine-operation contract and its runtime
  (`openapi_*` modules, `craft_suite_api.api`, the source-evidence scripts and
  their validation receipts). The nine reads keep their tool names.
## [0.5.3] - 2026-11-06

### Fixed
- Requires `scion-sdk>=0.8.2`: with the artifact exchange active, 0.8.1 appended the exchange input tree to the read roots of `filmcraft` and `cadcraft` (declared without a root flag), so the server refused to start (`UPSTREAM_DECL_INVALID`, CrashLoopBackOff). 0.8.2 leaves a flagless side alone (CONN-CRAFT-SUITE-API-APPS-R002).

## [0.5.2] - 2026-11-05

### Fixed
- `filmcraft` and `cadcraft` declare no filesystem-root flags: their `mcp`
  subcommand does not accept `--automation-read-root`/`--automation-write-root`,
  which made both upstreams fail `UPSTREAM_SPAWN_FAILED`. Their file access is
  bounded by the container; path arguments still go through the exchange
  (CONN-CRAFT-SUITE-API-APPS-R002). Needs `scion-sdk>=0.8.1`.

## [0.5.1] - 2026-11-05

### Fixed
- The `mcp` and `all` extras (and so the container image) now install the SDK
  `storage-s3` extra: the documented object-store sink failed in the image with
  `STORAGE_DEPENDENCY_MISSING` (CONN-CRAFT-SUITE-API-APPS-R014).

## [0.5.0] - 2026-11-05

### Added
- Artifact exchange for every app (CONN-CRAFT-SUITE-API-APPS-R013): each app call runs in its own run folder; a relative output path lands there, and after the call the outputs publish to every configured sink. Inputs accept `exchange://<sink>/<key>` or an `https` URL. Results link each output (`resource_link`) and list them under `scion/artifacts`.
- `docs/exchange.example.json`: an S3-compatible object-store sink with signed URLs and a WebDAV file-share sink in `ArtCraft/<app>/<YYYY-MM-DD>/<run>/` (CONN-CRAFT-SUITE-API-APPS-R014); deployment guide section.
- The generated app skills state the input forms and the output rule (CONN-CRAFT-SUITE-API-APPS-R016).

### Changed
- Requires `scion-sdk>=0.8.0,<0.9`.

## [0.4.0] - 2026-11-04

### Added
- ArtCraft suite MCP facade: eleven app upstreams are served behind this one connector through the SDK upstream registry, with lazy activation per app group, registry tools to list, load and unload groups, and local, remote and bridge overlays for reaching each app.
- Content tier: a per-app ontology, skill and prompts generated from the app sources, plus an offline drift gate (`scripts/generate_app_content.py --check`) wired into pre-commit and CI.

## [0.3.6] - 2026-11-01

### Fixed
- Write tools take an optional `confirm` argument and return a clean `cancelled` result, instead of an error, when a client that cannot elicit has not confirmed; requires `scion-sdk>=0.6.5,<0.7.0`.

## [0.3.5] - 2026-10-30

### Changed
- Requires `scion-sdk>=0.6.4,<0.7.0`; uv.lock relocked.

## [0.3.3] - 2026-10-23

### Changed
- Requires `agent-connector-sdk>=0.4.1`; data sources are declared in code (`connector_sources`).

## [Unreleased]

Scaffold generated: 2026-10-12. This is not a release or delivery date.

### Added
- Initial scaffold; release and delivery remain unclaimed.
- Modular subfolders for API wrappers (`api/`) and action-routed MCP tools (`mcp/`).
- Material-theme mkdocs documentation site (7 standard pages).
- Full pre-commit quality gate and flat `tests/` structure.

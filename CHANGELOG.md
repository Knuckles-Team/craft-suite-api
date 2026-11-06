# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

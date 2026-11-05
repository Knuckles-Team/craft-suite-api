# CONN-CRAFT-SUITE-API-APPS — ArtCraft suite upstream registry

Owner: craft-suite-api. Cross-repo IDs: `SCION-CONNECTOR-CONTROL-R914`, `ARBORA-FLEET-R059`, `ARBORA-FLEET-R060`, `ARBORA-FLEET-R061`, `CONN-CRAFT-SUITE-API-R003`.

## Purpose and user stories

The `craft-suite-api` server becomes the one MCP facade for the whole ArtCraft suite. Tier 1 is the existing backend connector. Tier 2 proxies the `mcp` server of each app command-line program through the SDK upstream registry. This spec owns the ArtCraft-specific part: which apps, which roots, which deployment modes and which acceptance gates.

## Why a new spec

Search: `git grep -n "upstream\|<app>-cli\|bridge\|stdio" -- specs` in this repository, and a read of `CONN-CRAFT-SUITE-API` and `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT`. The first owns the nine backend reads only. The second owns the packaged content only. No spec owns the per-app upstream declarations, the deployment modes or the phase gates. The generic registry is an SDK capability and lives in `SCION-CONNECTOR-CONTROL-R914`. This spec holds no registry code.

## User Scenarios & Testing

### User Story 1 - Use several apps through one server (Priority: P1)

An agent author connects to one server and works with photo, document and model files without wiring each app.

**Acceptance Scenarios**:

1. **Given** the facade has started with no activation, **When** the agent lists tools, **Then** it sees the thirteen Tier 1 and registry tools only (`CONN-CRAFT-SUITE-API-APPS-R007`).
2. **Given** a session, **When** it activates one app, **Then** the tools of that app appear as `<app>_<tool>` (`CONN-CRAFT-SUITE-API-APPS-R009`).

### User Story 2 - Run apps locally, remotely or on a desktop session (Priority: P2)

An operator picks the deployment mode for each app without changing code.

**Acceptance Scenarios**:

1. **Given** an overlay file for a remote app, **When** the server starts, **Then** that app is reached over HTTP and the others stay local (`CONN-CRAFT-SUITE-API-APPS-R005`).
2. **Given** a bridge overlay with a non-loopback address, **When** the server starts, **Then** it refuses (`CONN-CRAFT-SUITE-API-APPS-R006`).

### User Story 3 - Load one app at a time behind the gateway (Priority: P3)

A gateway user loads and unloads one app as a group.

**Acceptance Scenarios**:

1. **Given** the facade is registered once, **When** the user loads the group `photocraft`, **Then** only photocraft tools load (`CONN-CRAFT-SUITE-API-APPS-R008`).

### User Story 4 - Get app outputs where they are needed (Priority: P1)

An operator runs an app tool through the gateway. The output appears in the file share folder of that app and day, and in the object store. The caller gets a link.

**Acceptance Scenarios**:

1. **Given** the two sinks of the example, **When** a photocraft tool saves `out.png`, **Then** the file share holds `ArtCraft/photocraft/<date>/<run>/out.png`.
2. **Given** an input `exchange://files/in/a.png`, **When** the app opens it, **Then** the app reads the staged copy.

### Edge Cases

- An app command-line program is missing from `PATH`: only that app is `unavailable` (`CONN-CRAFT-SUITE-API-APPS-R004`).
- The Tier 1 backend is not configured: the server starts and Tier 1 calls refuse with a typed code (`CONN-CRAFT-SUITE-API-APPS-R001`).
- Roots are unset: every app gets no root flag and so no file access (`CONN-CRAFT-SUITE-API-APPS-R002`).
- An app update changes its tool list: the drift gate reports it (`CONN-CRAFT-SUITE-API-APPS-R011`).
- No exchange settings are present: the binding is inert, and app calls behave as before (`CONN-CRAFT-SUITE-API-APPS-R013`).
- An optional sink fails: the call succeeds and the result records the failure code (`CONN-CRAFT-SUITE-API-APPS-R014`).

## Requirements

- **FR-001**: Tier 1 stays unchanged and degrades when unconfigured. Rows: `CONN-CRAFT-SUITE-API-APPS-R001`.
- **FR-002**: Declare the eleven app upstreams with fail-closed roots. Rows: `CONN-CRAFT-SUITE-API-APPS-R002`.
- **FR-003**: Probe the app command-line programs for MCP support. Rows: `CONN-CRAFT-SUITE-API-APPS-R003`.
- **FR-004**: Support local, remote and bridge deployment. Rows: `CONN-CRAFT-SUITE-API-APPS-R004`, `CONN-CRAFT-SUITE-API-APPS-R005`, `CONN-CRAFT-SUITE-API-APPS-R006`.
- **FR-005**: Keep the initial tool list small. Rows: `CONN-CRAFT-SUITE-API-APPS-R007`.
- **FR-006**: Register the facade once and load one app at a time. Rows: `CONN-CRAFT-SUITE-API-APPS-R008`.
- **FR-008**: Exchange app inputs and outputs with configured sinks. Rows: `CONN-CRAFT-SUITE-API-APPS-R013`, `CONN-CRAFT-SUITE-API-APPS-R014`, `CONN-CRAFT-SUITE-API-APPS-R015`, `CONN-CRAFT-SUITE-API-APPS-R016`.
- **FR-007**: Pass four phased acceptance gates. Rows: `CONN-CRAFT-SUITE-API-APPS-R009`, `CONN-CRAFT-SUITE-API-APPS-R010`, `CONN-CRAFT-SUITE-API-APPS-R011`, `CONN-CRAFT-SUITE-API-APPS-R012`.

## Success Criteria

- **SC-001**: The first tool list holds exactly thirteen tools. Rows: `CONN-CRAFT-SUITE-API-APPS-R007`.
- **SC-002**: With roots unset, no root flag reaches any app process. Rows: `CONN-CRAFT-SUITE-API-APPS-R002`.
- **SC-003**: One failing app leaves ten apps callable. Rows: `CONN-CRAFT-SUITE-API-APPS-R010`.
- **SC-004**: Loading one group loads only that app. Rows: `CONN-CRAFT-SUITE-API-APPS-R008`.
- **SC-005**: One app call with an exchange input lands its output in both sinks. Rows: `CONN-CRAFT-SUITE-API-APPS-R015`.

## Assumptions

- The app command-line programs expose `mcp` as probed on the host: eleven of fourteen do, and lightcraft, designcraft and gridcraft are re-probed on app updates.
- The SDK registry rows (`SCION-CONNECTOR-CONTROL-R914`) land before the rows here that depend on them.
- The remote topology is supplied by the operator. This repository ships no host names.

## Scope and interfaces

In scope: the rows of [requirements.md](requirements.md). Out of scope: the registry code, the pool, the health report and the drift check (all in the SDK), and the group load rows (in the gateway).

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-CRAFT-SUITE-API-APPS-R001` | [plan.md](plan.md) | T-001 | [test-spec.md](test-spec.md) |
| FR-002 | `CONN-CRAFT-SUITE-API-APPS-R002` | [plan.md](plan.md) | T-002 | [test-spec.md](test-spec.md) |
| FR-003 | `CONN-CRAFT-SUITE-API-APPS-R003` | [plan.md](plan.md) | T-003 | [test-spec.md](test-spec.md) |
| FR-004 | `CONN-CRAFT-SUITE-API-APPS-R004`, `CONN-CRAFT-SUITE-API-APPS-R005`, `CONN-CRAFT-SUITE-API-APPS-R006` | [plan.md](plan.md) | T-004 to T-006 | [test-spec.md](test-spec.md) |
| FR-005 | `CONN-CRAFT-SUITE-API-APPS-R007` | [plan.md](plan.md) | T-007 | [test-spec.md](test-spec.md) |
| FR-006 | `CONN-CRAFT-SUITE-API-APPS-R008` | [plan.md](plan.md) | T-008 | [test-spec.md](test-spec.md) |
| FR-008 | `CONN-CRAFT-SUITE-API-APPS-R013` to `CONN-CRAFT-SUITE-API-APPS-R016` | [plan.md](plan.md) | T-013 to T-016 | [test-spec.md](test-spec.md) |
| FR-007 | `CONN-CRAFT-SUITE-API-APPS-R009` to `CONN-CRAFT-SUITE-API-APPS-R012` | [plan.md](plan.md) | T-009 to T-012 | [test-spec.md](test-spec.md) |

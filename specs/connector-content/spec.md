# CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT — The connector serves its packaged content

Owner: craft-suite-api. Cross-repo IDs: `SCION-CONNECTOR-CONTROL-R073`, `SCION-CONNECTOR-CONTROL-R022`, `MEDULLA-TYPED-PACKS-R071.2`, `MEDULLA-TYPED-PACKS-R102.3`, `MEDULLA-TYPED-PACKS-R105`, `CONN-CRAFT-SUITE-API-APPS-R002`.

## Purpose and user stories

The `craft-suite-api` server serves its packaged skills, prompts and ontology to any client, with no wiring of its own. The content covers the whole ArtCraft suite: one ontology file, one skill and a set of prompts for each app.

## User Scenarios & Testing

### User Story 1 - Find the skill for an app (Priority: P1)

An agent lists the server's resources and reads the skill of one app before it activates the app.

**Acceptance Scenarios**:

1. **Given** the default server, **When** the client lists `skill://` resources, **Then** it sees one skill for each of the eleven apps (`CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R004`).
2. **Given** a skill, **When** the agent reads its tool table, **Then** every tool is named `<app>_<tool>` and exists in the app snapshot (`CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R004`).

### User Story 2 - Ask the graph about apps and use cases (Priority: P2)

A graph user asks which apps exist and which use cases each app supports.

**Acceptance Scenarios**:

1. **Given** the imported pack, **When** the user queries the class `:Application`, **Then** the result includes `:App` (`CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R008`).
2. **Given** the imported pack, **When** the user queries the class `:Task`, **Then** the result includes `:UseCase` (`CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R008`).

### User Story 3 - Keep content current after an app update (Priority: P3)

A maintainer updates an app and sees what changed.

**Acceptance Scenarios**:

1. **Given** a changed tool schema, **When** the live gate runs, **Then** it names the changed tool (`CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R007`).
2. **Given** an edited generated file, **When** CI runs the offline gate, **Then** it fails with the file name (`CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R007`).

### Edge Cases

- A functionality names a tool that the snapshot lacks: generation fails (`CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R005`).
- A snapshot tool belongs to no functionality: the report lists it and the skill table still shows it (`CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R005`).
- An app has a source file and no snapshot: generation fails (`CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R006`).

## Requirements

- **FR-001**: Serve packaged content with no wiring. Rows: `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R001`.
- **FR-002**: Replace the stub with the core pack classes. Rows: `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R002`.
- **FR-003**: Generate one ontology file for each app. Rows: `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R003`.
- **FR-004**: Generate one skill for each app. Rows: `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R004`.
- **FR-005**: Generate prompts for each functionality. Rows: `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R005`.
- **FR-006**: Generate content from live tool snapshots. Rows: `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R006`.
- **FR-007**: Gate generated content against drift. Rows: `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R007`.
- **FR-008**: Prove the pack imports cleanly. Rows: `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R008`.
- **FR-009**: Ship the proven business workflows as skills, agent prompts and ontology contracts. Rows: `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R009`.

## Success Criteria

- **SC-001**: Eleven app skills and eleven app ontology files exist. Rows: `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R003`, `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R004`.
- **SC-002**: The pack import reports no orphan class. Rows: `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R008`.
- **SC-004**: Every packaged ontology class reaches `bfo:Entity` through the core, and every agent prompt names only skills and tools its ontology links. Rows: `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R009`.
- **SC-003**: Two generator runs give identical bytes. Rows: `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R006`.

## Assumptions

- The app command-line programs list their tools through `mcp`. Only a host with them runs `--refresh`.
- The engine rows `MEDULLA-TYPED-PACKS-R071.2`, `MEDULLA-TYPED-PACKS-R102.3` and `MEDULLA-TYPED-PACKS-R105` already cover how a pack ontology joins the core, so this spec adds no engine row.

## Scope and interfaces

In scope: the rows of [requirements.md](requirements.md). The upstream registry rows are in `CONN-CRAFT-SUITE-API-APPS`. Out of scope: engine ontology composition.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R001` | [plan.md](plan.md) | T-001 | [test-spec.md](test-spec.md) |
| FR-002 | `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R002` | [plan.md](plan.md) | T-002 | [test-spec.md](test-spec.md) |
| FR-003 | `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R003` | [plan.md](plan.md) | T-003 | [test-spec.md](test-spec.md) |
| FR-004 | `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R004` | [plan.md](plan.md) | T-004 | [test-spec.md](test-spec.md) |
| FR-005 | `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R005` | [plan.md](plan.md) | T-005 | [test-spec.md](test-spec.md) |
| FR-006 | `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R006` | [plan.md](plan.md) | T-006 | [test-spec.md](test-spec.md) |
| FR-007 | `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R007` | [plan.md](plan.md) | T-007 | [test-spec.md](test-spec.md) |
| FR-008 | `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R008` | [plan.md](plan.md) | T-008 | [test-spec.md](test-spec.md) |
| FR-009 | `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R009` | [plan.md](plan.md) | T-009 | [test-spec.md](test-spec.md) |

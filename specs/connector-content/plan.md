# CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

`pyproject.toml` declares `craft-suite-api` as the connector identity, and `create_mcp_server` resolves the packaged content of `craft_suite_api` from it. This plan adds the suite content: the core pack classes, one ontology file, one skill and a set of prompts for each app, all generated from live tool snapshots, with a drift gate.

## Technical Context

- **Language/Version**: Python 3.14 (floor 3.12)
- **Primary Dependencies**: scion-sdk with the `mcp` extra, which pins the MCP framework
- **Storage**: N/A; the connector stores nothing, and generated content is committed files
- **Testing**: pytest with fixture app command-line programs; a live smoke is opt-in
- **Target Platform**: Linux containers and developer hosts that carry the app command-line programs
- **Project Type**: connector (MCP server)
- **Performance Goals**: N/A
- **Constraints**: the SDK owns the registry, the lifecycle and the drift check; the connector reimplements none of them
- **Scale/Scope**: 8 rows, 11 apps

## Constitution Check

- One owner per concept: pass. The engine owns how a pack ontology joins the core. This spec owns the content only.
- Extend before you create: pass. The rows extend the packaged-content spec. The upstream rows are in `CONN-CRAFT-SUITE-API-APPS`.
- Packs roll up to the core: pass. Every pack class has a subclass path to a core class, and no file imports the core ontology.
- Complete rows: pass. Every new row holds a caller chain, a shape and a test reference.

## Project Structure

```text
craft_suite_api/ontology/artcraft.ttl           existing  rewritten: App, AppTool, UseCase
craft_suite_api/ontology/artcraft-<app>.ttl     new       generated, eleven files
craft_suite_api/skills/<app>/SKILL.md           new       generated, eleven files
craft_suite_api/prompts/<app>-<functionality>.json  new   generated
craft_suite_api/content_gen/                    new       render_ontology, render_skill, render_prompts
scripts/generate_app_content.py                 new       --check, --write, --refresh, --live
content/apps/<app>.yml                          new       authored summary, classes, functionalities
content/snapshots/<app>.tools.json              new       generated from live tool lists
```

## Phase 0: Research

No unknowns. The pack rules are in `MEDULLA-TYPED-PACKS-R071.2`, `MEDULLA-TYPED-PACKS-R102.3` and `MEDULLA-TYPED-PACKS-R105`. The suite facts are in [../craft-suite-apps/research.md](../craft-suite-apps/research.md).

## Phase 1: Design

### Existing system and reuse

The server already lists packaged `skills/`, `ontology/` and `prompts/` with no wiring (`CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R001`). The generator writes into those directories, so no server code changes. The drift fingerprint reuses the SDK `compatibility_fingerprint`.

### Decisions

The ontology is layered, not copied. One core pack file holds `:App`, `:AppTool` and `:UseCase`. Each app file holds one `:App` individual, its domain classes and its `:UseCase` individuals. Tools are not ontology individuals. The tool listing reaches the graph as virtual entries through the connector access contract, so the ontology stays small.

A pack file never imports the core ontology. It extends core classes with `rdfs:subClassOf`, as the engine requires.

Authored text is separate from generated text. Authors edit `content/apps/<app>.yml`. The generator owns everything under `craft_suite_api/` that it writes.

### Quality and release gates

Run `pipelines-hook spec-standard`, `pipelines-hook spec-status` and `ste-staged` on the spec directory. The offline drift gate runs in pre-commit and CI.

### Lifecycle by reuse (CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R010)

The lifecycle machine belongs to the scion-sdk ConnectorLifecycle pack. This connector declares no machine class. It types its app and backend individuals with the SDK classes and states in skills how to read a component that is not ready. The test lists the pack classes, so a state class declared here fails the build.

## Phase 2: Task approach

Order the work producer first: the core pack classes, then the generator, then the three renderers, then the drift gate, then the import proof.

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

Entry point: `build_server` (`craft_suite_api/mcp_server.py`) calls the SDK `build_server`, which lists the packaged content directories. The generator is a development command and has no run-time caller. Obsolete paths to delete: the stub classes in `artcraft.ttl`.

Row `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R010`: the packaged ontology is served as `ontology://` resources and imported by the pack import; the lifecycle states it points at come from the SDK pack; the skills are served by the SDK default content registration.

## Cross-repo seams

- Ontology joins the core: provider `MEDULLA-TYPED-PACKS-R105`, consumer `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R002`; see [contracts/medulla-ontology.md](contracts/medulla-ontology.md).

### Amendments

- 2026-11-06: lifecycle ontology by reuse (organization constitution Article XXXI). Row `CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R010` and children R010.1 and R010.2 describe component readiness for `CONN-CRAFT-SUITE-API-APPS-R018.3` without redeclaring the machine.

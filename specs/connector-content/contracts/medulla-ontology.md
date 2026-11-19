# Engine ontology seam contract

Provider: medulla MEDULLA-TYPED-PACKS-R105
Consumer: craft-suite-api CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R002

Counterpart: medulla `specs/typed-packs-and-catalog/requirements.md`, rows `MEDULLA-TYPED-PACKS-R071.2` and `MEDULLA-TYPED-PACKS-R102.3`.

## Wire shape

The pack carries the ontology files as Turtle entries. No file declares `owl:imports` of the core ontology. Each class has an `rdfs:subClassOf` path to a core class: `:App` to `:Application`, `:AppTool` to `:Tool`, `:UseCase` to `:Task`. App domain classes extend `:CreativeWork`, `:Document`, `:Artifact`, `:App` or `:AppTool`. A per-app file may import the sibling pack ontology `https://knuckles-team.github.io/ontology/connector/craft-common` only.

## Refusal codes

The engine refuses an import with `ONTOLOGY_PACK_IMPORTS_CORE`, `ONTOLOGY_ORPHAN` or `ONTOLOGY_CORE_CONFLICT`. The connector adds `CONTENT_PARENT_UNKNOWN` at generation time so it never ships a file that the engine would refuse.

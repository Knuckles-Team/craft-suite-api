"""CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R003: one ontology file per app, extending the core."""

from __future__ import annotations

from pathlib import Path

import pytest
import rdflib
from rdflib import OWL, RDF, RDFS, URIRef

from craft_suite_api.content_gen.errors import CONTENT_PARENT_UNKNOWN, ContentError
from craft_suite_api.content_gen.ontology import render_ontology
from craft_suite_api.content_gen.sources import (
    AppClass,
    AppSource,
    ToolSnapshot,
)

REPO = Path(__file__).resolve().parent.parent
APPS = (
    "photocraft",
    "wordcraft",
    "pdfcraft",
    "solidcraft",
    "vectorcraft",
    "figcraft",
    "effectcraft",
    "filmcraft",
    "soundcraft",
    "deckcraft",
    "cadcraft",
)
KG = "https://knuckles-team.github.io/ontology/connector"
KG_NS = KG + "/craft-common#"
CORE_NAMES = frozenset(
    {"Application", "Tool", "Task", "CreativeWork", "Document", "Artifact"}
)

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R003")


def _load(app: str) -> tuple[AppSource, ToolSnapshot]:
    from craft_suite_api.content_gen.sources import (
        load_app_source,
        load_snapshot,
    )

    return (
        load_app_source(REPO / "content" / "apps" / f"{app}.yml"),
        load_snapshot(REPO / "content" / "snapshots" / f"{app}.tools.json"),
    )


def _local_name(node: rdflib.Node) -> str:
    return str(node).rsplit("#", 1)[-1]


def test_each_app_file_extends_core_and_unknown_parent_refuses() -> None:
    core_graph = rdflib.Graph()
    core_graph.parse(
        REPO / "craft_suite_api" / "ontology" / "artcraft.ttl", format="turtle"
    )
    core_subs: dict[rdflib.Node, rdflib.Node] = {}
    for subject in core_graph.subjects(RDFS.subClassOf, None):
        parents = list(core_graph.objects(subject, RDFS.subClassOf))
        if len(parents) == 1:
            core_subs[subject] = parents[0]

    for app in APPS:
        source, snapshot = _load(app)
        text = render_ontology(source, snapshot)
        graph = rdflib.Graph()
        graph.parse(data=text, format="turtle")

        # The ontology node carries the app IRI and imports only the sibling.
        ontology = URIRef(f"{KG}/{app}")
        assert (ontology, OWL.imports, URIRef(f"{KG}/craft-common")) in graph
        assert (
            len(
                [
                    target
                    for target in graph.objects(ontology, OWL.imports)
                    if str(target) != f"{KG}/craft-common"
                ]
            )
            == 0
        )

        # The :App individual names its namespace and version.
        app_individual = list(graph.subjects(RDF.type, URIRef(KG_NS + "App")))
        assert len(app_individual) == 1
        node = app_individual[0]
        assert list(graph.objects(node, URIRef(KG_NS + "appNamespace"))) == [
            rdflib.Literal(app)
        ]
        assert list(graph.objects(node, URIRef(KG_NS + "appVersion"))) == [
            rdflib.Literal(snapshot.version)
        ]

        # Every domain class reaches a core class through the pack.
        for subject in graph.subjects(RDFS.subClassOf, None):
            current: rdflib.Node = list(graph.objects(subject, RDFS.subClassOf))[0]
            seen = {subject}
            while _local_name(current) not in CORE_NAMES and current not in seen:
                seen.add(current)
                if current not in core_subs:
                    pytest.fail(f"{app}: class {subject} chain broken at {current}")
                current = core_subs[current]

        # One :UseCase individual per functionality, wired to the app and tools.
        use_cases = list(graph.subjects(URIRef(KG_NS + "forApp"), None))
        assert len(use_cases) == len(source.functionalities)
        for use_case, func in zip(use_cases, source.functionalities, strict=True):
            tools = [
                str(value)
                for value in graph.objects(use_case, URIRef(KG_NS + "usesToolName"))
            ]
            assert tools == [f"{app}_{tool}" for tool in func.tools]

    # A class naming another parent refuses.
    source, snapshot = _load("cadcraft")
    bad = AppSource(
        app=source.app,
        summary=source.summary,
        classes=source.classes + (AppClass(name="Ghost", parent="Person"),),
        functionalities=source.functionalities,
    )
    with pytest.raises(ContentError) as excinfo:
        render_ontology(bad, snapshot)
    assert excinfo.value.code == CONTENT_PARENT_UNKNOWN

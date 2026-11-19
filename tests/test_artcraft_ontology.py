"""CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R002: the pack classes extend the core and import nothing."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest
import rdflib
from rdflib import RDFS, URIRef

PACKAGE = "craft_suite_api"
KG = "https://knuckles-team.github.io/ontology/core#"
CONNECTOR_NS = "https://knuckles-team.github.io/ontology/connector/craft-common#"
CORE_NAMES = frozenset(
    {"Application", "Tool", "Task", "CreativeWork", "Document", "Artifact"}
)

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R002")


def _pack_path() -> Path:
    root = Path(list(importlib.import_module(PACKAGE).__path__)[0])
    return root / "ontology" / "artcraft.ttl"


def _subclasses(graph: rdflib.Graph) -> dict[rdflib.Node, rdflib.Node]:
    subs: dict[rdflib.Node, rdflib.Node] = {}
    for subject in graph.subjects(RDFS.subClassOf, None):
        parents = list(graph.objects(subject, RDFS.subClassOf))
        if len(parents) == 1:
            subs[subject] = parents[0]
    return subs


def _local_name(node: rdflib.Node) -> str:
    return str(node).rsplit("#", 1)[-1]


def _reaches_core(
    start: rdflib.Node,
    core_names: frozenset[str],
    subs: dict[rdflib.Node, rdflib.Node],
) -> bool:
    current = start
    seen: set[rdflib.Node] = set()
    while _local_name(current) not in core_names and current not in seen:
        seen.add(current)
        if current not in subs:
            return False
        current = subs[current]
    return True


def test_pack_classes_extend_core_and_import_nothing() -> None:
    path = _pack_path()
    raw_text = path.read_text(encoding="utf-8")

    # The stub class and its properties are gone; the pack imports nothing.
    assert ":ArtcraftResource" not in raw_text
    assert "owl:imports" not in raw_text

    graph = rdflib.Graph()
    graph.parse(path, format="turtle")
    subs = _subclasses(graph)

    # The three pack classes exist and each reaches a core class.
    for name, core in {
        "App": "Application",
        "AppTool": "Tool",
        "UseCase": "Task",
    }.items():
        node = URIRef(KG.replace("core#", "connector/craft-common#") + name)
        assert node in subs, f":{name} is not declared"
        assert _reaches_core(node, CORE_NAMES, subs), (
            f":{name} does not reach a core class"
        )
        current = subs[node]
        seen = {node}
        while _local_name(current) != core and current not in seen:
            seen.add(current)
            current = subs[current]
        assert _local_name(current) == core, (
            f":{name} extends {_local_name(current)}, not :{core}"
        )

    # The five pack properties are declared as properties.
    from rdflib import OWL as _OWL
    from rdflib import RDF as _RDF

    for prop in ("ofApp", "forApp", "usesToolName", "appNamespace", "appVersion"):
        node = URIRef(KG.replace("core#", "connector/craft-common#") + prop)
        types = [str(t) for t in graph.objects(node, _RDF.type)]
        assert any("Property" in t for t in types), (
            f":{prop} is not declared as a property (types={types})"
        )
        assert (
            node,
            _RDF.type,
            _OWL.ObjectProperty
            if prop in ("ofApp", "forApp")
            else _OWL.DatatypeProperty,
        ) in graph, f":{prop} has the wrong property type"

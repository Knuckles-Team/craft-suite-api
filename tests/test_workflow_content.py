"""CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R009: proven workflows ship as skills, agent prompts and ontology.

Every packaged class reaches the core ontology, which is rooted under
``bfo:Entity``, through ``rdfs:subClassOf`` alone (the core is composed, never
imported), the same check the engine's ``ontology_modules_extend_core`` makes.
The core is read from the installed engine package's shipped ontology modules.
Each workflow's tool-use contract, skill and the agent prompts that use it
agree on the tools they name.
"""

from __future__ import annotations

import importlib
import json
import re
from pathlib import Path

import pytest
import rdflib
from rdflib import OWL, RDF, RDFS, URIRef

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R009")

PACKAGE = Path(list(importlib.import_module("craft_suite_api").__path__)[0])
KG = "http://knuckles.team/kg#"
CORE_IRI = URIRef("http://knuckles.team/kg/core")
BFO_ENTITY = URIRef("http://purl.obolibrary.org/obo/BFO_0000001")
TOOL_NAME = re.compile(r"^[a-z]+craft_[A-Za-z0-9_]+$|^craft_suite_[A-Za-z0-9_]+$")


def _core_graph() -> rdflib.Graph:
    medulla = Path(list(importlib.import_module("medulla").__path__)[0])
    graph = rdflib.Graph()
    for path in sorted((medulla / "ontology").glob("*-v1.ttl")):
        graph.parse(path, format="turtle")
    return graph


def _pack_graph() -> rdflib.Graph:
    graph = rdflib.Graph()
    for path in sorted((PACKAGE / "ontology").glob("*.ttl")):
        graph.parse(path, format="turtle")
    return graph


def _reaches_entity(cls, graph: rdflib.Graph, seen=frozenset()) -> bool:
    if cls == BFO_ENTITY:
        return True
    if cls in seen:
        return False
    return any(
        _reaches_entity(parent, graph, seen | {cls})
        for parent in graph.objects(cls, RDFS.subClassOf)
        if isinstance(parent, URIRef)
    )


def test_every_packaged_class_rolls_up_to_core_without_importing_it() -> None:
    pack = _pack_graph()
    assert (None, OWL.imports, CORE_IRI) not in pack
    for path in (PACKAGE / "ontology").glob("*.ttl"):
        assert "kg/core>" not in path.read_text(encoding="utf-8"), path.name
    union = _core_graph() + pack
    classes = set(pack.subjects(RDF.type, OWL.Class))
    assert URIRef(KG + "CraftWorkflow") in classes
    unrooted = sorted(str(c) for c in classes if not _reaches_entity(c, union))
    assert unrooted == [], f"classes with no rdfs:subClassOf path to core: {unrooted}"


def _workflows(graph: rdflib.Graph) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for workflow in graph.subjects(RDF.type, URIRef(KG + "CraftWorkflow")):
        contract = graph.value(workflow, URIRef(KG + "hasToolUseContract"))
        steps = sorted(
            (
                int(graph.value(step, URIRef(KG + "stepOrder"))),
                str(graph.value(step, URIRef(KG + "stepToolName"))),
            )
            for step in graph.objects(contract, URIRef(KG + "hasToolUseStep"))
        )
        out[str(workflow)] = {
            "steps": steps,
            "skills": {
                str(graph.value(skill, URIRef(KG + "skillName")))
                for skill in graph.subjects(URIRef(KG + "skillWalksWorkflow"), workflow)
            },
            "writes": set(graph.objects(workflow, URIRef(KG + "writesTo"))),
        }
    return out


def test_each_workflow_has_an_ordered_contract_a_skill_and_a_data_location() -> None:
    graph = _pack_graph()
    workflows = _workflows(graph)
    assert len(workflows) >= 3
    for iri, workflow in workflows.items():
        orders = [order for order, _ in workflow["steps"]]
        assert orders == list(range(1, len(orders) + 1)), iri
        assert all(TOOL_NAME.match(tool) for _, tool in workflow["steps"]), iri
        assert workflow["writes"], f"{iri} names no data location it writes"
        assert len(workflow["skills"]) == 1, iri
        (skill,) = workflow["skills"]
        text = (PACKAGE / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
        assert text.startswith("---\nname: " + skill + "\n"), skill
        # The skill walks the same tools, in the contract's order.
        cursor = 0
        for _, tool in workflow["steps"]:
            found = text.find(f"`{tool}`", cursor)
            assert found >= 0, (skill, tool)
            cursor = found + 1


def test_agent_prompts_are_complete_definitions_linked_in_the_ontology() -> None:
    graph = _pack_graph()
    prompts = list(graph.subjects(RDF.type, URIRef(KG + "CraftAgentPrompt")))
    names = {str(graph.value(p, URIRef(KG + "promptName"))) for p in prompts}
    assert "craft-suite-operator" in names
    assert {"marketing-asset-producer", "promo-video-editor", "brand-designer"} <= names
    for prompt in prompts:
        name = str(graph.value(prompt, URIRef(KG + "promptName")))
        document = json.loads(
            (PACKAGE / "prompts" / f"{name}.json").read_text(encoding="utf-8")
        )
        assert document["role"] == "system", name
        directive = document["instructions"]["core_directive"]
        for section in (
            "Role",
            "Goal",
            "Tools",
            "Skills",
            "Data",
            "Guardrails",
            "Outputs",
        ):
            assert f"## {section}" in directive, (name, section)
        linked_skills = {
            str(graph.value(skill, URIRef(KG + "skillName")))
            for skill in graph.objects(prompt, URIRef(KG + "promptUsesSkill"))
        }
        assert linked_skills, name
        assert set(document["skills"]) == linked_skills, name
        for skill in linked_skills:
            assert f"`{skill}`" in directive, (name, skill)
            assert (PACKAGE / "skills" / skill / "SKILL.md").is_file(), skill
        linked_tools = {
            str(t) for t in graph.objects(prompt, URIRef(KG + "promptUsesToolName"))
        }
        assert set(document["tools"]) == linked_tools, name
        for tool in linked_tools:
            assert f"`{tool}`" in directive, (name, tool)


def test_pack_declares_no_lifecycle_state_classes_of_its_own() -> None:
    """CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R010.1: reuse, never redeclare."""
    pack = _pack_graph()
    names = {
        str(c).rsplit("#", 1)[-1].lower() for c in pack.subjects(RDF.type, OWL.Class)
    }
    for word in (
        "warming",
        "ready",
        "degraded",
        "backoff",
        "stopped",
        "unconfigured",
        "transition",
        "lifecycle",
    ):
        assert not any(word in n for n in names), word
    assert (URIRef(KG + "lifecycleState"), RDF.type, OWL.ObjectProperty) in pack
    assert (None, OWL.imports, CORE_IRI) not in pack


def test_every_app_skill_states_the_not_ready_refusals_and_retry() -> None:
    """CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R010.2."""
    skills = sorted((PACKAGE / "skills").glob("*/SKILL.md"))
    skills = [s for s in skills if s.parent.name != "artcraft-starter"]
    assert len(skills) == 32
    for path in skills:
        text = path.read_text(encoding="utf-8")
        for needle in (
            "APP_WARMING",
            "APP_REGISTRY_UNREADABLE",
            "retry_after_s",
            "Backoff",
        ):
            assert needle in text, (path.parent.name, needle)
    prompt = (PACKAGE / "prompts" / "craft-suite-operator.json").read_text(
        encoding="utf-8"
    )
    for needle in (
        "APP_WARMING",
        "APP_REGISTRY_UNREADABLE",
        "retry_after_s",
        "Backoff",
    ):
        assert needle in prompt

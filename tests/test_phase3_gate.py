"""CONN-CRAFT-SUITE-API-APPS-R011: phase 3 gate — content tier, clean import.

Phase 3 proves the content tier for all eleven apps, calling the checks of
the content rows and adding no content logic:

- ``artcraft-<app>.ttl``, ``<app>/SKILL.md`` and at least one
  ``<app>-<functionality>.json`` prompt exist per app, the skill names the
  app and every prompt requires the app's namespace (R003 to R005);
- the offline drift gate (``scripts/generate_app_content.py --check``) is
  green on the committed content (R007);
- the pack built from the packaged content holds the twelve ontologies,
  the twelve skills, a prompt per app and the resource surface, and each
  app ontology imports the core module only, redeclares no core IRI and
  lets every declared class walk up to the engine's core hierarchy (the
  in-process half of R008's orphan proof).

The served half of R008 — the ``ConnectorPack.Import`` against a loopback
engine — runs only when the engine binary is present; the in-process
native engine exposes no ``ConnectorPack`` operation, so without the
binary that part is skipped with a clear reason while the gate stays
green.
"""

from __future__ import annotations

import asyncio
import importlib
import importlib.metadata
import io
import json
import shutil
import signal
import subprocess
import time
from collections import Counter
from contextlib import redirect_stdout
from pathlib import Path

import pytest
import rdflib
from rdflib import OWL, RDF, RDFS

from craft_suite_api.upstreams import APPS

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R011")

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "craft_suite_api"
CORE_ONTOLOGY = PACKAGE / "ontology" / "artcraft.ttl"

CONNECTOR = "craft-suite-api"
CORE_IRI = "http://knuckles.team/kg/artcraft"
KG = "http://knuckles.team/kg#"

#: The engine's top-level classes. The engine ontology is served by the
#: engine itself, so the in-process orphan proof treats these as roots:
#: a pack class whose parent chain never reaches one of them is the
#: ``ONTOLOGY_ORPHAN`` the served import would report.
ENGINE_ROOTS = (
    "Application",
    "Tool",
    "Task",
    "CreativeWork",
    "Document",
    "Artifact",
)


def _run_check() -> tuple[int, str]:
    """The offline drift gate in-process; returns (exit code, output)."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "phase3_generate_app_content", REPO / "scripts" / "generate_app_content.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = module.main(["--check"])
    return code, buffer.getvalue()


def _skill_name(skill_md: Path) -> str:
    """The ``name`` entry of a skill's front matter."""
    lines = skill_md.read_text(encoding="utf-8").splitlines()
    assert lines and lines[0] == "---", f"{skill_md} has no front matter"
    for line in lines[1:]:
        if line == "---":
            break
        if ":" in line and not line.startswith((" ", "\t")):
            key, _, value = line.partition(":")
            if key.strip() == "name":
                return value.strip()
    return ""


def _graph(path: Path) -> rdflib.Graph:
    graph = rdflib.Graph()
    graph.parse(str(path), format="turtle")
    return graph


def _reachable_core_classes(core: rdflib.Graph) -> set[str]:
    """The engine roots plus every core class that walks up to one."""
    reachable: set[str] = {KG + name for name in ENGINE_ROOTS}
    moved = True
    while moved:
        moved = False
        for subj, _, parent in core.triples((None, RDFS.subClassOf, None)):
            if str(parent) in reachable and str(subj) not in reachable:
                reachable.add(str(subj))
                moved = True
    return reachable


def _app_ontology_clean(app: str, core: rdflib.Graph, reachable: set[str]) -> None:
    """R008's in-process orphan proof for one app ontology.

    The file imports the core module only, declares no core IRI again,
    gives every declared class a parent, and lets every parent reach the
    engine's core hierarchy.
    """
    graph = _graph(PACKAGE / "ontology" / f"artcraft-{app}.ttl")
    imports = {str(target) for _, _, target in graph.triples((None, OWL.imports, None))}
    assert imports == {CORE_IRI}, (app, imports)
    # No core IRI redeclared by the app module.
    core_subjects = {str(subj) for subj, _, _ in core}
    assert {str(subj) for subj, _, _ in graph} & core_subjects == set(), app
    classes = {subj for subj, _, obj in graph.triples((None, RDF.type, OWL.Class))}
    parents = {
        (subj, str(parent))
        for subj, _, parent in graph.triples((None, RDFS.subClassOf, None))
    }
    # No orphan class: every declared class names a parent ...
    assert classes <= {subj for subj, _ in parents}, app
    # ... and every parent reaches the engine's core hierarchy.
    assert all(parent in reachable for _, parent in parents), app


async def _build_pack() -> object:
    """The connector content pack of the packaged content (R008 entry)."""
    from scion_sdk.artifacts.pack import build_connector_content_pack
    from scion_sdk.mcp.content import ConnectorContent

    package = importlib.import_module("craft_suite_api")
    root = Path(list(package.__path__)[0])
    content = ConnectorContent.for_package(
        "craft_suite_api", root, importlib.metadata.version("craft-suite-api")
    )
    assert content.connector == CONNECTOR
    return await build_connector_content_pack(content)


def _engine_binary() -> str | None:
    """The loopback engine binary, or ``None`` when the served path is absent."""
    try:
        from medulla.server_binary import resolve_server_binary
    except ImportError:
        resolve_server_binary = None
    if resolve_server_binary is not None:
        try:
            return resolve_server_binary()
        except Exception:  # ServerBinaryNotFoundError
            pass
    for name in ("medulla-server", "medulla-server"):
        found = shutil.which(name)
        if found is not None:
            return found
    return None


async def _wait_for_engine(process: subprocess.Popen, socket_path: Path) -> object:
    """Connect to the engine once its loopback socket answers."""
    from medulla.client import MedullaClient

    deadline = time.monotonic() + 30.0
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise AssertionError("the loopback engine exited while starting")
        if socket_path.exists():
            try:
                return await asyncio.wait_for(
                    MedullaClient.connect(
                        socket_path=str(socket_path), auth_mode="none"
                    ),
                    timeout=5.0,
                )
            except (OSError, ConnectionError):
                pass
        await asyncio.sleep(0.2)
    raise AssertionError("the loopback engine did not serve its socket in time")


async def _served_import(engine_path: str, pack: object, tmp_path: Path) -> None:
    """The served ConnectorPack.Import plus the two class queries of R008."""
    from medulla.generated._shared import (
        AgentLibraryMutationContext,
        McpCatalogSnapshotBinding,
    )
    from medulla.generated.connector_pack import PackImportResultImported
    from scion_sdk.sinks.medulla import MedullaSink

    socket_path = tmp_path / "medulla.sock"
    persist_dir = tmp_path / "persist"
    persist_dir.mkdir()
    process = subprocess.Popen(
        [
            engine_path,
            "--socket-path",
            str(socket_path),
            "--persist-dir",
            str(persist_dir),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    client = None
    try:
        client = await _wait_for_engine(process, socket_path)

        zero_digest = "0" * 64
        principal = "phase3:person"
        tenant = "phase3:tenant"

        async def authority(_connector: str) -> tuple[object, object]:
            """One deterministic loopback authority for the import."""
            catalog = McpCatalogSnapshotBinding(
                authorization_scope_digest=zero_digest,
                catalog_generation=1,
                child_connection_generation=1,
                configuration_revision=1,
                snapshot_digest=zero_digest,
            )
            context = AgentLibraryMutationContext(
                actor_scope="phase3:content-import",
                attempt_nonce=zero_digest,
                caller_principal=principal,
                created_at_ms=0,
                idempotency_key="phase3:content-import",
                policy_decision_id="phase3:policy-decision",
                policy_digest=zero_digest,
                policy_revision="phase3:v1",
                principal=principal,
                purpose_id="phase3:content-import",
                request_id=1,
                tenant_id=tenant,
            )
            return catalog, context

        sink = MedullaSink(client, pack_import_authority=authority)
        result = await sink.import_pack(pack)

        # The import lands with a receipt binding this connector, and the
        # receipt holds no ontology warning (no ONTOLOGY_ORPHAN, no
        # ONTOLOGY_PACK_IMPORTS_CORE).
        assert isinstance(result, PackImportResultImported)
        receipt = result.receipt
        assert receipt.connector == CONNECTOR
        assert not [
            warning
            for warning in receipt.warnings
            if warning.code.value.startswith("ONTOLOGY")
        ]

        # The class queries over the served graph reach the new subclasses.
        for parent, child in (("Application", "App"), ("Task", "UseCase")):
            rows = await client.rdf.sparql(
                "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n"
                f"SELECT DISTINCT ?child WHERE {{ ?child rdfs:subClassOf <{KG}{parent}> }}"
            )
            assert f"{KG}{child}" in {row["child"] for row in rows}
    finally:
        if client is not None:
            await client.close()
        process.send_signal(signal.SIGTERM)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def test_all_apps_have_content_and_pack_imports_clean(tmp_path) -> None:
    # (1) R003 to R005: the generated ontology, skill and prompts per app.
    for app in APPS:
        ontology = PACKAGE / "ontology" / f"artcraft-{app}.ttl"
        skill = PACKAGE / "skills" / app / "SKILL.md"
        assert ontology.is_file(), app
        assert skill.is_file(), app
        assert _skill_name(skill) == app, app
        prompts = sorted((PACKAGE / "prompts").glob(f"{app}-*.json"))
        assert prompts, f"{app}: no prompt file"
        for prompt in prompts:
            assert (
                json.loads(prompt.read_text(encoding="utf-8"))["requires_namespace"]
                == app
            )

    # (2) R007: the offline drift gate is green on the committed content.
    code, out = _run_check()
    assert code == 0, out
    assert "CONTENT_DRIFT" not in out
    assert f"check clean: {len(APPS)} apps" in out

    # (3) R008: the pack of the packaged content, and its structure.
    pack = asyncio.run(_build_pack())
    entries = pack.archive.entries
    kinds = Counter(entry.kind.value for entry in entries)
    # The authored workflow content (CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R009)
    # ships beside the generated per-app content: two workflow ontology
    # modules and one <app>-<task> skill per proven workflow.
    workflow_modules = {"artcraft-workflows.ttl", "artcraft-workflows-vocabulary.ttl"}
    workflow_skills = {
        path.parent.name
        for path in (PACKAGE / "skills").glob("*-*/SKILL.md")
        if path.parent.name != "artcraft-starter"
    }
    assert workflow_skills
    assert kinds["ontology"] == 1 + len(APPS) + len(workflow_modules)
    assert kinds["skill"] == 1 + len(APPS) + len(workflow_skills)
    assert kinds["prompt"] >= len(APPS)
    ontology_uris = {entry.uri for entry in entries if entry.kind.value == "ontology"}
    assert ontology_uris == {f"ontology://{CONNECTOR}/artcraft.ttl"} | {
        f"ontology://{CONNECTOR}/artcraft-{app}.ttl" for app in APPS
    } | {f"ontology://{CONNECTOR}/{name}" for name in workflow_modules}
    skill_uris = {entry.uri for entry in entries if entry.kind.value == "skill"}
    assert skill_uris == {f"skill://{app}/SKILL.md" for app in APPS} | {
        "skill://artcraft-starter/SKILL.md"
    } | {f"skill://{name}/SKILL.md" for name in workflow_skills}
    assert "connector://resources" in {entry.uri for entry in entries}
    prompt_uris = [entry.uri for entry in entries if entry.kind.value == "prompt"]
    for app in APPS:
        assert any(
            uri.rsplit("/", 1)[-1].startswith(f"{app}-") for uri in prompt_uris
        ), app

    # The core file imports nothing; each app ontology is clean against it.
    core = _graph(CORE_ONTOLOGY)
    assert not list(core.triples((None, OWL.imports, None)))
    for app in APPS:
        _app_ontology_clean(app, core, _reachable_core_classes(core))

    # (4) The served import half of R008: only with the engine binary.
    binary = _engine_binary()
    if binary is None:
        pytest.skip(
            "served pack import not proven: the medulla server binary "
            "(medulla[server], e.g. medulla-server) is not "
            "installed; the in-process native engine exposes no "
            "ConnectorPack operation, so the import can only be "
            "proven served."
        )
    asyncio.run(_served_import(binary, pack, tmp_path))

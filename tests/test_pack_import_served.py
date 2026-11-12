"""CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R008: the packaged content imports cleanly and answers a class query.

The hot path of the content tier: the served ``ConnectorPack.Import`` of
the pack built from the packaged content (``scion_sdk.artifacts.pack``),
against a loopback medulla engine. The receipt must hold no ontology
warning (no ``ONTOLOGY_ORPHAN``), and the class queries over
``:Application`` and ``:Task`` must reach the pack's new subclasses
``:App`` and ``:UseCase``.

The served path needs the engine server binary (``medulla[server]``,
resolved by ``medulla.server_binary.resolve_server_binary``; the
deployment name is ``medulla-server``). Without it the test skips
with a clear reason: the in-process native engine exposes no
``ConnectorPack`` operation, so the import can only be proven served.
"""

from __future__ import annotations

import importlib
import importlib.metadata
import shutil
import signal
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R008")

#: The packaged connector's fleet name and ontology namespace.
CONNECTOR = "craft-suite-api"
KG = "http://knuckles.team/kg#"

#: One loopback tenant/principal for the import authority.
TENANT = "phase4:tenant"
PRINCIPAL = "phase4:person"

#: The two class queries of the spec row: each core class must reach the
#: pack's new subclass.
CLASS_QUERIES = (
    ("Application", "App"),
    ("Task", "UseCase"),
)


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
    # The deployment name of the same binary.
    for name in ("medulla-server", "medulla-server"):
        found = shutil.which(name)
        if found is not None:
            return found
    return None


async def _wait_for_engine(process: subprocess.Popen, socket_path: Path) -> Any:
    """Connect to the engine once its loopback socket answers."""
    import asyncio

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


@pytest.fixture
async def loopback_engine(tmp_path):
    """A loopback medulla engine on a private socket, or a clean skip."""
    binary = _engine_binary()
    if binary is None:
        pytest.skip(
            "the medulla server binary (medulla[server], e.g. "
            "medulla-server) is not installed; the served "
            "ConnectorPack.Import path needs a loopback engine"
        )

    socket_path = tmp_path / "medulla.sock"
    persist_dir = tmp_path / "persist"
    persist_dir.mkdir()
    process = subprocess.Popen(
        [binary, "--socket-path", str(socket_path), "--persist-dir", str(persist_dir)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    client = None
    try:
        client = await _wait_for_engine(process, socket_path)
        yield client
    finally:
        if client is not None:
            await client.close()
        process.send_signal(signal.SIGTERM)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


async def _pack() -> Any:
    """Capture the packaged content into its connector pack archive."""
    from scion_sdk.artifacts.pack import build_connector_content_pack
    from scion_sdk.mcp.content import ConnectorContent

    package = importlib.import_module("craft_suite_api")
    root = Path(list(package.__path__)[0])
    content = ConnectorContent.for_package(
        "craft_suite_api", root, importlib.metadata.version("craft-suite-api")
    )
    assert content.connector == CONNECTOR
    return await build_connector_content_pack(content)


async def _import_served(client: Any, pack: Any) -> Any:
    """The served ConnectorPack.Import through the SDK sink."""
    from medulla.generated._shared import (
        AgentLibraryMutationContext,
        McpCatalogSnapshotBinding,
    )
    from scion_sdk.sinks.medulla import MedullaSink

    zero_digest = "0" * 64

    async def authority(_connector: str) -> Any:
        """One deterministic loopback authority for the import."""
        catalog = McpCatalogSnapshotBinding(
            authorization_scope_digest=zero_digest,
            catalog_generation=1,
            child_connection_generation=1,
            configuration_revision=1,
            snapshot_digest=zero_digest,
        )
        context = AgentLibraryMutationContext(
            actor_scope="phase4:content-import",
            attempt_nonce=zero_digest,
            caller_principal=PRINCIPAL,
            created_at_ms=0,
            idempotency_key="phase4:content-import",
            policy_decision_id="phase4:policy-decision",
            policy_digest=zero_digest,
            policy_revision="phase4:v1",
            principal=PRINCIPAL,
            purpose_id="phase4:content-import",
            request_id=1,
            tenant_id=TENANT,
        )
        return catalog, context

    sink = MedullaSink(client, pack_import_authority=authority)
    return await sink.import_pack(pack)


async def test_pack_imports_without_orphans_and_class_query_reaches_subclasses(
    loopback_engine,
) -> None:
    """T-008: the receipt holds no ontology warning; the class queries reach the subclasses."""
    pack = await _pack()

    # The pack holds the core ontology, the eleven app ontologies, the
    # twelve skills and the prompts of the packaged content.
    kinds = Counter(entry.kind.value for entry in pack.archive.entries)
    assert kinds["ontology"] == 12
    assert kinds["skill"] == 12
    assert kinds["prompt"] >= 11

    result = await _import_served(loopback_engine, pack)

    # The import lands with a receipt binding this connector, and the
    # receipt holds no ontology warning (no ONTOLOGY_ORPHAN).
    from medulla.generated.connector_pack import PackImportResultImported

    assert isinstance(result, PackImportResultImported)
    receipt = result.receipt
    assert receipt.connector == CONNECTOR
    assert receipt.tenant_id == TENANT
    assert not [
        warning
        for warning in receipt.warnings
        if warning.code.value.startswith("ONTOLOGY")
    ]

    # The class queries over the served graph reach the new subclasses.
    rows_by_parent = {}
    for parent, child in CLASS_QUERIES:
        rows = await loopback_engine.rdf.sparql(
            "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n"
            f"SELECT DISTINCT ?child WHERE {{ ?child rdfs:subClassOf <{KG}{parent}> }}"
        )
        rows_by_parent[parent] = {row["child"] for row in rows}
        assert f"{KG}{child}" in rows_by_parent[parent]

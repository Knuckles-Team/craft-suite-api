"""CONN-CRAFT-SUITE-API-APPS-R012: phase 4 acceptance gate — arbora fleet integration.

Wiring proven here (CONN-CRAFT-SUITE-API-APPS-R008, seam contract
``specs/craft-suite-apps/contracts/arbora-fleet.md``):

- the facade registers with the gateway once, as the single fleet server
  ``craft-suite-api``; no app gets its own fleet entry;
- every proxied tool carries the metadata ``scion/upstream`` =
  ``{namespace, upstream}``; the gateway reads ``namespace`` as the item
  group, so ``fleet.tools.load``/``fleet.tools.unload`` with ``groups``
  load and unload one whole app (ARBORA-FLEET-R061);
- the org manifest's existing ``connectors`` entry satisfies the coverage
  gate ``fleet.status`` with ``require_full_coverage``
  (ARBORA-FLEET-R060);
- a pin names a namespaced tool id such as ``photocraft_read_demo`` and
  survives a gateway restart (ARBORA-FLEET-R059).

The deployment behind the gateway sets ``SCION_UPSTREAM_ACTIVATION=active``
(``docs/fleet-deployment.md``), so the gateway catalog holds every app's
tools. The gate runs against a loopback gateway: the arbora served intent
surface (the six verbs over the operation registry) composed in-process,
with the real facade as the one registered fleet server and fixture app
CLIs (never the real CLIs) behind it.

arbora is not a dependency of this repository and is not installed in the
default CI venv, so the module skips with a clear reason here and runs on
a loopback gateway host.
"""

from __future__ import annotations

import inspect
import json
import sys
from contextlib import asynccontextmanager
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastmcp import Client, FastMCP
from scion_sdk.upstream_wire import UPSTREAM_META_KEY, UPSTREAM_META_NAMESPACE_KEY

#: The eleven declared apps (CONN-CRAFT-SUITE-API-APPS-R002).
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

#: The single fleet server the facade registers under.
FACADE_SERVER = "craft-suite-api"

#: The fixture CLI's three tools; the registry prefixes them with the
#: namespace, so ``photocraft_read_demo`` is a namespaced tool id.
FIXTURE_TOOLS = ("read_demo", "write_demo", "ask_once")

#: One session key for the loopback caller; the pin is keyed per principal,
#: so the same key models the caller's session across a gateway restart.
SESSION_KEY = "phase4:session"

pytestmark = [
    pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R012"),
    pytest.mark.integration,
]


def _seam_probe() -> str | None:
    """Return ``None`` when the loopback gateway seam is usable, else a reason.

    The seam contract needs the installed arbora to carry the group
    load/unload arguments (ARBORA-FLEET-R061), the strict coverage flag
    (ARBORA-FLEET-R060.3) and the pin operation (ARBORA-FLEET-R059).
    """
    try:
        import arbora  # noqa: F401
    except ImportError:
        return (
            "arbora is not installed in this environment; the phase 4 gate "
            "runs on a loopback gateway host"
        )
    try:
        from arbora.api.ops.fleet import (
            FleetLoadParams,
            FleetStatusParams,
            FleetUnloadParams,
            operations,
        )
    except ImportError as exc:
        return f"installed arbora does not expose the fleet operations: {exc}"
    missing = []
    for name, params, field in (
        ("FleetLoadParams", FleetLoadParams, "groups"),
        ("FleetUnloadParams", FleetUnloadParams, "groups"),
        ("FleetStatusParams", FleetStatusParams, "require_full_coverage"),
    ):
        if field not in params.model_fields:
            missing.append(f"{name}.{field}")
    if missing:
        return (
            "installed arbora predates the gateway seam contract: "
            + ", ".join(missing)
            + " are missing"
        )
    if "fleet.tools.pin" not in {spec.id for spec in operations()}:
        return "installed arbora has no fleet.tools.pin operation (ARBORA-FLEET-R059)"
    return None


async def _facade_catalog() -> tuple[dict[str, Any], ...]:
    """The facade's real tool listing, the gateway's catalog source.

    With ``SCION_UPSTREAM_ACTIVATION=active`` the facade lists every app's
    tools; each proxied tool carries the ``scion/upstream`` metadata the
    gateway reads as the item group.
    """
    from craft_suite_api.mcp_server import build_server

    async with Client(build_server(command_args=[])) as client:
        tools = await client.list_tools()
    catalog = []
    for tool in tools:
        meta = getattr(tool, "meta", None) or {}
        upstream = meta.get(UPSTREAM_META_KEY)
        namespace = (
            upstream.get(UPSTREAM_META_NAMESPACE_KEY)
            if isinstance(upstream, dict)
            else None
        )
        catalog.append(
            {
                "name": tool.name,
                "description": tool.description or "",
                "schema": dict(tool.input_schema or {}),
                "group": namespace,
            }
        )
    return tuple(catalog)


def _catalog_items(catalog: tuple[dict[str, Any], ...]) -> tuple[Any, ...]:
    """Catalog items for the single fleet server, group from the metadata."""
    from arbora.fleet.catalog_items import CatalogItem

    fields = CatalogItem.__dataclass_fields__
    items = []
    for tool in catalog:
        kwargs: dict[str, Any] = {}
        if "group" in fields:
            # ARBORA-FLEET-R061: the catalog builder fills the group from
            # the scion/upstream metadata's namespace; the loopback
            # catalog carries the same value the production probe would.
            kwargs["group"] = tool["group"]
        items.append(
            CatalogItem(
                f"fleet:tool:{FACADE_SERVER}/{tool['name']}",
                "tool",
                tool["name"],
                description=tool["description"],
                server=FACADE_SERVER,
                schema=tool["schema"],
                **kwargs,
            )
        )
    return tuple(items)


class _LoopbackGateway:
    """One loopback arbora gateway with the facade registered as
    ``craft-suite-api``.

    The composition follows arbora's own served-test pattern (its
    ``tests/fleet/catalog_fixture.py`` binds the same production
    ``Registry``/``MCPProjection``/``MultiplexerOps``/``FleetGateway``
    pieces): the served intent verbs answer through the operation
    registry, and the session load state is the real ``SessionLoads``.
    ``compose()`` builds one gateway process; calling it again models a
    gateway restart over the same durable pin store.
    """

    def __init__(
        self,
        *,
        catalog: tuple[dict[str, Any], ...],
        items: tuple[Any, ...],
        caller: Any,
        pin_store: Any,
        multiplexer: Any,
    ) -> None:
        self.catalog = catalog
        self.items = items
        self.caller = caller
        self._pin_store = pin_store
        self._multiplexer = multiplexer

    # -- one gateway process --------------------------------------------------

    async def compose(self) -> tuple[FastMCP, Any]:
        from arbora.api.invoke import InvokeServices, invoke
        from arbora.api.invoke.audit import EffectReservation
        from arbora.api.mcp.registration import FleetMCPBinding, register_mcp_tools
        from arbora.api.mcp.verbs import MCPProjection
        from arbora.api.ops.fleet import handle_fleet_call, operations
        from arbora.api.policy import PolicyGate
        from arbora.api.registry import Registry
        from arbora.fleet.catalog_items import FleetCatalog
        from arbora.fleet.gateway_ops import FleetGateway, tool_for_multiplexer_ops
        from arbora.fleet.multiplexer import make_governed_tool_mount
        from arbora.fleet.multiplexer_ops import MultiplexerOps
        from arbora.fleet.session_loads import SessionLoads

        caller = self.caller
        state = SimpleNamespace(caller=caller, dispatches=[])

        async def allowed(*_args: Any) -> bool:
            return True

        async def source() -> tuple[Any, ...]:
            return self.items

        def native_name(item: Any) -> str:
            return f"phase4__{item.name}"

        async def bound_invoke(op: Any, params: Any, current: Any, surface: Any) -> Any:
            return await invoke(op, params, current, surface, services=state.services)

        async def forbidden(*_args: Any, **_kwargs: Any) -> Any:
            raise AssertionError("loopback gateway reached an unexpected port")

        async def dispatch(op: Any, params: Any, context: Any) -> Any:
            state.dispatches.append(op.id)
            return await handle_fleet_call(context, params, op)

        async def current(supplied: Any) -> Any:
            assert supplied.principal == caller.principal
            assert supplied.tenant == caller.tenant
            return supplied

        @asynccontextmanager
        async def as_caller(supplied: Any) -> Any:
            assert supplied.principal == caller.principal
            yield object()

        mcp = FastMCP("phase4-loopback-gateway")
        registry = Registry(operations())
        policy = PolicyGate(mode="none")

        # A fresh session state machine per gateway process; the pin store
        # is the durable (loopback-engine) side that survives the restart.
        ops_kwargs: dict[str, Any] = {}
        if "pin_store" in inspect.signature(MultiplexerOps).parameters:
            ops_kwargs["pin_store"] = self._pin_store
        ops = MultiplexerOps(
            catalog=FleetCatalog([source], allowed),
            sessions=SessionLoads(),
            loadable=allowed,
            callable_item=allowed,
            mount=make_governed_tool_mount(mcp, self._multiplexer, native_name),
            notify=allowed,
            invoke=bound_invoke,
            health=lambda: {},
            native_name=native_name,
            session_key_for=lambda request_caller: request_caller.session,
            **ops_kwargs,
        )

        async def never_called(*_args: Any, **_kwargs: Any) -> Any:
            raise AssertionError("the loopback gate never calls a child tool")

        gateway = FleetGateway(
            tool_for=tool_for_multiplexer_ops(ops),
            policy_check=allowed,
            delegated_call=never_called,
            catalog_ops=ops,
        )

        runtime = SimpleNamespace(
            service_scopes=frozenset(),
            bindings={"fleet_gateway": gateway},
            verify_current=current,
            as_caller=as_caller,
            as_service=forbidden,
            check_subject_access=forbidden,
            dispatch=dispatch,
        )
        services = InvokeServices(
            registry=registry,
            runtime=runtime,
            plans=SimpleNamespace(
                issue=forbidden, validate=forbidden, consume=forbidden
            ),
            policy_gate=policy,
            audit_preflight=AsyncMock(return_value="phase4:audit"),
            audit_write=AsyncMock(),
            external_effect_operations=frozenset({"fleet.call"}),
            effects=SimpleNamespace(
                reserve=AsyncMock(
                    return_value=EffectReservation("phase4:reservation", "acquired")
                ),
                complete=AsyncMock(),
            ),
            fleet_effect=gateway.effect,
        )
        state.services = services
        projection = MCPProjection(
            registry,
            services,
            SimpleNamespace(scope_ref=lambda *args, **kwargs: "phase4:scope"),
            lambda: caller,
            policy,
            invoke,
        )
        binding = FleetMCPBinding(
            projection, ops, lambda request_caller: request_caller.session
        )
        await register_mcp_tools(mcp, self._multiplexer, binding)
        return mcp, ops

    # -- small readers over the catalog ---------------------------------------

    def ids(self, group: str | None) -> set[str]:
        """The catalog item ids of one group (``None``: the ungrouped)."""
        return {
            item.id
            for item in self.items
            if (item.group if "group" in item.__dataclass_fields__ else None) == group
        }

    def id_of(self, tool: str) -> str:
        """The catalog item id of one namespaced tool name."""
        return f"fleet:tool:{FACADE_SERVER}/{tool}"


async def _verb(
    client: Any, name: str, op: str, params: dict[str, Any] | None = None
) -> Any:
    """Call one served intent verb; return the op result value.

    A refusal envelope (``ok`` false / error code) fails the call loudly
    with the code, so a seam regression is visible at the call site.
    """
    result = await client.call_tool(name, {"op": op, "params": params or {}})
    envelope = result.structured_content
    if envelope.get("ok") is not True:
        code = (envelope.get("error") or {}).get("code", "UNKNOWN")
        raise AssertionError(f"{name}(op={op!r}) refused: {code}: {envelope}")
    value = envelope["result"]
    return value["value"] if isinstance(value, dict) and "value" in value else value


@pytest.fixture
async def loopback_gateway(tmp_path, app_cli_factory, monkeypatch) -> _LoopbackGateway:
    """A loopback gateway with the facade registered once, or a skip."""
    reason = _seam_probe()
    if reason is not None:
        pytest.skip(reason)

    from arbora.api.invoke import VerifiedCaller

    # The facade, deployed exactly as docs/fleet-deployment.md describes:
    # fixture app CLIs on the PATH (never the real CLIs), every namespace
    # active, so the one server's tools/list holds all eleven apps' tools.
    monkeypatch.setenv("SCION_UPSTREAM_ACTIVATION", "active")
    for app in APPS:
        app_cli_factory(app)

    # The single fleet server entry, exactly once.
    config = {
        "mcpServers": {
            FACADE_SERVER: {
                "command": sys.executable,
                "args": ["-m", "craft_suite_api.mcp_server"],
            }
        }
    }
    config_path = tmp_path / "mcp_config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    # The org manifest entry the coverage gate counts (ARBORA-FLEET-R060):
    # the connector's existing connectors entry, nothing added.
    config_dir = tmp_path / "arbora-config"
    config_dir.mkdir()
    (config_dir / "workspace.yml").write_text(
        f"connectors:\n  - repo: {FACADE_SERVER}\n    mcp_server: {FACADE_SERVER}\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("ARBORA_CONFIG_DIR", str(config_dir))

    # The multiplexer admits the one server from its MCP config, mirroring
    # arbora's tests/fleet/catalog_fixture.py::_install (the fixture keeps
    # the durable EG catalog reader unbound; this gate is not about it).
    from arbora.fleet.multiplexer import MCPMultiplexer

    class _NeverRead:
        async def read(self) -> Any:
            raise AssertionError("this gate did not compose an EG catalog")

    multiplexer = MCPMultiplexer(_NeverRead())
    multiplexer._catalog = {}
    for name, entry in config["mcpServers"].items():
        if not multiplexer._catalog_entry_admissible(
            name, entry, {"mcp-multiplexer", "arbora"}
        ):
            continue
        admitted = multiplexer._admit_catalog_entry(name, entry, False)
        if admitted is not None:
            multiplexer._catalog[name] = admitted

    # The durable pin store: the loopback engine's side of the restart.
    from arbora.fleet.pin_store import InMemoryPinStore

    pin_store = InMemoryPinStore()

    catalog = await _facade_catalog()
    items = _catalog_items(catalog)

    scopes = frozenset({"mcp:discover", "mcp:delegate"})
    caller = VerifiedCaller(
        principal="phase4:person",
        tenant="phase4:tenant",
        effective_scopes=scopes,
        engine_claims={
            "principal": "phase4:person",
            "tenant": "phase4:tenant",
            "scopes": list(scopes),
            "policy_version": "phase4:v1",
            "delegation": False,
        },
        principal_kind="human",
        authenticated=True,
        delegated=False,
        credential_kind="session",
        policy_revision="phase4:v1",
        request_id="phase4:request",
        session=SESSION_KEY,
    )
    return _LoopbackGateway(
        catalog=catalog,
        items=items,
        caller=caller,
        pin_store=pin_store,
        multiplexer=multiplexer,
    )


async def test_arbora_loads_and_unloads_one_app_group(
    loopback_gateway: _LoopbackGateway,
) -> None:
    """T-008 / R008: group load and unload move one whole app at a time."""
    gateway = loopback_gateway
    mcp, _ops = await gateway.compose()
    async with Client(mcp) as client:
        # The catalog holds the facade's tools, one fleet server in all.
        found = await _verb(
            client,
            "find",
            "fleet.catalog.search",
            {"browse": True, "servers": [FACADE_SERVER], "limit": 100},
        )
        listed = {item["name"] for item in found["items"]}
        assert listed
        for app in APPS:
            for tool in FIXTURE_TOOLS:
                assert f"{app}_{tool}" in listed
        assert all(item.get("server") == FACADE_SERVER for item in found["items"])

        # ... and the gateway split it into the app groups.
        photocraft_ids = gateway.ids("photocraft")
        wordcraft_ids = gateway.ids("wordcraft")
        assert len(photocraft_ids) == len(FIXTURE_TOOLS)
        assert len(wordcraft_ids) == len(FIXTURE_TOOLS)
        assert photocraft_ids.isdisjoint(wordcraft_ids)

        # Loading the group loads only that app's tools.
        loaded = await _verb(
            client, "manage", "fleet.tools.load", {"groups": ["photocraft"]}
        )
        assert set(loaded["loaded"]) == photocraft_ids
        assert not set(loaded["loaded"]) & wordcraft_ids

        # An unknown group is an empty result, not an error.
        empty = await _verb(
            client, "manage", "fleet.tools.load", {"groups": ["no_such_app"]}
        )
        assert empty["loaded"] == []

        # A second app loads alongside; unloading the first leaves it.
        await _verb(client, "manage", "fleet.tools.load", {"groups": ["wordcraft"]})
        await _verb(client, "manage", "fleet.tools.unload", {"groups": ["photocraft"]})
        status = await _verb(client, "ask", "fleet.status", {})
        session = status["session"]
        assert {row["id"] for row in session["loaded"]} == wordcraft_ids


async def test_coverage_passes_and_pin_survives_restart(
    loopback_gateway: _LoopbackGateway,
) -> None:
    """T-012 / R012: strict status passes; the pinned tool survives restart."""
    gateway = loopback_gateway
    pinned_id = gateway.id_of("photocraft_read_demo")

    # --- first gateway process: strict status and the pin --------------------
    mcp, _ops = await gateway.compose()
    async with Client(mcp) as client:
        status = await _verb(
            client, "ask", "fleet.status", {"require_full_coverage": True}
        )
        coverage = status["coverage"]
        assert coverage["ok"] is True
        assert coverage["missing"] == []
        assert coverage["zero_tools"] == []

        await _verb(client, "manage", "fleet.tools.pin", {"items": [pinned_id]})

    # --- gateway restart: fresh session state, same durable pin store --------
    restarted, restarted_ops = await gateway.compose()
    await restarted_ops.restore_pins(gateway.caller, SESSION_KEY)
    async with Client(restarted) as client:
        status = await _verb(client, "ask", "fleet.status", {})
        loaded = {row["id"] for row in status["session"]["loaded"]}
        assert pinned_id in loaded

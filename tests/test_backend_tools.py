"""The backend API served as one typed tool per operation.

CONN-CRAFT-SUITE-API-R007 (coverage and typed schemas), R008 (write
governance: typed refusals and audit) and R009 (hot-path proof).
"""

from __future__ import annotations

import base64
import json
import logging
import time
from pathlib import Path

import httpx
import pytest
from fastmcp import Client

from craft_suite_api.backend import (
    NAMESPACE,
    WRITES_DISABLED,
    backend_document,
    operation_classes,
    operation_count,
    operation_id,
    tool_names,
)
from craft_suite_api.error_authority import BACKEND_NOT_CONFIGURED

from .conftest import ORIGIN

TYPED_KEYS = ("type", "$ref", "anyOf", "oneOf", "allOf", "const", "enum")
TAGS = {"success": True, "tags": [], "maybe_cursor": None}


def _untyped(schema: dict) -> list[str]:
    return [
        name
        for name, prop in schema.get("properties", {}).items()
        if not any(key in prop for key in TYPED_KEYS)
    ]


def _never(request: httpx.Request) -> httpx.Response:
    raise AssertionError(f"no request may be sent: {request.method} {request.url}")


@pytest.mark.spec("CONN-CRAFT-SUITE-API-R007")
async def test_every_operation_is_one_typed_tool(backend):
    server = backend(_never, configured=False)
    async with Client(server) as client:
        tools = await client.list_tools()
    names = [tool.name for tool in tools]
    assert len(names) == len(set(names))
    assert len(tools) >= operation_count() >= 268
    assert set(tool_names().values()) <= set(names)
    assert all(len(f"{NAMESPACE}_{name}") <= 64 for name in names)
    for tool in tools:
        assert tool.input_schema["type"] == "object", tool.name
        assert _untyped(tool.input_schema) == [], tool.name
        assert tool.output_schema is not None, tool.name
        read_only = operation_classes()[operation_id(tool.name)] == "read"
        assert tool.annotations.readOnlyHint is read_only, tool.name
        assert ("confirm" in tool.input_schema["properties"]) is not read_only


@pytest.mark.spec("CONN-CRAFT-SUITE-API-R007")
def test_served_document_is_built_from_the_pinned_source():
    import hashlib

    from craft_suite_api.backend_spec import pinned_source

    # Nothing generated is committed: the served description is repaired from
    # the shipped published document at first use, after its pin is checked.
    package = Path(__file__).resolve().parents[1] / "craft_suite_api"
    assert not (package / "backend_openapi.json").exists()
    data, provenance = pinned_source()
    assert hashlib.sha256(data).hexdigest() == provenance["sha256"]
    document = backend_document()
    assert "servers" not in document
    assert document["components"]["securitySchemes"]["signed_session"]["name"] == (
        "session"
    )


@pytest.mark.spec("CONN-CRAFT-SUITE-API-R008")
async def test_unconfigured_backend_refuses_typed(backend):
    server = backend(_never, configured=False)
    async with Client(server) as client:
        result = await client.call_tool("list_tags_handler", {})
    assert result.structured_content == {
        "cancelled": True,
        "operation": f"{NAMESPACE}_list_tags_handler",
        "reason": BACKEND_NOT_CONFIGURED,
        "write_class": "read",
    }


@pytest.mark.spec("CONN-CRAFT-SUITE-API-R008")
@pytest.mark.parametrize(
    ("tool", "arguments", "klass"),
    [
        ("omni_api_image_generate_handler", {"prompt": "a lighthouse"}, "generation"),
        (
            "omni_upload_image_media_file_handler",
            {"uuid_idempotency_token": "u1", "file": "aGk="},
            "upload",
        ),
        ("logout_handler", {}, "account"),
    ],
)
async def test_writes_disabled_refuse_typed_and_audit(
    backend, caplog, tool, arguments, klass
):
    server = backend(_never, allow_writes=False)
    caplog.set_level(logging.INFO, logger="craft_suite_api.audit")
    async with Client(server) as client:
        result = await client.call_tool(
            tool, {**arguments, "confirm": True}, raise_on_error=False
        )
    assert result.structured_content == {
        "cancelled": True,
        "operation": f"{NAMESPACE}_{tool}",
        "reason": WRITES_DISABLED,
        "write_class": klass,
    }
    record = [r for r in caplog.records if r.name == "craft_suite_api.audit"][-1]
    assert (record.getMessage(), record.tool, record.write_class) == (
        "refused",
        f"{NAMESPACE}_{tool}",
        klass,
    )


@pytest.mark.spec("CONN-CRAFT-SUITE-API-R008")
async def test_unconfirmed_write_is_refused_then_confirm_sends(backend, caplog):
    sent: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        return httpx.Response(200, json={"success": True, "removed_count": 0})

    server = backend(respond, allow_writes=True)
    caplog.set_level(logging.INFO, logger="craft_suite_api.audit")
    tool = "clear_media_file_tags_handler"
    async with Client(server) as client:
        refused = await client.call_tool(
            tool, {"media_file_token": "m1"}, raise_on_error=False
        )
        assert refused.structured_content["cancelled"] is True
        assert refused.structured_content["write_class"] == "write"
        assert sent == []
        await client.call_tool(
            tool, {"media_file_token": "m1", "confirm": True}, raise_on_error=False
        )
    assert [(r.method, r.url.path) for r in sent] == [
        ("POST", "/v1/tags/media_file/clear/m1")
    ]
    assert "confirm" not in sent[0].url.params
    audit = [r for r in caplog.records if r.name == "craft_suite_api.audit"]
    assert [r.getMessage() for r in audit] == ["unconfirmed", "sent"]


@pytest.mark.spec("CONN-CRAFT-SUITE-API-R008")
async def test_upload_sends_the_decoded_file_as_a_binary_part(backend):
    sent: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        return httpx.Response(200, json={"success": True, "media_file_token": "f1"})

    server = backend(respond, allow_writes=True)
    payload = bytes(range(256))
    async with Client(server) as client:
        await client.call_tool(
            "omni_upload_image_media_file_handler",
            {
                "uuid_idempotency_token": "u1",
                "file": base64.b64encode(payload).decode(),
                "confirm": True,
            },
            raise_on_error=False,
        )
    (request,) = sent
    assert request.url.path == "/v1/omni_api/upload/image"
    assert request.headers["content-type"].startswith("multipart/form-data")
    assert payload in request.content


@pytest.mark.spec("CONN-CRAFT-SUITE-API-R009")
async def test_hot_path_read_reaches_the_exact_route_with_the_session(backend):
    sent: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        return httpx.Response(200, json=TAGS)

    server = backend(respond)
    async with Client(server) as client:
        started = time.perf_counter()
        result = await client.call_tool("list_tags_handler", {})
        elapsed = time.perf_counter() - started
    (request,) = sent
    assert str(request.url) == f"{ORIGIN}/v1/tags/list"
    assert request.headers["session"] == "synthetic-session"
    assert json.loads(json.dumps(result.structured_content)) == TAGS
    assert elapsed < 1.0

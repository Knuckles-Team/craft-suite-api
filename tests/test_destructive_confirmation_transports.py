"""Destructive writes over real transports (CONN-CRAFT-SUITE-API-R006).

The connector server runs as a subprocess three ways (stdio, unauthenticated
streamable HTTP on loopback, JWT streamable HTTP against a local JWKS) in front
of an in-process fake upstream that records every request. A real fastmcp client
that cannot elicit is refused cleanly with no upstream request until it repeats
the call with ``confirm=true``; a client that can elicit is asked and then writes.
"""

from __future__ import annotations

import base64
import json
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

import httpx
import pytest
from fastmcp import Client
from fastmcp.client.transports import StdioTransport, StreamableHttpTransport
from fastmcp.server.auth.providers.jwt import RSAKeyPair

from .test_source_contract import response_for

ISSUER = "https://idp.example.invalid/realms/homelab"
AUDIENCE = "agent-services"
ACTION = "get_folder_handler"
TOOL = f"craft_suite_{ACTION}"
ARGUMENTS = {"path": {"folder_token": "fixture_token"}}
CALL_TIMEOUT = 60

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-R006")


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _serve(handler: type[BaseHTTPRequestHandler]) -> HTTPServer:
    server = HTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


class _Upstream:
    """Fake provider recording every request it receives."""

    def __init__(self) -> None:
        self.requests: list[str] = []
        body = json.dumps(response_for(ACTION)).encode()
        recorded = self.requests

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802 - http.server API
                recorded.append(self.path)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_args: Any) -> None:
                return

        self.server = _serve(Handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"


def _jwks(keys: RSAKeyPair) -> dict[str, Any]:
    from cryptography.hazmat.primitives import serialization

    numbers = serialization.load_pem_public_key(
        keys.public_key.encode()
    ).public_numbers()

    def b64(value: int) -> str:
        raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

    return {
        "keys": [
            {
                "kty": "RSA",
                "kid": "test-key",
                "use": "sig",
                "alg": "RS256",
                "n": b64(numbers.n),
                "e": b64(numbers.e),
            }
        ]
    }


@pytest.fixture
def upstream():
    fake = _Upstream()
    yield fake
    fake.server.shutdown()


@pytest.fixture
def jwt_world():
    keys = RSAKeyPair.generate()
    body = json.dumps(_jwks(keys)).encode()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - http.server API
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args: Any) -> None:
            return

    server = _serve(Handler)
    token = keys.create_token(
        subject="arbora-service-account-id",
        issuer=ISSUER,
        audience=AUDIENCE,
        additional_claims={"azp": "arbora", "client_id": "arbora", "tenant_id": "t"},
        kid="test-key",
    )
    yield f"http://127.0.0.1:{server.server_address[1]}/jwks", token
    server.shutdown()


def _executable() -> str:
    found = Path(sys.executable).parent / "craft-suite-mcp"
    return str(found) if found.exists() else shutil.which("craft-suite-mcp") or ""


def _env(tmp_path: Path, upstream: _Upstream) -> dict[str, str]:
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("CRAFT_SUITE_", "AUTH_", "FASTMCP_", "MCP_"))
    }
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    env.update(
        HOME=str(home),
        XDG_CONFIG_HOME=str(tmp_path / "config"),
        CRAFT_SUITE_API_BASE_URL=upstream.url,
        CRAFT_SUITE_API_ALLOW_WRITES="true",
        CRAFT_SUITE_API_ALLOW_PLAINTEXT="true",
        CRAFT_SUITE_FIXTURE_SESSION="synthetic-session",
        CRAFT_SUITE_API_TOKEN_REF="env://CRAFT_SUITE_FIXTURE_SESSION",
        ENABLE_DELEGATION="false",
        MCP_FLEET_REGISTRATION="false",
        PYTHONUNBUFFERED="1",
    )
    return env


class _HttpServer:
    def __init__(self, argv: list[str], env: dict[str, str], tmp_path: Path) -> None:
        port = _free_port()
        self.url = f"http://127.0.0.1:{port}/mcp"
        self.log_path = tmp_path / f"server-{port}.log"
        self.log = self.log_path.open("w+", encoding="utf-8", errors="replace")
        full = [
            *argv,
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--allowed-hosts",
            f"127.0.0.1:{port},localhost:{port}",
        ]
        self.proc = subprocess.Popen(
            [_executable(), "--transport", "streamable-http", *full],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=self.log,
            text=True,
        )
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if self.proc.poll() is not None:
                raise AssertionError(f"server exited: {self.stop()}")
            try:
                httpx.get(f"http://127.0.0.1:{port}/health", timeout=1)
                return
            except httpx.HTTPError:
                time.sleep(0.2)
        raise AssertionError(f"server did not start: {self.stop()}")

    def stop(self) -> str:
        self.proc.terminate()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait()
        self.log.close()
        err = self.log_path.read_text(encoding="utf-8", errors="replace")
        print(f"--- server stderr ---\n{err[-6000:]}")
        return err


async def _accept(message: str, response_type: Any, params: Any, context: Any) -> Any:
    return response_type(confirmed=True) if response_type else None


async def _flow(open_client: Any, upstream: _Upstream, *, elicits: bool) -> None:
    kwargs: dict[str, Any] = {"timeout": CALL_TIMEOUT}
    if elicits:
        kwargs["elicitation_handler"] = _accept
    async with open_client(**kwargs) as client:
        if elicits:
            written = await client.call_tool(TOOL, ARGUMENTS, raise_on_error=False)
            assert not written.is_error, written.content
            assert written.structured_content["data"] == response_for(ACTION)
            assert len(upstream.requests) == 1
            return
        refused = await client.call_tool(TOOL, ARGUMENTS, raise_on_error=False)
        assert not refused.is_error, refused.content
        assert refused.structured_content["cancelled"] is True
        assert "confirm=true" in refused.structured_content["reason"]
        assert upstream.requests == [], "an unconfirmed write must not be sent"
        confirmed = await client.call_tool(
            TOOL, {**ARGUMENTS, "confirm": True}, raise_on_error=False
        )
        assert not confirmed.is_error, confirmed.content
        assert confirmed.structured_content["data"] == response_for(ACTION)
        assert upstream.requests == ["/v1/folders/folder/fixture_token"], (
            "confirm must not be forwarded upstream"
        )


@pytest.mark.timeout(180)
@pytest.mark.parametrize("elicits", [False, True])
async def test_stdio_no_auth_destructive_call(tmp_path, upstream, elicits):
    def open_client(**kwargs: Any) -> Client[Any]:
        transport = StdioTransport(
            command=_executable(),
            args=["--transport", "stdio"],
            env=_env(tmp_path, upstream),
        )
        return Client(transport, **kwargs)

    await _flow(open_client, upstream, elicits=elicits)


@pytest.mark.timeout(180)
@pytest.mark.parametrize("elicits", [False, True])
async def test_http_no_auth_localhost_destructive_call(tmp_path, upstream, elicits):
    server = _HttpServer(["--auth-type", "none"], _env(tmp_path, upstream), tmp_path)
    try:

        def open_client(**kwargs: Any) -> Client[Any]:
            return Client(StreamableHttpTransport(server.url), **kwargs)

        await _flow(open_client, upstream, elicits=elicits)
    finally:
        server.stop()


@pytest.mark.timeout(180)
@pytest.mark.parametrize("elicits", [False, True])
async def test_http_jwt_destructive_call(tmp_path, upstream, jwt_world, elicits):
    jwks_uri, token = jwt_world
    argv = [
        "--auth-type",
        "jwt",
        "--token-issuer",
        ISSUER,
        "--token-audience",
        AUDIENCE,
        "--token-jwks-uri",
        jwks_uri,
    ]
    server = _HttpServer(argv, _env(tmp_path, upstream), tmp_path)
    try:

        def open_client(**kwargs: Any) -> Client[Any]:
            return Client(StreamableHttpTransport(server.url, auth=token), **kwargs)

        await _flow(open_client, upstream, elicits=elicits)
    finally:
        server.stop()

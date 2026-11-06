"""CONN-CRAFT-SUITE-API-R001: credential references resolve through the SDK."""

import asyncio
from unittest.mock import MagicMock, patch

import httpx
import pytest

import craft_suite_api.auth as auth_module


@pytest.fixture(autouse=True)
def configured(monkeypatch):
    monkeypatch.setattr(auth_module, "load_config", lambda: None)
    monkeypatch.setenv("CRAFT_SUITE_API_BASE_URL", "https://service.example.invalid")
    monkeypatch.setenv("CRAFT_SUITE_API_TOKEN_REF", "env://SCAFFOLD_TEST_TOKEN")
    monkeypatch.setenv("SCAFFOLD_TEST_TOKEN", "test-token")
    monkeypatch.setenv("ENABLE_DELEGATION", "false")
    monkeypatch.delenv("CRAFT_SUITE_API_ALLOW_PLAINTEXT", raising=False)
    yield
    auth_module.close_client()


@pytest.mark.concept("CRAFT-SUITE-API-001")
@pytest.mark.spec("CONN-CRAFT-SUITE-API-R001")
def test_client_resolves_reference_and_cleans_up():
    seen = []

    def respond(request):
        seen.append(request)
        return httpx.Response(200, json={})

    tls = auth_module.resolve_tls_profile("craft-suite-api")
    tls_mock = MagicMock(wraps=tls, ssl_context=tls.ssl_context, proxy_url=None)
    with patch.object(auth_module, "resolve_tls_profile", return_value=tls_mock):
        client = auth_module.build_client(
            auth_module.backend_settings(), transport=httpx.MockTransport(respond)
        )

    async def call():
        async with client:
            await client.get("/v1/tags/list")

    asyncio.run(call())
    assert seen[0].headers["session"] == "test-token"
    assert "test-token" not in repr(client.auth)
    tls_mock.cleanup.assert_not_called()
    auth_module.close_client()
    tls_mock.cleanup.assert_called_once()


@pytest.mark.spec("CONN-CRAFT-SUITE-API-R001")
def test_missing_reference_sends_no_credential(monkeypatch):
    monkeypatch.delenv("CRAFT_SUITE_API_TOKEN_REF")
    seen = []

    def respond(request):
        seen.append(request)
        return httpx.Response(200, json={})

    client = auth_module.build_client(
        auth_module.backend_settings(), transport=httpx.MockTransport(respond)
    )

    async def call():
        async with client:
            await client.get("/v1/tags/list")

    asyncio.run(call())
    assert "session" not in seen[0].headers

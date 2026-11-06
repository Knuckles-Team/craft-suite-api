"""CONN-CRAFT-SUITE-API-R002: bounded backend requests through the real client."""

import asyncio

import httpx
import pytest

import craft_suite_api.auth as auth_module

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-R002")


@pytest.fixture
def make(monkeypatch):
    monkeypatch.setattr(auth_module, "load_config", lambda: None)
    monkeypatch.setenv("CRAFT_SUITE_FIXTURE_SESSION", "fixture-session")
    monkeypatch.setenv("CRAFT_SUITE_API_TOKEN_REF", "env://CRAFT_SUITE_FIXTURE_SESSION")
    monkeypatch.setenv("ENABLE_DELEGATION", "false")
    monkeypatch.delenv("CRAFT_SUITE_API_ALLOW_PLAINTEXT", raising=False)

    def create(respond, base_url="https://service.example.invalid"):
        monkeypatch.setenv("CRAFT_SUITE_API_BASE_URL", base_url)
        return auth_module.build_client(
            auth_module.backend_settings(), transport=httpx.MockTransport(respond)
        )

    yield create
    auth_module.close_client()


def _get(client, path="/v1/tags/list"):
    async def call():
        async with client:
            return await client.get(path)

    return asyncio.run(call())


def test_oversized_response_rejected(make):
    def declared(request):
        return httpx.Response(
            200, headers={"content-length": str(auth_module.MAX_BYTES + 1)}
        )

    with pytest.raises(auth_module.ResponseTooLarge):
        _get(make(declared))

    async def chunks():
        for _ in range(17):
            yield b"x" * 1024 * 1024

    def streamed(request):
        return httpx.Response(200, content=chunks())

    with pytest.raises(auth_module.ResponseTooLarge):
        _get(make(streamed))


def test_redirect_not_followed(make):
    seen = []

    def respond(request):
        seen.append(request.url.path)
        return httpx.Response(302, headers={"location": "https://elsewhere.invalid/x"})

    response = _get(make(respond))
    assert response.status_code == 302
    assert seen == ["/v1/tags/list"]


def test_response_deadline_enforced(make):
    client = make(lambda request: httpx.Response(200))
    assert client.timeout.read == auth_module.TIMEOUT_S
    assert client.timeout.connect == auth_module.TIMEOUT_S


@pytest.mark.parametrize(
    "base_url",
    ["https://service.example.invalid/api", "https://service.example.invalid/?q=1"],
)
def test_invalid_provider_origin_rejected(make, base_url):
    with pytest.raises(ValueError, match="origin without a path"):
        make(lambda request: httpx.Response(200), base_url=base_url)


def test_plaintext_credential_refused(make):
    with pytest.raises(ValueError, match="allow_plaintext"):
        make(lambda request: httpx.Response(200), base_url="http://service.invalid")

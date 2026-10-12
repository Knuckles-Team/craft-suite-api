"""Transport boundaries exercised through the production operation-bound client."""

import ssl

import httpx
import pytest
from agent_connector_sdk.auth.static import api_key_auth
from agent_connector_sdk.http.errors import TlsVerificationError
from agent_connector_sdk.tls.errors import TransportSecurityError
from agent_connector_sdk.tls.resolve import resolve_tls_profile

from artcraft_api import openapi_runtime
from artcraft_api.api import ApiClientSystem

ACTION = "omni_gen_audio_models_handler"
PAYLOAD = {"success": True, "models": [{"model": "suno_music"}], "providers": []}


@pytest.fixture
def client_factory(monkeypatch):
    monkeypatch.setenv("ARTCRAFT_FIXTURE_SESSION", "fixture-session")
    clients = []

    def create(
        handler, base_url="https://service.example.invalid", *, allow_plaintext=False
    ):
        client = ApiClientSystem(
            base_url,
            api_key_auth("env://ARTCRAFT_FIXTURE_SESSION", header="session"),
            credential_scheme="signed_session",
            transport=httpx.MockTransport(handler),
            allow_plaintext=allow_plaintext,
        )
        clients.append(client)
        return client

    yield create
    for client in clients:
        client.close()


def execute(client, **arguments):
    return client.execute("omni_gen", {"action": ACTION, **arguments})


def test_request_returns_json_and_uses_sdk_auth(client_factory):
    def respond(request):
        assert request.url == httpx.URL(
            "https://service.example.invalid/v1/omni_gen/models/audio"
        )
        assert request.headers["session"] == "fixture-session"
        assert "authorization" not in request.headers
        assert all(value == 30.0 for value in request.extensions["timeout"].values())
        return httpx.Response(200, json=PAYLOAD)

    client = client_factory(respond)
    assert execute(client)["data"] == PAYLOAD
    assert client.session.follow_redirects is False
    assert client.session.trust_env is False


@pytest.mark.parametrize(
    "path",
    [
        "https://other.example.invalid/catalog",
        "//other.example.invalid/catalog",
        "https://service.example.invalid:8443/catalog",
        "http://service.example.invalid/catalog",
    ],
)
def test_catalogued_path_cannot_escape_origin(client_factory, monkeypatch, path):
    calls = []
    client = client_factory(lambda request: calls.append(request))
    monkeypatch.setitem(openapi_runtime.CONTRACT["operations"][ACTION], "path", path)
    with pytest.raises(ValueError, match="configured provider origin"):
        execute(client)
    assert not calls


@pytest.mark.parametrize(
    "target",
    [
        "https://user:secret@service.example.invalid",
        "https://service.example.invalid/prefix",
        "https://service.example.invalid?key=secret",
        "https://service.example.invalid#fragment",
    ],
)
def test_invalid_provider_origin_rejected(client_factory, target):
    with pytest.raises(ValueError):
        client_factory(lambda request: httpx.Response(200), target)


def test_redirect_not_followed(client_factory):
    calls = []

    def respond(request):
        calls.append(request)
        return httpx.Response(
            302, headers={"location": "https://other.example.invalid"}
        )

    with pytest.raises(RuntimeError, match="HTTP 302"):
        execute(client_factory(respond))
    assert len(calls) == 1


@pytest.mark.parametrize("options", [{"follow_redirects": True}, {"timeout": None}])
def test_request_rejects_safety_overrides(client_factory, options):
    calls = []
    client = client_factory(lambda request: calls.append(request))
    with pytest.raises(ValueError):
        execute(client, **options)
    assert not calls


def test_plaintext_remote_rejected(client_factory):
    with pytest.raises(ValueError, match="plaintext"):
        client_factory(
            lambda request: httpx.Response(200), "http://service.example.invalid"
        )


def test_plaintext_opt_in_stays_on_configured_origin(client_factory, monkeypatch):
    calls = []

    def respond(request):
        calls.append(request)
        return httpx.Response(200, json=PAYLOAD)

    client = client_factory(
        respond, "http://service.example.invalid", allow_plaintext=True
    )
    assert execute(client)["data"] == PAYLOAD
    assert calls[0].url.scheme == "http"
    monkeypatch.setitem(
        openapi_runtime.CONTRACT["operations"][ACTION],
        "path",
        "https://service.example.invalid/catalog",
    )
    with pytest.raises(ValueError, match="configured provider origin"):
        execute(client)
    assert len(calls) == 1


def test_plaintext_opt_in_does_not_downgrade_https(client_factory):
    calls = []

    def fail_tls(request):
        calls.append(request)
        try:
            raise ssl.SSLCertVerificationError("certificate verification failed")
        except ssl.SSLCertVerificationError as exc:
            raise httpx.ConnectError("TLS handshake failed", request=request) from exc

    with pytest.raises(TlsVerificationError):
        execute(client_factory(fail_tls, allow_plaintext=True))
    assert len(calls) == 1
    assert calls[0].url.scheme == "https"


def test_tls_cannot_disable_verification():
    with pytest.raises(TransportSecurityError):
        resolve_tls_profile("artcraft", profile={"verify": False})
    profile = resolve_tls_profile("artcraft", profile={"trust_env": False})
    try:
        assert profile.ssl_context.verify_mode == ssl.CERT_REQUIRED
        assert profile.ssl_context.check_hostname
        assert profile.ssl_context.minimum_version >= ssl.TLSVersion.TLSv1_2
    finally:
        profile.cleanup()


def test_oversized_response_rejected(client_factory, monkeypatch):
    monkeypatch.setattr(openapi_runtime, "MAX_BYTES", 8)
    with pytest.raises(RuntimeError, match="response limit"):
        execute(
            client_factory(lambda request: httpx.Response(200, content=b"too large"))
        )


def test_stream_without_length_still_bounded(client_factory, monkeypatch):
    class Chunks(httpx.SyncByteStream):
        def __iter__(self):
            yield b"first"
            yield b"second"

    monkeypatch.setattr(openapi_runtime, "MAX_BYTES", 8)
    with pytest.raises(RuntimeError, match="response limit"):
        execute(client_factory(lambda request: httpx.Response(200, stream=Chunks())))


def test_response_deadline_enforced(client_factory, monkeypatch):
    class SlowChunk(httpx.SyncByteStream):
        def __iter__(self):
            monkeypatch.setattr(openapi_runtime.time, "monotonic", lambda: float("inf"))
            yield b"late"

    with pytest.raises(RuntimeError, match="response limit"):
        execute(client_factory(lambda request: httpx.Response(200, stream=SlowChunk())))

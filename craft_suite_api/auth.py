"""The backend client: SDK credential references, TLS and bounded transport.

CONN-CRAFT-SUITE-API-R001 (credential references) and R002 (bounded
requests). The SDK owns HTTP, auth and TLS; this module only picks the
settings and adds the response-size bound.
"""

from __future__ import annotations

from contextlib import ExitStack
from urllib.parse import urlsplit

import httpx
from scion_sdk.auth.delegation import DelegatedTokenAuth, DelegationSettings
from scion_sdk.auth.static import api_key_auth
from scion_sdk.config import load_config, setting
from scion_sdk.http.client import build_http_client
from scion_sdk.http.options import HttpClientOptions
from scion_sdk.http.retry import RetryPolicy
from scion_sdk.tls.resolve import resolve_tls_profile

from .bounds import MAX_BYTES, ResponseTooLarge, bound_response

__all__ = [
    "MAX_BYTES",
    "PLACEHOLDER_ORIGIN",
    "TIMEOUT_S",
    "BackendSettings",
    "ResponseTooLarge",
    "backend_settings",
    "build_client",
    "close_client",
]

TIMEOUT_S = 30.0
#: The origin an unconfigured connector's tools are built against; every call
#: is refused before it is used.
PLACEHOLDER_ORIGIN = "https://backend.not-configured.invalid"
SESSION_HEADER = "session"

_resources = ExitStack()


class BackendSettings:
    """The operator's backend settings, read once."""

    def __init__(self) -> None:
        load_config()
        self.base_url: str = setting("CRAFT_SUITE_API_BASE_URL", "")
        self.token_ref: str = setting("CRAFT_SUITE_API_TOKEN_REF", "")
        self.allow_writes: bool = bool(setting("CRAFT_SUITE_API_ALLOW_WRITES", False))
        self.allow_plaintext: bool = bool(
            setting("CRAFT_SUITE_API_ALLOW_PLAINTEXT", False)
        )

    @property
    def configured(self) -> bool:
        return bool(self.base_url)


def backend_settings() -> BackendSettings:
    return BackendSettings()


def _check_origin(settings: BackendSettings, credentialed: bool) -> None:
    parsed = urlsplit(settings.base_url)
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ValueError("Base URL must be the backend origin without a path")
    if credentialed and parsed.scheme == "http" and not settings.allow_plaintext:
        raise ValueError("Credential-bearing plaintext HTTP requires allow_plaintext")


def _auth(settings: BackendSettings, resources: ExitStack) -> httpx.Auth | None:
    delegation = DelegationSettings.from_settings()
    if delegation.enabled:
        token_tls = resolve_tls_profile("oidc")
        resources.callback(token_tls.cleanup)
        token_client = build_http_client(
            HttpClientOptions(base_url=delegation.token_endpoint, tls=token_tls)
        )
        resources.callback(token_client.close)
        return DelegatedTokenAuth(delegation, http_client=token_client)
    if settings.token_ref:
        return api_key_auth(settings.token_ref, header=SESSION_HEADER)
    return None


def build_client(
    settings: BackendSettings, *, transport: httpx.AsyncBaseTransport | None = None
) -> httpx.AsyncClient:
    """The governed async client the backend tools send through.

    One attempt, no redirects, a 30 s timeout and a 16 MiB response bound.
    An unconfigured backend gets a client on a placeholder origin that the
    governance middleware never lets a call reach.
    """
    global _resources
    if not settings.configured:
        return httpx.AsyncClient(base_url=PLACEHOLDER_ORIGIN, transport=transport)
    with ExitStack() as resources:
        auth = _auth(settings, resources)
        _check_origin(settings, credentialed=auth is not None)
        tls = resolve_tls_profile("craft-suite-api")
        resources.callback(tls.cleanup)
        client = build_http_client(
            HttpClientOptions(
                base_url=settings.base_url,
                auth=auth,
                tls=tls,
                retry=RetryPolicy(max_attempts=1),
                allow_plaintext=settings.allow_plaintext,
                timeout=TIMEOUT_S,
            ),
            transport=transport,
            async_=True,
        )
        client.follow_redirects = False
        client.event_hooks["response"].append(bound_response)
        _resources = resources.pop_all()
    return client


def close_client() -> None:
    """Release the TLS material and token client of the last built client."""
    _resources.close()

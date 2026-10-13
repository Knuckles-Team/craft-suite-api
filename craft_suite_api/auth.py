"""Resolve provider credentials through canonical SDK APIs and owned resources."""

from contextlib import ExitStack

import httpx
from agent_connector_sdk.auth.delegation import DelegatedTokenAuth, DelegationSettings
from agent_connector_sdk.auth.static import api_key_auth, bearer_auth
from agent_connector_sdk.config import load_config, setting
from agent_connector_sdk.http.client import create_http_client
from agent_connector_sdk.http.options import HttpClientOptions
from agent_connector_sdk.tls.resolve import resolve_tls_profile

from .api import ApiClientSystem
from .openapi_auth_scheme import AuthKind, declared_scheme
from .openapi_client import ClientPolicy
from .openapi_schema import CONTRACT

_client = None
_resources = ExitStack()


def _reference_auth(definition):
    reference = setting("CRAFT_SUITE_API_TOKEN_REF", "")
    if not reference:
        return httpx.Auth(), None
    if definition is None:
        raise ValueError("Unsupported provider authentication scheme")
    if definition.kind is AuthKind.HEADER:
        return api_key_auth(reference, header=definition.header), definition.name
    return bearer_auth(reference), definition.name


def _delegated_auth(definition, delegation, resources):
    if definition is None or definition.kind is not AuthKind.BEARER:
        raise ValueError("Delegation requires a declared HTTP bearer auth scheme")
    token_tls = resolve_tls_profile("oidc")
    resources.callback(token_tls.cleanup)
    token_client = create_http_client(
        HttpClientOptions(base_url=delegation.token_endpoint, tls=token_tls)
    )
    resources.callback(token_client.close)
    return DelegatedTokenAuth(delegation, http_client=token_client), definition.name


def _build_client(base_url, resources):
    scheme = setting("CRAFT_SUITE_API_AUTH_SCHEME", "signed_session")
    definition = declared_scheme(scheme, CONTRACT["security_schemes"])
    tls = resolve_tls_profile("craft-suite-api")
    resources.callback(tls.cleanup)
    delegation = DelegationSettings.from_settings()
    if delegation.enabled:
        auth, credential_scheme = _delegated_auth(definition, delegation, resources)
    else:
        auth, credential_scheme = _reference_auth(definition)
    policy = ClientPolicy(
        allow_writes=setting("CRAFT_SUITE_API_ALLOW_WRITES", False),
        allow_plaintext=setting("CRAFT_SUITE_API_ALLOW_PLAINTEXT", False),
    )
    client = ApiClientSystem(
        base_url=base_url,
        auth=auth,
        tls_profile=tls,
        credential_scheme=credential_scheme,
        policy=policy,
    )
    resources.callback(client.close)
    return client


def get_client():
    """Build one client; delegated auth resolves the verified caller per request."""
    global _client, _resources
    if _client is not None:
        return _client
    load_config()
    base_url = setting("CRAFT_SUITE_API_BASE_URL", "")
    if not base_url:
        raise ValueError("Provider base URL is required")
    with ExitStack() as resources:
        client = _build_client(base_url, resources)
        _resources = resources.pop_all()
        _client = client
    return client


def close_client():
    """Close the cached client, token client and materialized TLS resources."""
    global _client
    try:
        _resources.close()
    finally:
        _client = None

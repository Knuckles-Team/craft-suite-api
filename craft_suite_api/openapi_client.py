"""Operation-bound HTTP dispatch with explicit caller policy."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

from agent_connector_sdk.http.client import create_http_client
from agent_connector_sdk.http.options import HttpClientOptions
from agent_connector_sdk.http.retry import RetryPolicy

from .openapi_parameters import parameters, request_body
from .openapi_responses import read_response, response_value
from .openapi_schema import CONTRACT, validate

MAX_BYTES = 16 * 1024 * 1024


@dataclass(frozen=True)
class ClientPolicy:
    """Default-deny write and transport permissions from the operator."""

    allow_writes: bool = False
    allow_plaintext: bool = False


class OpenApiClient:
    """Dispatch only catalogued actions; perform each HTTP request exactly once."""

    def __init__(
        self,
        base_url,
        auth,
        tls_profile=None,
        *,
        credential_scheme=None,
        policy: ClientPolicy | None = None,
        transport=None,
    ):
        policy = policy or ClientPolicy()
        parsed = urlsplit(base_url)
        if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
            raise ValueError("Base URL must be the provider origin without a path")
        if credential_scheme and parsed.scheme == "http" and not policy.allow_plaintext:
            raise ValueError(
                "Credential-bearing plaintext HTTP requires allow_plaintext"
            )
        self.session = create_http_client(
            HttpClientOptions(
                base_url=base_url,
                auth=auth,
                tls=tls_profile,
                retry=RetryPolicy(max_attempts=1),
                allow_plaintext=policy.allow_plaintext,
                timeout=30.0,
            ),
            transport=transport,
        )
        self.credential_scheme = credential_scheme
        self.allow_writes = policy.allow_writes

    def close(self):
        self.session.close()

    def _authorize(self, operation):
        if not operation["read_only"] and not self.allow_writes:
            raise PermissionError("Writes require explicit operator enablement")
        requirements = operation["security"]
        if requirements and not any(
            not choice or set(choice) == {self.credential_scheme}
            for choice in requirements
        ):
            raise PermissionError("Action requires a supported credential reference")

    def execute(self, domain: str, arguments: dict[str, Any]):
        if domain not in CONTRACT["domains"]:
            raise ValueError("Unknown domain")
        validate(arguments, CONTRACT["schemas"][domain][0])
        operation = CONTRACT["operations"][arguments["action"]]
        if operation["domain"] != domain:
            raise ValueError("Action is outside this domain")
        self._authorize(operation)
        path, query, headers = parameters(operation, arguments)
        target = self.session.base_url.join(path)
        origin = self.session.base_url
        if (target.scheme, target.host, target.port) != (
            origin.scheme,
            origin.host,
            origin.port,
        ):
            raise ValueError(
                "Operation must stay within the configured provider origin"
            )
        options = {"params": query, "headers": headers, "follow_redirects": False}
        if "body" in arguments:
            options.update(
                request_body(operation, arguments["body"], max_bytes=MAX_BYTES)
            )
        return self._send(operation, path, options)

    def _send(self, operation, path, options):
        deadline = time.monotonic() + 60
        with self.session.stream(operation["method"], path, **options) as response:
            if not 200 <= response.status_code < 300:
                raise RuntimeError(
                    f"Provider returned HTTP {response.status_code}; no automatic retry"
                )
            body = read_response(response, deadline, max_bytes=MAX_BYTES)
            content_type, data = response_value(operation, response, body)
            result = {
                "action": operation["action"],
                "status": response.status_code,
                "content_type": content_type,
                "data": data,
            }
            validate(result, CONTRACT["schemas"][operation["domain"]][1])
            return result

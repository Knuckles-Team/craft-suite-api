"""The response-size bound on backend requests (CONN-CRAFT-SUITE-API-R002)."""

from __future__ import annotations

import httpx

__all__ = ["MAX_BYTES", "ResponseTooLarge", "bound_response"]

MAX_BYTES = 16 * 1024 * 1024


class ResponseTooLarge(RuntimeError):
    """The backend answered with more than ``MAX_BYTES``."""


class _BoundedStream(httpx.AsyncByteStream):
    def __init__(self, inner: httpx.AsyncByteStream, limit: int) -> None:
        self.inner = inner
        self.limit = limit

    async def __aiter__(self):
        seen = 0
        async for chunk in self.inner:
            seen += len(chunk)
            if seen > self.limit:
                raise ResponseTooLarge(f"response exceeds {self.limit} bytes")
            yield chunk

    async def aclose(self) -> None:
        await self.inner.aclose()


async def bound_response(response: httpx.Response) -> None:
    """Refuse a declared or streamed body larger than ``MAX_BYTES``."""
    declared = response.headers.get("content-length", "")
    if declared.isdigit() and int(declared) > MAX_BYTES:
        await response.aclose()
        raise ResponseTooLarge(f"response declares {declared} bytes")
    response.stream = _BoundedStream(response.stream, MAX_BYTES)

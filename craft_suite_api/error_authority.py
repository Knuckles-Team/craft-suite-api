"""Negotiate representations of the canonical bounded problem details."""

from collections.abc import Mapping
from dataclasses import dataclass

from .problem_details import (
    AGENT_ERROR_ACCEPT,
    BROWSER_HTML_MEDIA_TYPE,
    MAX_DETAIL_CHARS,
    PROBLEM_JSON_MEDIA_TYPE,
    STRUCTURED_MARKDOWN_MEDIA_TYPE,
    ProblemDetails,
)


@dataclass(frozen=True)
class RenderedError:
    """A transport-neutral response ready for an HTTP/MCP adapter."""

    status_code: int
    media_type: str
    body: str
    headers: Mapping[str, str]


def _media_candidate(item: str, offered: str, order: int):
    bits = [part.strip() for part in item.split(";")]
    token = bits[0].lower()
    try:
        quality = next(
            float(part.split("=", 1)[1].strip())
            for part in bits[1:]
            if part.lower().startswith("q=")
        )
    except (StopIteration, ValueError):
        quality = 1.0
    if not 0.0 <= quality <= 1.0:
        return None
    specificity = {offered: 2, "*/*": 1, offered.split("/", 1)[0] + "/*": 1}.get(token)
    if specificity is None:
        return None
    return specificity, quality, -order


def _accept_quality(accept: str, offered: str) -> tuple[float, int, int]:
    """Return q, specificity, and source order for one offered media type."""
    candidates = (
        _media_candidate(item, offered, order)
        for order, item in enumerate(accept.split(","))
    )
    specificity, quality, source_order = max(
        (candidate for candidate in candidates if candidate is not None),
        default=(-1, 0.0, -10_000),
    )
    return quality, specificity, source_order


def negotiate_media_type(accept: str | None) -> str:
    """Prefer agent formats, while retaining HTML for browser Accept headers."""
    if not accept or not accept.strip():
        return PROBLEM_JSON_MEDIA_TYPE
    offered = (
        PROBLEM_JSON_MEDIA_TYPE,
        STRUCTURED_MARKDOWN_MEDIA_TYPE,
        BROWSER_HTML_MEDIA_TYPE,
    )
    ranked = [
        (*_accept_quality(accept, media_type), -priority, media_type)
        for priority, media_type in enumerate(offered)
    ]
    supported = [candidate for candidate in ranked if candidate[0] > 0]
    return max(supported)[-1] if supported else PROBLEM_JSON_MEDIA_TYPE


def render_error(
    problem: ProblemDetails, *, accept: str | None = None
) -> RenderedError:
    """Negotiate one bounded representation without changing its semantics."""
    media_type = negotiate_media_type(accept)
    if media_type == STRUCTURED_MARKDOWN_MEDIA_TYPE:
        body = problem.to_markdown()
    elif media_type == BROWSER_HTML_MEDIA_TYPE:
        body = problem.to_html()
    else:
        media_type = PROBLEM_JSON_MEDIA_TYPE
        body = problem.to_json()
    headers = {
        "Content-Type": f"{media_type}; charset=utf-8",
        "Vary": "Accept",
    }
    if problem.retry_after_s is not None:
        headers["Retry-After"] = str(problem.retry_after_s)
    return RenderedError(
        status_code=problem.status,
        media_type=media_type,
        body=body,
        headers=headers,
    )


def error_response(
    *,
    status: int,
    code: str,
    instance: str,
    detail: str,
    type_uri: str = "",
    title: str = "",
    retryable: bool = False,
    retry_after_s: float | None = None,
    accept: str | None = None,
) -> RenderedError:
    """Construct and render a problem through the single package authority."""
    return render_error(
        ProblemDetails(
            status=status,
            code=code,
            instance=instance,
            detail=detail,
            type_uri=type_uri,
            title=title,
            retryable=retryable,
            retry_after_s=retry_after_s,
        ),
        accept=accept,
    )


__all__ = [
    "BROWSER_HTML_MEDIA_TYPE",
    "AGENT_ERROR_ACCEPT",
    "MAX_DETAIL_CHARS",
    "PROBLEM_JSON_MEDIA_TYPE",
    "ProblemDetails",
    "RenderedError",
    "STRUCTURED_MARKDOWN_MEDIA_TYPE",
    "error_response",
    "negotiate_media_type",
    "render_error",
]

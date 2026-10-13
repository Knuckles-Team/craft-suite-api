"""Bound and decode declared provider responses."""

import base64
import json
import time


def read_response(response, deadline, *, max_bytes):
    body = bytearray()
    for chunk in response.iter_bytes():
        if time.monotonic() > deadline or len(body) + len(chunk) > max_bytes:
            raise RuntimeError("Provider response limit exceeded")
        body.extend(chunk)
    return body


def _decode_response(mode, response, body):
    if mode == "json":
        try:
            return json.loads(body)
        except (ValueError, UnicodeDecodeError) as exc:
            raise ValueError("Provider response is not JSON") from exc
    if mode == "text":
        try:
            return body.decode(response.charset_encoding or "utf-8")
        except (UnicodeDecodeError, LookupError) as exc:
            raise ValueError("Provider text response cannot be decoded") from exc
    return base64.b64encode(body).decode()


def response_value(operation, response, body):
    content_type = response.headers.get("content-type", "").split(";", 1)[0].strip()
    status = str(response.status_code)
    expected = operation["responses"].get(status)
    if expected is None:
        raise ValueError("Undeclared provider success status")
    if not expected:
        if body:
            raise ValueError("Unexpected provider response body")
        return "", None
    if content_type not in expected:
        raise ValueError("Undeclared provider response media type")
    mode = operation["response_modes"][status][content_type]
    return content_type, _decode_response(mode, response, body)

"""Serialize validated operation parameters and request bodies."""

import base64
import json
from urllib.parse import quote

from .openapi_schema import CONTRACT


def _value(value):
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (str, int, float)):
        return str(value)
    raise ValueError("Unsupported parameter value")


def _path_value(value):
    rendered = _value(value)
    if rendered in {".", ".."} or any(c in rendered for c in "/\\%\r\n\x00"):
        raise ValueError("Unsafe path parameter")
    return quote(rendered, safe="")


def _query_value(query, parameter, value):
    name = parameter["name"]
    if isinstance(value, list):
        if parameter.get("explode", True):
            query.extend((name, _value(item)) for item in value)
        else:
            query.append((name, ",".join(_value(item) for item in value)))
    elif value is not None:
        query.append((name, _value(value)))


def _header_value(name, value):
    credential_headers = {
        str(scheme.get("name", "")).casefold()
        for scheme in CONTRACT["security_schemes"].values()
        if scheme.get("type") == "apiKey" and scheme.get("in") == "header"
    }
    if name.casefold() in credential_headers | {
        "authorization",
        "cookie",
        "host",
        "x-api-key",
    }:
        raise ValueError("Authentication headers are controlled by credentials")
    rendered = _value(value)
    if any(c in rendered for c in "\r\n\x00"):
        raise ValueError("Invalid header parameter")
    return rendered


def parameters(operation, arguments):
    path = operation["path"]
    query, headers = [], {}
    for parameter in operation["parameters"]:
        name, location = parameter["name"], parameter["in"]
        values = arguments.get(location, {})
        if name not in values:
            continue
        value = values[name]
        if location == "path":
            path = path.replace("{" + name + "}", _path_value(value))
        elif location == "query":
            _query_value(query, parameter, value)
        elif location == "header":
            headers[name] = _header_value(name, value)
    if "{" in path or "}" in path:
        raise ValueError("Missing path parameter")
    return path, query, headers


def _multipart(body, body_schema, definitions, *, max_bytes):
    while "$ref" in body_schema:
        body_schema = definitions[body_schema["$ref"].rsplit("/", 1)[1]]
    files, data = {}, {}
    for key, value in body.items():
        field = body_schema.get("properties", {}).get(key, {})
        if field.get("contentEncoding") == "base64":
            files[key] = (
                "upload",
                _decode_upload(value, max_bytes),
                "application/octet-stream",
            )
        else:
            data[key] = (
                json.dumps(value, separators=(",", ":"))
                if isinstance(value, (dict, list))
                else _value(value)
            )
    return {"files": files, "data": data}


def _decode_upload(value, max_bytes):
    try:
        decoded = base64.b64decode(value, validate=True)
    except (ValueError, TypeError) as exc:
        raise ValueError("Invalid base64 upload") from exc
    if len(decoded) > max_bytes:
        raise ValueError("Upload size limit exceeded")
    return decoded


def request_body(operation, body, *, max_bytes):
    if len(json.dumps(body).encode()) > max_bytes:
        raise ValueError("Request size limit exceeded")
    media = operation["content_type"]
    if media == "application/json":
        return {"json": body}
    if media == "application/x-www-form-urlencoded":
        return {"data": body}
    if media == "multipart/form-data":
        return _multipart(
            body,
            operation["input"]["properties"]["body"],
            CONTRACT["definitions"],
            max_bytes=max_bytes,
        )
    return {}

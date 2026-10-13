"""Declared OpenAPI formats are assertions, never silently missing extras."""

import pytest
from jsonschema import FormatChecker

from craft_suite_api.openapi_schema import validate


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("uri", "https://example.invalid/a?b=c"),
        ("uri", "urn:example:fixture"),
        ("date-time", "2026-10-13T12:30:00Z"),
        ("date-time", "2026-10-13T12:30:00+02:00"),
    ],
)
def test_required_formats_accept_valid_values(name, value):
    validate(value, {"type": "string", "format": name})


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("uri", "relative/path"),
        ("uri", "https://bad host.invalid"),
        ("date-time", "not-a-date-time"),
        ("date-time", "2026-10-13T12:30:00"),
        ("date-time", "2026-02-30T12:30:00Z"),
    ],
)
def test_malformed_formats_are_rejected_without_echo(name, value):
    with pytest.raises(ValueError, match="declared OpenAPI schema") as error:
        validate(value, {"type": "string", "format": name})
    assert value not in str(error.value)


@pytest.mark.parametrize("name", ["uri", "date-time", "unknown-provider-format"])
def test_missing_required_checker_fails_closed(name, monkeypatch):
    monkeypatch.delitem(FormatChecker.checkers, name, raising=False)
    with pytest.raises(
        RuntimeError, match="Required OpenAPI format checker is unavailable"
    ):
        validate("synthetic", {"type": "string", "format": name})


@pytest.mark.parametrize(
    "name", ["int32", "int64", "float", "double", "binary", "byte", "password"]
)
def test_representation_annotations_do_not_require_format_plugins(name):
    validate(
        1 if name in {"int32", "int64", "float", "double"} else "fixture",
        {"format": name},
    )

"""Captured operation contract and bounded JSON Schema validation."""

import json
from pathlib import Path

import regex
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError
from jsonschema.validators import extend

CONTRACT = json.loads(Path(__file__).with_name("openapi_contract.json").read_text())


def _pattern(_validator, pattern, *value_and_schema):
    """JSON Schema supplies the instance and schema as the final callback pair."""
    instance, _schema = value_and_schema
    if (
        isinstance(instance, str)
        and regex.search(pattern, instance, timeout=0.1) is None
    ):
        yield ValidationError("String does not satisfy its pattern")


def _format(*arguments):
    """Require actual format assertions; retain OpenAPI representation annotations."""
    validator, name, _instance, _schema = arguments
    if name in {"int32", "int64", "float", "double", "binary", "byte", "password"}:
        return
    checker = validator.format_checker
    if checker is None or name not in checker.checkers:
        raise RuntimeError(f"Required OpenAPI format checker is unavailable: {name}")
    yield from Draft202012Validator.VALIDATORS["format"](*arguments)


SchemaValidator = extend(Draft202012Validator, {"pattern": _pattern, "format": _format})


def validate(value, definition):
    """Validate without disclosing caller input or provider response values."""
    validator = SchemaValidator(definition, format_checker=FormatChecker())
    if next(validator.iter_errors(value), None) is not None:
        raise ValueError("Value does not satisfy the declared OpenAPI schema")

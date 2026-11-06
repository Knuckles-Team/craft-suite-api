"""CONN-CRAFT-SUITE-API-APPS-R019: command tool schemas are typed from the apps' prose."""

from __future__ import annotations

import pytest

from craft_suite_api.app_commands import (
    DISPATCH,
    build_command_tools,
    fragment_schema,
    typed_properties,
)

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R019")

RUN = {"type": "object", "properties": {"id": {}, "params": {}}}

# Signatures exactly as the shipped registries document them.
CROP = (
    '{"x":px,"y":px,"width":px,"height":px,"angle":-3600..3600=0,'
    '"deleteCroppedPixels":bool=true,"contentAware":bool=false,'
    '"targetWidth":px,"targetHeight":px,"resolution":ppi,'
    '"resample":"bicubic|bilinear|nearest|lanczos|preserveDetails"="bicubic"}'
    " → {x,y,width,height}"
)


def test_photocraft_crop_is_fully_typed() -> None:
    props = typed_properties(CROP)
    assert props["x"] == {"type": "number"}
    assert props["angle"] == {
        "type": "number",
        "minimum": -3600,
        "maximum": 3600,
        "default": 0,
    }
    assert props["deleteCroppedPixels"] == {"type": "boolean", "default": True}
    assert props["resample"] == {
        "type": "string",
        "enum": ["bicubic", "bilinear", "nearest", "lanczos", "preserveDetails"],
        "default": "bicubic",
    }
    assert props["resolution"] == {"type": "number"}


@pytest.mark.parametrize(
    ("segment", "expected"),
    [
        ('"text": string', {"type": "string"}),
        ('"matchCase"?: bool', {"type": "boolean"}),
        ("slide?: index", {"type": "integer"}),
        ("size?: [w,h] pt", {"type": "array"}),
        ("opts?: {a, b}", {"type": "object"}),
        (
            "style?: straight|elbow|curved",
            {"type": "string", "enum": ["straight", "elbow", "curved"]},
        ),
        ('"clips":[id]?', {"type": "array"}),
        ("opacity?: 0..1", {"type": "number", "minimum": 0, "maximum": 1}),
        ("full?: bool (cooks now)", {"type": "boolean"}),
        ("count=3", {"type": "number", "default": 3}),
        # Unions and prose stay open: a valid call is never refused.
        ("sheet: index | name", {}),
        ("canvas: id or name", {}),
        ("style: medium2-accent1|light1-accent2|none…", {}),
        ("feature: id|name", {}),
        ("text", {}),
        ('width?: pt=612|"210 mm"', {}),
    ],
)
def test_fragments_type_only_what_reads_without_doubt(segment, expected) -> None:
    assert fragment_schema(segment) == expected


def test_a_default_outside_the_enum_is_dropped() -> None:
    assert fragment_schema('"mode":"rgb|gray"="lab"') == {
        "type": "string",
        "enum": ["rgb", "gray"],
    }


def test_pdfcraft_json_schema_params_are_served_as_the_schema() -> None:
    entry = {
        "id": "page.insert",
        "params": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "doc": {"type": "integer", "minimum": 1},
                "at": {"type": "integer", "minimum": 1},
            },
            "required": ["doc"],
        },
    }
    (tool,) = build_command_tools("pdfcraft", DISPATCH["pdfcraft"], [entry], RUN)
    assert tool.parameters["properties"]["doc"] == {"type": "integer", "minimum": 1}
    assert tool.parameters["properties"]["at"] == {"type": "integer", "minimum": 1}
    assert tool.parameters["required"] == ["doc"]

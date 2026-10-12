"""Reproduce the reviewed ArtCraft subset using the embedded mcp-builder skill.

This provider adapter selects and documents reviewed operations. The skill remains
the sole OpenAPI compiler/runtime authority. No network or native build is used.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import json
import re
import sys
from pathlib import Path


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def references(value):
    if isinstance(value, dict):
        ref = value.get("$ref", "")
        if ref:
            if not ref.startswith("#/components/schemas/"):
                raise ValueError("Only local schema references are admitted")
            yield ref.rsplit("/", 1)[1]
        for item in value.values():
            yield from references(item)
    elif isinstance(value, list):
        for item in value:
            yield from references(item)


def generate(root: Path, skill: Path):
    spec_dir = root / "api-spec"
    review = json.loads((spec_dir / "source-review.json").read_text())
    raw = (spec_dir / "artcraft.public.openapi.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != review["public_schema_sha256"]:
        raise ValueError("Captured public schema changed; a new review is required")
    public = json.loads(raw)
    sources = {}
    for path, expected in review["source_files"].items():
        content = (spec_dir / "source" / path).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content)
        if (
            hashlib.sha256(content).hexdigest() != expected["sha256"]
            or blob.hexdigest() != expected["git_blob_sha"]
        ):
            raise ValueError(f"Pinned source changed: {path}")
        sources[path] = content.decode()

    # Two additive optional fields are explicit Option<Url>/Option<String> in
    # pinned Rust but absent from the public export. No unknown type is guessed.
    for name, fields in review.get("source_schema_additions", {}).items():
        definition = public["components"]["schemas"][name]
        for field, schema in fields.items():
            if field in definition["properties"]:
                raise ValueError("Source addition now exists upstream; review again")
            definition["properties"][field] = schema

    def evidence(path, needle):
        content = sources[path]
        offset = content.index(needle)
        line = content[:offset].count("\n") + 1
        return {
            "path": path,
            "line": line,
            "url": f"https://github.com/{review['upstream_repository']}/blob/"
            f"{review['upstream_commit']}/{path}#L{line}",
        }

    selected = {
        "openapi": public["openapi"],
        "info": {"title": "ArtCraft reviewed subset", "version": "0.0.1"},
        "paths": {},
        "components": {
            "schemas": {},
            "securitySchemes": {
                "signed_session": {"type": "apiKey", "in": "header", "name": "session"}
            },
        },
    }
    provenance = []
    policies = {}
    for item in sorted(review["operations"], key=lambda item: item["path"]):
        path = item["path"]
        operation = copy.deepcopy(public["paths"][path]["get"])
        action = operation["operationId"]
        handler = sources[item["handler"]]
        if f'path = "{path}"' not in handler or f"fn {action}(" not in handler:
            raise ValueError(
                f"Published operation does not match pinned handler: {path}"
            )
        response = operation["responses"]["200"]["content"]["application/json"][
            "schema"
        ]
        response_name = response["$ref"].rsplit("/", 1)[1]
        if f"Json<{response_name}>" not in handler:
            raise ValueError(f"Pinned response type mismatch: {path}")
        if f"web::get().to({action})" not in sources[item["routes"]]:
            raise ValueError(f"Pinned GET registration missing: {path}")
        security = {
            "public": [],
            "required_session": [{"signed_session": []}],
            "optional_session": [{}, {"signed_session": []}],
        }[item["auth"]]
        if (
            item["auth"] == "required_session"
            and "require_user_session(" not in handler
        ):
            raise ValueError(f"Required-session evidence missing: {path}")
        operation["security"] = security
        operation["description"] = item["notes"]
        # The SDK intentionally exposes sanitized HTTP errors, not their bodies.
        for status, body in operation["responses"].items():
            if not status.startswith("2"):
                body.pop("content", None)
        selected["paths"][path] = {"get": operation}
        row = {
            **item,
            "action": action,
            "method": "GET",
            "runtime_read_only": not item["effects"],
            "live_verified": False,
            "handler_evidence": evidence(item["handler"], f'path = "{path}"'),
            "registration_evidence": evidence(
                item["routes"], f"web::get().to({action})"
            ),
            "response_evidence": evidence(item["types"], f"pub struct {response_name}"),
        }
        provenance.append(row)
        policies[action] = row

    used = set()
    pending = list(references(selected["paths"]))
    while pending:
        name = pending.pop()
        if name not in used:
            used.add(name)
            definition = public["components"]["schemas"][name]
            pending.extend(references(definition))
            selected["components"]["schemas"][name] = copy.deepcopy(definition)

    # Check all reachable struct field names and required non-Option fields from
    # the captured Rust type files. This is deliberately not a full Rust parser.
    # Enum wire values and detailed serializer facets remain the published schema.
    structs = []
    for path, source in sources.items():
        for match in re.finditer(r"pub struct (\w+)\s*\{(.*?)^\}", source, re.S | re.M):
            name, body = match.groups()
            if name not in used:
                continue
            fields = dict(re.findall(r"^\s*pub (\w+):\s*([^\n,]+),", body, re.M))
            schema = selected["components"]["schemas"][name]
            if set(fields) != set(schema.get("properties", {})):
                raise ValueError(
                    f"Published field names differ from pinned source: {name}"
                )
            required = {
                key for key, value in fields.items() if not value.startswith("Option<")
            }
            if required != set(schema.get("required", [])):
                raise ValueError(
                    f"Published required fields differ from pinned source: {name}"
                )
            structs.append(
                {
                    "schema": name,
                    "fields": fields,
                    "evidence": evidence(path, match.group(0).split("\n")[0]),
                }
            )

    dump(spec_dir / "artcraft.reviewed.openapi.json", selected)
    dump(
        spec_dir / "source-provenance.json",
        {
            "public_schema_sha256": review["public_schema_sha256"],
            "upstream_commit": review["upstream_commit"],
            "operations": provenance,
            "struct_checks": sorted(structs, key=lambda row: row["schema"]),
            "source_schema_additions": review.get("source_schema_additions", {}),
            "unknowns": review["unknowns"],
            "withheld": review["withheld"],
        },
    )
    scripts = skill / "scripts"
    sys.path.insert(0, str(scripts))
    converter = importlib.import_module("openapi_converter")
    package = root / "artcraft_api"
    converter.generate(
        spec_dir / "artcraft.reviewed.openapi.json", package, "signed_session"
    )
    contract_path = package / "openapi_contract.json"
    contract = json.loads(contract_path.read_text())
    # Reviewed provider effects override the generic compiler's HTTP-method
    # heuristic. Never broaden effects to read-only during a regeneration.
    for action, operation in contract["operations"].items():
        policy = policies[action]
        operation["read_only"] = policy["runtime_read_only"]
        operation["source_effects"] = policy["effects"]
        operation["source_evidence"] = policy["handler_evidence"]
    dump(contract_path, contract)
    return {
        "operations": len(policies),
        "schemas": len(used),
        "struct_checks": len(structs),
        "domains": contract["domains"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", type=Path, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            generate(Path(__file__).resolve().parents[1], args.skill_dir.resolve()),
            sort_keys=True,
        )
    )

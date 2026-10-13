"""Resolve Craft's reviewed captures for the existing exact-tree proof gates."""

import argparse
import hashlib
import json
import os
from pathlib import Path

from schema_evidence_io import (
    base_policy,
    commit_id,
    compiler_capture,
    download,
    git_bytes,
    read_json,
    relative_path,
    require_regular_destination,
    save_verified,
)


def provider_capture(root, review, target):
    history = review["evidence_storage"]
    original = history["historical_capture_directory"] + "/artcraft.public.openapi.json"
    raw = git_bytes(root, history["historical_capture_commit"], original)
    save_verified(
        target / "artcraft.public.openapi.json",
        raw,
        {"sha256": review["public_schema_sha256"]},
    )
    if review["upstream_repository"] != "storytold/artcraft-services":
        raise ValueError("Unexpected Craft provider source")
    revision = commit_id(review["upstream_commit"])
    for name, expected in review["source_files"].items():
        path = relative_path(name)
        destination = target / "source" / path
        require_regular_destination(destination)
        data = (
            destination.read_bytes()
            if destination.is_file()
            else download(
                f"https://raw.githubusercontent.com/storytold/artcraft-services/{revision}/{path}",
                4 * 1024 * 1024,
            )
        )
        save_verified(destination, data, expected)


def prepare(root, *, base_ref=None):
    ci = root / ".ci"
    if ci.is_symlink():
        raise ValueError("Evidence workspace cannot be a symlink")
    captures, source = ci / "compiler-snapshots", ci / "schema-evidence"
    policy = read_json(root, "validation/generated-schemas.json")
    builder = compiler_capture(captures, policy)
    if base_ref and base_ref != "0" * 40:
        base_manifest = base_policy(root, base_ref)
        if (
            base_manifest
            and base_manifest["builder"]["commit"] != policy["builder"]["commit"]
        ):
            compiler_capture(captures, base_manifest)
    provider_capture(root, read_json(root, "api-spec/source-review.json"), source)
    result = {
        "MCP_BUILDER_SKILL_DIR": str(builder),
        "MCP_BUILDER_SNAPSHOT_ROOT": str(captures),
        "ARTCRAFT_SOURCE_EVIDENCE_DIR": str(source),
    }
    receipt = {
        "paths": result,
        "builder": policy["builder"],
        "source_review_sha256": hashlib.sha256(
            (root / "api-spec/source-review.json").read_bytes()
        ).hexdigest(),
    }
    destination = ci / "schema-evidence.json"
    require_regular_destination(destination)
    destination.write_text(json.dumps(receipt, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--github", action="store_true")
    args = parser.parse_args()
    result = prepare(
        Path(__file__).resolve().parents[1],
        base_ref=os.environ.get("CONNECTOR_SCHEMA_BASE_REF"),
    )
    if args.github:
        with Path(os.environ["GITHUB_ENV"]).open("a") as output:
            output.write("".join(f"{key}={value}\n" for key, value in result.items()))
    print(json.dumps(result))


if __name__ == "__main__":
    main()

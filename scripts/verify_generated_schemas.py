"""Prove the three approved schema artifacts before clone-policy exclusion.

This check is offline. It requires exact upstream captures and the published
mcp-builder source through explicit paths; absent inputs are a failure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_source_contract import generate

ARTIFACTS = (
    "api-spec/artcraft.reviewed.openapi.json",
    "craft_suite_api/openapi_contract.json",
    "schemas/mcp_tools.json",
)
MANIFEST = "validation/generated-schemas.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_policy(root: Path) -> dict:
    """An exact allowlist, never patterns or caller-selected handwritten paths."""
    policy = json.loads((root / MANIFEST).read_text())
    if policy.get("version") != 1 or set(policy["artifacts"]) != set(ARTIFACTS):
        raise ValueError(
            "Generated-schema policy must name exactly the three approved artifacts"
        )
    for name in ARTIFACTS:
        path = root / name
        if (
            path.is_symlink()
            or not path.resolve().is_relative_to(root.resolve())
            or not path.is_file()
            or digest(path) != policy["artifacts"][name]
        ):
            raise ValueError(f"Unverified generated artifact: {name}")
        json.loads(path.read_text())
    return policy


def generation_inputs(policy: dict) -> tuple[Path, Path]:
    """Match the compiler source to the reviewed release before importing it."""
    skill_value = os.environ.get("MCP_BUILDER_SKILL_DIR")
    evidence_value = os.environ.get("ARTCRAFT_SOURCE_EVIDENCE_DIR")
    if not skill_value or not evidence_value:
        raise ValueError(
            "Set MCP_BUILDER_SKILL_DIR and ARTCRAFT_SOURCE_EVIDENCE_DIR for verified regeneration"
        )
    skill, evidence = Path(skill_value), Path(evidence_value)
    for name, expected in policy["builder"]["compiler_sha256"].items():
        if name not in {"scripts/openapi_converter.py", "scripts/openapi_schema.py"}:
            raise ValueError("Unapproved compiler input")
        if digest(skill / name) != expected:
            raise ValueError(f"Published compiler input differs: {name}")
    if set(policy["builder"]["compiler_sha256"]) != {
        "scripts/openapi_converter.py",
        "scripts/openapi_schema.py",
    }:
        raise ValueError("Both compiler inputs must be verified")
    return skill, evidence


def verify_source_outputs(root: Path, skill: Path, evidence: Path) -> None:
    """Regenerate schemas separately, leaving handwritten runtime files intact."""
    with tempfile.TemporaryDirectory(prefix="artcraft-schema-proof-") as directory:
        output = Path(directory)
        (output / "api-spec").mkdir()
        shutil.copyfile(
            root / "api-spec/source-review.json", output / "api-spec/source-review.json"
        )
        generate(output, skill, evidence)
        for name in ARTIFACTS[:2]:
            if (output / name).read_bytes() != (root / name).read_bytes():
                raise ValueError(f"Generated schema differs from regeneration: {name}")


def verify(root: Path) -> dict:
    policy = load_policy(root)
    skill, evidence = generation_inputs(policy)
    verify_source_outputs(root, skill, evidence)
    result = subprocess.run(
        [sys.executable, str(root / "scripts/generate_tool_schemas.py"), "--check"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=45,
    )
    if result.returncode:
        raise ValueError("Native MCP schema validation/regeneration check failed")
    if load_policy(root) != policy:
        raise ValueError("Generated-schema policy changed during verification")
    return {"version": 1, "verified_artifacts": policy["artifacts"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.root.resolve()), sort_keys=True))
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as exc:
        raise SystemExit(f"Generated-schema verification failed: {exc}") from exc

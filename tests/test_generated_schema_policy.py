"""Exclusion admission fails closed for unverified or handwritten artifacts."""

import copy
import json
from pathlib import Path

import pytest

from scripts import generated_schema_clones as clones
from scripts import verify_generated_schemas as verification

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def policy_root(tmp_path):
    for name in (*verification.ARTIFACTS, verification.MANIFEST):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / name).read_bytes())
    return tmp_path


def rewrite_policy(root, edit):
    path = root / verification.MANIFEST
    policy = json.loads(path.read_text())
    edit(policy)
    path.write_text(json.dumps(policy))


@pytest.mark.parametrize(
    "path",
    [
        "craft_suite_api/auth.py",
        "schemas/handwritten.json",
        "schemas/*.json",
        "../outside.json",
    ],
)
def test_cannot_admit_handwritten_or_wildcard_paths(policy_root, path):
    rewrite_policy(
        policy_root, lambda policy: policy["artifacts"].update({path: "0" * 64})
    )
    with pytest.raises(ValueError, match="exactly the three"):
        verification.load_policy(policy_root)


def test_missing_manifest_has_no_exclusion(policy_root):
    (policy_root / verification.MANIFEST).unlink()
    with pytest.raises(FileNotFoundError):
        verification.load_policy(policy_root)


@pytest.mark.parametrize("name", verification.ARTIFACTS)
def test_changed_schema_is_not_verified(policy_root, name):
    with (policy_root / name).open("a") as stream:
        stream.write(" ")
    with pytest.raises(ValueError, match="Unverified generated artifact"):
        verification.load_policy(policy_root)


def test_forged_digest_does_not_replace_regeneration(
    policy_root, monkeypatch, tmp_path
):
    name = verification.ARTIFACTS[0]
    (policy_root / name).write_text('{"handwritten": true}')
    rewrite_policy(
        policy_root,
        lambda policy: policy["artifacts"].update(
            {name: verification.digest(policy_root / name)}
        ),
    )
    verification.load_policy(policy_root)

    def regenerate(output, _skill, _evidence):
        for artifact in verification.ARTIFACTS[:2]:
            target = output / artifact
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / artifact).read_bytes())

    (policy_root / "api-spec/source-review.json").write_text("{}")
    monkeypatch.setattr(verification, "generate", regenerate)
    with pytest.raises(ValueError, match="differs from regeneration"):
        verification.verify_source_outputs(policy_root, tmp_path, tmp_path)


def test_missing_generation_inputs_fail_closed(policy_root, monkeypatch):
    monkeypatch.delenv("MCP_BUILDER_SKILL_DIR", raising=False)
    monkeypatch.delenv("ARTCRAFT_SOURCE_EVIDENCE_DIR", raising=False)
    with pytest.raises(ValueError, match="Set MCP_BUILDER"):
        verification.verify(policy_root)


def test_unverified_compiler_fails_closed(policy_root, monkeypatch, tmp_path):
    monkeypatch.setenv("MCP_BUILDER_SKILL_DIR", str(tmp_path))
    monkeypatch.setenv("ARTCRAFT_SOURCE_EVIDENCE_DIR", str(tmp_path))
    policy = verification.load_policy(policy_root)
    for name in policy["builder"]["compiler_sha256"]:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# Unverified compiler\n")
    with pytest.raises(ValueError, match="Published compiler input differs"):
        verification.generation_inputs(policy)


def test_no_subset_can_disable_a_required_check(policy_root):
    rewrite_policy(
        policy_root, lambda policy: policy["artifacts"].pop(verification.ARTIFACTS[0])
    )
    with pytest.raises(ValueError, match="exactly the three"):
        verification.load_policy(policy_root)


def simulate_generation(monkeypatch, returncode):
    monkeypatch.setattr(verification, "generation_inputs", lambda _policy: (ROOT, ROOT))
    monkeypatch.setattr(verification, "verify_source_outputs", lambda *_args: None)
    monkeypatch.setattr(
        verification.subprocess,
        "run",
        lambda *_args, **_kwargs: verification.subprocess.CompletedProcess(
            [], returncode
        ),
    )


def test_native_schema_failure_blocks_exclusion(policy_root, monkeypatch):
    simulate_generation(monkeypatch, 1)
    with pytest.raises(ValueError, match="Native MCP schema"):
        verification.verify(policy_root)


def test_manifest_changes_during_verification_are_rejected(policy_root, monkeypatch):
    original = verification.load_policy(policy_root)
    changed = copy.deepcopy(original)
    changed["scope"] = "changed during run"
    reads = iter([original, changed])
    monkeypatch.setattr(verification, "load_policy", lambda _root: next(reads))
    simulate_generation(monkeypatch, 0)
    with pytest.raises(ValueError, match="changed during"):
        verification.verify(policy_root)


def test_only_schema_to_schema_pairs_are_excluded():
    schema, contract = verification.ARTIFACTS[:2]
    pairs = {}
    for paths in (
        (schema, contract),
        (schema, schema),
        ("handwritten.py", schema),
        ("a.py", "b.py"),
    ):
        key = ("json", "fragment", paths, 0)
        pairs[key] = tuple((path, 1, 20) for path in paths)
    retained = clones.retain_pairs(pairs, {schema: "verified", contract: "verified"})
    assert {key[2] for key in retained} == {
        ("handwritten.py", schema),
        ("a.py", "b.py"),
    }
    assert clones.retain_pairs(pairs, {}) == pairs


def test_old_tree_without_policy_has_no_exclusions(tmp_path):
    assert clones.verified_artifacts(tmp_path, ROOT) == {}


@pytest.mark.parametrize(
    "receipt", [{}, {"version": 1, "verified_artifacts": {"handwritten.py": "0" * 64}}]
)
def test_incomplete_or_handwritten_verifier_receipt_is_rejected(
    policy_root, monkeypatch, receipt
):
    monkeypatch.setattr(
        clones.subprocess,
        "run",
        lambda *_args, **_kwargs: clones.subprocess.CompletedProcess(
            [], 0, stdout=json.dumps(receipt)
        ),
    )
    with pytest.raises(ValueError, match="incomplete or unexpected"):
        clones.verified_artifacts(policy_root, ROOT)


def test_failed_exact_tree_verifier_has_no_exclusions(policy_root, monkeypatch):
    monkeypatch.setattr(
        clones.subprocess,
        "run",
        lambda *_args, **_kwargs: clones.subprocess.CompletedProcess([], 1),
    )
    with pytest.raises(ValueError, match="no exclusions admitted"):
        clones.verified_artifacts(policy_root, ROOT)


def test_verifier_receives_scanned_tree_not_working_tree(policy_root, monkeypatch):
    receipt = {
        "version": 1,
        "verified_artifacts": verification.load_policy(policy_root)["artifacts"],
    }
    calls = []

    def execute(arguments, **kwargs):
        calls.append((arguments, kwargs))
        return clones.subprocess.CompletedProcess(
            arguments, 0, stdout=json.dumps(receipt)
        )

    monkeypatch.setattr(clones.subprocess, "run", execute)
    assert clones.verified_artifacts(policy_root, ROOT) == receipt["verified_artifacts"]
    arguments, options = calls[0]
    assert arguments[1] == str(policy_root / "scripts/verify_generated_schemas.py")
    assert arguments[-1] == str(policy_root)
    assert options["cwd"] == policy_root


def test_symlink_artifact_cannot_be_excluded(policy_root):
    artifact = policy_root / verification.ARTIFACTS[0]
    artifact.unlink()
    artifact.symlink_to(ROOT / verification.ARTIFACTS[0])
    with pytest.raises(ValueError, match="Unverified generated artifact"):
        verification.load_policy(policy_root)


@pytest.mark.parametrize("mutation", ["rewrite", "new-file", "mode"])
def test_verifier_cannot_change_handwritten_scanner_inputs(
    policy_root, monkeypatch, mutation
):
    handwritten = policy_root / "handwritten.py"
    handwritten.write_text("value = 1\n")
    receipt = {
        "version": 1,
        "verified_artifacts": verification.load_policy(policy_root)["artifacts"],
    }

    def execute(arguments, **_kwargs):
        if mutation == "rewrite":
            handwritten.write_text("value = 2\n")
        elif mutation == "mode":
            handwritten.chmod(0o700)
        else:
            (policy_root / "extra.py").write_text("value = 1\n")
        return clones.subprocess.CompletedProcess(
            arguments, 0, stdout=json.dumps(receipt)
        )

    monkeypatch.setattr(clones.subprocess, "run", execute)
    with pytest.raises(ValueError, match="changed the scanned tree"):
        clones.verified_artifacts(policy_root, ROOT)

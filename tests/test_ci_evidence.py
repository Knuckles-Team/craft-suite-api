"""Craft evidence preparation must reject altered bytes and redirected paths."""

import hashlib
import importlib
import io
import json
import sys
import tarfile
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
evidence = importlib.import_module("schema_evidence_io")
prepare = importlib.import_module("prepare_schema_evidence")


@pytest.mark.parametrize("value", ["main", "1" * 39, "A" * 40, "../escape"])
def test_only_full_immutable_revisions(value):
    with pytest.raises(ValueError, match="immutable"):
        evidence.commit_id(value)


@pytest.mark.parametrize("value", ["/absolute", "../outside", "safe/../../escape", ""])
def test_capture_paths_cannot_escape(value):
    with pytest.raises(ValueError, match="inside"):
        evidence.relative_path(value)


def test_sha_and_blob_must_both_match():
    data = b"captured\n"
    expected = {
        "sha256": hashlib.sha256(data).hexdigest(),
        "git_blob_sha": hashlib.sha1(b"blob 9\0" + data).hexdigest(),
    }
    evidence.verify_bytes(data, expected)
    with pytest.raises(ValueError, match="SHA-256"):
        evidence.verify_bytes(b"changed", expected)
    expected["git_blob_sha"] = "0" * 40
    with pytest.raises(ValueError, match="Git blob"):
        evidence.verify_bytes(data, expected)


def test_symlink_ancestor_rejected_before_read_or_write(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    link = tmp_path / "capture"
    link.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="symlinks"):
        evidence.save_verified(
            link / "source.txt",
            b"captured",
            {"sha256": hashlib.sha256(b"captured").hexdigest()},
        )
    assert list(outside.iterdir()) == []


def test_bounded_download(monkeypatch):
    monkeypatch.setattr(
        evidence.urllib.request,
        "urlopen",
        lambda *_args, **_kwargs: io.BytesIO(b"too long"),
    )
    with pytest.raises(ValueError, match="byte bound"):
        evidence.download("https://example.invalid", limit=3)


def archive_bytes(name, data):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        member = tarfile.TarInfo(name)
        member.size = len(data)
        archive.addfile(member, io.BytesIO(data))
    return buffer.getvalue()


@pytest.mark.parametrize("corrupt", [False, True])
def test_compiler_capture_checks_reviewed_bytes(tmp_path, monkeypatch, corrupt):
    name = "scripts/openapi_converter.py"
    data = b"# canonical compiler\n"
    archive = archive_bytes(
        "repo/universal_skills/agent-tools/mcp-builder/" + name, data
    )
    monkeypatch.setattr(evidence, "download", lambda _url: archive)
    policy = {
        "builder": {
            "commit": "1" * 40,
            "compiler_sha256": {
                name: "0" * 64 if corrupt else hashlib.sha256(data).hexdigest()
            },
        }
    }
    if corrupt:
        with pytest.raises(ValueError, match="SHA-256"):
            evidence.compiler_capture(tmp_path, policy)
    else:
        target = evidence.compiler_capture(tmp_path, policy)
        assert (target / name).read_bytes() == data


def test_compiler_archive_traversal_rejected(tmp_path, monkeypatch):
    archive = archive_bytes(
        "repo/universal_skills/agent-tools/mcp-builder/../../escape.py", b"bad"
    )
    monkeypatch.setattr(evidence, "download", lambda _url: archive)
    with pytest.raises(ValueError, match="inside"):
        evidence.compiler_capture(
            tmp_path, {"builder": {"commit": "1" * 40, "compiler_sha256": {}}}
        )


def test_historical_schema_is_not_replaced_by_mutable_docs(tmp_path, monkeypatch):
    data = b'{"original":true}'
    monkeypatch.setattr(prepare, "git_bytes", lambda *_args: data)
    monkeypatch.setattr(
        prepare, "download", lambda *_args: pytest.fail("No mutable docs fetch allowed")
    )
    review = {
        "evidence_storage": {
            "historical_capture_commit": "1" * 40,
            "historical_capture_directory": "api-spec",
        },
        "public_schema_sha256": hashlib.sha256(data).hexdigest(),
        "upstream_repository": "storytold/artcraft-services",
        "upstream_commit": "2" * 40,
        "source_files": {},
    }
    prepare.provider_capture(tmp_path, review, tmp_path / "capture")
    assert json.loads(
        (tmp_path / "capture/artcraft.public.openapi.json").read_text()
    ) == {"original": True}


def test_cached_source_symlink_is_rejected_before_read(tmp_path, monkeypatch):
    target = tmp_path / "capture"
    target.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "fixture.rs").write_text("outside")
    (target / "source").symlink_to(outside, target_is_directory=True)
    raw = b"{}"
    monkeypatch.setattr(prepare, "git_bytes", lambda *_args: raw)
    monkeypatch.setattr(
        Path,
        "read_bytes",
        lambda _self: pytest.fail("Read preceded symlink validation"),
    )
    review = {
        "evidence_storage": {
            "historical_capture_commit": "1" * 40,
            "historical_capture_directory": "api-spec",
        },
        "public_schema_sha256": hashlib.sha256(raw).hexdigest(),
        "upstream_repository": "storytold/artcraft-services",
        "upstream_commit": "2" * 40,
        "source_files": {"fixture.rs": {"sha256": "0" * 64}},
    }
    with pytest.raises(ValueError, match="symlinks"):
        prepare.provider_capture(tmp_path, review, target)


def test_receipt_symlink_is_rejected(tmp_path, monkeypatch):
    ci = tmp_path / ".ci"
    ci.mkdir()
    (tmp_path / "api-spec").mkdir()
    (tmp_path / "api-spec/source-review.json").write_text("{}")
    outside = tmp_path / "outside.json"
    outside.write_text("preserved")
    (ci / "schema-evidence.json").symlink_to(outside)
    monkeypatch.setattr(prepare, "read_json", lambda *_args: {"builder": {}})
    monkeypatch.setattr(prepare, "compiler_capture", lambda *_args: ci / "compiler")
    monkeypatch.setattr(prepare, "provider_capture", lambda *_args: None)
    with pytest.raises(ValueError, match="symlinks"):
        prepare.prepare(tmp_path)
    assert outside.read_text() == "preserved"

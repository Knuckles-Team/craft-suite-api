"""Fetch bounded immutable public evidence, then verify its declared hashes."""

import hashlib
import io
import json
import re
import subprocess
import tarfile
import urllib.request
from pathlib import PurePosixPath


def commit_id(value):
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ValueError("Evidence requires a full immutable commit ID")
    return value


def relative_path(value):
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not value:
        raise ValueError("Evidence path must remain inside its capture")
    return path


def git_bytes(root, revision, path):
    return subprocess.check_output(
        ["git", "show", f"{commit_id(revision)}:{relative_path(path)}"], cwd=root
    )


def download(url, limit=32 * 1024 * 1024):
    with urllib.request.urlopen(url, timeout=30) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("Evidence download exceeds its byte bound")
    return data


def verify_bytes(data, expected):
    if hashlib.sha256(data).hexdigest() != expected["sha256"]:
        raise ValueError("Evidence SHA-256 differs from reviewed source")
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if "git_blob_sha" in expected and blob != expected["git_blob_sha"]:
        raise ValueError("Evidence Git blob differs from reviewed source")


def require_regular_destination(target):
    if any(path.is_symlink() for path in (target, *target.parents)):
        raise ValueError("Evidence destination cannot contain symlinks")


def save_verified(target, data, expected):
    verify_bytes(data, expected)
    require_regular_destination(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def compiler_capture(root, policy):
    revision = commit_id(policy["builder"]["commit"])
    target = root / revision
    require_regular_destination(target)
    archive = download(
        f"https://codeload.github.com/Knuckles-Team/universal-skills/tar.gz/{revision}"
    )
    prefix = "universal_skills/agent-tools/mcp-builder/"
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as source:
        for member in source:
            path = member.name.partition("/")[2]
            if member.isfile() and path.startswith(prefix):
                name = relative_path(path[len(prefix) :])
                destination = target / name
                require_regular_destination(destination)
                if member.size > 4 * 1024 * 1024:
                    raise ValueError("Compiler evidence file exceeds its byte bound")
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(source.extractfile(member).read())
    for name, digest in policy["builder"]["compiler_sha256"].items():
        verify_bytes((target / relative_path(name)).read_bytes(), {"sha256": digest})
    return target


def read_json(root, relative):
    return json.loads((root / relative).read_text())


def base_policy(root, revision):
    revision = commit_id(revision)
    subprocess.check_call(["git", "cat-file", "-e", revision + "^{commit}"], cwd=root)
    manifest = "validation/generated-schemas.json"
    found = subprocess.check_output(
        ["git", "ls-tree", "--name-only", revision, "--", manifest], cwd=root
    )
    return json.loads(git_bytes(root, revision, manifest)) if found else None

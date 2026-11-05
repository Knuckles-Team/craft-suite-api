"""CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R006: the generator is deterministic and refuses without a snapshot."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from craft_suite_api.content_gen import errors as content_errors

REPO = Path(__file__).resolve().parent.parent

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R006")


def _script() -> Path:
    return REPO / "scripts" / "generate_app_content.py"


def _run(script_args: list[str]) -> tuple[int, str]:
    import importlib.util

    spec = importlib.util.spec_from_file_location("generate_app_content", _script())
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    import io
    from contextlib import redirect_stdout

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = module.main(script_args)
    return code, buffer.getvalue()


def _copy_into(tmp_path: Path) -> tuple[Path, Path]:
    content = tmp_path / "content"
    package = tmp_path / "craft_suite_api"
    shutil.copytree(REPO / "content", content)
    for name in ("ontology", "skills", "prompts"):
        shutil.copytree(REPO / "craft_suite_api" / name, package / name)
    return content, package


def _generated_bytes(package: Path) -> dict[str, bytes]:
    paths = (
        list(package.glob("ontology/artcraft-*.ttl"))
        + list(package.glob("skills/*/SKILL.md"))
        + list(package.glob("prompts/*.json"))
    )
    return {str(path.relative_to(package)): path.read_bytes() for path in sorted(paths)}


def test_write_is_deterministic_and_missing_snapshot_refuses(tmp_path) -> None:
    content, package = _copy_into(tmp_path)
    args = ["--write", "--content-dir", str(content), "--package-dir", str(package)]

    code, out = _run(args)
    assert code == 0, out
    first = _generated_bytes(package)

    code, out = _run(args)
    assert code == 0, out
    assert _generated_bytes(package) == first

    # An app with a source file but no snapshot refuses.
    snapshot = content / "snapshots" / "cadcraft.tools.json"
    snapshot.unlink()
    code, out = _run(args)
    assert code == 1
    assert content_errors.CONTENT_SNAPSHOT_MISSING in out
    assert "cadcraft" in out

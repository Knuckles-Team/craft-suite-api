"""Parity with universal-skills PR17's local-source image contract, without a build."""

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_image_inputs_are_packaged():
    """The image is rendered at build time from the shared template; the packaged inputs it installs exist."""
    version = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    assert version
    for name in [
        "pyproject.toml",
        "README.md",
        "LICENSE",
        "craft_suite_api/api_spec/backend.openapi.json",
        "craft_suite_api/api_spec/backend.source.json",
    ]:
        assert (ROOT / name).is_file()
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert (
        "api_spec/*.json"
        in metadata["tool"]["setuptools"]["package-data"]["craft_suite_api"]
    )


def test_source_build_docs_use_exact_reviewed_commit():
    docs = (ROOT / "docs/deployment.md").read_text()
    assert "git rev-parse --verify 'HEAD^{commit}'" in docs
    assert 'git archive --format=tar "$SOURCE_COMMIT"' in docs
    assert "org.opencontainers.image.revision=$SOURCE_COMMIT" in docs
    assert "does not freeze the index-resolved dependency closure" in docs
    assert "runtime artifact contract" in docs

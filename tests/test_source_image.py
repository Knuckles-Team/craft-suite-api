"""Parity with universal-skills PR17's local-source image contract, without a build."""

import configparser
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_source_image_installs_this_checkout_and_runtime_contract():
    docker = (ROOT / "docker/Dockerfile").read_text()
    assert "WORKDIR /src" in docker
    assert "COPY pyproject.toml README.md LICENSE ./" in docker
    assert "COPY craft_suite_api/ ./craft_suite_api/" in docker
    assert '--prerelease=allow ".[mcp]"' in docker
    assert '"craft-suite-api[mcp]' not in docker
    assert "COPY --from=builder-mcp /usr/local /usr/local" in docker
    assert "FROM mcp AS default" in docker
    assert "COPY . " not in docker
    assert "git clone" not in docker
    for name in [
        "pyproject.toml",
        "README.md",
        "LICENSE",
        "craft_suite_api/openapi_contract.json",
        "craft_suite_api/connector_manifest.yml",
    ]:
        assert (ROOT / name).is_file()
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert (
        "openapi_contract.json"
        in metadata["tool"]["setuptools"]["package-data"]["craft_suite_api"]
    )
    config = configparser.ConfigParser(interpolation=None)
    config.read(ROOT / ".bumpversion.cfg")
    assert not any("docker/Dockerfile" in section for section in config.sections())


def test_source_build_docs_use_exact_reviewed_commit():
    docs = (ROOT / "docs/deployment.md").read_text()
    assert "git rev-parse --verify 'HEAD^{commit}'" in docs
    assert 'git archive --format=tar "$SOURCE_COMMIT"' in docs
    assert "org.opencontainers.image.revision=$SOURCE_COMMIT" in docs
    assert "does not freeze the index-resolved dependency closure" in docs
    assert "runtime artifact contract" in docs

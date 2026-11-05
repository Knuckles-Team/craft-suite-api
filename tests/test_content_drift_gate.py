"""CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R007: the offline and live drift gates."""

from __future__ import annotations

import asyncio
import os
import shutil
import stat
import sys
from pathlib import Path

import pytest

from craft_suite_api.content_gen.errors import (
    CONTENT_DRIFT,
    CONTENT_SNAPSHOT_STALE,
)

REPO = Path(__file__).resolve().parent.parent
FIXTURE = REPO / "tests" / "fixtures" / "fake_app_cli.py"
APP = "testapp"

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R007")


def _run(script_args: list[str]) -> tuple[int, str]:
    import importlib.util
    import io
    from contextlib import redirect_stdout

    spec = importlib.util.spec_from_file_location(
        "generate_app_content", REPO / "scripts" / "generate_app_content.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = module.main(script_args)
    return code, buffer.getvalue()


def _make_wrapper(bin_dir: Path, drift: bool) -> None:
    bin_dir.mkdir(parents=True, exist_ok=True)
    wrapper = bin_dir / f"{APP}-cli"
    wrapper.write_text(
        "#!/bin/sh\n"
        + ("export FAKE_APP_CLI_TOOL_DRIFT=1\n" if drift else "")
        + f'exec "{sys.executable}" "{FIXTURE}" "$@"\n',
        encoding="utf-8",
    )
    wrapper.chmod(wrapper.stat().st_mode | stat.S_IEXEC)


def _write_source(content_dir: Path) -> None:
    apps = content_dir / "apps"
    apps.mkdir(parents=True, exist_ok=True)
    (apps / f"{APP}.yml").write_text(
        f"app: {APP}\n"
        "summary: A fixture app for the drift gate.\n"
        "classes:\n"
        "  - name: TestThing\n"
        "    parent: Artifact\n"
        "    description: A fixture thing.\n"
        "functionality:\n"
        "  - name: use_it\n"
        "    description: Read, write and ask.\n"
        "    tools: [read_demo, write_demo, ask_once]\n",
        encoding="utf-8",
    )


def test_offline_gate_flags_edited_file_and_live_gate_flags_stale_snapshot(
    tmp_path, monkeypatch
) -> None:
    # --- offline gate -------------------------------------------------------
    content = tmp_path / "content"
    package = tmp_path / "craft_suite_api"
    shutil.copytree(REPO / "content", content)
    for name in ("ontology", "skills", "prompts"):
        shutil.copytree(REPO / "craft_suite_api" / name, package / name)
    args = ["--check", "--content-dir", str(content), "--package-dir", str(package)]
    code, out = _run(args)
    assert code == 0, out

    target = package / "skills" / "cadcraft" / "SKILL.md"
    target.write_text(target.read_text(encoding="utf-8") + "edited\n", encoding="utf-8")
    code, out = _run(args)
    assert code == 1
    assert CONTENT_DRIFT in out
    assert "SKILL.md" in out

    # --- live gate ----------------------------------------------------------
    live_content = tmp_path / "live" / "content"
    live_package = tmp_path / "live" / "craft_suite_api"
    (live_package / "ontology").mkdir(parents=True)
    _write_source(live_content)

    bin_nodrift = tmp_path / "bin" / "nodrift"
    bin_drift = tmp_path / "bin" / "drift"
    _make_wrapper(bin_nodrift, drift=False)
    _make_wrapper(bin_drift, drift=True)

    # The committed snapshot comes from the CLI without drift.
    monkeypatch.setenv("PATH", str(bin_nodrift) + os.pathsep + os.environ["PATH"])
    import importlib.util as _ilu

    spec = _ilu.spec_from_file_location(
        "generate_app_content_live", REPO / "scripts" / "generate_app_content.py"
    )
    module = _ilu.module_from_spec(spec)
    spec.loader.exec_module(module)
    snapshot = asyncio.run(module.refresh_app(APP, 30.0))
    (live_content / "snapshots").mkdir(parents=True, exist_ok=True)
    (live_content / "snapshots" / f"{APP}.tools.json").write_text(
        module.snapshot_json(snapshot), encoding="utf-8"
    )

    # The live CLI now drifts: the gate must flag the changed tool.
    monkeypatch.setenv("PATH", str(bin_drift) + os.pathsep + os.environ["PATH"])
    code, out = _run(
        [
            "--live",
            "--content-dir",
            str(live_content),
            "--package-dir",
            str(live_package),
        ]
    )
    assert code == 1
    assert CONTENT_SNAPSHOT_STALE in out
    assert APP in out
    assert "changed=" in out

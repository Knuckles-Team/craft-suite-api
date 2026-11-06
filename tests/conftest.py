from pathlib import Path

import httpx
import pytest


@pytest.fixture
def backend(monkeypatch):
    """Build the backend sub-server over a fake transport.

    ``make(respond, allow_writes=..., configured=...)`` returns the
    sub-server; ``respond`` receives every outbound ``httpx.Request``.
    """
    from craft_suite_api import auth
    from craft_suite_api.backend import Gate, build_backend_server

    monkeypatch.setattr(auth, "load_config", lambda: None)
    monkeypatch.setenv("CRAFT_SUITE_FIXTURE_SESSION", "synthetic-session")
    monkeypatch.setenv("CRAFT_SUITE_API_TOKEN_REF", "env://CRAFT_SUITE_FIXTURE_SESSION")
    monkeypatch.setenv("ENABLE_DELEGATION", "false")

    def make(respond, *, allow_writes=False, configured=True):
        if configured:
            monkeypatch.setenv("CRAFT_SUITE_API_BASE_URL", ORIGIN)
        else:
            monkeypatch.delenv("CRAFT_SUITE_API_BASE_URL", raising=False)
        settings = auth.backend_settings()
        client = auth.build_client(settings, transport=httpx.MockTransport(respond))
        return build_backend_server(
            client, Gate(configured=configured, allow_writes=allow_writes)
        )

    yield make
    auth.close_client()


ORIGIN = "https://craft.example.invalid"


@pytest.fixture
def app_cli_factory(tmp_path, monkeypatch):
    """Place fixture app CLIs (tests/fixtures/fake_app_cli.py) on the PATH.

    Returns ``make(app, **knobs) -> wrapper_path``. The factory prepends its
    bin directory to the PATH for the rest of the test.
    """
    import os
    import stat
    import sys

    fixture = Path(__file__).resolve().parent / "fixtures" / "fake_app_cli.py"
    bin_dir = tmp_path / "app-bin"
    bin_dir.mkdir()
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])

    def make(
        app,
        *,
        die=False,
        no_mcp=False,
        drift=False,
        files=False,
        version="0.0.1-fixture",
    ):
        wrapper = bin_dir / f"{app}-cli"
        knobs = {
            "FAKE_APP_CLI_DIE_ON_MCP": die,
            "FAKE_APP_CLI_NO_MCP": no_mcp,
            "FAKE_APP_CLI_TOOL_DRIFT": drift,
            "FAKE_APP_CLI_FILES": files,
        }
        env_lines = [f"{name}=1" for name, enabled in knobs.items() if enabled]
        body = "\n".join(f"export {line}\n" for line in env_lines)
        wrapper.write_text(
            "#!/bin/sh\n"
            + body
            + f'FAKE_APP_CLI_APP="{app}"\n'
            + "export FAKE_APP_CLI_APP\n"
            + f'FAKE_APP_CLI_VERSION="{version}"\n'
            + "export FAKE_APP_CLI_VERSION\n"
            + f'exec "{sys.executable}" "{fixture}" "$@"\n',
            encoding="utf-8",
        )
        wrapper.chmod(wrapper.stat().st_mode | stat.S_IEXEC)
        return wrapper

    return make


@pytest.fixture
def overlay_writer(tmp_path):
    """Write one overlay TOML mapping apps to commands; returns the path."""
    import textwrap

    def write(entries: dict) -> Path:
        lines = []
        for name, command in entries.items():
            lines.append("[[upstream]]")
            lines.append(f'name = "{name}"')
            lines.append(f'command = "{command}"')
            lines.append("")
        path = tmp_path / f"overlay-{len(lines // 4)}.toml"
        path.write_text(textwrap.dedent("\n".join(lines)), encoding="utf-8")
        return path

    return write

from contextlib import closing
from pathlib import Path
from unittest.mock import MagicMock

import httpx
import pytest
from scion_sdk.auth.static import api_key_auth

from craft_suite_api.api import ApiClientSystem
from craft_suite_api.openapi_client import ClientPolicy


@pytest.fixture
def mock_api_client():
    client = MagicMock()
    client.get_system_status.return_value = {"status": "OK"}
    return client


@pytest.fixture
def synthetic_session_client(monkeypatch):
    """Create a closing synthetic-session client with caller-owned HTTP replies."""
    monkeypatch.setenv("CRAFT_SUITE_FIXTURE_SESSION", "synthetic-session")
    monkeypatch.setenv("ENABLE_DELEGATION", "false")

    def create(respond, *, allow_writes):
        return closing(
            ApiClientSystem(
                "https://craft.example.invalid",
                api_key_auth("env://CRAFT_SUITE_FIXTURE_SESSION", header="session"),
                credential_scheme="signed_session",
                policy=ClientPolicy(allow_writes=allow_writes),
                transport=httpx.MockTransport(respond),
            )
        )

    return create


def native_tool(arguments):
    """The per-operation tool name and its arguments for a contract call."""
    from craft_suite_api.openapi_runtime import operation_tool_name

    rest = {key: value for key, value in arguments.items() if key != "action"}
    return operation_tool_name(arguments["action"]), rest


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

    def make(app, *, die=False, no_mcp=False, drift=False, version="0.0.1-fixture"):
        wrapper = bin_dir / f"{app}-cli"
        env_lines = []
        if die:
            env_lines.append("FAKE_APP_CLI_DIE_ON_MCP=1")
        if no_mcp:
            env_lines.append("FAKE_APP_CLI_NO_MCP=1")
        if drift:
            env_lines.append("FAKE_APP_CLI_TOOL_DRIFT=1")
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

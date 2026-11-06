"""CONN-CRAFT-SUITE-API-APPS-R001: Tier 1 stays unchanged and degrades when unconfigured."""

from __future__ import annotations

import asyncio

import pytest
from fastmcp import Client

from craft_suite_api import _tier1_readiness
from craft_suite_api.error_authority import BACKEND_NOT_CONFIGURED

TIER1 = frozenset(
    {
        "craft_suite_get_folder_handler",
        "craft_suite_list_folders_handler",
        "craft_suite_status_alert_handler",
        "craft_suite_omni_gen_audio_models_handler",
        "craft_suite_omni_gen_image_models_handler",
        "craft_suite_omni_gen_mesh_models_handler",
        "craft_suite_omni_gen_splat_models_handler",
        "craft_suite_list_media_file_tags_handler",
        "craft_suite_list_tags_handler",
    }
)

pytestmark = pytest.mark.spec("CONN-CRAFT-SUITE-API-APPS-R001")


async def _listings():
    from craft_suite_api.mcp_server import build_server

    async with Client(build_server(command_args=[])) as client:
        tools = {tool.name for tool in await client.list_tools()}
    return tools


async def _call(tool: str):
    from craft_suite_api.mcp_server import build_server

    async with Client(build_server(command_args=[])) as client:
        result = await client.call_tool(tool, {})
    return result


def test_unconfigured_backend_lists_tools_and_refuses_typed(monkeypatch) -> None:
    monkeypatch.delenv("CRAFT_SUITE_API_BASE_URL", raising=False)

    # The former Tier 1 reads are still listed.
    tools = asyncio.run(_listings())
    assert TIER1 <= tools

    # A Tier 1 call answers the typed refusal, not a raw exception.
    for tool in ("craft_suite_status_alert_handler", "craft_suite_list_tags_handler"):
        result = asyncio.run(_call(tool))
        assert result.structured_content == {
            "cancelled": True,
            "operation": tool,
            "reason": BACKEND_NOT_CONFIGURED,
            "write_class": "read",
        }


def test_readiness_reports_not_configured_and_stays_ready(monkeypatch) -> None:
    monkeypatch.delenv("CRAFT_SUITE_API_BASE_URL", raising=False)
    probe = asyncio.run(_tier1_readiness())
    assert probe.ready is True
    assert probe.detail == {"backend": "not_configured"}

    monkeypatch.setenv("CRAFT_SUITE_API_BASE_URL", "https://service.example.invalid")
    probe = asyncio.run(_tier1_readiness())
    assert probe.ready is True
    assert probe.detail == {"backend": "configured"}


@pytest.mark.parametrize(
    ("url", "plaintext"),
    [
        ("https://craft.example.invalid/with/a/path", "false"),
        ("http://craft.example.invalid", "false"),
    ],
)
def test_unusable_backend_setting_starts_and_refuses_typed(
    monkeypatch, url, plaintext
) -> None:
    from craft_suite_api.error_authority import BACKEND_CONFIG_INVALID
    from craft_suite_api.mcp import BACKEND_STATE

    monkeypatch.setenv("CRAFT_SUITE_API_BASE_URL", url)
    monkeypatch.setenv("CRAFT_SUITE_API_ALLOW_PLAINTEXT", plaintext)
    monkeypatch.setenv("CRAFT_SUITE_FIXTURE_SESSION", "synthetic-session")
    monkeypatch.setenv("CRAFT_SUITE_API_TOKEN_REF", "env://CRAFT_SUITE_FIXTURE_SESSION")
    monkeypatch.setenv("ENABLE_DELEGATION", "false")
    try:
        # The server builds and lists the backend tools.
        tools = asyncio.run(_listings())
        assert TIER1 <= tools
        result = asyncio.run(_call("craft_suite_list_tags_handler"))
        assert result.structured_content == {
            "cancelled": True,
            "operation": "craft_suite_list_tags_handler",
            "reason": BACKEND_CONFIG_INVALID,
            "write_class": "read",
        }
        probe = asyncio.run(_tier1_readiness())
        assert probe.ready is True
        assert probe.detail == {"backend": "invalid", "code": BACKEND_CONFIG_INVALID}
    finally:
        BACKEND_STATE.clear()

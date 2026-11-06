"""The ArtCraft suite's upstream MCP declarations (CONN-CRAFT-SUITE-API-APPS-R002).

Every app runs ``<app>-cli mcp`` as a pooled stdio child behind this
connector's server; the SDK owns the registry, the pool and the health.
This module adds data only. Filesystem grants come from two operator
settings of absolute paths split by the platform path separator. An
unset setting holds no root, which denies access: the SDK passes no
flag. Write roots never default to the read roots.

Every app the vendor ships with an ``mcp`` subcommand is declared; the
``craft-suite-probe`` (CONN-CRAFT-SUITE-API-APPS-R003) re-checks the set.
"""

from __future__ import annotations

import os

from scion_sdk.config import setting
from scion_sdk.mcp.upstreams import ExchangeBinding, SandboxRoots, UpstreamDecl

__all__ = [
    "APPS",
    "FLAGLESS_APPS",
    "ROOT_FLAGS",
    "EXCHANGE",
    "READ_ROOTS_SETTING",
    "WRITE_ROOTS_SETTING",
    "UPSTREAMS",
    "build_upstreams",
    "root_paths",
]

#: The apps that expose an ``mcp`` subcommand, as of the last probe.
APPS = (
    "photocraft",
    "wordcraft",
    "pdfcraft",
    "solidcraft",
    "vectorcraft",
    "figcraft",
    "effectcraft",
    "filmcraft",
    "soundcraft",
    "deckcraft",
    "cadcraft",
    "designcraft",
    "gridcraft",
    "lightcraft",
    "materialcraft",
    "texturecraft",
)

READ_ROOTS_SETTING = "CRAFT_SUITE_READ_ROOTS"
WRITE_ROOTS_SETTING = "CRAFT_SUITE_WRITE_ROOTS"

READ_FLAG = "--automation-read-root"
WRITE_FLAG = "--automation-write-root"

#: Apps whose ``mcp`` subcommand has no filesystem-root flags (verified
#: against ``<app>-cli mcp --help`` in the shipped image). They take no root
#: flag, so the operator's root settings cannot reach them and the SDK passes
#: nothing. Their file access is bounded by the container, not by a flag;
#: calls that carry a ``path`` argument still run through the artifact
#: exchange, which stages them in the run directory.
FLAGLESS_APPS = ("filmcraft", "cadcraft", "gridcraft", "lightcraft")

#: Apps whose root flags have other names than ``READ_FLAG``/``WRITE_FLAG``
#: (verified against ``<app>-cli mcp --help``). solidcraft takes one
#: ``--allow-path DIR`` per folder it may read or write, and silently ignores
#: the automation flags, so without this its exports outside the folders of
#: designs it opened or saved refused.
ROOT_FLAGS = {
    "materialcraft": ("--read-root", "--write-root"),
    "solidcraft": ("--allow-path", "--allow-path"),
}

#: The arguments whose relative values land in the run's output directory
#: (CONN-CRAFT-SUITE-API-APPS-R013). Every app writes beneath its write root.
EXCHANGE = ExchangeBinding(path_args=("path", "dir", "out", "out_dir"))


def root_paths(setting_name: str) -> tuple[str, ...]:
    """Absolute roots from one operator setting, split by ``os.pathsep``.

    An unset or empty setting holds no root, which denies access. A
    relative path refuses at declaration time with the SDK's
    ``UPSTREAM_ROOT_UNSAFE``; this splitter checks nothing.
    """
    raw = setting(setting_name, "")
    if not raw:
        return ()
    return tuple(part for part in raw.split(os.pathsep) if part)


def build_upstreams() -> tuple[UpstreamDecl, ...]:
    """One declaration per app, with the operator's root settings applied."""
    read = root_paths(READ_ROOTS_SETTING)
    write = root_paths(WRITE_ROOTS_SETTING)
    return tuple(_declare(app, read, write) for app in APPS)


def _declare(app: str, read: tuple[str, ...], write: tuple[str, ...]) -> UpstreamDecl:
    """One app's declaration; a flagless app passes no root flag at all."""
    if app in FLAGLESS_APPS:
        sandbox = SandboxRoots(read_flag=None, write_flag=None)
    else:
        read_flag, write_flag = ROOT_FLAGS.get(app, (READ_FLAG, WRITE_FLAG))
        sandbox = SandboxRoots(
            read=read, write=write, read_flag=read_flag, write_flag=write_flag
        )
    return UpstreamDecl(
        name=app,
        kind="stdio",
        command=f"{app}-cli",
        args=("mcp",),
        sandbox=sandbox,
        exchange=EXCHANGE,
    )


#: The declarations the connector serves; the settings are read once, at
#: import, because the operator sets them before starting the server.
UPSTREAMS: tuple[UpstreamDecl, ...] = build_upstreams()

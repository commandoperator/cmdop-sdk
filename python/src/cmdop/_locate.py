"""Locate the ``cmdop-core`` binary the client spawns.

Single fat-wheel model: one ``py3-none-any`` wheel ships ALL 5 prebuilt
binaries as package data in ``cmdop/_bin/cmdop-core-<plat>-<arch>[.exe]``.
The runtime resolver below picks the host's binary from that dir, so a single
wheel installs everywhere and pip needs no platform-tag matching.

Resolution order:

1. ``CMDOP_CORE_BINARY`` env override (dev / local tests / offline escape hatch
   — point it at a ``go build``'d binary).
2. The host's baked binary, ``cmdop/_bin/cmdop-core-<plat>-<arch>[.exe]``,
   where ``<plat>-<arch>`` comes from ``sys.platform`` + ``platform.machine()``
   normalized to the npm/Node vocabulary (darwin/linux/win32 ; x64/arm64).

In all cases the binary is ``chmod``'d ``+x`` defensively (wheel/zip archives
can strip the executable bit) and the Windows ``.exe`` suffix is honoured.
"""

from __future__ import annotations

import os
import platform
import stat
import sys
from importlib.resources import as_file, files

# sys.platform -> npm/Node `process.platform` vocabulary (darwin/linux/win32).
# sys.platform is already "darwin"/"linux"; Windows reports "win32" too, so the
# only real normalization is making sure we never emit anything else.
_PLATFORMS = {"darwin": "darwin", "linux": "linux", "win32": "win32"}

# platform.machine() (lowercased) -> npm `process.arch` vocabulary (x64/arm64).
_ARCHES = {
    "x86_64": "x64",
    "amd64": "x64",
    "arm64": "arm64",
    "aarch64": "arm64",
}


def _host_slug() -> str | None:
    """Return ``<plat>-<arch>`` for this host, or None if unsupported."""
    plat = _PLATFORMS.get(sys.platform)
    arch = _ARCHES.get(platform.machine().lower())
    if plat is None or arch is None:
        return None
    return f"{plat}-{arch}"


def _binary_name() -> str:
    """The host's baked binary filename, e.g. ``cmdop-core-darwin-arm64``."""
    slug = _host_slug()
    exe = ".exe" if sys.platform == "win32" else ""
    return f"cmdop-core-{slug}{exe}"


def _make_executable(path: str) -> None:
    if sys.platform == "win32":
        return
    try:
        mode = os.stat(path).st_mode
        os.chmod(path, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except OSError:
        # Read-only store (nix, some CI caches) — the bit may already be set.
        pass


def locate_binary() -> str:
    """Return an absolute path to a runnable ``cmdop-core`` binary.

    Raises :class:`FileNotFoundError` if neither the override nor a baked binary
    is present, or if the host platform/arch has no prebuilt binary.
    """
    override = os.environ.get("CMDOP_CORE_BINARY")
    if override:
        if not os.path.exists(override):
            raise FileNotFoundError(
                f"CMDOP_CORE_BINARY points at a missing file: {override}"
            )
        _make_executable(override)
        return override

    slug = _host_slug()
    if slug is None:
        raise FileNotFoundError(
            f"cmdop-core has no prebuilt binary for {sys.platform}/"
            f"{platform.machine().lower()}. Set CMDOP_CORE_BINARY to a "
            "`go build -o /path/cmdop-core ./cmd/cmdop-core` output."
        )

    name = _binary_name()
    try:
        resource = files("cmdop._bin").joinpath(name)
        with as_file(resource) as p:
            path = str(p)
        if not os.path.exists(path):
            raise FileNotFoundError(path)
    except (FileNotFoundError, ModuleNotFoundError, OSError) as exc:
        raise FileNotFoundError(
            f"cmdop-core binary not found ({name}). The 5 baked binaries ship "
            "in the wheel under cmdop/_bin/; reinstall cmdop, or set "
            "CMDOP_CORE_BINARY to a `go build -o /path/cmdop-core "
            "./cmd/cmdop-core` output."
        ) from exc

    _make_executable(path)
    return path

"""Binary-locate tests: ``CMDOP_CORE_BINARY`` override, defensive chmod, the
``.exe`` suffix on Windows, and the actionable error when no binary is present.
"""

from __future__ import annotations

import os
import stat
import sys

import pytest

from cmdop import _locate
from cmdop._locate import _binary_name, _host_slug, locate_binary


def test_override_resolves_and_is_made_executable(tmp_path, monkeypatch) -> None:
    fake = tmp_path / "cmdop-core"
    fake.write_text("#!/bin/sh\nexit 0\n")
    fake.chmod(0o644)  # strip exec bit to prove locate re-adds it
    monkeypatch.setenv("CMDOP_CORE_BINARY", str(fake))

    resolved = locate_binary()
    assert resolved == str(fake)
    if sys.platform != "win32":
        assert os.stat(resolved).st_mode & stat.S_IXUSR


def test_override_missing_file_raises(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("CMDOP_CORE_BINARY", str(tmp_path / "nope"))
    with pytest.raises(FileNotFoundError, match="points at a missing file"):
        locate_binary()


def test_no_override_no_baked_binary_raises_actionable(monkeypatch) -> None:
    monkeypatch.delenv("CMDOP_CORE_BINARY", raising=False)
    # The baked binary (cmdop._bin) is absent in the dev tree (Phase 4 adds
    # it at release time) — the error must point the user at CMDOP_CORE_BINARY.
    with pytest.raises(FileNotFoundError, match="CMDOP_CORE_BINARY"):
        locate_binary()


def test_binary_name_per_platform_and_windows_exe(monkeypatch) -> None:
    # Fat wheel: the binary name carries the host slug, e.g. cmdop-core-linux-x64.
    monkeypatch.setattr(_locate.sys, "platform", "linux")
    monkeypatch.setattr(_locate.platform, "machine", lambda: "x86_64")
    assert _host_slug() == "linux-x64"
    assert _binary_name() == "cmdop-core-linux-x64"

    monkeypatch.setattr(_locate.sys, "platform", "win32")
    monkeypatch.setattr(_locate.platform, "machine", lambda: "AMD64")
    assert _host_slug() == "win32-x64"
    assert _binary_name() == "cmdop-core-win32-x64.exe"

    monkeypatch.setattr(_locate.sys, "platform", "darwin")
    monkeypatch.setattr(_locate.platform, "machine", lambda: "arm64")
    assert _host_slug() == "darwin-arm64"
    assert _binary_name() == "cmdop-core-darwin-arm64"


def test_host_slug_unsupported_returns_none(monkeypatch) -> None:
    monkeypatch.setattr(_locate.sys, "platform", "freebsd")
    monkeypatch.setattr(_locate.platform, "machine", lambda: "x86_64")
    assert _host_slug() is None


def test_unsupported_platform_raises(monkeypatch) -> None:
    monkeypatch.delenv("CMDOP_CORE_BINARY", raising=False)
    monkeypatch.setattr(_locate.sys, "platform", "freebsd")
    monkeypatch.setattr(_locate.platform, "machine", lambda: "x86_64")
    with pytest.raises(FileNotFoundError, match="no prebuilt binary"):
        locate_binary()

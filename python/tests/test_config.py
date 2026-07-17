from __future__ import annotations

import pytest

from cmdop.config import DEFAULT_TIMEOUT_MS, ClientConfig


def test_local_client_needs_no_explicit_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("CMDOP_TOKEN", "CMDOP_BASE_URL", "CMDOP_TIMEOUT_MS"):
        monkeypatch.delenv(name, raising=False)
    assert ClientConfig.resolve() == ClientConfig(timeout_ms=DEFAULT_TIMEOUT_MS)


def test_explicit_values_override_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CMDOP_TOKEN", "env")
    monkeypatch.setenv("CMDOP_BASE_URL", "https://env/")
    config = ClientConfig.resolve(token="arg", base_url="https://arg///", timeout_ms=99)
    assert config == ClientConfig(token="arg", base_url="https://arg", timeout_ms=99)


def test_platform_api_key_is_not_a_relay_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CMDOP_TOKEN", raising=False)
    monkeypatch.setenv("CMDOP_API_KEY", "platform-only")
    assert ClientConfig.resolve().token is None


def test_timeout_must_be_positive() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        ClientConfig.resolve(timeout_ms=0)

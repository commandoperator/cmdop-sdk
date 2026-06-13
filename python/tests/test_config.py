"""ClientConfig.resolve() env-precedence tests."""

from __future__ import annotations

import pytest

from cmdop.config import DEFAULT_BASE_URL, DEFAULT_TIMEOUT_MS, ClientConfig

ENV_KEYS = [
    "CMDOP_TOKEN",
    "CMDOP_API_KEY",
    "CMDOP_BASE_URL",
    "CMDOP_FLEET_ID",
    "CMDOP_TIMEOUT_MS",
]


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_explicit_token_wins_over_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CMDOP_TOKEN", "from-env")
    assert ClientConfig.resolve(token="explicit").token == "explicit"


def test_token_env_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CMDOP_TOKEN", "env-token")
    assert ClientConfig.resolve().token == "env-token"


def test_cmdop_token_wins_over_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CMDOP_TOKEN", "the-token")
    monkeypatch.setenv("CMDOP_API_KEY", "the-api-key")
    assert ClientConfig.resolve().token == "the-token"


def test_api_key_used_when_token_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CMDOP_API_KEY", "the-api-key")
    assert ClientConfig.resolve().token == "the-api-key"


def test_missing_token_raises() -> None:
    with pytest.raises(ValueError, match="No token"):
        ClientConfig.resolve()


def test_defaults() -> None:
    cfg = ClientConfig.resolve(token="t")
    assert cfg.base_url == DEFAULT_BASE_URL
    assert cfg.fleet_id is None
    assert cfg.timeout_ms == DEFAULT_TIMEOUT_MS


def test_base_url_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CMDOP_BASE_URL", "https://env.example.com")
    assert ClientConfig.resolve(token="t").base_url == "https://env.example.com"
    assert (
        ClientConfig.resolve(token="t", base_url="https://explicit.example.com/").base_url
        == "https://explicit.example.com"
    )


def test_fleet_and_timeout_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CMDOP_FLEET_ID", "fleet-123")
    monkeypatch.setenv("CMDOP_TIMEOUT_MS", "5000")
    cfg = ClientConfig.resolve(token="t")
    assert cfg.fleet_id == "fleet-123"
    assert cfg.timeout_ms == 5000


def test_explicit_timeout_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CMDOP_TIMEOUT_MS", "5000")
    assert ClientConfig.resolve(token="t", timeout_ms=12345).timeout_ms == 12345

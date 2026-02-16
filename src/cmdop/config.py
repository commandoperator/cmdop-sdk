"""
SDK Configuration using pydantic-settings.

Provides hierarchical configuration with environment variable support.

Loading order (later overrides earlier):
1. Default values in this file
2. Environment variables (CMDOP_ prefix)
3. .env file (if present)
4. Explicit constructor arguments
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SDKSettings(BaseSettings):
    """
    SDK configuration with hierarchical loading.

    All settings can be overridden via environment variables with CMDOP_ prefix.

    Example:
        export CMDOP_CONNECT_TIMEOUT=15.0
        export CMDOP_RETRY_ATTEMPTS=3
        export CMDOP_LOG_JSON=false

    Usage:
        from cmdop.config import get_settings

        settings = get_settings()
        print(settings.retry_attempts)
    """

    model_config = SettingsConfigDict(
        env_prefix="CMDOP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ==================== Connection ====================

    connect_timeout: Annotated[float, Field(ge=1.0, le=120.0)] = 10.0
    """Connection timeout in seconds. Default: 10.0"""

    request_timeout: Annotated[float, Field(ge=1.0, le=300.0)] = 30.0
    """Request timeout in seconds. Default: 30.0"""

    # ==================== Streaming ====================

    keepalive_interval: Annotated[float, Field(ge=10.0, le=30.0)] = 25.0
    """Keep-alive ping interval in seconds. Must be < 30s for NAT. Default: 25.0"""

    queue_max_size: Annotated[int, Field(ge=100, le=10000)] = 1000
    """Maximum pending messages in queue. Default: 1000"""

    queue_put_timeout: Annotated[float, Field(ge=1.0, le=30.0)] = 5.0
    """Timeout for queue put operations in seconds. Default: 5.0"""

    # ==================== Resilience (stamina) ====================

    retry_attempts: Annotated[int, Field(ge=1, le=20)] = 5
    """Maximum retry attempts. Default: 5"""

    retry_timeout: Annotated[float, Field(ge=5.0, le=120.0)] = 30.0
    """Total retry timeout in seconds. Default: 30.0"""

    # ==================== Circuit Breaker (aiobreaker) ====================

    circuit_fail_max: Annotated[int, Field(ge=1, le=20)] = 5
    """Failures before opening circuit. Default: 5"""

    circuit_reset_timeout: Annotated[float, Field(ge=10.0, le=300.0)] = 60.0
    """Seconds before trying half-open. Default: 60.0"""

    # ==================== Logging (structlog) ====================

    log_json: bool = True
    """Output JSON format (True for production, False for development)."""

    log_level: str = "INFO"
    """Minimum log level: DEBUG, INFO, WARNING, ERROR. Default: INFO"""

    # ==================== gRPC ====================

    max_message_size: Annotated[int, Field(ge=1024 * 1024)] = 32 * 1024 * 1024
    """Maximum gRPC message size in bytes. Default: 32MB"""

    # ==================== API Endpoints ====================

    api_base_url: str = "https://api.cmdop.com"
    """Base URL for REST API calls."""

    grpc_server: str = "grpc.cmdop.com:443"
    """gRPC server address for remote connections."""


# Singleton pattern with lru_cache
_settings: SDKSettings | None = None


def get_settings() -> SDKSettings:
    """
    Get SDK settings singleton.

    Settings are loaded once and cached. To reload, use reset_settings().

    Returns:
        SDKSettings instance

    Usage:
        settings = get_settings()
        print(settings.retry_attempts)
    """
    global _settings
    if _settings is None:
        _settings = SDKSettings()
    return _settings


def reset_settings() -> None:
    """
    Reset settings singleton.

    Forces reload of settings on next get_settings() call.
    Useful for testing or when environment changes.
    """
    global _settings
    _settings = None


def configure_settings(**overrides: object) -> SDKSettings:
    """
    Configure settings with explicit overrides.

    Args:
        **overrides: Settings to override

    Returns:
        New SDKSettings instance (also sets singleton)

    Usage:
        settings = configure_settings(
            retry_attempts=3,
            log_json=False,
        )
    """
    global _settings
    _settings = SDKSettings(**overrides)  # type: ignore[arg-type]
    return _settings

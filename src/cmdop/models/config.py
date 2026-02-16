"""
Configuration models for CMDOP SDK.

These models control connection behavior, timeouts, retries, and keepalive.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class KeepaliveConfig(BaseModel):
    """HTTP/2 keepalive settings for long-lived connections."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    time_ms: Annotated[int, Field(ge=1000, le=300_000)] = 30_000
    """Interval between keepalive pings (ms). Default: 30s"""

    timeout_ms: Annotated[int, Field(ge=500, le=60_000)] = 5_000
    """Timeout waiting for ping response (ms). Default: 5s"""

    permit_without_calls: bool = True
    """Send pings even when no active RPCs."""


class RetryConfig(BaseModel):
    """Exponential backoff retry configuration."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    max_attempts: Annotated[int, Field(ge=1, le=10)] = 3
    """Maximum retry attempts. Default: 3"""

    initial_backoff_seconds: Annotated[float, Field(ge=0.1, le=10.0)] = 1.0
    """Initial backoff delay. Default: 1s"""

    max_backoff_seconds: Annotated[float, Field(ge=1.0, le=300.0)] = 30.0
    """Maximum backoff delay. Default: 30s"""

    backoff_multiplier: Annotated[float, Field(ge=1.0, le=5.0)] = 2.0
    """Multiplier per attempt. Default: 2.0"""

    jitter_fraction: Annotated[float, Field(ge=0.0, le=0.5)] = 0.1
    """Random jitter fraction. Default: 0.1 (10%)"""

    retryable_codes: tuple[str, ...] = ("UNAVAILABLE", "RESOURCE_EXHAUSTED")
    """gRPC status codes to retry on."""


class ConnectionConfig(BaseModel):
    """Full connection configuration for SDK client."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    # Timeouts
    connect_timeout_seconds: Annotated[float, Field(ge=1.0, le=60.0)] = 10.0
    """Timeout for initial connection. Default: 10s"""

    request_timeout_seconds: Annotated[float, Field(ge=1.0, le=300.0)] = 30.0
    """Default timeout for unary RPCs. Default: 30s"""

    stream_timeout_seconds: Annotated[float, Field(ge=0.0)] = 0.0
    """Timeout for streaming RPCs. 0 = no timeout."""

    # Keepalive
    keepalive: KeepaliveConfig = Field(default_factory=KeepaliveConfig)
    """HTTP/2 keepalive settings."""

    # Retry
    retry: RetryConfig = Field(default_factory=RetryConfig)
    """Retry policy for transient failures."""

    # gRPC options
    max_message_size_mb: Annotated[int, Field(ge=1, le=100)] = 50
    """Maximum message size in MB. Default: 50MB"""

    @property
    def grpc_options(self) -> list[tuple[str, int]]:
        """Convert to gRPC channel options."""
        return [
            ("grpc.keepalive_time_ms", self.keepalive.time_ms),
            ("grpc.keepalive_timeout_ms", self.keepalive.timeout_ms),
            (
                "grpc.keepalive_permit_without_calls",
                1 if self.keepalive.permit_without_calls else 0,
            ),
            ("grpc.max_send_message_length", self.max_message_size_mb * 1024 * 1024),
            ("grpc.max_receive_message_length", self.max_message_size_mb * 1024 * 1024),
        ]


# Default configuration instance
DEFAULT_CONFIG = ConnectionConfig()

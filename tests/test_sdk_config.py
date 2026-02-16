"""
Tests for SDK configuration module (pydantic-settings).
"""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from cmdop.config import (
    SDKSettings,
    configure_settings,
    get_settings,
    reset_settings,
)


class TestSDKSettings:
    """Tests for SDKSettings pydantic-settings model."""

    def setup_method(self):
        """Reset settings before each test."""
        reset_settings()

    def teardown_method(self):
        """Reset settings after each test."""
        reset_settings()

    def test_default_values(self):
        """Test default configuration values."""
        settings = SDKSettings()

        # Connection defaults
        assert settings.connect_timeout == 10.0
        assert settings.request_timeout == 30.0

        # Streaming defaults
        assert settings.keepalive_interval == 25.0
        assert settings.queue_max_size == 1000
        assert settings.queue_put_timeout == 5.0

        # Resilience defaults
        assert settings.retry_attempts == 5
        assert settings.retry_timeout == 30.0
        assert settings.circuit_fail_max == 5
        assert settings.circuit_reset_timeout == 60.0

        # Logging defaults
        assert settings.log_json is True
        assert settings.log_level == "INFO"

        # gRPC defaults
        assert settings.max_message_size == 32 * 1024 * 1024  # 32MB

        # API defaults
        assert settings.api_base_url == "https://api.cmdop.com"
        assert settings.grpc_server == "grpc.cmdop.com:443"

    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        with patch.dict(os.environ, {
            "CMDOP_CONNECT_TIMEOUT": "15.0",
            "CMDOP_RETRY_ATTEMPTS": "3",
            "CMDOP_LOG_JSON": "false",
            "CMDOP_LOG_LEVEL": "DEBUG",
        }):
            reset_settings()
            settings = SDKSettings()

            assert settings.connect_timeout == 15.0
            assert settings.retry_attempts == 3
            assert settings.log_json is False
            assert settings.log_level == "DEBUG"

    def test_validation_connect_timeout_min(self):
        """Test connect_timeout minimum validation."""
        with pytest.raises(ValidationError):
            SDKSettings(connect_timeout=0.5)  # Below minimum of 1.0

    def test_validation_connect_timeout_max(self):
        """Test connect_timeout maximum validation."""
        with pytest.raises(ValidationError):
            SDKSettings(connect_timeout=150.0)  # Above maximum of 120.0

    def test_validation_retry_attempts_min(self):
        """Test retry_attempts minimum validation."""
        with pytest.raises(ValidationError):
            SDKSettings(retry_attempts=0)  # Below minimum of 1

    def test_validation_retry_attempts_max(self):
        """Test retry_attempts maximum validation."""
        with pytest.raises(ValidationError):
            SDKSettings(retry_attempts=25)  # Above maximum of 20

    def test_validation_keepalive_interval_min(self):
        """Test keepalive_interval minimum validation."""
        with pytest.raises(ValidationError):
            SDKSettings(keepalive_interval=5.0)  # Below minimum of 10.0

    def test_validation_keepalive_interval_max(self):
        """Test keepalive_interval maximum validation."""
        with pytest.raises(ValidationError):
            SDKSettings(keepalive_interval=35.0)  # Above maximum of 30.0

    def test_validation_queue_max_size_min(self):
        """Test queue_max_size minimum validation."""
        with pytest.raises(ValidationError):
            SDKSettings(queue_max_size=50)  # Below minimum of 100

    def test_validation_max_message_size_min(self):
        """Test max_message_size minimum validation."""
        with pytest.raises(ValidationError):
            SDKSettings(max_message_size=1024)  # Below minimum of 1MB


class TestSettingsSingleton:
    """Tests for settings singleton pattern."""

    def setup_method(self):
        """Reset settings before each test."""
        reset_settings()

    def teardown_method(self):
        """Reset settings after each test."""
        reset_settings()

    def test_get_settings_returns_same_instance(self):
        """Test that get_settings returns singleton."""
        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    def test_reset_settings_clears_singleton(self):
        """Test that reset_settings clears the singleton."""
        settings1 = get_settings()
        reset_settings()
        settings2 = get_settings()

        # Different instances after reset
        assert settings1 is not settings2

    def test_configure_settings_creates_new_instance(self):
        """Test that configure_settings creates new singleton."""
        original = get_settings()

        configured = configure_settings(
            retry_attempts=10,
            log_json=False,
        )

        assert configured.retry_attempts == 10
        assert configured.log_json is False

        # New singleton is returned by get_settings
        assert get_settings() is configured
        assert get_settings() is not original


class TestSettingsEdgeCases:
    """Tests for edge cases and special scenarios."""

    def setup_method(self):
        """Reset settings before each test."""
        reset_settings()

    def teardown_method(self):
        """Reset settings after each test."""
        reset_settings()

    def test_extra_fields_ignored(self):
        """Test that extra fields are ignored (extra='ignore')."""
        # Should not raise even with unknown field
        settings = SDKSettings(unknown_field="value")  # type: ignore

        # Default values should be used
        assert settings.connect_timeout == 10.0

    def test_valid_log_levels(self):
        """Test valid log levels are accepted."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            settings = SDKSettings(log_level=level)
            assert settings.log_level == level

    def test_env_prefix_is_cmdop(self):
        """Test that environment variable prefix is CMDOP_."""
        assert SDKSettings.model_config.get("env_prefix") == "CMDOP_"

    def test_boundary_values_accepted(self):
        """Test boundary values are accepted."""
        settings = SDKSettings(
            connect_timeout=1.0,  # min
            request_timeout=300.0,  # max
            keepalive_interval=10.0,  # min
            retry_attempts=1,  # min
            circuit_fail_max=20,  # max
        )

        assert settings.connect_timeout == 1.0
        assert settings.request_timeout == 300.0
        assert settings.keepalive_interval == 10.0
        assert settings.retry_attempts == 1
        assert settings.circuit_fail_max == 20

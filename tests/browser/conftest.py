"""Shared fixtures for browser tests."""

from unittest.mock import MagicMock

import pytest


class MockChannel:
    """Mock gRPC channel for testing."""
    pass


class MockTransport:
    """Mock transport for testing services."""

    def __init__(self):
        self._channel = MockChannel()
        self._config = MagicMock()
        self._config.request_timeout_seconds = 30.0
        self._mode = "test"

    @property
    def channel(self):
        return self._channel

    @property
    def async_channel(self):
        return self._channel

    @property
    def metadata(self):
        return [("authorization", "Bearer test_token")]

    @property
    def config(self):
        return self._config

    @property
    def mode(self):
        return self._mode


@pytest.fixture
def mock_transport():
    """Create mock transport for tests."""
    return MockTransport()


@pytest.fixture
def mock_stub():
    """Create mock gRPC stub."""
    return MagicMock()

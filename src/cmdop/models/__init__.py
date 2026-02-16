"""
CMDOP SDK Models.

Pydantic 2 models for configuration, requests, and responses.
All models use strict validation with extra="forbid".
"""

from cmdop.models.base import SDKBaseModel
from cmdop.models.agent import (
    AgentEventType,
    AgentResult,
    AgentRunOptions,
    AgentRunRequest,
    AgentStreamEvent,
    AgentToolResult,
    AgentType,
    AgentUsage,
)
from cmdop.models.config import (
    ConnectionConfig,
    KeepaliveConfig,
    RetryConfig,
)
from cmdop.models.extract import (
    ExtractErrorCode,
    ExtractMetrics,
    ExtractOptions,
    ExtractResult,
    TokenUsage,
)
from cmdop.models.files import (
    FileEntry,
    FileInfo,
    FileType,
)
from cmdop.models.terminal import (
    CreateSessionRequest,
    OutputChunk,
    ResizeRequest,
    SessionInfo,
    SessionListItem,
    SessionListResponse,
    SessionMode,
    SessionState,
    SignalType,
)

__all__ = [
    # Base
    "SDKBaseModel",
    # Config
    "ConnectionConfig",
    "KeepaliveConfig",
    "RetryConfig",
    # Terminal
    "CreateSessionRequest",
    "SessionInfo",
    "SessionListItem",
    "SessionListResponse",
    "SessionState",
    "SessionMode",
    "SignalType",
    "OutputChunk",
    "ResizeRequest",
    # Files
    "FileEntry",
    "FileInfo",
    "FileType",
    # Extract
    "ExtractErrorCode",
    "ExtractMetrics",
    "ExtractOptions",
    "ExtractResult",
    "TokenUsage",
    # Agent
    "AgentType",
    "AgentEventType",
    "AgentUsage",
    "AgentToolResult",
    "AgentRunOptions",
    "AgentStreamEvent",
    "AgentResult",
    "AgentRunRequest",
]

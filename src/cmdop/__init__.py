"""
CMDOP Python SDK.

Python SDK for programmatic interaction with CMDOP agents.
Supports remote mode (cloud relay) and local mode (direct IPC).

Quick Start:
    >>> from cmdop import CMDOPClient
    >>>
    >>> # Remote mode
    >>> client = CMDOPClient.remote(api_key="cmdop_live_xxx")
    >>> session = client.terminal.create()
    >>> client.terminal.send_input(session.session_id, b"ls\\n")
    >>>
    >>> # File operations
    >>> files = client.files.list("/home/user")
    >>> content = client.files.read("/etc/hosts")

Structured Extraction:
    >>> from pydantic import BaseModel
    >>> class Config(BaseModel):
    ...     host: str
    ...     port: int
    >>>
    >>> result = client.extract.run(Config, "Find database config")
    >>> if result.success:
    ...     print(result.data.host)  # Type-safe access

Async Usage:
    >>> from cmdop import AsyncCMDOPClient
    >>>
    >>> async with AsyncCMDOPClient.remote(api_key="cmdop_live_xxx") as client:
    ...     session = await client.terminal.create()
    ...     await client.terminal.send_input(session.session_id, b"ls\\n")
"""

from cmdop.client import AsyncCMDOPClient, CMDOPClient
from cmdop.config import SDKSettings, configure_settings, get_settings
from cmdop.exceptions import (
    AgentBusyError,
    AgentError,
    AgentNotRunningError,
    AgentOfflineError,
    AuthenticationError,
    BrowserElementNotFoundError,
    BrowserError,
    BrowserNavigationError,
    BrowserSessionClosedError,
    CMDOPError,
    ConnectionError,
    ConnectionLostError,
    ConnectionTimeoutError,
    FeatureNotAvailableError,
    FileError,
    FileNotFoundError,
    FilePermissionError,
    FileTooLargeError,
    InvalidAPIKeyError,
    PermissionDeniedError,
    RateLimitError,
    SessionClosedError,
    SessionError,
    SessionInterruptedError,
    SessionNotFoundError,
    StalePortFileError,
    TokenExpiredError,
)
from cmdop.models import (
    SDKBaseModel,
    AgentEventType,
    AgentResult,
    AgentRunOptions,
    AgentRunRequest,
    AgentStreamEvent,
    AgentToolResult,
    AgentType,
    AgentUsage,
    ConnectionConfig,
    CreateSessionRequest,
    ExtractErrorCode,
    ExtractMetrics,
    ExtractOptions,
    ExtractResult,
    FileEntry,
    FileInfo,
    FileType,
    KeepaliveConfig,
    OutputChunk,
    ResizeRequest,
    RetryConfig,
    SessionInfo,
    SessionListItem,
    SessionListResponse,
    SessionMode,
    SessionState,
    SignalType,
    TokenUsage,
)
from cmdop.transport import (
    AgentInfo,
    LocalTransport,
    RemoteTransport,
    TransportType,
    discover_agent,
)
from cmdop.streaming import (
    StreamCallback,
    StreamEvent,
    StreamState,
    TerminalStream,
)
from cmdop.discovery import (
    AgentDiscovery,
    AgentStatus,
    RemoteAgentInfo,
    get_online_agents,
    list_agents,
)
from cmdop.helpers import (
    NetworkAnalyzer,
    NetworkSnapshot,
    RequestSnapshot,
    # Desktop management
    ensure_desktop_running,
    start_desktop,
    handle_cmdop_error,
    with_auto_restart,
)
from cmdop.services.download import DownloadResult
from cmdop.logging import (
    get_logger,
    setup_logging,
    find_project_root,
    get_log_dir,
)

__version__ = "0.1.38"

__all__ = [
    # Version
    "__version__",
    # Clients
    "CMDOPClient",
    "AsyncCMDOPClient",
    # Config (pydantic-settings)
    "SDKSettings",
    "get_settings",
    "configure_settings",
    # Transport
    "LocalTransport",
    "RemoteTransport",
    "TransportType",
    "AgentInfo",
    "discover_agent",
    # Config models (legacy)
    "ConnectionConfig",
    "KeepaliveConfig",
    "RetryConfig",
    # Terminal models
    "CreateSessionRequest",
    "SessionInfo",
    "SessionListItem",
    "SessionListResponse",
    "SessionState",
    "SessionMode",
    "SignalType",
    "OutputChunk",
    "ResizeRequest",
    # File models
    "FileEntry",
    "FileInfo",
    "FileType",
    # Streaming
    "TerminalStream",
    "StreamState",
    "StreamEvent",
    "StreamCallback",
    # Discovery (remote)
    "AgentDiscovery",
    "AgentStatus",
    "RemoteAgentInfo",
    "list_agents",
    "get_online_agents",
    # Base model
    "SDKBaseModel",
    # Extract models
    "ExtractErrorCode",
    "ExtractMetrics",
    "ExtractOptions",
    "ExtractResult",
    "TokenUsage",
    # Agent models
    "AgentType",
    "AgentEventType",
    "AgentUsage",
    "AgentToolResult",
    "AgentRunOptions",
    "AgentStreamEvent",
    "AgentResult",
    "AgentRunRequest",
    # Exceptions
    "CMDOPError",
    "ConnectionError",
    "AgentNotRunningError",
    "StalePortFileError",
    "ConnectionTimeoutError",
    "ConnectionLostError",
    "AuthenticationError",
    "InvalidAPIKeyError",
    "PermissionDeniedError",
    "TokenExpiredError",
    "AgentError",
    "AgentOfflineError",
    "AgentBusyError",
    "FeatureNotAvailableError",
    "SessionError",
    "SessionNotFoundError",
    "SessionClosedError",
    "SessionInterruptedError",
    "FileError",
    "FileNotFoundError",
    "FilePermissionError",
    "FileTooLargeError",
    "RateLimitError",
    # Browser exceptions
    "BrowserError",
    "BrowserSessionClosedError",
    "BrowserNavigationError",
    "BrowserElementNotFoundError",
    # Helpers
    "NetworkAnalyzer",
    "NetworkSnapshot",
    "RequestSnapshot",
    # Desktop management
    "ensure_desktop_running",
    "start_desktop",
    "handle_cmdop_error",
    "with_auto_restart",
    # Logging
    "get_logger",
    "setup_logging",
    "find_project_root",
    "get_log_dir",
    # Download
    "DownloadResult",
]

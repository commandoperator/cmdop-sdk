"""
CMDOP SDK Exception Hierarchy.

All SDK exceptions inherit from CMDOPError for easy catching.
Exceptions are organized by category: connection, auth, session, etc.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grpc import RpcError


# =============================================================================
# Base Exception
# =============================================================================


class CMDOPError(Exception):
    """Base exception for all CMDOP SDK errors."""

    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.message = message
        # Store cause but suppress chain display
        self._original_cause = cause

    def __str__(self) -> str:
        return self.message


# =============================================================================
# Connection Errors
# =============================================================================


class ConnectionError(CMDOPError):
    """Base for connection-related errors."""


class AgentNotRunningError(ConnectionError):
    """Local agent is not running or not discoverable."""

    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = (
                "CMDOP agent is not running.\n\n"
                "To fix, run one of:\n"
                "  • cmdop serve          # Start local server\n"
                "  • Open CMDOP Desktop   # Starts server automatically\n"
            )
        super().__init__(message)


class StalePortFileError(ConnectionError):
    """Discovery file exists but agent is unreachable (likely crashed)."""

    def __init__(self, discovery_path: str) -> None:
        self.discovery_path = discovery_path
        super().__init__(f"Stale discovery file at {discovery_path}")

    def cleanup(self) -> None:
        """Remove the stale discovery file."""
        import os

        try:
            os.remove(self.discovery_path)
        except OSError:
            pass


class ConnectionTimeoutError(ConnectionError):
    """Connection attempt timed out."""

    def __init__(
        self,
        timeout_seconds: float = 30.0,
        *,
        operation: str | None = None,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.operation = operation
        if operation:
            msg = f"{operation}: timed out after {timeout_seconds}s"
        else:
            msg = f"Connection timed out after {timeout_seconds}s"
        msg += "\n\nPossible causes:\n"
        msg += "  • Agent is offline or not connected to cloud relay\n"
        msg += "  • Network connectivity issues\n"
        msg += "  • Server is overloaded\n"
        super().__init__(msg)


class ConnectionLostError(ConnectionError):
    """Connection was lost during operation."""


# =============================================================================
# Authentication Errors
# =============================================================================


class AuthenticationError(CMDOPError):
    """Base for authentication errors."""


class InvalidAPIKeyError(AuthenticationError):
    """API key is invalid or expired."""

    def __init__(self, message: str = "Invalid API key") -> None:
        super().__init__(message)


class PermissionDeniedError(AuthenticationError):
    """Permission denied (e.g., UID mismatch on Unix socket)."""

    def __init__(
        self,
        message: str = "Permission denied",
        *,
        agent_uid: int | None = None,
        caller_uid: int | None = None,
    ) -> None:
        self.agent_uid = agent_uid
        self.caller_uid = caller_uid
        if agent_uid is not None and caller_uid is not None:
            message = f"{message} (agent UID: {agent_uid}, caller UID: {caller_uid})"
        super().__init__(message)


class TokenExpiredError(AuthenticationError):
    """Authentication token has expired."""


# =============================================================================
# Agent Errors
# =============================================================================


class AgentError(CMDOPError):
    """Base for agent-related errors."""


class AgentOfflineError(AgentError):
    """Target agent is not connected to cloud relay."""

    def __init__(self, agent_id: str | None = None) -> None:
        self.agent_id = agent_id
        msg = f"Agent {agent_id} is offline" if agent_id else "Agent is offline"
        super().__init__(msg)


class AgentBusyError(AgentError):
    """Agent is busy and cannot accept new requests."""


class FeatureNotAvailableError(AgentError):
    """Requested feature is not available in current mode."""

    def __init__(self, feature: str, mode: str) -> None:
        self.feature = feature
        self.mode = mode
        super().__init__(f"Feature '{feature}' is not available in {mode} mode")


# =============================================================================
# Browser Errors
# =============================================================================


class BrowserError(CMDOPError):
    """Base for browser-related errors."""


class BrowserSessionClosedError(BrowserError):
    """Browser session or page was closed unexpectedly."""

    def __init__(self, error_detail: str = "") -> None:
        self.error_detail = error_detail
        message = (
            "Browser session was closed unexpectedly.\n\n"
            "Possible causes:\n"
            "  • Browser process crashed\n"
            "  • CMDOP Desktop was restarted\n"
            "  • Page navigation caused session to close\n\n"
            "To fix:\n"
            "  • Restart CMDOP Desktop or run: cmdop serve\n"
            "  • Create a new browser session\n"
        )
        if error_detail:
            message += f"\nDetails: {error_detail}"
        super().__init__(message)


class BrowserNavigationError(BrowserError):
    """Navigation to URL failed."""

    def __init__(self, url: str, error_detail: str = "") -> None:
        self.url = url
        self.error_detail = error_detail
        message = f"Failed to navigate to: {url}"
        if "target closed" in error_detail.lower():
            message += (
                "\n\nBrowser session was closed. "
                "Restart CMDOP Desktop or cmdop serve."
            )
        elif "timeout" in error_detail.lower():
            message += "\n\nPage took too long to load. Try increasing timeout."
        elif error_detail:
            message += f"\n\nDetails: {error_detail}"
        super().__init__(message)


class BrowserElementNotFoundError(BrowserError):
    """Element not found by selector."""

    def __init__(self, selector: str, operation: str = "find") -> None:
        self.selector = selector
        self.operation = operation
        message = (
            f"Element not found: {selector}\n\n"
            "Tips:\n"
            "  • Check selector syntax (CSS selector)\n"
            "  • Element may not be loaded yet - use wait_for()\n"
            "  • Use browser DevTools to verify selector\n"
        )
        super().__init__(message)


# =============================================================================
# Session Errors
# =============================================================================


class SessionError(CMDOPError):
    """Base for session-related errors."""


class SessionNotFoundError(SessionError):
    """Terminal session not found."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        super().__init__(f"Session not found: {session_id}")


class SessionClosedError(SessionError):
    """Attempted operation on a closed session."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        super().__init__(f"Session is closed: {session_id}")


class SessionInterruptedError(SessionError):
    """Session was interrupted (connection lost mid-stream)."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        super().__init__(f"Session interrupted: {session_id}")


# =============================================================================
# File Errors
# =============================================================================


class FileError(CMDOPError):
    """Base for file operation errors."""


class FileNotFoundError(FileError):
    """File or directory not found."""

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"File not found: {path}")


class FilePermissionError(FileError):
    """Permission denied for file operation."""

    def __init__(self, path: str, operation: str) -> None:
        self.path = path
        self.operation = operation
        super().__init__(f"Permission denied: {operation} on {path}")


class FileTooLargeError(FileError):
    """File exceeds size limit."""

    def __init__(self, path: str, size_bytes: int, max_bytes: int) -> None:
        self.path = path
        self.size_bytes = size_bytes
        self.max_bytes = max_bytes
        super().__init__(
            f"File too large: {path} ({size_bytes} bytes, max {max_bytes})"
        )


# =============================================================================
# Rate Limiting
# =============================================================================


class RateLimitError(CMDOPError):
    """Rate limit exceeded."""

    def __init__(self, retry_after_seconds: float | None = None) -> None:
        self.retry_after_seconds = retry_after_seconds
        msg = "Rate limit exceeded"
        if retry_after_seconds:
            msg += f", retry after {retry_after_seconds}s"
        super().__init__(msg)


# =============================================================================
# gRPC Error Mapping
# =============================================================================


def from_grpc_error(error: RpcError) -> CMDOPError:
    """Convert gRPC error to SDK exception."""
    from grpc import StatusCode

    code = error.code()
    details = error.details() or ""

    # Map gRPC status codes to SDK exceptions
    if code == StatusCode.UNAUTHENTICATED:
        return InvalidAPIKeyError(details or "Invalid API key")
    if code == StatusCode.PERMISSION_DENIED:
        return PermissionDeniedError(details or "Permission denied")
    if code == StatusCode.NOT_FOUND:
        return SessionNotFoundError(details or "Session not found")
    if code == StatusCode.UNAVAILABLE:
        return AgentOfflineError()
    if code == StatusCode.DEADLINE_EXCEEDED:
        return ConnectionTimeoutError(30.0)
    if code == StatusCode.RESOURCE_EXHAUSTED:
        return RateLimitError()
    if code == StatusCode.CANCELLED:
        return SessionInterruptedError(details or "unknown")

    # Generic error - keep it simple
    return CMDOPError(details or f"gRPC error: {code.name}")

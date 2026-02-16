"""
Local authentication mechanisms for CMDOP SDK.

Supports:
- SO_PEERCRED: Kernel-level UID verification on Linux/macOS
- File Token: Token-based auth for Windows and containers

SO_PEERCRED is preferred on Unix systems as it's un-spoofable
by unprivileged processes.
"""

from __future__ import annotations

import os
import platform
import socket
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from cmdop.exceptions import AuthenticationError, PermissionDeniedError

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class PeerCredentials:
    """
    Unix socket peer credentials from SO_PEERCRED.

    These are provided by the kernel and cannot be spoofed
    by unprivileged processes.
    """

    pid: int
    """Process ID of peer."""

    uid: int
    """User ID of peer."""

    gid: int
    """Group ID of peer."""


def get_peer_credentials(sock: socket.socket) -> PeerCredentials:
    """
    Get peer credentials from Unix socket via SO_PEERCRED.

    Uses kernel-level credential passing to identify the
    connecting process. This is un-spoofable by unprivileged
    processes.

    Args:
        sock: Connected Unix domain socket

    Returns:
        PeerCredentials with pid, uid, gid

    Raises:
        OSError: If SO_PEERCRED is not available
        AuthenticationError: If credentials cannot be obtained

    Note:
        Only works on Linux and macOS with Unix sockets.
    """
    system = platform.system()

    try:
        if system == "Linux":
            # Linux: SO_PEERCRED returns struct ucred {pid, uid, gid}
            SO_PEERCRED = 17
            creds = sock.getsockopt(
                socket.SOL_SOCKET,
                SO_PEERCRED,
                struct.calcsize("3i"),
            )
            pid, uid, gid = struct.unpack("3i", creds)
            return PeerCredentials(pid=pid, uid=uid, gid=gid)

        elif system == "Darwin":
            # macOS: LOCAL_PEERCRED returns struct xucred
            # Order is different: uid, gid, then groups
            LOCAL_PEERCRED = 0x001
            SOL_LOCAL = 0

            # struct xucred has: version(4), uid(4), ngroups(2), groups[16](4*16)
            # We only need version, uid, and first group (gid)
            XUCRED_SIZE = 4 + 4 + 2 + (4 * 16)

            try:
                creds = sock.getsockopt(SOL_LOCAL, LOCAL_PEERCRED, XUCRED_SIZE)
                # Parse xucred structure
                version, uid = struct.unpack_from("Ii", creds, 0)
                ngroups = struct.unpack_from("H", creds, 8)[0]
                if ngroups > 0:
                    gid = struct.unpack_from("I", creds, 10)[0]
                else:
                    gid = 0

                # PID is not available via LOCAL_PEERCRED on macOS
                # We use 0 as placeholder
                return PeerCredentials(pid=0, uid=uid, gid=gid)
            except (OSError, struct.error):
                # Fallback: try LOCAL_PEEREPID for PID
                # This is a separate call on macOS
                raise AuthenticationError(
                    "Failed to get peer credentials on macOS"
                )

        else:
            raise AuthenticationError(
                f"SO_PEERCRED not supported on {system}"
            )

    except OSError as e:
        raise AuthenticationError(f"Failed to get peer credentials: {e}") from e


def verify_peer_uid(sock: socket.socket, expected_uid: int | None = None) -> PeerCredentials:
    """
    Verify that peer UID matches expected UID.

    If expected_uid is None, uses current process UID.

    Args:
        sock: Connected Unix domain socket
        expected_uid: Expected peer UID (default: current user)

    Returns:
        PeerCredentials if UIDs match

    Raises:
        PermissionDeniedError: If UIDs don't match
        AuthenticationError: If credentials cannot be obtained
    """
    if expected_uid is None:
        expected_uid = os.getuid()

    creds = get_peer_credentials(sock)

    if creds.uid != expected_uid:
        raise PermissionDeniedError(
            "UID mismatch",
            agent_uid=creds.uid,
            caller_uid=expected_uid,
        )

    return creds


class FileTokenAuth:
    """
    File-based token authentication for Windows and containers.

    The agent writes a random token to a file readable only by
    the owner. The SDK reads this token and sends it in gRPC
    metadata for every request.

    This is less secure than SO_PEERCRED but works on all
    platforms.
    """

    def __init__(self, token_path: str | Path) -> None:
        """
        Initialize file token auth.

        Args:
            token_path: Path to token file

        Raises:
            AuthenticationError: If token file doesn't exist or is unreadable
        """
        self._token_path = Path(token_path).expanduser()
        self._token = self._read_token()

    def _read_token(self) -> str:
        """Read and validate token from file."""
        if not self._token_path.exists():
            raise AuthenticationError(
                f"Token file not found: {self._token_path}"
            )

        # Check file permissions (should be owner-only)
        if platform.system() != "Windows":
            stat = self._token_path.stat()
            mode = stat.st_mode & 0o777

            # Warn if file is readable by others
            if mode & 0o077:
                # File is readable by group or others - security risk
                import warnings

                warnings.warn(
                    f"Token file {self._token_path} has insecure permissions "
                    f"({oct(mode)}). Should be 0600.",
                    SecurityWarning,
                    stacklevel=3,
                )

        try:
            token = self._token_path.read_text().strip()
        except OSError as e:
            raise AuthenticationError(
                f"Cannot read token file: {e}"
            ) from e

        if len(token) < 32:
            raise AuthenticationError(
                f"Token too short ({len(token)} chars, minimum 32)"
            )

        return token

    @property
    def token(self) -> str:
        """Get the authentication token."""
        return self._token

    @property
    def token_path(self) -> Path:
        """Get path to token file."""
        return self._token_path

    def metadata(self) -> list[tuple[str, str]]:
        """
        Generate gRPC metadata for authentication.

        Returns:
            List of metadata tuples for gRPC calls
        """
        return [("authorization", f"Bearer {self._token}")]

    def __repr__(self) -> str:
        return f"<FileTokenAuth path={self._token_path}>"


class SecurityWarning(UserWarning):
    """Warning for security-related issues."""

    pass


def get_local_auth_metadata(
    token_path: str | Path | None = None,
) -> list[tuple[str, str]]:
    """
    Get authentication metadata for local connection.

    On Unix with Unix sockets, SO_PEERCRED is used automatically
    by the server, so no explicit auth metadata is needed.

    On Windows or when using TCP, file token auth is required.

    Args:
        token_path: Path to token file (required for Windows/TCP)

    Returns:
        List of metadata tuples (may be empty for Unix socket)
    """
    system = platform.system()

    if system == "Windows" or token_path:
        if token_path is None:
            # Default token path for Windows
            local_app_data = os.environ.get("LOCALAPPDATA", "")
            if local_app_data:
                token_path = Path(local_app_data) / "cmdop" / "token"
            else:
                token_path = Path.home() / ".cmdop" / "token"

        auth = FileTokenAuth(token_path)
        return auth.metadata()

    # Unix socket with SO_PEERCRED - no explicit auth needed
    return []


def supports_peercred() -> bool:
    """
    Check if current platform supports SO_PEERCRED.

    Returns:
        True on Linux/macOS, False on Windows and others
    """
    return platform.system() in ("Linux", "Darwin")

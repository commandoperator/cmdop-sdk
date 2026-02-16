"""
Agent discovery for local connections.

Finds running cmdop_go agent via discovery file (~/.cmdop/agent.info).
Handles stale files, platform differences, and liveness checks.
"""

from __future__ import annotations

import json
import os
import platform
import socket
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from cmdop.exceptions import AgentNotRunningError, StalePortFileError

if TYPE_CHECKING:
    pass


class TransportType(str, Enum):
    """IPC transport mechanism."""

    UNIX_SOCKET = "unix"
    NAMED_PIPE = "pipe"
    TCP = "tcp"


@dataclass(frozen=True)
class AgentInfo:
    """
    Information about running agent from discovery file.

    The agent writes this file on startup at ~/.cmdop/agent.info
    """

    version: str
    """Agent version string (e.g., '1.0.30')."""

    pid: int
    """Agent process ID."""

    transport: TransportType
    """IPC transport type."""

    address: str
    """Connection address (socket path, pipe name, or host:port)."""

    token_path: str | None
    """Path to auth token file (for Windows/containers)."""

    started_at: datetime
    """When agent was started."""

    @classmethod
    def from_dict(cls, data: dict) -> AgentInfo:
        """Create AgentInfo from dictionary (parsed JSON)."""
        return cls(
            version=data["version"],
            pid=data["pid"],
            transport=TransportType(data["transport"]),
            address=data["address"],
            token_path=data.get("token_path"),
            started_at=cls._parse_timestamp(data["started_at"]),
        )

    @staticmethod
    def _parse_timestamp(ts: str) -> datetime:
        """Parse ISO 8601 timestamp with flexible decimal places."""
        # Replace Z with +00:00 for UTC
        ts = ts.replace("Z", "+00:00")
        # Try direct parsing first
        try:
            return datetime.fromisoformat(ts)
        except ValueError:
            pass
        # Handle non-standard decimal places (e.g., .9804 -> .980400)
        import re
        match = re.match(r"(.+\.\d+)(\+.+)", ts)
        if match:
            base, tz = match.groups()
            # Pad or truncate to 6 decimal places
            dot_pos = base.rfind(".")
            decimals = base[dot_pos + 1 :]
            decimals = (decimals + "000000")[:6]
            ts = base[: dot_pos + 1] + decimals + tz
            return datetime.fromisoformat(ts)
        # Fallback: return now
        return datetime.now()


@dataclass
class DiscoveryResult:
    """Result of agent discovery process."""

    found: bool
    """Whether agent was found."""

    agent_info: AgentInfo | None = None
    """Agent info if found."""

    discovery_path: Path | None = None
    """Path where agent was discovered."""

    error: str | None = None
    """Error message if discovery failed."""


def get_default_discovery_paths() -> list[Path]:
    """
    Get platform-specific default discovery paths.

    Returns paths in priority order:
    1. Environment variable override
    2. User home directory
    3. System-wide location
    """
    paths: list[Path] = []

    # Environment variable override (highest priority)
    env_path = os.environ.get("CMDOP_AGENT_INFO")
    if env_path:
        paths.append(Path(env_path))

    # Platform-specific paths
    system = platform.system()

    if system == "Windows":
        # Windows: use LOCALAPPDATA
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        if local_app_data:
            paths.append(Path(local_app_data) / "cmdop" / "agent.info")
        paths.append(Path.home() / ".cmdop" / "agent.info")
    else:
        # Linux/macOS: use XDG or home
        xdg_runtime = os.environ.get("XDG_RUNTIME_DIR")
        if xdg_runtime:
            paths.append(Path(xdg_runtime) / "cmdop" / "agent.info")

        paths.append(Path.home() / ".cmdop" / "agent.info")
        paths.append(Path("/var/run/cmdop/agent.info"))

    return paths


def read_discovery_file(path: Path) -> AgentInfo | None:
    """
    Read and parse agent discovery file.

    Args:
        path: Path to discovery file

    Returns:
        AgentInfo if file exists and is valid, None otherwise
    """
    if not path.exists():
        return None

    try:
        with open(path) as f:
            data = json.load(f)
        return AgentInfo.from_dict(data)
    except (json.JSONDecodeError, KeyError, ValueError):
        return None


def check_agent_alive(info: AgentInfo, timeout: float = 2.0) -> bool:
    """
    Check if agent is actually responding at discovered address.

    Performs a low-level socket connection test to verify
    the agent process is still running and accepting connections.

    Args:
        info: Agent info from discovery file
        timeout: Connection timeout in seconds

    Returns:
        True if agent responds, False otherwise
    """
    try:
        if info.transport == TransportType.UNIX_SOCKET:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect(info.address)
            sock.close()
            return True

        elif info.transport == TransportType.TCP:
            host, port_str = info.address.rsplit(":", 1)
            port = int(port_str)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.close()
            return True

        elif info.transport == TransportType.NAMED_PIPE:
            # Windows named pipes - check if pipe exists
            # Pipe names are like: \\.\pipe\cmdop-{session_id}
            if platform.system() == "Windows":
                import ctypes

                INVALID_HANDLE_VALUE = -1
                GENERIC_READ = 0x80000000
                OPEN_EXISTING = 3

                handle = ctypes.windll.kernel32.CreateFileW(
                    info.address,
                    GENERIC_READ,
                    0,
                    None,
                    OPEN_EXISTING,
                    0,
                    None,
                )
                if handle != INVALID_HANDLE_VALUE:
                    ctypes.windll.kernel32.CloseHandle(handle)
                    return True
            return False

    except (OSError, socket.error, ValueError):
        return False

    return False


def check_process_running(pid: int) -> bool:
    """
    Check if process with given PID is running.

    Args:
        pid: Process ID to check

    Returns:
        True if process exists, False otherwise
    """
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def discover_agent(
    custom_paths: list[Path | str] | None = None,
    verify_alive: bool = True,
    use_defaults: bool = True,
) -> DiscoveryResult:
    """
    Discover running cmdop agent.

    Searches for agent discovery file in standard locations,
    optionally verifies agent is responding.

    Args:
        custom_paths: Additional paths to check (prepended to defaults)
        verify_alive: Whether to verify agent is actually responding
        use_defaults: Whether to include default discovery paths

    Returns:
        DiscoveryResult with agent info or error details

    Example:
        >>> result = discover_agent()
        >>> if result.found:
        ...     print(f"Agent at {result.agent_info.address}")
        ... else:
        ...     print(f"Agent not found: {result.error}")
    """
    # Build search paths
    paths: list[Path] = []

    if custom_paths:
        for p in custom_paths:
            paths.append(Path(p) if isinstance(p, str) else p)

    if use_defaults:
        paths.extend(get_default_discovery_paths())

    # Search for discovery file
    for path in paths:
        path = path.expanduser()

        agent_info = read_discovery_file(path)
        if agent_info is None:
            continue

        # Found a discovery file
        if verify_alive:
            # First check if PID is still running
            if not check_process_running(agent_info.pid):
                # Process dead, file is stale
                return DiscoveryResult(
                    found=False,
                    discovery_path=path,
                    error=f"Stale discovery file (PID {agent_info.pid} not running)",
                )

            # Then verify socket/pipe is responding
            if not check_agent_alive(agent_info):
                return DiscoveryResult(
                    found=False,
                    agent_info=agent_info,
                    discovery_path=path,
                    error="Agent process exists but not responding",
                )

        return DiscoveryResult(
            found=True,
            agent_info=agent_info,
            discovery_path=path,
        )

    # No discovery file found
    return DiscoveryResult(
        found=False,
        error="No agent discovery file found",
    )


def require_agent(
    custom_paths: list[Path | str] | None = None,
    use_defaults: bool = True,
) -> tuple[AgentInfo, Path]:
    """
    Discover agent or raise exception.

    Convenience function that raises appropriate exceptions
    instead of returning DiscoveryResult.

    Args:
        custom_paths: Additional paths to check
        use_defaults: Whether to include default discovery paths

    Returns:
        Tuple of (AgentInfo, discovery_path)

    Raises:
        AgentNotRunningError: No agent found
        StalePortFileError: Discovery file exists but agent dead
    """
    result = discover_agent(custom_paths=custom_paths, verify_alive=True, use_defaults=use_defaults)

    if result.found and result.agent_info:
        return result.agent_info, result.discovery_path  # type: ignore

    if result.discovery_path and result.agent_info:
        # File exists but agent not responding
        raise StalePortFileError(str(result.discovery_path))

    if result.discovery_path:
        # File exists but stale (PID dead)
        raise StalePortFileError(str(result.discovery_path))

    # No file found at all
    raise AgentNotRunningError(
        "No cmdop agent found. Start with: cmdop agent start"
    )


def cleanup_stale_discovery(path: Path | str) -> bool:
    """
    Remove stale discovery file.

    Args:
        path: Path to discovery file

    Returns:
        True if file was removed, False if it didn't exist
    """
    path = Path(path)
    try:
        path.unlink()
        return True
    except FileNotFoundError:
        return False

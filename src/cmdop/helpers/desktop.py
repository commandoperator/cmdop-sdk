"""
CMDOP Desktop management helpers.

Cross-platform utilities for starting, stopping, and ensuring
CMDOP Desktop is running.
"""

from __future__ import annotations

import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, TypeVar

from cmdop.exceptions import AgentNotRunningError, StalePortFileError
from cmdop.transport.discovery import discover_agent, cleanup_stale_discovery

T = TypeVar("T")


# =============================================================================
# Platform-specific paths
# =============================================================================

def get_cmdop_app_path() -> Path | None:
    """Get platform-specific path to CMDOP Desktop app."""
    system = platform.system()

    if system == "Darwin":
        path = Path("/Applications/CMDOP.app")
        if path.exists():
            return path
        # Check user Applications
        user_path = Path.home() / "Applications" / "CMDOP.app"
        if user_path.exists():
            return user_path

    elif system == "Windows":
        # Common Windows install locations
        paths = [
            Path(r"C:\Program Files\CMDOP\CMDOP.exe"),
            Path(r"C:\Program Files (x86)\CMDOP\CMDOP.exe"),
            Path.home() / "AppData" / "Local" / "Programs" / "CMDOP" / "CMDOP.exe",
        ]
        for path in paths:
            if path.exists():
                return path

    elif system == "Linux":
        # Linux: check if cmdop binary is available
        try:
            result = subprocess.run(
                ["which", "cmdop"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except Exception:
            pass

    return None


# =============================================================================
# Core functions
# =============================================================================

def start_desktop(timeout: float = 15.0, quiet: bool = False) -> bool:
    """
    Start CMDOP Desktop application.

    Cross-platform function that starts CMDOP Desktop and waits
    for the agent to become available.

    Args:
        timeout: Maximum time to wait for agent to start (seconds)
        quiet: If True, suppress output messages

    Returns:
        True if agent started successfully, False otherwise
    """
    system = platform.system()

    def log(msg: str) -> None:
        if not quiet:
            print(msg)

    log("🔄 Starting CMDOP Desktop...")

    try:
        if system == "Darwin":
            app_path = get_cmdop_app_path()
            if app_path:
                subprocess.Popen(
                    ["open", str(app_path)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                log("❌ CMDOP.app not found in /Applications")
                return False

        elif system == "Windows":
            app_path = get_cmdop_app_path()
            # DETACHED_PROCESS = 0x00000008
            detached_process = 0x00000008
            if app_path:
                subprocess.Popen(
                    [str(app_path)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=detached_process,
                )
            else:
                # Try start command as fallback
                subprocess.Popen(
                    ["cmd", "/c", "start", "", "CMDOP"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    shell=True,
                )

        elif system == "Linux":
            # Linux: start cmdop serve in background
            subprocess.Popen(
                ["cmdop", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

        else:
            log(f"❌ Unsupported platform: {system}")
            return False

    except Exception as e:
        log(f"❌ Failed to start CMDOP: {e}")
        return False

    log("⏳ Waiting for CMDOP to initialize...")

    # Poll until agent is available
    start_time = time.time()
    last_dot_time = start_time

    while time.time() - start_time < timeout:
        result = discover_agent(verify_alive=True)
        if result.found:
            log("✅ CMDOP Desktop started successfully")
            return True

        # Print dots to show progress
        if not quiet and time.time() - last_dot_time >= 1.0:
            print(".", end="", flush=True)
            last_dot_time = time.time()

        time.sleep(0.3)

    if not quiet:
        print()  # Newline after dots
    log(f"❌ CMDOP did not start within {timeout}s")
    return False


def ensure_desktop_running(
    timeout: float = 15.0,
    auto_start: bool = True,
    exit_on_failure: bool = True,
) -> bool:
    """
    Ensure CMDOP Desktop is running, starting it if needed.

    This is the main function to use before browser operations.
    Handles stale discovery files automatically.

    Args:
        timeout: Time to wait for agent if starting
        auto_start: If True, attempt to start CMDOP if not running
        exit_on_failure: If True, call sys.exit(1) on failure

    Returns:
        True if CMDOP is running

    Raises:
        SystemExit: If exit_on_failure=True and CMDOP cannot be started

    Example:
        >>> from cmdop.helpers import ensure_desktop_running
        >>> ensure_desktop_running()  # Starts CMDOP if needed
        >>> # Now safe to use browser
        >>> client = CMDOPClient.local()
    """
    result = discover_agent(verify_alive=True)

    if result.found:
        return True

    # Handle stale discovery file
    if result.discovery_path:
        print(f"⚠️  Cleaning stale discovery file: {result.discovery_path}")
        cleanup_stale_discovery(result.discovery_path)

    print("⚠️  CMDOP Desktop is not running")

    if not auto_start:
        if exit_on_failure:
            print("\nStart CMDOP Desktop manually:")
            _print_start_instructions()
            sys.exit(1)
        return False

    # Try to start
    if start_desktop(timeout=timeout):
        return True

    if exit_on_failure:
        print("\n💡 Try starting CMDOP Desktop manually:")
        _print_start_instructions()
        sys.exit(1)

    return False


def handle_cmdop_error(
    error: Exception,
    auto_restart: bool = True,
    exit_on_failure: bool = True,
) -> bool:
    """
    Handle CMDOP connection errors with auto-restart.

    Use this in except blocks to handle AgentNotRunningError
    and StalePortFileError gracefully.

    Args:
        error: The exception that was raised
        auto_restart: If True, attempt to restart CMDOP
        exit_on_failure: If True, call sys.exit(1) if restart fails

    Returns:
        True if CMDOP was restarted successfully

    Example:
        >>> try:
        ...     client = CMDOPClient.local()
        ...     session = client.browser.create_session()
        ... except (StalePortFileError, AgentNotRunningError) as e:
        ...     if handle_cmdop_error(e):
        ...         # Retry the operation
        ...         client = CMDOPClient.local()
    """
    if isinstance(error, StalePortFileError):
        print(f"\n⚠️  CMDOP Desktop crashed (stale file: {error.discovery_path})")
        error.cleanup()
    elif isinstance(error, AgentNotRunningError):
        print("\n⚠️  CMDOP Desktop is not running")
    else:
        # Unknown error, re-raise
        raise error

    if not auto_restart:
        if exit_on_failure:
            print("\nStart CMDOP Desktop:")
            _print_start_instructions()
            sys.exit(1)
        return False

    if start_desktop():
        return True

    if exit_on_failure:
        print("\n💡 Try starting CMDOP Desktop manually:")
        _print_start_instructions()
        sys.exit(1)

    return False


def with_auto_restart(
    func: Callable[..., T],
    *args,
    max_retries: int = 1,
    **kwargs,
) -> T:
    """
    Execute function with automatic CMDOP restart on failure.

    Wraps a function that uses CMDOP and automatically handles
    connection errors by restarting CMDOP Desktop.

    Args:
        func: Function to execute
        *args: Arguments to pass to function
        max_retries: Maximum restart attempts
        **kwargs: Keyword arguments to pass to function

    Returns:
        Result of the function

    Example:
        >>> def parse_page():
        ...     client = CMDOPClient.local()
        ...     with client.browser.create_session() as session:
        ...         session.navigate("https://example.com")
        ...         return session.get_text("body")
        ...
        >>> result = with_auto_restart(parse_page)
    """
    last_error: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except (StalePortFileError, AgentNotRunningError) as e:
            last_error = e

            if attempt < max_retries:
                print(f"\n🔄 CMDOP error (attempt {attempt + 1}/{max_retries + 1})")
                if handle_cmdop_error(e, auto_restart=True, exit_on_failure=False):
                    continue

            # Last attempt failed
            handle_cmdop_error(e, auto_restart=False, exit_on_failure=True)

    # Should not reach here, but just in case
    if last_error:
        raise last_error
    raise RuntimeError("Unexpected error in with_auto_restart")


# =============================================================================
# Private helpers
# =============================================================================

def _print_start_instructions() -> None:
    """Print platform-specific start instructions."""
    system = platform.system()

    if system == "Darwin":
        print("  open /Applications/CMDOP.app")
    elif system == "Windows":
        print("  Start CMDOP from Start Menu")
        print("  or run: CMDOP.exe")
    elif system == "Linux":
        print("  cmdop serve")
    else:
        print("  Start CMDOP Desktop application")

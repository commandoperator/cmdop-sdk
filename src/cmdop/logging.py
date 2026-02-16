"""
Universal Python logger with Rich console output and file persistence.

Auto-detects project root by looking for Python project markers:
- pyproject.toml
- setup.py
- requirements.txt
- .git

Usage:
    from cmdop.logging import get_logger

    log = get_logger(__name__)
    log.info("Hello world")
    log.error("Something failed", exc_info=True)

    # Or with custom settings
    log = get_logger(__name__, level="DEBUG", log_to_file=True)
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Literal

# Try to import Rich, fallback to standard logging if not available
try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.traceback import install as install_rich_traceback

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

__all__ = [
    "get_logger",
    "setup_logging",
    "find_project_root",
    "get_log_dir",
]

# Project markers to search for (in priority order)
PROJECT_MARKERS = [
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
    "Pipfile",
    ".git",
]

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Cache for project root
_project_root_cache: Path | None = None
_logging_configured: bool = False


def find_project_root(start_path: Path | None = None) -> Path | None:
    """
    Find Python project root by searching for project markers.

    Searches upward from start_path (default: cwd) looking for:
    - pyproject.toml
    - setup.py
    - requirements.txt
    - .git

    Returns:
        Path to project root, or None if not found
    """
    global _project_root_cache

    if _project_root_cache is not None:
        return _project_root_cache

    if start_path is None:
        start_path = Path.cwd()

    path = start_path.resolve()

    for current in [path] + list(path.parents):
        for marker in PROJECT_MARKERS:
            if (current / marker).exists():
                _project_root_cache = current
                return current

    return None


def get_log_dir(app_name: str = "app") -> Path:
    """
    Get log directory path.

    Priority:
    1. Project root / logs (if project root found)
    2. ~/.local/logs/{app_name} (Linux/macOS)
    3. Current working directory / logs

    Creates directory if it doesn't exist.

    Args:
        app_name: Application name for fallback directory

    Returns:
        Path to log directory
    """
    # Try project root first
    project_root = find_project_root()
    if project_root:
        log_dir = project_root / "logs"
    else:
        # Fallback to home directory
        home = Path.home()
        if sys.platform == "darwin":
            log_dir = home / "Library" / "Logs" / app_name
        elif sys.platform == "win32":
            log_dir = home / "AppData" / "Local" / app_name / "logs"
        else:  # Linux and others
            log_dir = home / ".local" / "logs" / app_name

    # Create directory if needed
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logging(
    level: LogLevel = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
    app_name: str = "app",
    rich_tracebacks: bool = True,
) -> None:
    """
    Configure root logger with Rich console and file handlers.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to write logs to file
        log_to_console: Whether to output to console
        app_name: Application name for log file naming
        rich_tracebacks: Install Rich traceback handler for exceptions
    """
    global _logging_configured

    if _logging_configured:
        return

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler with Rich (if available)
    if log_to_console:
        if RICH_AVAILABLE:
            console = Console(stderr=True)
            console_handler = RichHandler(
                console=console,
                show_time=True,
                show_path=True,
                rich_tracebacks=True,
                tracebacks_show_locals=True,
                markup=True,
            )
            console_handler.setFormatter(logging.Formatter("%(message)s"))
        else:
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s | %(levelname)-8s | %(name)s - %(message)s",
                    datefmt="%H:%M:%S",
                )
            )
        root_logger.addHandler(console_handler)

    # File handler
    if log_to_file:
        log_dir = get_log_dir(app_name)
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = log_dir / f"{app_name}_{date_str}.log"

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        root_logger.addHandler(file_handler)

    # Install Rich tracebacks globally
    if rich_tracebacks and RICH_AVAILABLE:
        install_rich_traceback(show_locals=True, suppress=[])

    _logging_configured = True


def get_logger(
    name: str | None = None,
    level: LogLevel | None = None,
    log_to_file: bool = True,
    app_name: str = "app",
) -> logging.Logger:
    """
    Get a configured logger instance.

    On first call, sets up the logging system with Rich console output
    and file persistence.

    Args:
        name: Logger name (typically __name__)
        level: Override log level (default: INFO)
        log_to_file: Whether to write to log file
        app_name: Application name for log file

    Returns:
        Configured logger instance

    Example:
        log = get_logger(__name__)
        log.info("Starting process")
        log.debug("Debug details: %s", data)
        log.error("Failed!", exc_info=True)
    """
    # Setup logging system on first call
    setup_logging(
        level=level or "INFO",
        log_to_file=log_to_file,
        app_name=app_name,
    )

    logger = logging.getLogger(name)

    # Override level if specified
    if level:
        logger.setLevel(getattr(logging, level))

    return logger


# Convenience aliases
debug = lambda msg, *args, **kw: get_logger().debug(msg, *args, **kw)
info = lambda msg, *args, **kw: get_logger().info(msg, *args, **kw)
warning = lambda msg, *args, **kw: get_logger().warning(msg, *args, **kw)
error = lambda msg, *args, **kw: get_logger().error(msg, *args, **kw)
critical = lambda msg, *args, **kw: get_logger().critical(msg, *args, **kw)

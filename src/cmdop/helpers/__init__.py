"""CMDOP SDK helpers."""

from cmdop.helpers.network_analyzer import (
    NetworkAnalyzer,
    NetworkSnapshot,
    RequestSnapshot,
)
from cmdop.helpers.desktop import (
    ensure_desktop_running,
    start_desktop,
    handle_cmdop_error,
    with_auto_restart,
    get_cmdop_app_path,
)
from cmdop.helpers.syntax import (
    print_code,
    print_file,
    print_diff,
    print_json,
    print_yaml,
    print_shell_output,
    detect_language,
    cat,
    highlight,
)

__all__ = [
    # Network
    "NetworkAnalyzer",
    "NetworkSnapshot",
    "RequestSnapshot",
    # Desktop management
    "ensure_desktop_running",
    "start_desktop",
    "handle_cmdop_error",
    "with_auto_restart",
    "get_cmdop_app_path",
    # Syntax highlighting
    "print_code",
    "print_file",
    "print_diff",
    "print_json",
    "print_yaml",
    "print_shell_output",
    "detect_language",
    "cat",
    "highlight",
]

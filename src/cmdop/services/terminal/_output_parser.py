"""
Terminal output parser helpers.

Parses raw PTY output to extract clean command output.
Handles various terminal escape sequences, prompts, and markers.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ParsedOutput:
    """Parsed terminal output result."""

    output: bytes
    """Clean command output (without markers, prompts, escape sequences)."""

    exit_code: int
    """Command exit code (-1 if unknown)."""

    raw: bytes
    """Original raw output for debugging."""


# =============================================================================
# ANSI/Terminal Escape Sequence Patterns
# =============================================================================

# OSC (Operating System Command) - terminal title, etc.
# Format: ESC ] <code> ; <text> BEL  or  ESC ] <code> ; <text> ESC \
OSC_PATTERN = re.compile(rb"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)")

# CSI (Control Sequence Introducer) - cursor, colors, etc.
# Format: ESC [ <params> <letter>
CSI_PATTERN = re.compile(rb"\x1b\[[0-9;?]*[A-Za-z]")

# Simple escape sequences (cursor save/restore, etc.)
SIMPLE_ESC_PATTERN = re.compile(rb"\x1b[78=>]")

# Carriage return without newline (overwrites line)
CR_PATTERN = re.compile(rb"\r(?!\n)")


def strip_ansi_escapes(data: bytes) -> bytes:
    """Remove ANSI escape sequences from terminal output."""
    result = data
    result = OSC_PATTERN.sub(b"", result)
    result = CSI_PATTERN.sub(b"", result)
    result = SIMPLE_ESC_PATTERN.sub(b"", result)
    result = CR_PATTERN.sub(b"", result)
    return result


# =============================================================================
# Prompt Detection
# =============================================================================

# Common prompt patterns (user@host:path$ or similar)
PROMPT_PATTERNS = [
    # user@hostname:~/path$ or user@hostname:~/path#
    re.compile(rb"^[a-zA-Z0-9_-]+@[a-zA-Z0-9_.-]+:[^\n]*[#\$%>]\s*$"),
    # [user@hostname path]$ (bash with brackets)
    re.compile(rb"^\[[^\]]+\][#\$%>]\s*$"),
    # hostname:path# (root style)
    re.compile(rb"^[a-zA-Z0-9_.-]+:[^\n]*#\s*$"),
    # Simple prompts: $ or # or % or >
    re.compile(rb"^[#\$%>]\s*$"),
    # PS1 with exit code: [0]user@host$
    re.compile(rb"^\[\d+\][^\n]*[#\$%>]\s*$"),
]


def is_prompt_line(line: bytes) -> bool:
    """Check if line looks like a shell prompt."""
    stripped = line.strip()
    if not stripped:
        return False

    # Check against known prompt patterns
    for pattern in PROMPT_PATTERNS:
        if pattern.match(stripped):
            return True

    # Heuristic: ends with common prompt chars after @ or :
    # This catches most prompts without being too aggressive
    if re.search(rb"[@:][^\n]{0,50}[#\$%>]\s*$", stripped):
        # But not if it looks like output (contains common output patterns)
        if b"=" in stripped or b"  " in stripped:
            return False
        return True

    return False


def is_command_echo_line(line: bytes, command: bytes, markers: list[bytes]) -> bool:
    """Check if line is the shell echoing the command back."""
    # Contains the command we sent
    if command in line:
        return True
    # Contains our markers (from echo command)
    for marker in markers:
        if marker in line:
            return True
    return False


# =============================================================================
# Main Parser
# =============================================================================

def parse_terminal_output(
    raw_output: bytes,
    command: str,
    start_marker: str,
    end_marker: str,
) -> ParsedOutput:
    """
    Parse raw PTY output to extract clean command output.

    Args:
        raw_output: Raw bytes from terminal buffer.
        command: The command that was executed.
        start_marker: Marker printed before command output.
        end_marker: Marker printed after command output (followed by exit code).

    Returns:
        ParsedOutput with clean output and exit code.
    """
    start_bytes = start_marker.encode()
    end_bytes = end_marker.encode()
    command_bytes = command.encode()

    # Default result
    result = ParsedOutput(output=b"", exit_code=-1, raw=raw_output)

    # Find markers
    if start_bytes not in raw_output or end_bytes not in raw_output:
        return result

    # Find the LAST occurrence of markers (in case of multiple executions)
    start_idx = raw_output.rindex(start_bytes)
    end_idx = raw_output.rindex(end_bytes)

    if end_idx <= start_idx:
        return result

    # Extract exit code (digits after end marker)
    try:
        after_end = raw_output[end_idx + len(end_bytes):end_idx + len(end_bytes) + 10]
        exit_str = after_end.split(b"\n")[0].strip()
        if exit_str.isdigit():
            result.exit_code = int(exit_str)
        else:
            result.exit_code = 0
    except (ValueError, IndexError):
        result.exit_code = 0

    # Extract content between markers
    # Skip to newline after start marker
    content_start = raw_output.find(b"\n", start_idx)
    if content_start == -1:
        content_start = start_idx + len(start_bytes)
    else:
        content_start += 1  # Skip the newline

    content = raw_output[content_start:end_idx]

    # Strip ANSI escape sequences
    content = strip_ansi_escapes(content)

    # Process line by line
    lines = content.split(b"\n")
    output_lines: list[bytes] = []
    markers = [start_bytes, end_bytes, b"__cmdop_ec="]

    for line in lines:
        # Skip command echo lines
        if is_command_echo_line(line, command_bytes, markers):
            continue
        # Skip prompt lines
        if is_prompt_line(line):
            continue
        # Skip empty lines at start/end (will strip later anyway)
        output_lines.append(line)

    result.output = b"\n".join(output_lines).strip()
    return result

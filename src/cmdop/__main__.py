"""
CMDOP SDK CLI entry point.

Usage:
    python -m cmdop ssh my-server
    python -m cmdop fleet status
    python -m cmdop tui
"""

from cmdop.cli import main

if __name__ == "__main__":
    main()

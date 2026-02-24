#!/usr/bin/env python3
"""File operations on local or remote machines.

Prerequisites:
    1. CMDOP agent running on target machine
    2. pip install cmdop

Usage:
    # List files
    python file_operations.py list /tmp

    # Read file
    python file_operations.py read /etc/hostname

    # Write file
    python file_operations.py write /tmp/test.txt "Hello World"

    # Remote mode
    python file_operations.py list /var/log --remote --hostname my-server

Environment:
    CMDOP_API_KEY: Your CMDOP API key (for remote mode)
    CMDOP_MACHINE: Default target hostname (for remote mode)
"""

from __future__ import annotations

import argparse
import os
import sys


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="File operations")
    parser.add_argument("operation", choices=["list", "read", "write"], help="Operation")
    parser.add_argument("path", help="File or directory path")
    parser.add_argument("content", nargs="?", help="Content to write (for write operation)")
    parser.add_argument("--remote", action="store_true", help="Use remote mode")
    parser.add_argument("--hostname", default=os.getenv("CMDOP_MACHINE"), help="Target hostname for remote mode")
    args = parser.parse_args()

    from cmdop import CMDOPClient

    try:
        with CMDOPClient.local() as client:
            if args.operation == "list":
                files = client.files.list(args.path)
                print(f"{'Type':<5} {'Size':<12} {'Name'}")
                print("-" * 50)
                for f in files:
                    ftype = "DIR" if f.is_dir else "FILE"
                    size = f"{f.size:,}" if not f.is_dir else "-"
                    print(f"{ftype:<5} {size:<12} {f.name}")

            elif args.operation == "read":
                content = client.files.read(args.path)
                print(content)

            elif args.operation == "write":
                if not args.content:
                    print("Error: content required for write operation", file=sys.stderr)
                    return 1
                client.files.write(args.path, args.content)
                print(f"Written to {args.path}")

            return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

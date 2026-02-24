#!/usr/bin/env python3
"""SSH-like terminal connection.

Prerequisites:
    1. CMDOP agent running on target machine
    2. pip install cmdop

Usage:
    # Connect to default machine (CMDOP_MACHINE env)
    python terminal_ssh.py

    # Connect to specific hostname
    python terminal_ssh.py my-server

    # Execute single command
    python terminal_ssh.py --exec "ls -la"
    python terminal_ssh.py my-server --exec "uname -a"

    # With custom timeout
    python terminal_ssh.py --exec "apt update" --timeout 120

Environment:
    CMDOP_API_KEY: Your CMDOP API key
    CMDOP_MACHINE: Default target hostname
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys


async def main() -> int:
    """Main entry point."""
    default_hostname = os.getenv("CMDOP_MACHINE")
    default_api_key = os.getenv("CMDOP_API_KEY", "")

    parser = argparse.ArgumentParser(
        description="SSH-like terminal connection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Default target: {default_hostname or '(not configured)'}

Examples:
  python terminal_ssh.py                    # SSH to default machine
  python terminal_ssh.py my-server          # SSH to specific machine
  python terminal_ssh.py -e "ls -la"        # Execute command
  python terminal_ssh.py -e "sleep 5" -t 10 # With timeout
""",
    )
    parser.add_argument(
        "hostname",
        nargs="?",
        default=default_hostname,
        help=f"Target hostname (default: {default_hostname})",
    )
    parser.add_argument(
        "--exec", "-e",
        dest="command",
        help="Execute single command instead of interactive session",
    )
    parser.add_argument(
        "--timeout", "-t",
        type=float,
        default=60.0,
        help="Command timeout in seconds (default: 60)",
    )
    parser.add_argument(
        "--api-key",
        default=default_api_key,
        help="CMDOP API key (default: CMDOP_API_KEY env)",
    )
    args = parser.parse_args()

    if not args.api_key:
        print("Error: No API key. Set CMDOP_API_KEY env or use --api-key", file=sys.stderr)
        return 1

    if not args.hostname:
        print("Error: No hostname. Set CMDOP_MACHINE env or pass as argument", file=sys.stderr)
        return 1

    from cmdop import AsyncCMDOPClient

    async with AsyncCMDOPClient.remote(api_key=args.api_key) as client:
        session = await client.terminal.get_active_session(hostname=args.hostname)

        if not session:
            print(f"No active session found for '{args.hostname}'", file=sys.stderr)

            response = await client.terminal.list_sessions(status="connected", limit=10)
            if response.sessions:
                print("\nAvailable machines:", file=sys.stderr)
                for s in response.sessions:
                    status = f"({s.heartbeat_age_seconds}s ago)" if s.heartbeat_age_seconds else ""
                    print(f"  - {s.machine_hostname} {status}", file=sys.stderr)
            return 1

        print(f"Connected to: {session.machine_hostname}")

        if args.command:
            print(f"$ {args.command}\n")
            output, code = await client.terminal.execute(
                args.command,
                session_id=session.session_id,
                timeout=args.timeout,
            )
            print(output.decode())
            if code != 0:
                print(f"Exit code: {code}")
            return code if code >= 0 else 1
        else:
            from cmdop.services.terminal.tui import ssh_connect

            return await ssh_connect(
                session.machine_hostname,
                args.api_key,
                session_id=session.session_id,
            )


if __name__ == "__main__":
    try:
        code = asyncio.run(main())
        sys.exit(code)
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(130)

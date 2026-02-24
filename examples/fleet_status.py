#!/usr/bin/env python3
"""Check status of all connected machines.

Prerequisites:
    1. CMDOP agent running on target machines
    2. pip install cmdop

Usage:
    python fleet_status.py

Environment:
    CMDOP_API_KEY: Your CMDOP API key
"""

from __future__ import annotations

import asyncio
import os
import sys


async def main() -> int:
    """Main entry point."""
    api_key = os.getenv("CMDOP_API_KEY", "")
    if not api_key:
        print("Error: Set CMDOP_API_KEY environment variable", file=sys.stderr)
        return 1

    from cmdop import AsyncCMDOPClient

    async with AsyncCMDOPClient.remote(api_key=api_key) as client:
        response = await client.terminal.list_sessions()

        print(f"Workspace: {response.workspace_name}")
        print(f"Total machines: {response.total}")
        print()

        if not response.sessions:
            print("No connected machines")
            return 0

        print(f"{'Status':<8} {'Hostname':<30} {'OS':<10} {'Shell':<15} {'Heartbeat':<10}")
        print("-" * 80)

        for session in response.sessions:
            status = "ON" if session.status == "connected" else "OFF"
            hostname = session.machine_hostname[:28]
            os_name = session.os[:8] if session.os else "unknown"
            shell = session.shell.split("/")[-1][:13] if session.shell else "n/a"
            heartbeat = f"{session.heartbeat_age_seconds}s" if session.heartbeat_age_seconds else "n/a"

            print(f"{status:<8} {hostname:<30} {os_name:<10} {shell:<15} {heartbeat:<10}")

    return 0


if __name__ == "__main__":
    try:
        code = asyncio.run(main())
        sys.exit(code)
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(130)

#!/usr/bin/env python3
"""AI agent with Pydantic structured output.

Prerequisites:
    1. CMDOP agent running on target machine
    2. pip install cmdop

Usage:
    python agent_structured.py
    python agent_structured.py --hostname my-server

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
    parser = argparse.ArgumentParser(description="AI agent with structured output")
    parser.add_argument("--hostname", default=os.getenv("CMDOP_MACHINE"), help="Target hostname")
    parser.add_argument("--api-key", default=os.getenv("CMDOP_API_KEY", ""), help="CMDOP API key")
    args = parser.parse_args()

    if not args.api_key:
        print("Error: Set CMDOP_API_KEY environment variable", file=sys.stderr)
        return 1

    if not args.hostname:
        print("Error: Set CMDOP_MACHINE env or use --hostname", file=sys.stderr)
        return 1

    from pydantic import BaseModel, Field

    from cmdop import AsyncCMDOPClient

    class ServerHealth(BaseModel):
        hostname: str
        cpu_percent: float = Field(description="CPU usage percentage")
        memory_percent: float = Field(description="Memory usage percentage")
        disk_free_gb: float = Field(description="Free disk space in GB")
        issues: list[str] = Field(description="List of detected issues")

    async with AsyncCMDOPClient.remote(api_key=args.api_key) as client:
        await client.agent.set_machine(args.hostname)

        result = await client.agent.run(
            prompt="Check server health and report any issues",
            output_model=ServerHealth,
        )

        health: ServerHealth = result.data

        print(f"Host:   {health.hostname}")
        print(f"CPU:    {health.cpu_percent:.1f}%")
        print(f"Memory: {health.memory_percent:.1f}%")
        print(f"Disk:   {health.disk_free_gb:.1f} GB free")

        if health.issues:
            print(f"\nIssues ({len(health.issues)}):")
            for issue in health.issues:
                print(f"  - {issue}")
        else:
            print("\nNo issues detected")

    return 0


if __name__ == "__main__":
    try:
        code = asyncio.run(main())
        sys.exit(code)
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(130)

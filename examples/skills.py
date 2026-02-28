#!/usr/bin/env python3
"""Skills: list, inspect, and run AI skills on remote machines.

Prerequisites:
    1. CMDOP agent running on target machine
    2. pip install cmdop

Usage:
    # List all skills
    python skills.py list

    # Show skill details
    python skills.py show code-review

    # Run a skill
    python skills.py run code-review "Review the auth module"

    # Run with structured output
    python skills.py run code-review "Review this code" --structured

Environment:
    CMDOP_API_KEY: Your CMDOP API key
    CMDOP_MACHINE: Default target hostname
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys


async def cmd_list(client, hostname: str) -> int:
    """List all available skills."""
    await client.skills.set_machine(hostname)
    skills = await client.skills.list()

    if not skills:
        print("No skills installed")
        return 0

    print(f"{'Name':<25} {'Origin':<12} {'Description'}")
    print("-" * 70)
    for s in skills:
        print(f"{s.name:<25} {s.origin:<12} {s.description[:40]}")

    print(f"\nTotal: {len(skills)} skills")
    return 0


async def cmd_show(client, hostname: str, skill_name: str) -> int:
    """Show detailed skill info."""
    await client.skills.set_machine(hostname)
    detail = await client.skills.show(skill_name)

    if not detail.found:
        print(f"Skill not found: {skill_name}")
        if detail.error:
            print(f"Error: {detail.error}")
        return 1

    info = detail.info
    print(f"Name:        {info.name}")
    print(f"Description: {info.description}")
    print(f"Author:      {info.author or 'n/a'}")
    print(f"Version:     {info.version or 'n/a'}")
    print(f"Model:       {info.model or 'default'}")
    print(f"Origin:      {info.origin}")
    print(f"Source:      {detail.source}")

    if info.required_bins:
        print(f"Requires:    {', '.join(info.required_bins)}")
    if info.required_env:
        print(f"Env vars:    {', '.join(info.required_env)}")

    if detail.content:
        print(f"\n--- System Prompt ---\n{detail.content[:500]}")
        if len(detail.content) > 500:
            print(f"... ({len(detail.content)} chars total)")

    return 0


async def cmd_run(client, hostname: str, skill_name: str, prompt: str, structured: bool) -> int:
    """Run a skill."""
    await client.skills.set_machine(hostname)

    if structured:
        from pydantic import BaseModel, Field

        class SkillOutput(BaseModel):
            summary: str = Field(description="Brief summary of the result")
            score: int = Field(default=0, description="Quality score 1-10")
            items: list[str] = Field(default_factory=list, description="Key findings")

        result = await client.skills.run(
            skill_name,
            prompt,
            output_model=SkillOutput,
        )

        if result.success and result.data:
            print(f"Summary: {result.data.summary}")
            print(f"Score:   {result.data.score}/10")
            if result.data.items:
                print("Findings:")
                for item in result.data.items:
                    print(f"  - {item}")
        elif not result.success:
            print(f"Error: {result.error}")
            return 1
    else:
        result = await client.skills.run(skill_name, prompt)

        if result.success:
            print(result.text)
        else:
            print(f"Error: {result.error}")
            return 1

    print(f"\n--- {result.duration_seconds:.1f}s | {result.usage.total_tokens} tokens ---")
    return 0


async def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="CMDOP Skills")
    parser.add_argument("command", choices=["list", "show", "run"], help="Command")
    parser.add_argument("args", nargs="*", help="Skill name and/or prompt")
    parser.add_argument("--hostname", default=os.getenv("CMDOP_MACHINE"), help="Target hostname")
    parser.add_argument("--api-key", default=os.getenv("CMDOP_API_KEY", ""), help="CMDOP API key")
    parser.add_argument("--structured", action="store_true", help="Use structured output (for run)")
    args = parser.parse_args()

    if not args.api_key:
        print("Error: Set CMDOP_API_KEY environment variable", file=sys.stderr)
        return 1

    if not args.hostname:
        print("Error: Set CMDOP_MACHINE env or use --hostname", file=sys.stderr)
        return 1

    from cmdop import AsyncCMDOPClient

    async with AsyncCMDOPClient.remote(api_key=args.api_key) as client:
        if args.command == "list":
            return await cmd_list(client, args.hostname)

        elif args.command == "show":
            if not args.args:
                print("Error: skill name required", file=sys.stderr)
                return 1
            return await cmd_show(client, args.hostname, args.args[0])

        elif args.command == "run":
            if len(args.args) < 2:
                print("Error: skill name and prompt required", file=sys.stderr)
                return 1
            return await cmd_run(
                client, args.hostname, args.args[0], args.args[1], args.structured,
            )

    return 0


if __name__ == "__main__":
    try:
        code = asyncio.run(main())
        sys.exit(code)
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(130)

"""Run on the selected machine with its own installed Python environment."""
import asyncio
import json
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    upstream = StdioServerParameters(command=sys.executable, args=[str(Path(__file__).with_name("server.py"))])
    async with asyncio.timeout(40), stdio_client(upstream) as (reader, writer):
        async with ClientSession(reader, writer) as client:
            await client.initialize()
            tools = await client.list_tools()
            if [tool.name for tool in tools.tools] != ["latest_build"]:
                raise RuntimeError("unexpected tools")
            result = await client.call_tool("latest_build", {})
            if result.is_error or result.structured_content != {"job": "demo-build", "tests_passed": 3, "tests_failed": 0}:
                raise RuntimeError("unexpected build report")
            print(json.dumps(result.structured_content))


if __name__ == "__main__":
    asyncio.run(main())

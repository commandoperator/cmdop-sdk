"""A product-owned stdio MCP server exposing one packaged job report."""
import json
from pathlib import Path

from fastmcp import FastMCP

app = FastMCP("Example build reports")


@app.tool
def latest_build() -> dict:
    """Read the build report shipped with the demo application."""
    return json.loads(Path(__file__).with_name("build.json").read_text(encoding="utf-8"))


if __name__ == "__main__":
    app.run(transport="stdio")

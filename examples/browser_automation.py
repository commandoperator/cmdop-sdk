#!/usr/bin/env python3
"""Browser automation on remote machines.

Prerequisites:
    1. CMDOP agent running on target machine
    2. pip install cmdop

Usage:
    python browser_automation.py https://example.com
    python browser_automation.py https://example.com --hostname my-server

Environment:
    CMDOP_API_KEY: Your CMDOP API key
    CMDOP_MACHINE: Default target hostname
"""

from __future__ import annotations

import argparse
import os
import sys


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Browser automation")
    parser.add_argument("url", help="URL to navigate to")
    parser.add_argument("--hostname", default=os.getenv("CMDOP_MACHINE"), help="Target hostname")
    parser.add_argument("--api-key", default=os.getenv("CMDOP_API_KEY", ""), help="CMDOP API key")
    parser.add_argument("--headless", action="store_true", help="Run browser without UI")
    args = parser.parse_args()

    if not args.api_key:
        print("Error: Set CMDOP_API_KEY environment variable", file=sys.stderr)
        return 1

    if not args.hostname:
        print("Error: Set CMDOP_MACHINE env or use --hostname", file=sys.stderr)
        return 1

    from cmdop import CMDOPClient

    try:
        with CMDOPClient.remote(api_key=args.api_key) as client:
            with client.browser.create_session(headless=args.headless) as session:
                session.navigate(args.url)

                title = session.execute_script("return document.title")
                print(f"Title: {title}")

                # Extract all links
                links = session.dom.extract("a[href]", "href")
                print(f"\nFound {len(links)} links:")
                for link in links[:10]:
                    print(f"  {link}")
                if len(links) > 10:
                    print(f"  ... and {len(links) - 10} more")

                # Take screenshot
                screenshot = session.screenshot()
                print(f"\nScreenshot: {len(screenshot)} bytes")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""Network analyzer for discovering API endpoints and creating request snapshots."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field
from urllib.parse import urlparse, parse_qs

if TYPE_CHECKING:
    from cmdop.services.browser.session import BrowserSession
    from cmdop.services.browser.models import NetworkExchange


class RequestSnapshot(BaseModel):
    """Complete snapshot of an API request for reproduction."""

    # Request info
    url: str
    method: str = "GET"
    headers: dict[str, str] = Field(default_factory=dict)
    body: str = ""

    # Response info
    status: int | None = None
    content_type: str = ""
    size: int = 0

    # Parsed URL parts
    base_url: str = ""
    path: str = ""
    query_params: dict[str, list[str]] = Field(default_factory=dict)

    # Data analysis
    data_key: str | None = None
    item_count: int | None = None
    item_fields: list[str] = Field(default_factory=list)
    sample_response: Any = None

    # Session data
    cookies: dict[str, str] = Field(default_factory=dict)

    def to_curl(self) -> str:
        """Generate curl command to reproduce request."""
        parts = [f"curl -X {self.method}"]

        # Add headers
        for key, value in self.headers.items():
            if key.lower() not in ("host", "content-length"):
                parts.append(f"-H '{key}: {value}'")

        # Add cookies if not in headers
        if self.cookies and "cookie" not in [k.lower() for k in self.headers]:
            cookie_str = "; ".join(f"{k}={v}" for k, v in self.cookies.items())
            parts.append(f"-H 'Cookie: {cookie_str}'")

        # Add body
        if self.body:
            parts.append(f"-d '{self.body}'")

        # Add URL
        parts.append(f"'{self.url}'")

        return " \\\n  ".join(parts)

    def to_httpx(self) -> str:
        """Generate httpx Python code to reproduce request."""
        lines = ["import httpx", ""]

        # Headers
        if self.headers:
            lines.append("headers = {")
            for key, value in self.headers.items():
                if key.lower() not in ("host", "content-length"):
                    lines.append(f'    "{key}": "{value}",')
            lines.append("}")
        else:
            lines.append("headers = {}")

        # Cookies
        if self.cookies:
            lines.append("")
            lines.append("cookies = {")
            for key, value in self.cookies.items():
                lines.append(f'    "{key}": "{value}",')
            lines.append("}")
        else:
            lines.append("cookies = {}")

        # Request
        lines.append("")
        if self.method == "GET":
            lines.append(f'response = httpx.get("{self.url}", headers=headers, cookies=cookies)')
        elif self.method == "POST":
            if self.body:
                lines.append(f'data = {repr(self.body)}')
                lines.append(f'response = httpx.post("{self.url}", headers=headers, cookies=cookies, content=data)')
            else:
                lines.append(f'response = httpx.post("{self.url}", headers=headers, cookies=cookies)')
        else:
            lines.append(f'response = httpx.request("{self.method}", "{self.url}", headers=headers, cookies=cookies)')

        lines.append("print(response.json())")

        return "\n".join(lines)


class NetworkSnapshot(BaseModel):
    """Complete snapshot of network activity for a site."""

    url: str
    timestamp: str = ""

    # Session data
    cookies: dict[str, str] = Field(default_factory=dict)
    local_storage: dict[str, str] = Field(default_factory=dict)

    # Captured requests
    api_requests: list[RequestSnapshot] = Field(default_factory=list)
    json_requests: list[RequestSnapshot] = Field(default_factory=list)
    other_requests: list[dict] = Field(default_factory=list)

    # Stats
    total_requests: int = 0
    total_bytes: int = 0

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(indent=indent)

    def best_api(self) -> RequestSnapshot | None:
        """Get the best data API (largest response, then most items)."""
        if not self.api_requests:
            return None
        return max(self.api_requests, key=lambda r: (r.size, r.item_count or 0))


class NetworkAnalyzer:
    """Analyze network requests to discover API endpoints.

    Creates complete request snapshots including cookies, headers, and
    all data needed to reproduce API calls.

    Usage:
        from cmdop import CMDOPClient
        from cmdop.helpers import NetworkAnalyzer

        client = CMDOPClient.local()
        with client.browser.create_session(headless=False) as b:
            analyzer = NetworkAnalyzer(b)

            # Interactive mode - user clicks pagination
            snapshot = analyzer.capture("https://example.com/cars", wait_seconds=30)

            # Get best API endpoint
            if snapshot.api_requests:
                best = snapshot.best_api()
                print(f"API: {best.url}")
                print(f"Curl: {best.to_curl()}")
    """

    # Common keys that contain data arrays
    DATA_KEYS = [
        "data", "items", "results", "list", "records",
        "cars", "vehicles", "products", "listings", "entries",
        "rows", "content", "objects", "elements", "collection",
    ]

    def __init__(self, session: "BrowserSession"):
        """Initialize with browser session."""
        self._session = session

    def capture(
        self,
        url: str,
        wait_seconds: int = 30,
        url_pattern: str = "",
        clear_initial: bool = True,
        same_origin: bool = True,
        min_size: int = 100,
        max_size: int = 5_000_000,
        countdown_message: str = "Click pagination!",
    ) -> NetworkSnapshot:
        """Capture network requests while user interacts with page.

        Args:
            url: Page URL to open
            wait_seconds: Time to wait for user interactions
            url_pattern: Optional regex filter for API URLs
            clear_initial: Clear page load requests before capture
            same_origin: Only capture requests to same domain (default True)
            min_size: Min response size in bytes (filter tracking pixels)
            max_size: Max response size in bytes (filter images/assets)
            countdown_message: Message to show in countdown toast

        Returns:
            NetworkSnapshot with all captured requests and session data
        """
        from cmdop.services.browser.models import WaitUntil
        from datetime import datetime

        b = self._session
        snapshot = NetworkSnapshot(
            url=url,
            timestamp=datetime.now().isoformat(),
        )

        # Extract base domain for filtering
        base_domain = self._extract_base_domain(url)

        # Enable network capture
        b.network.enable(max_exchanges=500, max_response_size=5_000_000)

        try:
            print(f"Opening {url}...")
            b.navigate(url, timeout_ms=90000, wait_until=WaitUntil.LOAD)

            # Wait for page to be interactive
            try:
                b.wait_for("body", timeout_ms=10000)
            except Exception:
                pass
            time.sleep(2)

            if clear_initial:
                b.network.clear()

            # Show countdown while user interacts
            b.visual.countdown(wait_seconds, countdown_message)

            # Get cookies
            b.visual.toast("Getting cookies...")
            try:
                cookies = b.get_cookies()
                snapshot.cookies = {c.name: c.value for c in cookies}
            except Exception:
                pass

            # Get stats
            b.visual.toast("Getting network stats...")
            stats = b.network.stats()
            snapshot.total_requests = stats.total_captured
            snapshot.total_bytes = stats.total_bytes

            b.visual.toast(f"Captured {stats.total_captured} requests")

            # Get XHR/Fetch calls
            b.visual.toast("Filtering XHR/Fetch...")
            # print("Calling network.filter...", flush=True)
            api_calls = b.network.filter(
                url_pattern=url_pattern,
                resource_types=["xhr", "fetch"],
            )
            # print(f"Filter returned {len(api_calls)} calls", flush=True)

            # Filter by domain
            # print("Filtering by domain...", flush=True)
            if same_origin:
                api_calls = [
                    call for call in api_calls
                    if base_domain in urlparse(call.request.url).netloc
                ]
            # print(f"After domain filter: {len(api_calls)}", flush=True)

            # # Show sizes before filtering
            # for call in api_calls:
            #     size = call.response.size if call.response else 0
            #     print(f"  {call.request.url[:60]}... size={size}", flush=True)

            # Filter by response size (ignore tracking pixels and heavy assets)
            # print(f"Filtering by size ({min_size}-{max_size})...", flush=True)
            api_calls = [
                call for call in api_calls
                if call.response and min_size <= call.response.size <= max_size
            ]
            # print(f"After size filter: {len(api_calls)}", flush=True)

            # print("Showing toast...", flush=True)
            b.visual.toast(f"Found {len(api_calls)} API calls")

            # Analyze calls - all JSON responses are API requests
            # print(f"Analyzing {len(api_calls)} calls...", flush=True)
            for call in api_calls:
                req = self._create_snapshot(call, snapshot.cookies)
                if req:
                    if req.content_type and "json" in req.content_type:
                        snapshot.api_requests.append(req)
                    else:
                        snapshot.other_requests.append({
                            "url": call.request.url,
                            "method": call.request.method,
                            "status": call.response.status if call.response else None,
                        })

            # print("Analysis done", flush=True)

        finally:
            # print("Disabling network capture...", flush=True)
            b.network.disable()
            # print("Network disabled", flush=True)

        # print("Returning snapshot", flush=True)
        return snapshot

    def _extract_base_domain(self, url: str) -> str:
        """Extract base domain from URL, handling country-code TLDs."""
        parsed = urlparse(url)
        host = parsed.netloc.replace("www.", "")
        parts = host.split(".")

        # Country-code second-level domains
        cc_slds = {"co", "com", "net", "org", "ac", "go", "ne", "or"}

        if len(parts) >= 3 and parts[-2] in cc_slds:
            return ".".join(parts[-3:])  # bobaedream.co.kr
        elif len(parts) >= 2:
            return ".".join(parts[-2:])  # kcar.com
        return host

    def _create_snapshot(
        self,
        exchange: "NetworkExchange",
        session_cookies: dict[str, str],
    ) -> RequestSnapshot | None:
        """Create request snapshot from network exchange."""
        if not exchange.response:
            return None

        parsed = urlparse(exchange.request.url)

        snapshot = RequestSnapshot(
            url=exchange.request.url,
            method=exchange.request.method,
            headers=dict(exchange.request.headers),
            body=exchange.request.body.decode("utf-8", errors="ignore") if exchange.request.body else "",
            status=exchange.response.status,
            content_type=exchange.response.content_type or "",
            size=exchange.response.size,
            base_url=f"{parsed.scheme}://{parsed.netloc}",
            path=parsed.path,
            query_params=parse_qs(parsed.query),
            cookies=session_cookies,
        )

        # Parse JSON response
        if "json" in snapshot.content_type.lower():
            try:
                data = exchange.json_body()
                snapshot.sample_response = data

                if isinstance(data, list):
                    snapshot.item_count = len(data)
                    if data and isinstance(data[0], dict):
                        snapshot.item_fields = list(data[0].keys())
                elif isinstance(data, dict):
                    for key in self.DATA_KEYS:
                        if key in data and isinstance(data[key], list):
                            snapshot.data_key = key
                            snapshot.item_count = len(data[key])
                            if data[key] and isinstance(data[key][0], dict):
                                snapshot.item_fields = list(data[key][0].keys())
                            break
            except Exception:
                pass

        return snapshot


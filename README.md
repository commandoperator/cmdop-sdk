# CMDOP

**Your OS. Online.**

Full access to your machines from anywhere. Not files — the whole system.

```
Your Code ──── Cloud Relay ──── Agent (on server)
                   │
       Outbound only, works through any NAT/firewall
```

## Why CMDOP?

| Problem | CMDOP Solution |
|---------|----------------|
| VPN requires client install | SDK works without VPN |
| SSH needs port forwarding | Agent uses outbound connection |
| Screen sharing is laggy | gRPC streaming, real-time |
| File sync is just files | Full OS access: terminal + files + browser |
| AI returns text | Structured output with Pydantic |

## Install

```bash
pip install cmdop
```

## Quick Start

```python
from cmdop import AsyncCMDOPClient

async with AsyncCMDOPClient.remote(api_key="cmd_xxx") as client:
    # Terminal
    await client.terminal.set_machine("my-server")
    output, code = await client.terminal.execute("uname -a")

    # Files
    content = await client.files.read("/etc/hostname")
    await client.files.write("/tmp/config.json", b'{"key": "value"}')

    # AI Agent with typed output
    from pydantic import BaseModel

    class Health(BaseModel):
        cpu: float
        memory: float
        issues: list[str]

    result = await client.agent.run("Check server health", output_schema=Health)
    health: Health = result.output  # Typed!

    # Browser automation on remote machine
    with client.browser.create_session() as b:
        b.navigate("https://internal-app.local")
        b.click("button.submit")
```

## Connection

```python
from cmdop import CMDOPClient, AsyncCMDOPClient

# Remote (via cloud relay) - works through any NAT
client = CMDOPClient.remote(api_key="cmd_xxx")

# Local (direct IPC to running agent)
client = CMDOPClient.local()

# Async
async with AsyncCMDOPClient.remote(api_key="cmd_xxx") as client:
    ...
```

---

## Terminal

Execute commands, stream output, SSH into machines.

```python
async with AsyncCMDOPClient.remote(api_key="cmd_xxx") as client:
    # Set target machine once
    await client.terminal.set_machine("my-server")

    # Execute and get output
    output, code = await client.terminal.execute("ls -la")
    print(output.decode())

    # Interactive operations
    await client.terminal.send_input("echo hello\n")
    await client.terminal.resize(120, 40)
    await client.terminal.send_signal(SignalType.SIGINT)
```

**SSH-like interactive session:**
```bash
# CLI
cmdop ssh my-server

# Python
from cmdop.services.terminal.tui.ssh import ssh_connect
asyncio.run(ssh_connect('my-server', 'cmd_xxx'))
```

**Real-time streaming:**
```python
stream = client.terminal.stream()
stream.on_output(lambda data: print(data.decode(), end=""))
await stream.attach(session.session_id)
await stream.send_input(b"tail -f /var/log/app.log\n")
```

**Session discovery:**
```python
# List all machines
response = await client.terminal.list_sessions()
for s in response.sessions:
    print(f"{s.machine_hostname}: {s.status}")

# Get specific machine
session = await client.terminal.get_active_session("prod-server")
```

---

## Files

Read, write, list files on remote machines. No scp/sftp needed.

```python
# Set target machine once
await client.files.set_machine("my-server")

# File operations
files = await client.files.list("/var/log", include_hidden=True)
content = await client.files.read("/etc/nginx/nginx.conf")
await client.files.write("/tmp/config.json", b'{"key": "value"}')

# More operations
await client.files.copy("/src", "/dst")
await client.files.move("/old", "/new")
await client.files.mkdir("/new/dir")
await client.files.delete("/tmp/old", recursive=True)
info = await client.files.info("/path/file.txt")
```

---

## AI Agent

Run AI tasks with structured, typed output.

```python
from pydantic import BaseModel, Field

class ServerHealth(BaseModel):
    hostname: str
    cpu_percent: float = Field(description="CPU usage percentage")
    memory_percent: float
    disk_free_gb: float
    issues: list[str] = Field(description="List of detected issues")

result = await client.agent.run(
    prompt="Check server health and report any issues",
    output_schema=ServerHealth
)

# Typed response - not just text!
health: ServerHealth = result.output
if health.cpu_percent > 90:
    alert(f"{health.hostname} CPU critical!")
```

---

## Browser

Automate browsers on remote machines. Bypass CORS, inherit cookies.

```python
from cmdop.services.browser.models import WaitUntil

with client.browser.create_session(headless=False) as s:
    s.navigate("https://shop.com", wait_until=WaitUntil.NETWORKIDLE)

    # Interact
    s.click("button.buy", move_cursor=True)
    s.type("input[name=q]", "search term")
    s.wait_for(".results")

    # Extract
    title = s.execute_script("return document.title")
    screenshot = s.screenshot()
    cookies = s.get_cookies()
```

**`create_session` parameters:**
| Parameter | Default | Description |
|-----------|---------|-------------|
| `headless` | `False` | Run browser without UI |
| `provider` | `"camoufox"` | Browser provider |
| `profile_id` | `None` | Profile for session persistence |
| `block_images` | `False` | Disable loading images |
| `block_media` | `False` | Disable loading audio/video |

### Browser Capabilities

**Scrolling:**
```python
s.scroll.js("down", 500)           # JS scroll
s.scroll.to_bottom()               # Page bottom
s.scroll.to_element(".item")       # Scroll into view
s.scroll.infinite(extract_fn, limit=100)  # Infinite scroll with extraction
```

**Input:**
```python
s.input.click_js(".btn")           # JS click (reliable)
s.input.click_all("See more")      # Click all matching
s.input.key("Escape")              # Press key
s.input.hover(".tooltip")          # Hover
s.input.mouse_move(500, 300)       # Move cursor
```

**DOM:**
```python
s.dom.html(".container")           # Get HTML
s.dom.text(".title")               # Get text
s.dom.extract(".items", "href")    # Get attribute list
s.dom.select("#country", "US")     # Dropdown select
s.dom.close_modal()                # Close dialogs
```

**Fetch (bypass CORS):**
```python
data = s.fetch.json("/api/items")         # Fetch JSON
results = s.fetch.all(["/api/a", "/api/b"])  # Parallel
```

**Network capture:**
```python
s.network.enable(max_exchanges=1000)
s.navigate(url)

api = s.network.last("/api/data")
data = api.json_body()

posts = s.network.filter(
    url_pattern="/api/posts",
    methods=["GET", "POST"],
    status_codes=[200],
)

s.network.export_har()  # Export to HAR
```

---

## NetworkAnalyzer

Discover API endpoints by capturing traffic.

```python
from cmdop.helpers import NetworkAnalyzer

with client.browser.create_session(headless=False) as b:
    analyzer = NetworkAnalyzer(b)

    snapshot = analyzer.capture(
        "https://example.com/products",
        wait_seconds=30,
        countdown_message="Click pagination!",
    )

    if snapshot.api_requests:
        best = snapshot.best_api()
        print(best.url)
        print(best.item_count)
        print(best.to_curl())      # curl command
        print(best.to_httpx())     # Python code
```

---

## Download

Download files from URLs via remote server.

```python
from pathlib import Path

async with AsyncCMDOPClient.remote(api_key="cmd_xxx") as client:
    # Set target machine
    await client.download.set_machine("my-server")
    client.download.configure(api_key="cmd_xxx")

    result = await client.download.url(
        url="https://example.com/large-file.zip",
        local_path=Path("./large-file.zip"),
    )

    if result.success:
        print(result)  # DownloadResult(ok, 139.2MB, 245.3s, 0.6MB/s)
```

Handles cloud relay limits automatically:
- Small files (≤10MB): Direct chunked transfer
- Large files (>10MB): Split on remote, download parts

---

## SDKBaseModel

Auto-cleaning Pydantic model for scraped data.

```python
from cmdop import SDKBaseModel

class Product(SDKBaseModel):
    __base_url__ = "https://shop.com"
    name: str = ""    # "  iPhone 15  \n" → "iPhone 15"
    price: int = 0    # "$1,299.00" → 1299
    rating: float = 0 # "4.5 stars" → 4.5
    url: str = ""     # "/p/123" → "https://shop.com/p/123"

products = Product.from_list(raw["items"])  # Auto dedupe + filter
```

---

## Architecture

```
┌─────────────┐    gRPC/HTTP2    ┌─────────────┐    gRPC    ┌─────────┐
│   Python    │◀────────────────▶│   Django    │◀──────────▶│  Agent  │
│     SDK     │   Bidirectional  │   Relay     │  Outbound  │  (Go)   │
└─────────────┘                  └─────────────┘            └─────────┘
      │                                │                         │
      ▼                                ▼                         ▼
┌─────────────┐                 ┌─────────────┐           ┌───────────┐
│  Terminal   │                 │  Centrifugo │           │   Shell   │
│  Files      │                 │  WebSocket  │           │   Files   │
│  Browser    │                 │  Real-time  │           │   Browser │
│  Agent      │                 │             │           │           │
└─────────────┘                 └─────────────┘           └───────────┘
```

**Key points:**
- Agent makes outbound connection (no port forwarding)
- SDK connects via gRPC (works through any firewall)
- All services multiplexed over single connection
- Self-hosted relay option (Django)

---

## Comparison

| Feature | CMDOP | Tailscale | ngrok | SSH |
|---------|-------|-----------|-------|-----|
| Terminal streaming | gRPC | VPN + SSH | No | Yes |
| File operations | Built-in | SFTP | No | SCP |
| Browser automation | Built-in | No | No | No |
| AI agent | Built-in | No | No | No |
| NAT traversal | Outbound | WireGuard | Outbound | Port forward |
| Client install | None | VPN client | None | SSH client |
| Structured output | Pydantic | No | No | No |

---

## Requirements

- Python 3.10+
- CMDOP agent running locally or API key for remote access

## Links

- [Documentation](https://cmdop.com/docs/)
- [Agent Download](https://cmdop.com/download)
- [GitHub](https://github.com/commandoperator/cmdop-sdk)

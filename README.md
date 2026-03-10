# CMDOP

![CMDOP](https://raw.githubusercontent.com/markolofsen/assets/main/libs/cmdop_sdk.webp)

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
| File sync is just files | Full OS access: terminal + files |
| AI returns text | Structured output with Pydantic |
| No reusable workflows | Skills: predefined AI tasks with tools |

## Install

```bash
pip install cmdop
```

## Quick Start

```python
from cmdop import AsyncCMDOPClient

async with AsyncCMDOPClient.remote(api_key="cmdop_xxx") as client:
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

    await client.agent.set_machine("my-server")
    result = await client.agent.run("Check server health", output_model=Health)
    health: Health = result.data  # Typed!

    # Skills — run predefined AI workflows
    await client.skills.set_machine("my-server")
    skills = await client.skills.list()
    result = await client.skills.run("code-review", "Review the auth module")

```

## Connection

```python
from cmdop import CMDOPClient, AsyncCMDOPClient

# Remote (via cloud relay) - works through any NAT
client = CMDOPClient.remote(api_key="cmdop_xxx")

# Local (direct IPC to running agent)
client = CMDOPClient.local()

# Async
async with AsyncCMDOPClient.remote(api_key="cmdop_xxx") as client:
    ...
```

---

## Terminal

Execute commands, stream output, SSH into machines.

```python
async with AsyncCMDOPClient.remote(api_key="cmdop_xxx") as client:
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

await client.agent.set_machine("my-server")
result = await client.agent.run(
    prompt="Check server health and report any issues",
    output_model=ServerHealth,
)

# Typed response - not just text!
health: ServerHealth = result.data
if health.cpu_percent > 90:
    alert(f"{health.hostname} CPU critical!")
```

---

## Skills

Run predefined AI workflows on remote machines. Skills are reusable prompt templates with tool access.

```python
await client.skills.set_machine("my-server")

# List available skills
skills = await client.skills.list()
for skill in skills:
    print(f"{skill.name}: {skill.description} ({skill.origin})")

# Inspect a skill
detail = await client.skills.show("code-review")
if detail.found:
    print(detail.content)   # System prompt markdown
    print(detail.source)    # File path on machine

# Run a skill
result = await client.skills.run("code-review", "Review the auth module")
print(result.text)
print(f"Took {result.duration_seconds}s, {result.usage.total_tokens} tokens")
```

**Structured output:**
```python
from pydantic import BaseModel

class Review(BaseModel):
    score: int
    summary: str
    issues: list[str]

result = await client.skills.run(
    "code-review",
    "Review the auth module",
    output_model=Review,
)
review: Review = result.data
print(f"Score: {review.score}/10")
```

**Custom options:**
```python
from cmdop import SkillRunOptions

result = await client.skills.run(
    "summarize",
    "Summarize the project README",
    options=SkillRunOptions(model="openai/gpt-4o", timeout_seconds=120),
)
```

---

## Download

Download files from URLs via remote server.

```python
from pathlib import Path

async with AsyncCMDOPClient.remote(api_key="cmdop_xxx") as client:
    # Set target machine
    await client.download.set_machine("my-server")
    client.download.configure(api_key="cmdop_xxx")

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
│   Python    │◀────────────────▶│   Cloud     │◀──────────▶│  Agent  │
│     SDK     │   Bidirectional  │   Relay     │  Outbound  │  (Go)   │
└─────────────┘                  └─────────────┘            └─────────┘
```

**Key points:**
- Agent makes outbound connection (no port forwarding)
- SDK connects via gRPC (works through any firewall)
- All services multiplexed over single connection

---

## Comparison

| Feature | CMDOP | Tailscale | ngrok | SSH |
|---------|-------|-----------|-------|-----|
| Terminal streaming | gRPC | VPN + SSH | No | Yes |
| File operations | Built-in | SFTP | No | SCP |
| AI agent | Built-in | No | No | No |
| Reusable AI skills | Built-in | No | No | No |
| NAT traversal | Outbound | WireGuard | Outbound | Port forward |
| Client install | None | VPN client | None | SSH client |
| Structured output | Pydantic | No | No | No |

---

## Requirements

- Python 3.10+
- CMDOP agent running locally or API key for remote access

## Links

- [Examples](examples/)
- [Documentation](https://cmdop.com/docs/sdk/python)
- [Bot Documentation](https://cmdop.com/docs/sdk/python-bot)
- [Skills Catalog](https://cmdop.com/skills/)
- [Agent Download](https://cmdop.com/download)
- [GitHub](https://github.com/commandoperator/cmdop-sdk)

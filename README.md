# CMDOP

![CMDOP](https://raw.githubusercontent.com/markolofsen/assets/main/libs/cmdop/cmdop.webp)

**Your OS. Online.**

Full access to your machines from anywhere. Not files — the whole system.

```
Your Code ──── Cloud Relay ──── Agent (on server)
                   │
       Outbound only, works through any NAT/firewall
```

## Install

```bash
pip install cmdop
```

The package still imports as `cmdop`. The installed CLI entry point is **`cmdop-sdk`** (`ssh`, `fleet`, `exec`, `tui`) so it does not collide with the main CMDOP desktop/Go binary on `PATH`.

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

## Documentation

| Topic | Description |
|-------|-------------|
| [Terminal](docs/terminal.md) | Execute commands, stream output, SSH sessions |
| [Auth](docs/auth.md) | Agent password authentication, session tokens |
| [Files](docs/files.md) | Read, write, list files on remote machines |
| [Agent](docs/agent.md) | AI tasks with structured typed output |
| [Skills](docs/skills.md) | Predefined AI workflows with tool access |
| [Download](docs/download.md) | Download files from URLs via remote server |
| [SDKBaseModel](docs/base_model.md) | Auto-cleaning Pydantic model for scraped data |

## Architecture

```
┌─────────────┐    gRPC/HTTP2    ┌─────────────┐    gRPC    ┌─────────┐
│   Python    │◀────────────────▶│   Cloud     │◀──────────▶│  Agent  │
│     SDK     │   Bidirectional  │   Relay     │  Outbound  │  (Go)   │
└─────────────┘                  └─────────────┘            └─────────┘
```

- Agent makes outbound connection (no port forwarding)
- SDK connects via gRPC (works through any firewall)
- All services multiplexed over single connection

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

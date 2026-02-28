# CMDOP SDK Examples

Practical examples for common CMDOP operations.

## Prerequisites

1. Download agent from [cmdop.com/downloads](https://cmdop.com/downloads/)
2. Install and authorize the agent on your machine
3. Get API key from [my.cmdop.com/dashboard/settings](https://my.cmdop.com/dashboard/settings/)

## Install

```bash
pip install cmdop
```

## Examples

| Example | Description |
|---------|-------------|
| [terminal_ssh.py](terminal_ssh.py) | SSH-like terminal connection and command execution |
| [file_operations.py](file_operations.py) | Read, write, and list files on remote machines |
| [fleet_status.py](fleet_status.py) | Check status of all connected machines |
| [agent_structured.py](agent_structured.py) | AI agent with Pydantic structured output |
| [skills.py](skills.py) | List, inspect, and run AI skills |
| [browser_automation.py](browser_automation.py) | Browser automation on remote machines |

## Configuration

All examples use environment variables:

```bash
export CMDOP_API_KEY="cmdop_xxx"    # Your API key
export CMDOP_MACHINE="my-server"    # Default target machine
```

Or pass via CLI arguments where supported.

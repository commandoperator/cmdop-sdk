# Terminal

Execute commands, stream output, SSH into machines.

## Basic Usage

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

## SSH-like Interactive Session

```bash
# CLI (Python SDK)
cmdop-sdk ssh my-server

# Python
from cmdop.services.terminal.tui.ssh import ssh_connect
asyncio.run(ssh_connect('my-server', 'cmd_xxx'))
```

## Real-time Streaming

```python
stream = client.terminal.stream()
stream.on_output(lambda data: print(data.decode(), end=""))
await stream.attach(session.session_id)
await stream.send_input(b"tail -f /var/log/app.log\n")
```

## Session Discovery

```python
# List all machines
response = await client.terminal.list_sessions()
for s in response.sessions:
    print(f"{s.machine_hostname}: {s.status}")

# Get specific machine
session = await client.terminal.get_active_session("prod-server")
```

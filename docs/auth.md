# Agent Password Authentication

When an agent has a password set (`CMDOP_DAEMON_AGENT_PASSWORD`), `attach()` handles the challenge automatically.

## Password Options

```python
# Option 1: pass password directly
await stream.attach(session.session_id, password="my-secret")

# Option 2: env var (best for CI/automation)
# CMDOP_AGENT_PASSWORD=my-secret python script.py
await stream.attach(session.session_id)

# Option 3: interactive — SDK prompts stdin if neither is set
await stream.attach(session.session_id)
# → "Agent password required: "
```

## Session Token

After successful password verification, the server sends an `AuthSuccess` message containing a session token. The SDK stores it automatically and includes it as `x-session-token` metadata on all subsequent unary RPCs (SendInput, FileWrite, RunAgent, etc.). No extra code needed.

```python
# Full example: attach with password → unary RPCs just work
async with AsyncCMDOPClient.remote(api_key="cmdop_xxx") as client:
    stream = client.terminal.attach_stream(session_id)
    await stream.attach(session_id, password="secret")
    # session_token is now set on transport — all unary RPCs are authenticated
    await stream.send_input(b"ls -la\n")
```

"""
SSH-like terminal connection.

Provides simple raw terminal passthrough for connecting to remote machines.

ARCHITECTURE:
=============
SDK connects to existing agent session via gRPC streaming.

Flow:
1. SDK calls get_active_session(hostname) → returns agent's session_id
2. SDK calls stream.attach(session_id) → connects to Django with agent's session_id
3. Django sees "sdk-python-*-attach" version → adds SDK to _sdk_subscribers[session_id]
4. SDK sends input → Django forwards to agent queue
5. Agent sends output → Django forwards to all SDK subscribers

CRITICAL: session_id must be the REAL agent session_id from get_active_session().
If SDK uses wrong session_id, Django won't find the agent queue and output won't work.

Troubleshooting:
- "No active session" → Agent not connected, check: cmdop status
- Input works but no output → session_id mismatch, check Django logs
- Connection timeout → Agent disconnected during attach
"""

from __future__ import annotations

import asyncio
import sys
from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel

from cmdop.services.terminal.tui.modes import (
    enter_raw_mode,
    exit_raw_mode,
    get_terminal_size,
    is_tty,
    setup_resize_handler,
)

if TYPE_CHECKING:
    from cmdop.streaming.terminal import TerminalStream

console = Console()


async def ssh_connect(
    hostname: str,
    api_key: str,
    session_id: str | None = None,
) -> int:
    """
    Connect to a remote machine with SSH-like terminal experience.

    Establishes a bidirectional terminal stream and provides
    raw terminal passthrough for interactive shell access.

    Args:
        hostname: Machine hostname to connect to (partial match).
        api_key: CMDOP API key for authentication.
        session_id: Optional specific session ID to connect to.
                   If None, will find active session for hostname.

    Returns:
        Exit code (0 for success, 1 for error).

    Example:
        >>> import asyncio
        >>> asyncio.run(ssh_connect("my-server", "cmd_xxx"))

    Note:
        Requires a TTY for interactive operation.
        Press Ctrl+D to disconnect gracefully.
    """
    from cmdop import AsyncCMDOPClient

    # Check for TTY
    if not is_tty():
        console.print("[red]Error:[/] ssh_connect requires an interactive terminal (TTY)")
        return 1

    stream: TerminalStream | None = None

    try:
        async with AsyncCMDOPClient.remote(api_key=api_key) as client:
            # =========================================================
            # STEP 1: Find agent session
            # We need the REAL session_id from the connected agent.
            # This is critical - if we use wrong session_id, Django
            # won't be able to forward output back to us.
            # =========================================================
            if session_id is None:
                from cmdop.exceptions import (
                    CMDOPError,
                    InvalidAPIKeyError,
                    ConnectionTimeoutError,
                    AgentOfflineError,
                )

                with console.status(f"[cyan]Finding session for [bold]{hostname}[/bold]...[/]"):
                    try:
                        session = await client.terminal.set_machine(hostname)
                    except InvalidAPIKeyError:
                        console.print(
                            "\n[red]Error:[/] Invalid API key\n\n"
                            "[dim]Check your API key in config.py or environment variables.[/]\n"
                        )
                        return 1
                    except ConnectionTimeoutError:
                        console.print(
                            f"\n[red]Error:[/] Connection timeout for '[bold]{hostname}[/bold]'\n\n"
                            "[dim]Possible causes:[/]\n"
                            "  • Agent is offline\n"
                            "  • Network connectivity issues\n"
                            "  • Server is overloaded\n"
                        )
                        return 1
                    except AgentOfflineError:
                        console.print(
                            f"\n[red]Error:[/] Agent offline for '[bold]{hostname}[/bold]'\n\n"
                            "[dim]Start the agent on the target machine:[/]\n"
                            "  • cmdop connect\n"
                        )
                        return 1
                    except CMDOPError as e:
                        console.print(f"\n[red]Error:[/] {e}\n")
                        return 1

                # CRITICAL: Use agent's real session_id
                session_id = session.session_id
                console.print(
                    f"[green]✓[/] Found session: [bold]{session.machine_hostname}[/bold] "
                    f"[dim](id: {session_id[:8]}...)[/]"
                )

            # =========================================================
            # STEP 2: Create stream and attach to agent session
            # We use attach() not connect() because we're subscribing
            # to an existing agent session, not creating new one.
            # =========================================================
            stream = client.terminal.stream()

            # Setup output handler - called when agent sends output
            def on_output(data: bytes) -> None:
                """Write terminal output to stdout."""
                sys.stdout.buffer.write(data)
                sys.stdout.buffer.flush()

            def on_error(code: str, message: str, is_fatal: bool) -> None:
                """Handle stream errors."""
                console.print(f"\n[red]Error:[/] {code}: {message}")
                if is_fatal:
                    stream._shutdown.set()

            def on_disconnect(_reason: str) -> None:
                """Handle disconnection."""
                pass  # Silently handle, we'll print on exit

            stream.on_output(on_output)
            stream.on_error(on_error)
            stream.on_disconnect(on_disconnect)

            # Attach to existing agent session (NOT connect!)
            # This sends RegisterRequest with version="sdk-python-*-attach"
            # Django will add us to _sdk_subscribers[session_id]
            with console.status("[cyan]Connecting...[/]"):
                try:
                    await stream.attach(session_id)
                except TimeoutError:
                    console.print(
                        f"\n[red]Connection timeout[/]\n\n"
                        "[dim]The agent may have disconnected. Try:[/]\n"
                        f"  • Check agent status: cmdop status {hostname}\n"
                        "  • Reconnect agent on the machine\n"
                    )
                    return 1
                except Exception as e:
                    console.print(f"[red]Connection failed:[/] {e}")
                    return 1

            console.print(
                Panel(
                    "[green]Connected![/] Press [bold]Ctrl+D[/] to disconnect.\n\n"
                    "[dim]Tip: Use [/][cyan]ccat[/][dim] for syntax-highlighted file viewing[/]",
                    title="SSH Session",
                    border_style="green",
                )
            )
            print()  # Extra newline before terminal

            # =========================================================
            # STEP 3: Run terminal I/O loop
            # Read local input → send to agent
            # Receive agent output → write to stdout (via on_output)
            # =========================================================
            exit_code = await _run_terminal_loop(stream)

            # Close stream gracefully
            try:
                await stream.close("user_disconnect")
            except Exception:
                pass

            return exit_code

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print()  # Newline after ^C
        console.print("\n[yellow]Session interrupted.[/]")
        if stream:
            try:
                await stream.close("interrupted")
            except Exception:
                pass
        return 130

    except Exception as e:
        console.print(f"\n[red]Error:[/] {e}")
        return 1

    finally:
        # Always restore terminal state
        exit_raw_mode()
        console.print("\n[dim]Disconnected.[/]")


async def _run_terminal_loop(stream: TerminalStream) -> int:
    """
    Run the main terminal I/O loop.

    Reads input from stdin and sends to remote agent.
    Output from agent is handled by on_output callback.

    Args:
        stream: Connected terminal stream.

    Returns:
        Exit code.
    """
    import select

    # Enter raw mode for character-by-character input
    if not enter_raw_mode():
        console.print("[yellow]Warning:[/] Could not enter raw mode")

    # Setup resize handler to forward terminal size changes
    async def on_resize(cols: int, rows: int) -> None:
        """Forward resize to remote."""
        try:
            await stream.send_resize(cols, rows)
        except Exception:
            pass

    def resize_callback(cols: int, rows: int) -> None:
        """Sync wrapper for async resize handler."""
        asyncio.create_task(on_resize(cols, rows))

    setup_resize_handler(resize_callback)

    # Send initial terminal size
    cols, rows = get_terminal_size()
    try:
        await stream.send_resize(cols, rows)
    except Exception:
        pass

    try:
        # Main input loop
        while stream.is_connected:
            # Check for input with timeout (non-blocking)
            try:
                readable, _, _ = select.select([sys.stdin], [], [], 0.1)
            except (ValueError, OSError):
                break

            if readable:
                try:
                    # Read raw input (non-blocking)
                    data = sys.stdin.buffer.read1(1024)  # type: ignore
                except AttributeError:
                    # Fallback for stdin without read1
                    data = sys.stdin.buffer.read(1)

                if not data:
                    # EOF (Ctrl+D)
                    break

                # Check for Ctrl+D (ASCII 4)
                if b"\x04" in data:
                    break

                # Send input to remote agent
                try:
                    await stream.send_input(data)
                except Exception:
                    break

            # Small sleep to prevent busy loop
            await asyncio.sleep(0.01)

        return 0

    except asyncio.CancelledError:
        return 0
    except KeyboardInterrupt:
        return 130
    except Exception:
        return 1
    finally:
        # Restore terminal to normal mode
        exit_raw_mode()


async def ssh_execute(
    hostname: str,
    command: str,
    api_key: str,
    timeout: float = 30.0,
) -> tuple[bytes, int]:
    """
    Execute a command on remote machine via SSH-like connection.

    Non-interactive command execution that returns output.

    Args:
        hostname: Machine hostname to connect to.
        command: Command to execute.
        api_key: CMDOP API key.
        timeout: Maximum execution time in seconds.

    Returns:
        Tuple of (output_bytes, exit_code).

    Example:
        >>> output, code = await ssh_execute("my-server", "ls -la", "cmd_xxx")
        >>> print(output.decode())
    """
    from cmdop import AsyncCMDOPClient

    async with AsyncCMDOPClient.remote(api_key=api_key) as client:
        # Find active agent session
        session = await client.terminal.get_active_session(hostname=hostname)
        if session is None:
            raise ValueError(f"No active session found for '{hostname}'")

        # Execute command using agent's session_id
        return await client.terminal.execute(
            command,
            timeout=timeout,
            session_id=session.session_id,
        )

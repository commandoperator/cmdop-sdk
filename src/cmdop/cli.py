"""
CMDOP SDK CLI.

Usage:
    cmdop ssh my-server
    cmdop ssh my-server --exec "ls -la"
    cmdop fleet status
    cmdop tui
"""

from __future__ import annotations

import asyncio
import os
import sys
from typing import TYPE_CHECKING

import click
from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from cmdop import AsyncCMDOPClient

console = Console()
err_console = Console(stderr=True)


def get_api_key(ctx: click.Context) -> str:
    """Get API key from context or environment."""
    api_key = ctx.obj.get("api_key") if ctx.obj else None
    if not api_key:
        api_key = os.getenv("CMDOP_API_KEY", "")
    if not api_key:
        err_console.print("[red]Error:[/red] Set CMDOP_API_KEY environment variable")
        raise SystemExit(1)
    return api_key


@click.group()
@click.option("--api-key", envvar="CMDOP_API_KEY", help="CMDOP API key")
@click.version_option(package_name="cmdop")
@click.pass_context
def main(ctx: click.Context, api_key: str | None) -> None:
    """CMDOP SDK command-line interface."""
    ctx.ensure_object(dict)
    ctx.obj["api_key"] = api_key


# =============================================================================
# SSH Command
# =============================================================================


@main.command()
@click.argument("hostname", required=False)
@click.option("--exec", "-e", "execute", help="Execute single command")
@click.option("--session-id", "-s", help="Specific session ID")
@click.option("--timeout", "-t", default=30.0, help="Command timeout in seconds")
@click.pass_context
def ssh(
    ctx: click.Context,
    hostname: str | None,
    execute: str | None,
    session_id: str | None,
    timeout: float,
) -> None:
    """SSH-like terminal connection.

    Connect to a remote machine interactively or execute a single command.

    Examples:

        cmdop ssh my-server

        cmdop ssh my-server --exec "ls -la"

        cmdop ssh --session-id abc123
    """
    api_key = get_api_key(ctx)
    code = asyncio.run(_ssh_async(api_key, hostname, execute, session_id, timeout))
    raise SystemExit(code)


async def _ssh_async(
    api_key: str,
    hostname: str | None,
    execute: str | None,
    session_id: str | None,
    timeout: float,
) -> int:
    """Async SSH implementation."""
    from cmdop import AsyncCMDOPClient

    async with AsyncCMDOPClient.remote(api_key=api_key) as client:
        # Resolve session
        if not session_id:
            session = await client.terminal.get_active_session(hostname=hostname)
            if not session:
                if hostname:
                    err_console.print(f"[red]No session found for[/red] '{hostname}'")
                else:
                    err_console.print("[red]No active sessions found[/red]")
                await _show_available_sessions(client)
                return 1
            session_id = session.session_id
            resolved_hostname = session.machine_hostname
        else:
            resolved_hostname = hostname or "unknown"

        # Execute or interactive
        if execute:
            output, code = await client.terminal.execute(
                execute,
                session_id=session_id,
                timeout=timeout,
            )
            sys.stdout.buffer.write(output)
            return code
        else:
            from cmdop.services.terminal.tui import ssh_connect

            console.print(f"Connecting to [cyan]{resolved_hostname}[/cyan]...")
            return await ssh_connect(resolved_hostname, api_key, session_id=session_id)


async def _show_available_sessions(client: AsyncCMDOPClient) -> None:
    """Show available sessions."""
    response = await client.terminal.list_sessions(limit=5)
    if response.sessions:
        err_console.print("\n[dim]Available machines:[/dim]")
        for s in response.sessions:
            err_console.print(f"  [cyan]{s.machine_hostname}[/cyan]")


# =============================================================================
# Fleet Command
# =============================================================================


@main.group()
def fleet() -> None:
    """Fleet management commands."""
    pass


@fleet.command("status")
@click.option("--limit", "-n", default=50, help="Maximum machines to show")
@click.pass_context
def fleet_status(ctx: click.Context, limit: int) -> None:
    """Show status of all connected machines."""
    api_key = get_api_key(ctx)
    asyncio.run(_fleet_status_async(api_key, limit))


async def _fleet_status_async(api_key: str, limit: int) -> None:
    """Async fleet status implementation."""
    from cmdop import AsyncCMDOPClient

    async with AsyncCMDOPClient.remote(api_key=api_key) as client:
        response = await client.terminal.list_sessions(limit=limit)

        console.print(f"[dim]Workspace:[/dim] {response.workspace_name}")
        console.print(f"[dim]Total machines:[/dim] {response.total}\n")

        if not response.sessions:
            console.print("[yellow]No connected machines[/yellow]")
            return

        table = Table(show_header=True, header_style="bold")
        table.add_column("Status", width=8)
        table.add_column("Hostname", width=30)
        table.add_column("OS", width=10)
        table.add_column("Shell", width=15)
        table.add_column("Heartbeat", width=10)

        for session in response.sessions:
            status = "[green]online[/green]" if session.status == "connected" else "[red]offline[/red]"
            hostname = session.machine_hostname[:28]
            os_name = session.os[:8] if session.os else "unknown"
            shell = session.shell.split("/")[-1][:13] if session.shell else "n/a"
            heartbeat = f"{session.heartbeat_age_seconds}s" if session.heartbeat_age_seconds else "n/a"

            table.add_row(status, hostname, os_name, shell, heartbeat)

        console.print(table)


@fleet.command("list")
@click.option("--status", "-s", help="Filter by status (connected/disconnected)")
@click.option("--limit", "-n", default=50, help="Maximum machines to show")
@click.pass_context
def fleet_list(ctx: click.Context, status: str | None, limit: int) -> None:
    """List all machines (simple format)."""
    api_key = get_api_key(ctx)
    asyncio.run(_fleet_list_async(api_key, status, limit))


async def _fleet_list_async(api_key: str, status: str | None, limit: int) -> None:
    """Async fleet list implementation."""
    from cmdop import AsyncCMDOPClient

    async with AsyncCMDOPClient.remote(api_key=api_key) as client:
        response = await client.terminal.list_sessions(status=status, limit=limit)

        for session in response.sessions:
            icon = "[green]●[/green]" if session.status == "connected" else "[red]●[/red]"
            console.print(f"{icon} {session.machine_hostname}")


# =============================================================================
# Exec Command (shorthand)
# =============================================================================


@main.command()
@click.argument("hostname")
@click.argument("command", nargs=-1, required=True)
@click.option("--timeout", "-t", default=30.0, help="Command timeout in seconds")
@click.pass_context
def exec(
    ctx: click.Context,
    hostname: str,
    command: tuple[str, ...],
    timeout: float,
) -> None:
    """Execute command on remote machine.

    Shorthand for: cmdop ssh HOSTNAME --exec "COMMAND"

    Examples:

        cmdop exec my-server ls -la

        cmdop exec my-server cat /etc/hostname
    """
    api_key = get_api_key(ctx)
    cmd = " ".join(command)
    code = asyncio.run(_ssh_async(api_key, hostname, cmd, None, timeout))
    raise SystemExit(code)


# =============================================================================
# TUI Command
# =============================================================================


@main.command()
@click.pass_context
def tui(ctx: click.Context) -> None:
    """Interactive TUI application.

    Launch full terminal UI with machine list, multiple tabs,
    and rich terminal rendering.

    Requires: textual
    """
    api_key = get_api_key(ctx)
    code = asyncio.run(_tui_async(api_key))
    raise SystemExit(code)


async def _tui_async(api_key: str) -> int:
    """Async TUI implementation."""
    try:
        from cmdop.services.terminal.tui.app import run_tui

        return await run_tui(api_key)
    except ImportError:
        err_console.print(
            "[red]TUI requires textual.[/red]\n"
            "Install with: [cyan]pip install textual[/cyan]"
        )
        return 1


# =============================================================================
# Entry Point
# =============================================================================


if __name__ == "__main__":
    main()

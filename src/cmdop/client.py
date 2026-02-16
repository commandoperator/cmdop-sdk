"""
CMDOP Client - Main entry point for the SDK.

Provides CMDOPClient (sync) and AsyncCMDOPClient (async) classes
with namespace-based access to services.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cmdop.services.agent import AgentService, AsyncAgentService
from cmdop.services.browser import AsyncBrowserService, BrowserService
from cmdop.services.download import AsyncDownloadService, DownloadService
from cmdop.services.extract import AsyncExtractService, ExtractService
from cmdop.services.files import AsyncFilesService, FilesService
from cmdop.services.terminal import AsyncTerminalService, TerminalService
from cmdop.transport.local import LocalTransport
from cmdop.transport.remote import RemoteTransport

if TYPE_CHECKING:
    from pathlib import Path

    from cmdop.models.config import ConnectionConfig
    from cmdop.transport.base import BaseTransport


class CMDOPClient:
    """
    Synchronous CMDOP client.

    Main entry point for SDK operations. Provides namespace-based
    access to services: terminal, files, etc.

    Use factory methods to create instances:
    - CMDOPClient.remote() - Connect via cloud relay
    - CMDOPClient.local() - Connect to local agent (Phase 2)

    Example:
        >>> client = CMDOPClient.remote(api_key="cmdop_live_xxx")
        >>> session = client.terminal.create()
        >>> client.terminal.send_input(session.session_id, b"ls\\n")
        >>> files = client.files.list("/home/user")
    """

    def __init__(self, transport: BaseTransport) -> None:
        """
        Initialize client with transport.

        Use factory methods instead of direct construction.

        Args:
            transport: Configured transport instance
        """
        self._transport = transport
        self._terminal: TerminalService | None = None
        self._files: FilesService | None = None
        self._extract: ExtractService | None = None
        self._agent: AgentService | None = None
        self._browser: BrowserService | None = None
        self._download: DownloadService | None = None

    @classmethod
    def remote(
        cls,
        api_key: str,
        server: str = "grpc.cmdop.com:443",
        agent_id: str | None = None,
        config: ConnectionConfig | None = None,
        insecure: bool = False,
    ) -> CMDOPClient:
        """
        Create client connected via cloud relay.

        Args:
            api_key: CMDOP API key (cmd_xxx)
            server: Cloud relay endpoint
            agent_id: Target agent UUID (uses default if None)
            config: Connection configuration
            insecure: Use insecure connection (no TLS). For local dev only.

        Returns:
            Connected CMDOPClient instance

        Raises:
            ValueError: If API key format is invalid
            AuthenticationError: If API key is rejected
            AgentOfflineError: If target agent is offline
        """
        transport = RemoteTransport(
            api_key=api_key,
            server=server,
            agent_id=agent_id,
            config=config,
            insecure=insecure,
        )
        return cls(transport)

    @classmethod
    def local(
        cls,
        config: ConnectionConfig | None = None,
        discovery_paths: list[Path | str] | None = None,
        use_defaults: bool = True,
    ) -> CMDOPClient:
        """
        Create client connected to local agent.

        Discovers local agent via port file and connects
        via Unix socket (Linux/macOS) or Named Pipe (Windows).

        Args:
            config: Connection configuration
            discovery_paths: Override default discovery paths
            use_defaults: Whether to include default discovery paths

        Returns:
            Connected CMDOPClient instance

        Raises:
            AgentNotRunningError: No local agent found
            StalePortFileError: Discovery file exists but agent dead
            PermissionDeniedError: UID mismatch on Unix socket

        Example:
            >>> client = CMDOPClient.local()
            >>> files = client.files.list("/tmp")
        """
        transport = LocalTransport.discover(
            config=config,
            custom_paths=discovery_paths,
            use_defaults=use_defaults,
        )
        return cls(transport)

    @classmethod
    def from_transport(cls, transport: BaseTransport) -> CMDOPClient:
        """
        Create client from existing transport.

        Useful for custom transport configurations or testing.

        Args:
            transport: Pre-configured transport instance

        Returns:
            CMDOPClient using the provided transport
        """
        return cls(transport)

    @property
    def transport(self) -> BaseTransport:
        """Get underlying transport."""
        return self._transport

    @property
    def terminal(self) -> TerminalService:
        """
        Terminal service for session management.

        Provides: create, send_input, resize, close, get_history
        """
        if self._terminal is None:
            self._terminal = TerminalService(self._transport)
        return self._terminal

    @property
    def files(self) -> FilesService:
        """
        Files service for file system operations.

        Provides: list, read, write, delete, copy, move, mkdir, info
        """
        if self._files is None:
            self._files = FilesService(self._transport)
        return self._files

    @property
    def extract(self) -> ExtractService:
        """
        Extract service for structured data extraction.

        Provides: run (with Pydantic model support)

        Example:
            >>> from pydantic import BaseModel
            >>> class Config(BaseModel):
            ...     host: str
            ...     port: int
            >>> result = client.extract.run(Config, "Find database config")
            >>> if result.success:
            ...     print(result.data.host)
        """
        if self._extract is None:
            self._extract = ExtractService(self._transport)
        return self._extract

    @property
    def agent(self) -> AgentService:
        """
        Agent service for AI agent execution.

        Provides: run (blocking execution)

        NOTE: Agent streaming is only available in async mode.
        Use AsyncCMDOPClient.agent.run_stream() for streaming.

        Example:
            >>> result = client.agent.run("What files are in /tmp?")
            >>> print(result.text)
        """
        if self._agent is None:
            self._agent = AgentService(self._transport)
        return self._agent

    @property
    def browser(self) -> BrowserService:
        """
        Browser service for direct programmatic control.

        Provides: create_session, navigate, click, type, extract, etc.

        NOTE: This is direct control without LLM - use CSS selectors,
        regex patterns, and JavaScript for data extraction.

        Example:
            >>> with client.browser.create_session() as session:
            ...     session.navigate("https://google.com")
            ...     session.type("input[name='q']", "Python")
            ...     session.click("input[name='btnK']")
            ...     results = session.extract(".result-title")
        """
        if self._browser is None:
            self._browser = BrowserService(self._transport)
        return self._browser

    @property
    def download(self) -> DownloadService:
        """
        Download service for remote file downloads.

        Downloads files from URLs on remote server and transfers
        to local machine using chunked transfer.

        Example:
            >>> result = client.download.url(
            ...     url="https://example.com/data.csv.gz",
            ...     local_path=Path("./data.csv.gz"),
            ... )
            >>> if result.success:
            ...     print(f"Downloaded {result.size} bytes")
        """
        if self._download is None:
            self._download = DownloadService(self._transport)
        return self._download

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._transport.is_connected

    @property
    def mode(self) -> str:
        """Get connection mode (remote/local)."""
        return self._transport.mode

    def close(self) -> None:
        """Close client and release resources."""
        self._transport.close()

    def __enter__(self) -> CMDOPClient:
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        return f"<CMDOPClient mode={self.mode} connected={self.is_connected}>"


class AsyncCMDOPClient:
    """
    Asynchronous CMDOP client.

    Async variant for use in async applications (FastAPI, aiohttp, etc.).

    Example:
        >>> async with AsyncCMDOPClient.remote(api_key="cmdop_live_xxx") as client:
        ...     session = await client.terminal.create()
        ...     await client.terminal.send_input(session.session_id, b"ls\\n")
        ...
        >>> # List available agents
        >>> agents = await AsyncCMDOPClient.list_agents(api_key="cmdop_live_xxx")
    """

    @staticmethod
    async def list_agents(api_key: str) -> list:
        """
        List agents available for API key.

        Static method - can be called without creating a client.

        Args:
            api_key: CMDOP API key.

        Returns:
            List of RemoteAgentInfo objects.

        Example:
            >>> agents = await AsyncCMDOPClient.list_agents("cmdop_live_xxx")
            >>> online = [a for a in agents if a.is_online]
            >>> print(f"Found {len(online)} online agents")
        """
        from cmdop.discovery import AgentDiscovery

        discovery = AgentDiscovery(api_key)
        return await discovery.list_agents()

    @staticmethod
    async def get_online_agents(api_key: str) -> list:
        """
        List only online agents.

        Args:
            api_key: CMDOP API key.

        Returns:
            List of online RemoteAgentInfo objects.
        """
        from cmdop.discovery import AgentDiscovery

        discovery = AgentDiscovery(api_key)
        return await discovery.get_online_agents()

    def __init__(self, transport: BaseTransport) -> None:
        """
        Initialize async client with transport.

        Args:
            transport: Configured transport instance
        """
        self._transport = transport
        self._terminal: AsyncTerminalService | None = None
        self._files: AsyncFilesService | None = None
        self._extract: AsyncExtractService | None = None
        self._agent: AsyncAgentService | None = None
        self._browser: AsyncBrowserService | None = None
        self._download: AsyncDownloadService | None = None

    @classmethod
    def remote(
        cls,
        api_key: str,
        server: str = "grpc.cmdop.com:443",
        agent_id: str | None = None,
        config: ConnectionConfig | None = None,
        insecure: bool = False,
    ) -> AsyncCMDOPClient:
        """
        Create async client connected via cloud relay.

        Args:
            api_key: CMDOP API key
            server: Cloud relay endpoint
            agent_id: Target agent UUID
            config: Connection configuration
            insecure: Use insecure connection (no TLS). For local dev only.

        Returns:
            Connected AsyncCMDOPClient instance
        """
        transport = RemoteTransport(
            api_key=api_key,
            server=server,
            agent_id=agent_id,
            config=config,
            insecure=insecure,
        )
        return cls(transport)

    @classmethod
    def local(
        cls,
        config: ConnectionConfig | None = None,
        discovery_paths: list[Path | str] | None = None,
        use_defaults: bool = True,
    ) -> AsyncCMDOPClient:
        """
        Create async client connected to local agent.

        Args:
            config: Connection configuration
            discovery_paths: Override default discovery paths
            use_defaults: Whether to include default discovery paths

        Returns:
            Connected AsyncCMDOPClient instance

        Raises:
            AgentNotRunningError: No local agent found
            StalePortFileError: Discovery file exists but agent dead
        """
        transport = LocalTransport.discover(
            config=config,
            custom_paths=discovery_paths,
            use_defaults=use_defaults,
        )
        return cls(transport)

    @classmethod
    def from_transport(cls, transport: BaseTransport) -> AsyncCMDOPClient:
        """Create async client from existing transport."""
        return cls(transport)

    @property
    def transport(self) -> BaseTransport:
        """Get underlying transport."""
        return self._transport

    @property
    def terminal(self) -> AsyncTerminalService:
        """Terminal service for async session management."""
        if self._terminal is None:
            self._terminal = AsyncTerminalService(self._transport)
        return self._terminal

    @property
    def files(self) -> AsyncFilesService:
        """Files service for async file operations."""
        if self._files is None:
            self._files = AsyncFilesService(self._transport)
        return self._files

    @property
    def extract(self) -> AsyncExtractService:
        """Extract service for async structured data extraction."""
        if self._extract is None:
            self._extract = AsyncExtractService(self._transport)
        return self._extract

    @property
    def agent(self) -> AsyncAgentService:
        """
        Agent service for async AI agent execution.

        Provides: run, run_stream (with streaming events)

        Example:
            >>> result = await client.agent.run("Deploy the app")
            >>> print(result.text)

            >>> async for event in client.agent.run_stream("Check logs"):
            ...     if event.type == AgentEventType.TOKEN:
            ...         print(event.payload_data.get("token", ""), end="")
        """
        if self._agent is None:
            self._agent = AsyncAgentService(self._transport)
        return self._agent

    @property
    def browser(self) -> AsyncBrowserService:
        """
        Async browser service (stub - not implemented).

        Use sync CMDOPClient.browser instead.
        """
        if self._browser is None:
            self._browser = AsyncBrowserService(self._transport)
        return self._browser

    @property
    def download(self) -> AsyncDownloadService:
        """
        Async download service for remote file downloads.

        Example:
            >>> result = await client.download.url(
            ...     url="https://example.com/data.csv.gz",
            ...     local_path=Path("./data.csv.gz"),
            ... )
        """
        if self._download is None:
            self._download = AsyncDownloadService(self._transport)
        return self._download

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._transport.is_connected

    @property
    def mode(self) -> str:
        """Get connection mode."""
        return self._transport.mode

    async def close(self) -> None:
        """Close client and release resources."""
        await self._transport.aclose()

    async def __aenter__(self) -> AsyncCMDOPClient:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()

    def __repr__(self) -> str:
        return f"<AsyncCMDOPClient mode={self.mode} connected={self.is_connected}>"

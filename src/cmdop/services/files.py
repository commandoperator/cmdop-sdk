"""
Files service for CMDOP SDK.

Provides file system operations: list, read, write, delete, copy, move.
Supports both sync and async patterns.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from cmdop.models.files import (
    FileEntry,
    FileInfo,
    FileType,
    ListDirectoryResponse,
)
from cmdop.models.terminal import SessionListItem
from cmdop.services.base import BaseService

if TYPE_CHECKING:
    from cmdop.transport.base import BaseTransport


def _parse_file_type(pb_type: int) -> FileType:
    """Convert protobuf file type to enum."""
    # Map based on proto enum values
    type_map = {
        0: FileType.UNKNOWN,
        1: FileType.FILE,
        2: FileType.DIRECTORY,
        3: FileType.SYMLINK,
    }
    return type_map.get(pb_type, FileType.UNKNOWN)


def _parse_timestamp(ts: Any) -> datetime | None:
    """Convert protobuf timestamp to datetime."""
    if ts is None:
        return None
    try:
        if hasattr(ts, "seconds"):
            return datetime.fromtimestamp(ts.seconds, tz=timezone.utc)
        return None
    except (ValueError, OSError):
        return None


class FilesService(BaseService):
    """
    Synchronous files service.

    Provides file system operations.

    Example:
        >>> # Using set_machine (recommended)
        >>> client.files.set_machine("my-server")
        >>> entries = client.files.list("/home/user")
        >>>
        >>> # Or with explicit session_id
        >>> session = client.terminal.get_active_session()
        >>> client.files.set_session_id(session.session_id)
        >>> entries = client.files.list("/home/user")
    """

    def __init__(self, transport: BaseTransport) -> None:
        super().__init__(transport)
        self._stub: Any = None
        self._session_id: str | None = None
        self._cached_hostname: str | None = None
        self._cached_session_info: SessionListItem | None = None

    def set_machine(self, hostname: str, partial_match: bool = True) -> SessionListItem:
        """
        Set target machine by hostname for file operations.

        Uses GetSessionByHostname RPC for efficient server-side resolution.
        Caches session_id for all subsequent file operations.

        Args:
            hostname: Machine hostname.
            partial_match: If True, allows partial hostname matching (default).
                          If False, requires exact hostname match.

        Returns:
            SessionListItem for the found session.

        Raises:
            CMDOPError: If no active session found, or hostname is ambiguous.

        Example:
            >>> client.files.set_machine("my-server")
            >>> files = client.files.list("/tmp")
        """
        from cmdop._generated.rpc_messages.session_pb2 import (
            GetSessionByHostnameRequest,
        )
        from cmdop.exceptions import CMDOPError

        request = GetSessionByHostnameRequest(
            hostname=hostname,
            partial_match=partial_match,
        )
        response = self._call_sync(self._get_stub.GetSessionByHostname, request)

        if not response.found:
            if response.ambiguous:
                raise CMDOPError(
                    f"Ambiguous hostname '{hostname}' matches {response.matches_count} machines. "
                    "Use a more specific hostname or set partial_match=False."
                )
            raise CMDOPError(response.error or f"No active session found for hostname: {hostname}")

        # Parse connected_at timestamp
        connected_at = None
        if response.connected_at and response.connected_at.seconds > 0:
            connected_at = datetime.fromtimestamp(
                response.connected_at.seconds, tz=timezone.utc
            )

        # Build SessionListItem
        session = SessionListItem(
            session_id=response.session_id,
            machine_hostname=response.machine_hostname,
            machine_name=response.machine_name,
            status=response.status,
            os=response.os,
            agent_version=response.agent_version,
            heartbeat_age_seconds=response.heartbeat_age_seconds,
            has_shell=response.has_shell,
            shell=response.shell,
            working_directory=response.working_directory,
            connected_at=connected_at,
        )

        # Cache session info
        self._cached_hostname = response.machine_hostname
        self._session_id = response.session_id
        self._cached_session_info = session
        return session

    def set_session_id(self, session_id: str) -> None:
        """
        Set session ID for file operations.

        Required for remote connections. For local IPC, session_id is optional.
        Prefer set_machine() for hostname-based targeting.

        Args:
            session_id: Session ID from terminal.get_active_session() or terminal.create()
        """
        self._session_id = session_id

    def clear_session(self) -> None:
        """Clear cached session and hostname."""
        self._session_id = None
        self._cached_hostname = None
        self._cached_session_info = None

    @property
    def current_session(self) -> SessionListItem | None:
        """Get currently cached session info."""
        return self._cached_session_info

    @property
    def current_hostname(self) -> str | None:
        """Get currently cached hostname."""
        return self._cached_hostname

    def _get_session_id(self, session_id: str | None = None) -> str:
        """Get session ID from parameter or stored value."""
        sid = session_id or self._session_id
        if not sid:
            # For local IPC, use empty string (server will handle)
            # For remote, this will likely fail but let server return proper error
            return ""
        return sid

    @property
    def _get_stub(self) -> Any:
        """Lazy-load gRPC stub."""
        if self._stub is None:
            from cmdop._generated.service_pb2_grpc import (
                TerminalStreamingServiceStub,
            )

            self._stub = TerminalStreamingServiceStub(self._channel)
        return self._stub

    def list(
        self,
        path: str,
        include_hidden: bool = False,
        page_size: int = 100,
        page_token: str | None = None,
        session_id: str | None = None,
    ) -> ListDirectoryResponse:
        """
        List directory contents.

        Args:
            path: Directory path to list
            include_hidden: Include hidden files
            page_size: Number of entries per page
            page_token: Pagination token
            session_id: Session ID (uses stored value if not provided)

        Returns:
            Directory listing response
        """
        from cmdop._generated.file_rpc.directory_pb2 import (
            FileListDirectoryRpcRequest,
        )

        request = FileListDirectoryRpcRequest(
            session_id=self._get_session_id(session_id),
            path=path,
            page_size=page_size,
            include_hidden=include_hidden,
        )
        if page_token:
            request.page_token = page_token

        response = self._call_sync(self._get_stub.FileListDirectory, request)

        entries = []
        for entry in response.result.entries:
            entries.append(
                FileEntry(
                    name=entry.name,
                    path=entry.path,
                    type=_parse_file_type(entry.type),
                    size=entry.size,
                    modified_at=_parse_timestamp(entry.modified_at),
                    is_hidden=entry.name.startswith("."),
                )
            )

        return ListDirectoryResponse(
            path=response.result.current_path,
            entries=entries,
            next_page_token=response.result.next_page_token or None,
            total_count=response.result.total_count,
        )

    def read(
        self,
        path: str,
        offset: int = 0,
        length: int = 0,
        session_id: str | None = None,
        timeout: float | None = None,
    ) -> bytes:
        """
        Read file contents.

        Args:
            path: File path to read
            offset: Byte offset to start reading from
            length: Number of bytes to read (0 = entire file)
            session_id: Session ID (uses stored value if not provided)
            timeout: Request timeout in seconds (default: 300s for large files)

        Returns:
            File contents as bytes
        """
        from cmdop._generated.file_rpc.file_crud_pb2 import FileReadRpcRequest

        request = FileReadRpcRequest(
            session_id=self._get_session_id(session_id),
            path=path,
            offset=offset,
            length=length,
        )
        # Use longer timeout for file reads (default 300s)
        response = self._call_sync(
            self._get_stub.FileRead,
            request,
            timeout=timeout or 300.0,
        )
        return response.result.content

    def write(
        self,
        path: str,
        content: bytes | str,
        create_parents: bool = False,
        overwrite: bool = True,
        session_id: str | None = None,
    ) -> None:
        """
        Write file contents.

        Args:
            path: File path to write
            content: Content to write (bytes or string)
            create_parents: Create parent directories
            overwrite: Overwrite existing file
            session_id: Session ID (uses stored value if not provided)
        """
        from cmdop._generated.file_rpc.file_crud_pb2 import FileWriteRpcRequest

        if isinstance(content, str):
            content = content.encode("utf-8")

        request = FileWriteRpcRequest(
            session_id=self._get_session_id(session_id),
            path=path,
            content=content,
            create_parents=create_parents,
        )

        self._call_sync(self._get_stub.FileWrite, request)

    def delete(
        self,
        path: str,
        recursive: bool = False,
        session_id: str | None = None,
    ) -> None:
        """
        Delete file or directory.

        Args:
            path: Path to delete
            recursive: Delete directory recursively
            session_id: Session ID (uses stored value if not provided)
        """
        from cmdop._generated.file_rpc.file_crud_pb2 import FileDeleteRpcRequest

        request = FileDeleteRpcRequest(
            session_id=self._get_session_id(session_id),
            path=path,
            recursive=recursive,
        )

        self._call_sync(self._get_stub.FileDelete, request)

    def copy(
        self,
        source: str,
        destination: str,
        session_id: str | None = None,
    ) -> None:
        """
        Copy file or directory.

        Args:
            source: Source path
            destination: Destination path
            session_id: Session ID (uses stored value if not provided)
        """
        from cmdop._generated.file_rpc.file_crud_pb2 import FileCopyRpcRequest

        request = FileCopyRpcRequest(
            session_id=self._get_session_id(session_id),
            source_path=source,
            destination_path=destination,
        )

        self._call_sync(self._get_stub.FileCopy, request)

    def move(
        self,
        source: str,
        destination: str,
        session_id: str | None = None,
    ) -> None:
        """
        Move/rename file or directory.

        Args:
            source: Source path
            destination: Destination path
            session_id: Session ID (uses stored value if not provided)
        """
        from cmdop._generated.file_rpc.file_crud_pb2 import FileMoveRpcRequest

        request = FileMoveRpcRequest(
            session_id=self._get_session_id(session_id),
            source_path=source,
            destination_path=destination,
        )

        self._call_sync(self._get_stub.FileMove, request)

    def info(self, path: str, session_id: str | None = None) -> FileInfo:
        """
        Get file information.

        Args:
            path: File path
            session_id: Session ID (uses stored value if not provided)

        Returns:
            Detailed file information
        """
        from cmdop._generated.file_rpc.file_crud_pb2 import FileGetInfoRpcRequest

        request = FileGetInfoRpcRequest(
            session_id=self._get_session_id(session_id),
            path=path,
        )
        response = self._call_sync(self._get_stub.FileGetInfo, request)

        entry = response.result.entry
        return FileInfo(
            path=entry.path,
            type=_parse_file_type(entry.type),
            size=entry.size,
            modified_at=_parse_timestamp(entry.modified_at),
            permissions=entry.permissions if hasattr(entry, "permissions") else None,
        )

    def mkdir(
        self,
        path: str,
        create_parents: bool = True,
        session_id: str | None = None,
    ) -> None:
        """
        Create directory.

        Args:
            path: Directory path to create
            create_parents: Create parent directories
            session_id: Session ID (uses stored value if not provided)
        """
        from cmdop._generated.file_rpc.file_crud_pb2 import (
            FileCreateDirectoryRpcRequest,
        )

        request = FileCreateDirectoryRpcRequest(
            session_id=self._get_session_id(session_id),
            path=path,
            create_parents=create_parents,
        )

        self._call_sync(self._get_stub.FileCreateDirectory, request)


class AsyncFilesService(BaseService):
    """
    Asynchronous files service.

    Provides async file system operations.

    Example:
        >>> # Using set_machine (recommended)
        >>> await client.files.set_machine("my-server")
        >>> entries = await client.files.list("/home/user")
        >>>
        >>> # Or with explicit session_id
        >>> session = await client.terminal.get_active_session()
        >>> client.files.set_session_id(session.session_id)
        >>> entries = await client.files.list("/home/user")
    """

    def __init__(self, transport: BaseTransport) -> None:
        super().__init__(transport)
        self._stub: Any = None
        self._session_id: str | None = None
        self._cached_hostname: str | None = None
        self._cached_session_info: SessionListItem | None = None

    async def set_machine(self, hostname: str, partial_match: bool = True) -> SessionListItem:
        """
        Set target machine by hostname for file operations.

        Uses GetSessionByHostname RPC for efficient server-side resolution.
        Caches session_id for all subsequent file operations.

        Args:
            hostname: Machine hostname.
            partial_match: If True, allows partial hostname matching (default).
                          If False, requires exact hostname match.

        Returns:
            SessionListItem for the found session.

        Raises:
            CMDOPError: If no active session found, or hostname is ambiguous.

        Example:
            >>> await client.files.set_machine("my-server")
            >>> files = await client.files.list("/tmp")
        """
        from cmdop._generated.rpc_messages.session_pb2 import (
            GetSessionByHostnameRequest,
        )
        from cmdop.exceptions import CMDOPError

        request = GetSessionByHostnameRequest(
            hostname=hostname,
            partial_match=partial_match,
        )
        response = await self._call_async(self._get_stub.GetSessionByHostname, request)

        if not response.found:
            if response.ambiguous:
                raise CMDOPError(
                    f"Ambiguous hostname '{hostname}' matches {response.matches_count} machines. "
                    "Use a more specific hostname or set partial_match=False."
                )
            raise CMDOPError(response.error or f"No active session found for hostname: {hostname}")

        # Parse connected_at timestamp
        connected_at = None
        if response.connected_at and response.connected_at.seconds > 0:
            connected_at = datetime.fromtimestamp(
                response.connected_at.seconds, tz=timezone.utc
            )

        # Build SessionListItem
        session = SessionListItem(
            session_id=response.session_id,
            machine_hostname=response.machine_hostname,
            machine_name=response.machine_name,
            status=response.status,
            os=response.os,
            agent_version=response.agent_version,
            heartbeat_age_seconds=response.heartbeat_age_seconds,
            has_shell=response.has_shell,
            shell=response.shell,
            working_directory=response.working_directory,
            connected_at=connected_at,
        )

        # Cache session info
        self._cached_hostname = response.machine_hostname
        self._session_id = response.session_id
        self._cached_session_info = session
        return session

    def set_session_id(self, session_id: str) -> None:
        """
        Set session ID for file operations.

        Required for remote connections. For local IPC, session_id is optional.
        Prefer set_machine() for hostname-based targeting.

        Args:
            session_id: Session ID from terminal.get_active_session() or terminal.create()
        """
        self._session_id = session_id

    def clear_session(self) -> None:
        """Clear cached session and hostname."""
        self._session_id = None
        self._cached_hostname = None
        self._cached_session_info = None

    @property
    def current_session(self) -> SessionListItem | None:
        """Get currently cached session info."""
        return self._cached_session_info

    @property
    def current_hostname(self) -> str | None:
        """Get currently cached hostname."""
        return self._cached_hostname

    def _get_session_id(self, session_id: str | None = None) -> str:
        """Get session ID from parameter or stored value."""
        sid = session_id or self._session_id
        if not sid:
            return ""
        return sid

    @property
    def _get_stub(self) -> Any:
        """Lazy-load async gRPC stub."""
        if self._stub is None:
            from cmdop._generated.service_pb2_grpc import (
                TerminalStreamingServiceStub,
            )

            self._stub = TerminalStreamingServiceStub(self._async_channel)
        return self._stub

    async def list(
        self,
        path: str,
        include_hidden: bool = False,
        page_size: int = 100,
        page_token: str | None = None,
        session_id: str | None = None,
    ) -> ListDirectoryResponse:
        """List directory contents."""
        from cmdop._generated.file_rpc.directory_pb2 import (
            FileListDirectoryRpcRequest,
        )

        request = FileListDirectoryRpcRequest(
            session_id=self._get_session_id(session_id),
            path=path,
            page_size=page_size,
            include_hidden=include_hidden,
        )
        if page_token:
            request.page_token = page_token

        response = await self._call_async(self._get_stub.FileListDirectory, request)

        entries = []
        for entry in response.result.entries:
            entries.append(
                FileEntry(
                    name=entry.name,
                    path=entry.path,
                    type=_parse_file_type(entry.type),
                    size=entry.size,
                    modified_at=_parse_timestamp(entry.modified_at),
                    is_hidden=entry.name.startswith("."),
                )
            )

        return ListDirectoryResponse(
            path=response.result.current_path,
            entries=entries,
            next_page_token=response.result.next_page_token or None,
            total_count=response.result.total_count,
        )

    async def read(
        self,
        path: str,
        offset: int = 0,
        length: int = 0,
        session_id: str | None = None,
        timeout: float | None = None,
    ) -> bytes:
        """
        Read file contents.

        Args:
            path: File path to read
            offset: Byte offset to start reading from
            length: Number of bytes to read (0 = entire file)
            session_id: Session ID (uses stored value if not provided)
            timeout: Request timeout in seconds (default: 300s for large files)

        Returns:
            File contents as bytes
        """
        from cmdop._generated.file_rpc.file_crud_pb2 import FileReadRpcRequest

        request = FileReadRpcRequest(
            session_id=self._get_session_id(session_id),
            path=path,
            offset=offset,
            length=length,
        )
        # Use longer timeout for file reads (default 300s)
        response = await self._call_async(
            self._get_stub.FileRead,
            request,
            timeout=timeout or 300.0,
        )
        return response.result.content

    async def write(
        self,
        path: str,
        content: bytes | str,
        create_parents: bool = False,
        overwrite: bool = True,
        session_id: str | None = None,
    ) -> None:
        """Write file contents."""
        from cmdop._generated.file_rpc.file_crud_pb2 import FileWriteRpcRequest

        if isinstance(content, str):
            content = content.encode("utf-8")

        request = FileWriteRpcRequest(
            session_id=self._get_session_id(session_id),
            path=path,
            content=content,
            create_parents=create_parents,
        )
        await self._call_async(self._get_stub.FileWrite, request)

    async def delete(
        self,
        path: str,
        recursive: bool = False,
        session_id: str | None = None,
    ) -> None:
        """Delete file or directory."""
        from cmdop._generated.file_rpc.file_crud_pb2 import FileDeleteRpcRequest

        request = FileDeleteRpcRequest(
            session_id=self._get_session_id(session_id),
            path=path,
            recursive=recursive,
        )
        await self._call_async(self._get_stub.FileDelete, request)

    async def copy(
        self,
        source: str,
        destination: str,
        session_id: str | None = None,
    ) -> None:
        """Copy file or directory."""
        from cmdop._generated.file_rpc.file_crud_pb2 import FileCopyRpcRequest

        request = FileCopyRpcRequest(
            session_id=self._get_session_id(session_id),
            source_path=source,
            destination_path=destination,
        )
        await self._call_async(self._get_stub.FileCopy, request)

    async def move(
        self,
        source: str,
        destination: str,
        session_id: str | None = None,
    ) -> None:
        """Move/rename file or directory."""
        from cmdop._generated.file_rpc.file_crud_pb2 import FileMoveRpcRequest

        request = FileMoveRpcRequest(
            session_id=self._get_session_id(session_id),
            source_path=source,
            destination_path=destination,
        )
        await self._call_async(self._get_stub.FileMove, request)

    async def info(self, path: str, session_id: str | None = None) -> FileInfo:
        """Get file information."""
        from cmdop._generated.file_rpc.file_crud_pb2 import FileGetInfoRpcRequest

        request = FileGetInfoRpcRequest(
            session_id=self._get_session_id(session_id),
            path=path,
        )
        response = await self._call_async(self._get_stub.FileGetInfo, request)

        entry = response.result.entry
        return FileInfo(
            path=entry.path,
            type=_parse_file_type(entry.type),
            size=entry.size,
            modified_at=_parse_timestamp(entry.modified_at),
        )

    async def mkdir(
        self,
        path: str,
        create_parents: bool = True,
        session_id: str | None = None,
    ) -> None:
        """Create directory."""
        from cmdop._generated.file_rpc.file_crud_pb2 import (
            FileCreateDirectoryRpcRequest,
        )

        request = FileCreateDirectoryRpcRequest(
            session_id=self._get_session_id(session_id),
            path=path,
            create_parents=create_parents,
        )
        await self._call_async(self._get_stub.FileCreateDirectory, request)

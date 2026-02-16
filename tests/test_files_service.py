"""
Tests for CMDOP SDK Files service.

Tests verify the service layer logic by mocking the underlying gRPC calls.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from cmdop.models.files import (
    FileEntry,
    FileInfo,
    FileType,
    ListDirectoryResponse,
)
from cmdop.services.files import (
    FilesService,
    AsyncFilesService,
    _parse_file_type,
    _parse_timestamp,
)


class MockChannel:
    """Mock gRPC channel for testing."""
    pass


class MockTransport:
    """Mock transport for testing services."""

    def __init__(self):
        self._channel = MockChannel()
        self._config = MagicMock()
        self._config.request_timeout_seconds = 30.0
        self._mode = "test"

    @property
    def channel(self):
        return self._channel

    @property
    def async_channel(self):
        return self._channel

    @property
    def metadata(self):
        return [("authorization", "Bearer test_token")]

    @property
    def config(self):
        return self._config

    @property
    def mode(self):
        return self._mode


class TestParseFileType:
    """Test _parse_file_type helper function."""

    def test_parse_unknown(self):
        """Test parsing unknown file type."""
        assert _parse_file_type(0) == FileType.UNKNOWN

    def test_parse_file(self):
        """Test parsing file type."""
        assert _parse_file_type(1) == FileType.FILE

    def test_parse_directory(self):
        """Test parsing directory type."""
        assert _parse_file_type(2) == FileType.DIRECTORY

    def test_parse_symlink(self):
        """Test parsing symlink type."""
        assert _parse_file_type(3) == FileType.SYMLINK

    def test_parse_invalid(self):
        """Test parsing invalid type returns unknown."""
        assert _parse_file_type(999) == FileType.UNKNOWN
        assert _parse_file_type(-1) == FileType.UNKNOWN


class TestParseTimestamp:
    """Test _parse_timestamp helper function."""

    def test_parse_valid_timestamp(self):
        """Test parsing valid protobuf timestamp."""
        mock_ts = MagicMock()
        mock_ts.seconds = 1704067200  # 2024-01-01 00:00:00 UTC

        result = _parse_timestamp(mock_ts)

        assert result is not None
        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc

    def test_parse_none_timestamp(self):
        """Test parsing None returns None."""
        result = _parse_timestamp(None)
        assert result is None

    def test_parse_no_seconds_attribute(self):
        """Test parsing object without seconds attribute."""
        mock_ts = MagicMock(spec=[])
        del mock_ts.seconds

        result = _parse_timestamp(mock_ts)
        assert result is None


class TestFilesServiceCreation:
    """Test FilesService initialization."""

    def test_service_creation(self):
        """Test service can be created with transport."""
        transport = MockTransport()
        service = FilesService(transport)
        assert service._transport == transport
        assert service._stub is None

    def test_transport_property(self):
        """Test transport property access."""
        transport = MockTransport()
        service = FilesService(transport)
        assert service.transport == transport


class TestFilesServiceList:
    """Test FilesService.list method."""

    def test_list_directory_basic(self):
        """Test listing directory with basic response."""
        transport = MockTransport()
        service = FilesService(transport)

        # Create mock response
        mock_entry1 = MagicMock()
        mock_entry1.name = "file1.txt"
        mock_entry1.path = "/home/user/file1.txt"
        mock_entry1.type = 1  # FILE
        mock_entry1.size = 1024
        mock_entry1.modified_at = MagicMock(seconds=1704067200)

        mock_entry2 = MagicMock()
        mock_entry2.name = "subdir"
        mock_entry2.path = "/home/user/subdir"
        mock_entry2.type = 2  # DIRECTORY
        mock_entry2.size = 4096
        mock_entry2.modified_at = MagicMock(seconds=1704067200)

        mock_result = MagicMock()
        mock_result.current_path = "/home/user"
        mock_result.entries = [mock_entry1, mock_entry2]
        mock_result.next_page_token = ""
        mock_result.total_count = 2

        mock_response = MagicMock()
        mock_response.result = mock_result

        mock_stub = MagicMock()
        mock_stub.FileListDirectory = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.directory_pb2.FileListDirectoryRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            result = service.list("/home/user")

        assert isinstance(result, ListDirectoryResponse)
        assert result.path == "/home/user"
        assert len(result.entries) == 2
        assert result.entries[0].name == "file1.txt"
        assert result.entries[0].type == FileType.FILE
        assert result.entries[1].name == "subdir"
        assert result.entries[1].type == FileType.DIRECTORY
        assert result.total_count == 2

    def test_list_directory_hidden_files(self):
        """Test listing with hidden files detection."""
        transport = MockTransport()
        service = FilesService(transport)

        mock_entry = MagicMock()
        mock_entry.name = ".hidden_file"
        mock_entry.path = "/home/user/.hidden_file"
        mock_entry.type = 1
        mock_entry.size = 100
        mock_entry.modified_at = None

        mock_result = MagicMock()
        mock_result.current_path = "/home/user"
        mock_result.entries = [mock_entry]
        mock_result.next_page_token = ""
        mock_result.total_count = 1

        mock_response = MagicMock()
        mock_response.result = mock_result

        mock_stub = MagicMock()
        mock_stub.FileListDirectory = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.directory_pb2.FileListDirectoryRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            result = service.list("/home/user", include_hidden=True)

        assert result.entries[0].is_hidden is True

    def test_list_directory_pagination(self):
        """Test listing with pagination."""
        transport = MockTransport()
        service = FilesService(transport)

        mock_result = MagicMock()
        mock_result.current_path = "/home/user"
        mock_result.entries = []
        mock_result.next_page_token = "next_page_token_123"
        mock_result.total_count = 200

        mock_response = MagicMock()
        mock_response.result = mock_result

        mock_stub = MagicMock()
        mock_stub.FileListDirectory = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.directory_pb2.FileListDirectoryRpcRequest") as MockRequest:
            mock_request_instance = MagicMock()
            MockRequest.return_value = mock_request_instance
            result = service.list("/home/user", page_size=50, page_token="prev_token")

        assert result.next_page_token == "next_page_token_123"


class TestFilesServiceRead:
    """Test FilesService.read method."""

    def test_read_file(self):
        """Test reading file contents."""
        transport = MockTransport()
        service = FilesService(transport)

        mock_result = MagicMock()
        mock_result.content = b"file content here\n"

        mock_response = MagicMock()
        mock_response.result = mock_result

        mock_stub = MagicMock()
        mock_stub.FileRead = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.file_crud_pb2.FileReadRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            result = service.read("/path/to/file.txt")
            MockRequest.assert_called_once_with(
                session_id="", path="/path/to/file.txt", offset=0, length=0
            )

        assert result == b"file content here\n"

    def test_read_file_binary(self):
        """Test reading binary file."""
        transport = MockTransport()
        service = FilesService(transport)

        binary_content = bytes([0x00, 0x01, 0x02, 0xFF, 0xFE])

        mock_result = MagicMock()
        mock_result.content = binary_content

        mock_response = MagicMock()
        mock_response.result = mock_result

        mock_stub = MagicMock()
        mock_stub.FileRead = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.file_crud_pb2.FileReadRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            result = service.read("/path/to/binary.bin")

        assert result == binary_content


class TestFilesServiceWrite:
    """Test FilesService.write method."""

    def test_write_file_bytes(self):
        """Test writing bytes to file."""
        transport = MockTransport()
        service = FilesService(transport)

        mock_stub = MagicMock()
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.file_crud_pb2.FileWriteRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            service.write("/path/to/file.txt", b"content bytes")
            MockRequest.assert_called_once_with(
                session_id="",
                path="/path/to/file.txt",
                content=b"content bytes",
                create_parents=False,
            )

    def test_write_file_string(self):
        """Test writing string to file (auto-encoded)."""
        transport = MockTransport()
        service = FilesService(transport)

        mock_stub = MagicMock()
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.file_crud_pb2.FileWriteRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            service.write("/path/to/file.txt", "string content")
            MockRequest.assert_called_once_with(
                session_id="",
                path="/path/to/file.txt",
                content=b"string content",
                create_parents=False,
            )

    def test_write_file_create_parents(self):
        """Test writing with create_parents flag."""
        transport = MockTransport()
        service = FilesService(transport)

        mock_stub = MagicMock()
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.file_crud_pb2.FileWriteRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            service.write("/new/path/file.txt", b"content", create_parents=True)
            MockRequest.assert_called_once_with(
                session_id="",
                path="/new/path/file.txt",
                content=b"content",
                create_parents=True,
            )


class TestFilesServiceDelete:
    """Test FilesService.delete method."""

    def test_delete_file(self):
        """Test deleting a file."""
        transport = MockTransport()
        service = FilesService(transport)

        mock_stub = MagicMock()
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.file_crud_pb2.FileDeleteRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            service.delete("/path/to/file.txt")
            MockRequest.assert_called_once_with(
                session_id="",
                path="/path/to/file.txt",
                recursive=False,
            )

    def test_delete_directory_recursive(self):
        """Test deleting directory recursively."""
        transport = MockTransport()
        service = FilesService(transport)

        mock_stub = MagicMock()
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.file_crud_pb2.FileDeleteRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            service.delete("/path/to/dir", recursive=True)
            MockRequest.assert_called_once_with(
                session_id="",
                path="/path/to/dir",
                recursive=True,
            )


class TestFilesServiceCopy:
    """Test FilesService.copy method."""

    def test_copy_file(self):
        """Test copying a file."""
        transport = MockTransport()
        service = FilesService(transport)

        mock_stub = MagicMock()
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.file_crud_pb2.FileCopyRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            service.copy("/source/file.txt", "/dest/file.txt")
            MockRequest.assert_called_once_with(
                session_id="",
                source_path="/source/file.txt",
                destination_path="/dest/file.txt",
            )


class TestFilesServiceMove:
    """Test FilesService.move method."""

    def test_move_file(self):
        """Test moving a file."""
        transport = MockTransport()
        service = FilesService(transport)

        mock_stub = MagicMock()
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.file_crud_pb2.FileMoveRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            service.move("/old/path/file.txt", "/new/path/file.txt")
            MockRequest.assert_called_once_with(
                session_id="",
                source_path="/old/path/file.txt",
                destination_path="/new/path/file.txt",
            )


class TestFilesServiceInfo:
    """Test FilesService.info method."""

    def test_get_file_info(self):
        """Test getting file information."""
        transport = MockTransport()
        service = FilesService(transport)

        mock_entry = MagicMock()
        mock_entry.path = "/path/to/file.txt"
        mock_entry.type = 1  # FILE
        mock_entry.size = 2048
        mock_entry.modified_at = MagicMock(seconds=1704067200)
        mock_entry.permissions = "rw-r--r--"

        mock_result = MagicMock()
        mock_result.entry = mock_entry

        mock_response = MagicMock()
        mock_response.result = mock_result

        mock_stub = MagicMock()
        mock_stub.FileGetInfo = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.file_crud_pb2.FileGetInfoRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            result = service.info("/path/to/file.txt")
            MockRequest.assert_called_once_with(session_id="", path="/path/to/file.txt")

        assert isinstance(result, FileInfo)
        assert result.path == "/path/to/file.txt"
        assert result.type == FileType.FILE
        assert result.size == 2048


class TestFilesServiceMkdir:
    """Test FilesService.mkdir method."""

    def test_mkdir_default(self):
        """Test creating directory with defaults."""
        transport = MockTransport()
        service = FilesService(transport)

        mock_stub = MagicMock()
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.file_crud_pb2.FileCreateDirectoryRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            service.mkdir("/new/directory")
            MockRequest.assert_called_once_with(
                session_id="",
                path="/new/directory",
                create_parents=True,
            )

    def test_mkdir_no_parents(self):
        """Test creating directory without parents."""
        transport = MockTransport()
        service = FilesService(transport)

        mock_stub = MagicMock()
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.file_crud_pb2.FileCreateDirectoryRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            service.mkdir("/existing/new_dir", create_parents=False)
            MockRequest.assert_called_once_with(
                session_id="",
                path="/existing/new_dir",
                create_parents=False,
            )


class TestAsyncFilesService:
    """Test AsyncFilesService class."""

    def test_async_service_creation(self):
        """Test async service can be created."""
        transport = MockTransport()
        service = AsyncFilesService(transport)
        assert service._transport == transport
        assert service._stub is None

    @pytest.mark.asyncio
    async def test_async_list(self):
        """Test async list directory."""
        transport = MockTransport()
        service = AsyncFilesService(transport)

        mock_result = MagicMock()
        mock_result.current_path = "/home/user"
        mock_result.entries = []
        mock_result.next_page_token = ""
        mock_result.total_count = 0

        mock_response = MagicMock()
        mock_response.result = mock_result

        async def mock_file_list_directory(*args, **kwargs):
            return mock_response

        mock_stub = MagicMock()
        mock_stub.FileListDirectory = mock_file_list_directory
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.directory_pb2.FileListDirectoryRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            result = await service.list("/home/user")

        assert isinstance(result, ListDirectoryResponse)
        assert result.path == "/home/user"

    @pytest.mark.asyncio
    async def test_async_read(self):
        """Test async read file."""
        transport = MockTransport()
        service = AsyncFilesService(transport)

        mock_result = MagicMock()
        mock_result.content = b"async content"

        mock_response = MagicMock()
        mock_response.result = mock_result

        async def mock_file_read(*args, **kwargs):
            return mock_response

        mock_stub = MagicMock()
        mock_stub.FileRead = mock_file_read
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.file_crud_pb2.FileReadRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            result = await service.read("/file.txt")

        assert result == b"async content"

    @pytest.mark.asyncio
    async def test_async_write(self):
        """Test async write file."""
        transport = MockTransport()
        service = AsyncFilesService(transport)

        async def mock_file_write(*args, **kwargs):
            return MagicMock()

        mock_stub = MagicMock()
        mock_stub.FileWrite = mock_file_write
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.file_crud_pb2.FileWriteRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            await service.write("/file.txt", "content")
            MockRequest.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_delete(self):
        """Test async delete."""
        transport = MockTransport()
        service = AsyncFilesService(transport)

        async def mock_file_delete(*args, **kwargs):
            return MagicMock()

        mock_stub = MagicMock()
        mock_stub.FileDelete = mock_file_delete
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.file_crud_pb2.FileDeleteRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            await service.delete("/file.txt")
            MockRequest.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_copy(self):
        """Test async copy."""
        transport = MockTransport()
        service = AsyncFilesService(transport)

        async def mock_file_copy(*args, **kwargs):
            return MagicMock()

        mock_stub = MagicMock()
        mock_stub.FileCopy = mock_file_copy
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.file_crud_pb2.FileCopyRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            await service.copy("/src", "/dst")
            MockRequest.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_move(self):
        """Test async move."""
        transport = MockTransport()
        service = AsyncFilesService(transport)

        async def mock_file_move(*args, **kwargs):
            return MagicMock()

        mock_stub = MagicMock()
        mock_stub.FileMove = mock_file_move
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.file_crud_pb2.FileMoveRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            await service.move("/old", "/new")
            MockRequest.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_info(self):
        """Test async info."""
        transport = MockTransport()
        service = AsyncFilesService(transport)

        mock_entry = MagicMock()
        mock_entry.path = "/file.txt"
        mock_entry.type = 1
        mock_entry.size = 100
        mock_entry.modified_at = None

        mock_result = MagicMock()
        mock_result.entry = mock_entry

        mock_response = MagicMock()
        mock_response.result = mock_result

        async def mock_file_get_info(*args, **kwargs):
            return mock_response

        mock_stub = MagicMock()
        mock_stub.FileGetInfo = mock_file_get_info
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.file_crud_pb2.FileGetInfoRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            result = await service.info("/file.txt")

        assert isinstance(result, FileInfo)

    @pytest.mark.asyncio
    async def test_async_mkdir(self):
        """Test async mkdir."""
        transport = MockTransport()
        service = AsyncFilesService(transport)

        async def mock_file_create_directory(*args, **kwargs):
            return MagicMock()

        mock_stub = MagicMock()
        mock_stub.FileCreateDirectory = mock_file_create_directory
        service._stub = mock_stub

        with patch("cmdop._generated.file_rpc.file_crud_pb2.FileCreateDirectoryRpcRequest") as MockRequest:
            MockRequest.return_value = MagicMock()
            await service.mkdir("/new/dir")
            MockRequest.assert_called_once()

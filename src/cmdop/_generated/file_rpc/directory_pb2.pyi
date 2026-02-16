import file_operations_pb2 as _file_operations_pb2
from file_operations import common_pb2 as _common_pb2
from file_operations import directory_pb2 as _directory_pb2
from file_operations import file_crud_pb2 as _file_crud_pb2
from file_operations import archive_pb2 as _archive_pb2
from file_operations import search_pb2 as _search_pb2
from file_operations import transfer_pb2 as _transfer_pb2
from file_operations import hls_pb2 as _hls_pb2
from file_operations import changes_pb2 as _changes_pb2
from file_operations import requests_pb2 as _requests_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FileListDirectoryRpcRequest(_message.Message):
    __slots__ = ("session_id", "path", "include_hidden", "page_size", "page_token")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_HIDDEN_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    path: str
    include_hidden: bool
    page_size: int
    page_token: str
    def __init__(self, session_id: _Optional[str] = ..., path: _Optional[str] = ..., include_hidden: bool = ..., page_size: _Optional[int] = ..., page_token: _Optional[str] = ...) -> None: ...

class FileListDirectoryRpcResponse(_message.Message):
    __slots__ = ("success", "error", "result")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    result: _directory_pb2.FileListDirectoryResult
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., result: _Optional[_Union[_directory_pb2.FileListDirectoryResult, _Mapping]] = ...) -> None: ...

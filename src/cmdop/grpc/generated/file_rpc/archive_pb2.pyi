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
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FileCreateArchiveRpcRequest(_message.Message):
    __slots__ = ("session_id", "source_paths", "destination_path", "format", "include_hidden")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_PATHS_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_PATH_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_HIDDEN_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    source_paths: _containers.RepeatedScalarFieldContainer[str]
    destination_path: str
    format: str
    include_hidden: bool
    def __init__(self, session_id: _Optional[str] = ..., source_paths: _Optional[_Iterable[str]] = ..., destination_path: _Optional[str] = ..., format: _Optional[str] = ..., include_hidden: bool = ...) -> None: ...

class FileCreateArchiveRpcResponse(_message.Message):
    __slots__ = ("success", "error", "result")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    result: _archive_pb2.FileCreateArchiveResult
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., result: _Optional[_Union[_archive_pb2.FileCreateArchiveResult, _Mapping]] = ...) -> None: ...

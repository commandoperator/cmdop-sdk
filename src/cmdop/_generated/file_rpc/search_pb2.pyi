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

class FileSearchRpcRequest(_message.Message):
    __slots__ = ("session_id", "path", "filename_pattern", "content_pattern", "case_sensitive", "include_hidden", "max_results", "max_depth", "context_lines")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    FILENAME_PATTERN_FIELD_NUMBER: _ClassVar[int]
    CONTENT_PATTERN_FIELD_NUMBER: _ClassVar[int]
    CASE_SENSITIVE_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_HIDDEN_FIELD_NUMBER: _ClassVar[int]
    MAX_RESULTS_FIELD_NUMBER: _ClassVar[int]
    MAX_DEPTH_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_LINES_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    path: str
    filename_pattern: str
    content_pattern: str
    case_sensitive: bool
    include_hidden: bool
    max_results: int
    max_depth: int
    context_lines: int
    def __init__(self, session_id: _Optional[str] = ..., path: _Optional[str] = ..., filename_pattern: _Optional[str] = ..., content_pattern: _Optional[str] = ..., case_sensitive: bool = ..., include_hidden: bool = ..., max_results: _Optional[int] = ..., max_depth: _Optional[int] = ..., context_lines: _Optional[int] = ...) -> None: ...

class FileSearchRpcResponse(_message.Message):
    __slots__ = ("success", "error", "result")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    result: _search_pb2.FileSearchResult
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., result: _Optional[_Union[_search_pb2.FileSearchResult, _Mapping]] = ...) -> None: ...

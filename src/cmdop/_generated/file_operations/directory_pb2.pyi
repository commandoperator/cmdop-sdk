from file_operations import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FileListDirectoryRequest(_message.Message):
    __slots__ = ("path", "page_size", "page_token", "include_hidden", "visibility_mode")
    PATH_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_HIDDEN_FIELD_NUMBER: _ClassVar[int]
    VISIBILITY_MODE_FIELD_NUMBER: _ClassVar[int]
    path: str
    page_size: int
    page_token: str
    include_hidden: bool
    visibility_mode: _common_pb2.FileVisibilityMode
    def __init__(self, path: _Optional[str] = ..., page_size: _Optional[int] = ..., page_token: _Optional[str] = ..., include_hidden: bool = ..., visibility_mode: _Optional[_Union[_common_pb2.FileVisibilityMode, str]] = ...) -> None: ...

class FileListDirectoryResult(_message.Message):
    __slots__ = ("current_path", "entries", "next_page_token", "total_count", "has_more")
    CURRENT_PATH_FIELD_NUMBER: _ClassVar[int]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    HAS_MORE_FIELD_NUMBER: _ClassVar[int]
    current_path: str
    entries: _containers.RepeatedCompositeFieldContainer[_common_pb2.StreamFileEntry]
    next_page_token: str
    total_count: int
    has_more: bool
    def __init__(self, current_path: _Optional[str] = ..., entries: _Optional[_Iterable[_Union[_common_pb2.StreamFileEntry, _Mapping]]] = ..., next_page_token: _Optional[str] = ..., total_count: _Optional[int] = ..., has_more: bool = ...) -> None: ...

class FileCreateDirectoryRequest(_message.Message):
    __slots__ = ("path", "create_parents")
    PATH_FIELD_NUMBER: _ClassVar[int]
    CREATE_PARENTS_FIELD_NUMBER: _ClassVar[int]
    path: str
    create_parents: bool
    def __init__(self, path: _Optional[str] = ..., create_parents: bool = ...) -> None: ...

class FileCreateDirectoryResult(_message.Message):
    __slots__ = ("entry",)
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    entry: _common_pb2.StreamFileEntry
    def __init__(self, entry: _Optional[_Union[_common_pb2.StreamFileEntry, _Mapping]] = ...) -> None: ...

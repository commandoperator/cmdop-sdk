from file_operations import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FileCreateArchiveRequest(_message.Message):
    __slots__ = ("source_paths", "destination_path", "format", "include_hidden", "visibility_mode")
    SOURCE_PATHS_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_PATH_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_HIDDEN_FIELD_NUMBER: _ClassVar[int]
    VISIBILITY_MODE_FIELD_NUMBER: _ClassVar[int]
    source_paths: _containers.RepeatedScalarFieldContainer[str]
    destination_path: str
    format: str
    include_hidden: bool
    visibility_mode: _common_pb2.FileVisibilityMode
    def __init__(self, source_paths: _Optional[_Iterable[str]] = ..., destination_path: _Optional[str] = ..., format: _Optional[str] = ..., include_hidden: bool = ..., visibility_mode: _Optional[_Union[_common_pb2.FileVisibilityMode, str]] = ...) -> None: ...

class FileCreateArchiveResult(_message.Message):
    __slots__ = ("entry", "bytes_archived", "files_archived", "dirs_archived")
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    BYTES_ARCHIVED_FIELD_NUMBER: _ClassVar[int]
    FILES_ARCHIVED_FIELD_NUMBER: _ClassVar[int]
    DIRS_ARCHIVED_FIELD_NUMBER: _ClassVar[int]
    entry: _common_pb2.StreamFileEntry
    bytes_archived: int
    files_archived: int
    dirs_archived: int
    def __init__(self, entry: _Optional[_Union[_common_pb2.StreamFileEntry, _Mapping]] = ..., bytes_archived: _Optional[int] = ..., files_archived: _Optional[int] = ..., dirs_archived: _Optional[int] = ...) -> None: ...

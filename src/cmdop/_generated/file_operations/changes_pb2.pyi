from google.protobuf import timestamp_pb2 as _timestamp_pb2
from file_operations import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FileChangeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FILE_CHANGE_UNSPECIFIED: _ClassVar[FileChangeType]
    FILE_CHANGE_CREATE: _ClassVar[FileChangeType]
    FILE_CHANGE_MODIFY: _ClassVar[FileChangeType]
    FILE_CHANGE_DELETE: _ClassVar[FileChangeType]
    FILE_CHANGE_MOVE: _ClassVar[FileChangeType]
FILE_CHANGE_UNSPECIFIED: FileChangeType
FILE_CHANGE_CREATE: FileChangeType
FILE_CHANGE_MODIFY: FileChangeType
FILE_CHANGE_DELETE: FileChangeType
FILE_CHANGE_MOVE: FileChangeType

class FileChange(_message.Message):
    __slots__ = ("change_type", "item", "old_path")
    CHANGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    ITEM_FIELD_NUMBER: _ClassVar[int]
    OLD_PATH_FIELD_NUMBER: _ClassVar[int]
    change_type: FileChangeType
    item: _common_pb2.StreamFileEntry
    old_path: str
    def __init__(self, change_type: _Optional[_Union[FileChangeType, str]] = ..., item: _Optional[_Union[_common_pb2.StreamFileEntry, _Mapping]] = ..., old_path: _Optional[str] = ...) -> None: ...

class FileGetChangesRequest(_message.Message):
    __slots__ = ("since_sequence", "path", "limit", "cursor")
    SINCE_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    since_sequence: int
    path: str
    limit: int
    cursor: str
    def __init__(self, since_sequence: _Optional[int] = ..., path: _Optional[str] = ..., limit: _Optional[int] = ..., cursor: _Optional[str] = ...) -> None: ...

class FileGetChangesResult(_message.Message):
    __slots__ = ("changes", "current_sequence", "server_timestamp", "has_more", "next_cursor", "state_digest")
    CHANGES_FIELD_NUMBER: _ClassVar[int]
    CURRENT_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    SERVER_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    HAS_MORE_FIELD_NUMBER: _ClassVar[int]
    NEXT_CURSOR_FIELD_NUMBER: _ClassVar[int]
    STATE_DIGEST_FIELD_NUMBER: _ClassVar[int]
    changes: _containers.RepeatedCompositeFieldContainer[FileChange]
    current_sequence: int
    server_timestamp: float
    has_more: bool
    next_cursor: str
    state_digest: str
    def __init__(self, changes: _Optional[_Iterable[_Union[FileChange, _Mapping]]] = ..., current_sequence: _Optional[int] = ..., server_timestamp: _Optional[float] = ..., has_more: bool = ..., next_cursor: _Optional[str] = ..., state_digest: _Optional[str] = ...) -> None: ...

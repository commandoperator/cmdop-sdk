from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GetHistoryRequest(_message.Message):
    __slots__ = ("session_id", "limit", "offset")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    limit: int
    offset: int
    def __init__(self, session_id: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class GetHistoryResponse(_message.Message):
    __slots__ = ("commands", "total")
    COMMANDS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    commands: _containers.RepeatedScalarFieldContainer[str]
    total: int
    def __init__(self, commands: _Optional[_Iterable[str]] = ..., total: _Optional[int] = ...) -> None: ...

class GetOutputRequest(_message.Message):
    __slots__ = ("session_id", "offset", "limit")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    offset: int
    limit: int
    def __init__(self, session_id: _Optional[str] = ..., offset: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class GetOutputResponse(_message.Message):
    __slots__ = ("data", "total_bytes", "has_more")
    DATA_FIELD_NUMBER: _ClassVar[int]
    TOTAL_BYTES_FIELD_NUMBER: _ClassVar[int]
    HAS_MORE_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    total_bytes: int
    has_more: bool
    def __init__(self, data: _Optional[bytes] = ..., total_bytes: _Optional[int] = ..., has_more: bool = ...) -> None: ...

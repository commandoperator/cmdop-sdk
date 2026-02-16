from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class HlsGetPlaylistRpcRequest(_message.Message):
    __slots__ = ("session_id", "path", "quality", "start_time")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    path: str
    quality: str
    start_time: float
    def __init__(self, session_id: _Optional[str] = ..., path: _Optional[str] = ..., quality: _Optional[str] = ..., start_time: _Optional[float] = ...) -> None: ...

class HlsGetPlaylistRpcResponse(_message.Message):
    __slots__ = ("success", "error", "content", "content_type", "duration", "segment_duration")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    SEGMENT_DURATION_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    content: bytes
    content_type: str
    duration: float
    segment_duration: int
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., content: _Optional[bytes] = ..., content_type: _Optional[str] = ..., duration: _Optional[float] = ..., segment_duration: _Optional[int] = ...) -> None: ...

class HlsGetSegmentRpcRequest(_message.Message):
    __slots__ = ("session_id", "path", "quality", "segment_num", "start_time")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FIELD_NUMBER: _ClassVar[int]
    SEGMENT_NUM_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    path: str
    quality: str
    segment_num: int
    start_time: float
    def __init__(self, session_id: _Optional[str] = ..., path: _Optional[str] = ..., quality: _Optional[str] = ..., segment_num: _Optional[int] = ..., start_time: _Optional[float] = ...) -> None: ...

class HlsGetSegmentRpcResponse(_message.Message):
    __slots__ = ("success", "error", "content", "content_type", "created_new_session")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_NEW_SESSION_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    content: bytes
    content_type: str
    created_new_session: bool
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., content: _Optional[bytes] = ..., content_type: _Optional[str] = ..., created_new_session: bool = ...) -> None: ...

class HlsStopSessionRpcRequest(_message.Message):
    __slots__ = ("session_id", "path")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    path: str
    def __init__(self, session_id: _Optional[str] = ..., path: _Optional[str] = ...) -> None: ...

class HlsStopSessionRpcResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

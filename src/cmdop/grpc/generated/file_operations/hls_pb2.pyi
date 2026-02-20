from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class HlsGetPlaylistRequest(_message.Message):
    __slots__ = ("path", "quality", "start_time")
    PATH_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    path: str
    quality: str
    start_time: float
    def __init__(self, path: _Optional[str] = ..., quality: _Optional[str] = ..., start_time: _Optional[float] = ...) -> None: ...

class HlsGetPlaylistResult(_message.Message):
    __slots__ = ("content", "content_type", "duration", "segment_duration")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    SEGMENT_DURATION_FIELD_NUMBER: _ClassVar[int]
    content: bytes
    content_type: str
    duration: float
    segment_duration: int
    def __init__(self, content: _Optional[bytes] = ..., content_type: _Optional[str] = ..., duration: _Optional[float] = ..., segment_duration: _Optional[int] = ...) -> None: ...

class HlsGetSegmentRequest(_message.Message):
    __slots__ = ("path", "quality", "segment_num", "start_time")
    PATH_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FIELD_NUMBER: _ClassVar[int]
    SEGMENT_NUM_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    path: str
    quality: str
    segment_num: int
    start_time: float
    def __init__(self, path: _Optional[str] = ..., quality: _Optional[str] = ..., segment_num: _Optional[int] = ..., start_time: _Optional[float] = ...) -> None: ...

class HlsGetSegmentResult(_message.Message):
    __slots__ = ("content", "content_type", "created_new_session")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_NEW_SESSION_FIELD_NUMBER: _ClassVar[int]
    content: bytes
    content_type: str
    created_new_session: bool
    def __init__(self, content: _Optional[bytes] = ..., content_type: _Optional[str] = ..., created_new_session: bool = ...) -> None: ...

class HlsStopSessionRequest(_message.Message):
    __slots__ = ("path",)
    PATH_FIELD_NUMBER: _ClassVar[int]
    path: str
    def __init__(self, path: _Optional[str] = ...) -> None: ...

class HlsStopSessionResult(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

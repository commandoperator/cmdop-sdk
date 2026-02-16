from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SendInputRequest(_message.Message):
    __slots__ = ("session_id", "data")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    data: bytes
    def __init__(self, session_id: _Optional[str] = ..., data: _Optional[bytes] = ...) -> None: ...

class SendInputResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class SendResizeRequest(_message.Message):
    __slots__ = ("session_id", "cols", "rows")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    COLS_FIELD_NUMBER: _ClassVar[int]
    ROWS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    cols: int
    rows: int
    def __init__(self, session_id: _Optional[str] = ..., cols: _Optional[int] = ..., rows: _Optional[int] = ...) -> None: ...

class SendResizeResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class SendSignalRequest(_message.Message):
    __slots__ = ("session_id", "signal")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    signal: int
    def __init__(self, session_id: _Optional[str] = ..., signal: _Optional[int] = ...) -> None: ...

class SendSignalResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

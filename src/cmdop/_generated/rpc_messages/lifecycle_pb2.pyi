from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EnterBackgroundRequest(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class EnterBackgroundResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class WakeFromBackgroundRequest(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class WakeFromBackgroundResponse(_message.Message):
    __slots__ = ("success", "error", "pending_commands")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PENDING_COMMANDS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    pending_commands: _containers.RepeatedCompositeFieldContainer[PendingCommand]
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., pending_commands: _Optional[_Iterable[_Union[PendingCommand, _Mapping]]] = ...) -> None: ...

class PendingCommand(_message.Message):
    __slots__ = ("command_id", "type", "data", "queued_at")
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    QUEUED_AT_FIELD_NUMBER: _ClassVar[int]
    command_id: str
    type: str
    data: bytes
    queued_at: int
    def __init__(self, command_id: _Optional[str] = ..., type: _Optional[str] = ..., data: _Optional[bytes] = ..., queued_at: _Optional[int] = ...) -> None: ...

class QueueCommandRequest(_message.Message):
    __slots__ = ("session_id", "command")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    command: PendingCommand
    def __init__(self, session_id: _Optional[str] = ..., command: _Optional[_Union[PendingCommand, _Mapping]] = ...) -> None: ...

class QueueCommandResponse(_message.Message):
    __slots__ = ("queued", "push_sent", "status", "error")
    QUEUED_FIELD_NUMBER: _ClassVar[int]
    PUSH_SENT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    queued: bool
    push_sent: bool
    status: str
    error: str
    def __init__(self, queued: bool = ..., push_sent: bool = ..., status: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

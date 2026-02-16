from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("healthy", "version", "active_sessions", "connected_clients")
    HEALTHY_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_SESSIONS_FIELD_NUMBER: _ClassVar[int]
    CONNECTED_CLIENTS_FIELD_NUMBER: _ClassVar[int]
    healthy: bool
    version: str
    active_sessions: int
    connected_clients: int
    def __init__(self, healthy: bool = ..., version: _Optional[str] = ..., active_sessions: _Optional[int] = ..., connected_clients: _Optional[int] = ...) -> None: ...

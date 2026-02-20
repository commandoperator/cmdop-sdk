from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TunnelState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TUNNEL_STATE_UNSPECIFIED: _ClassVar[TunnelState]
    TUNNEL_STATE_CREATING: _ClassVar[TunnelState]
    TUNNEL_STATE_ACTIVE: _ClassVar[TunnelState]
    TUNNEL_STATE_CLOSED: _ClassVar[TunnelState]
    TUNNEL_STATE_ERROR: _ClassVar[TunnelState]

class TunnelProtocol(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TUNNEL_PROTOCOL_HTTP: _ClassVar[TunnelProtocol]
    TUNNEL_PROTOCOL_HTTPS: _ClassVar[TunnelProtocol]
    TUNNEL_PROTOCOL_TCP: _ClassVar[TunnelProtocol]
TUNNEL_STATE_UNSPECIFIED: TunnelState
TUNNEL_STATE_CREATING: TunnelState
TUNNEL_STATE_ACTIVE: TunnelState
TUNNEL_STATE_CLOSED: TunnelState
TUNNEL_STATE_ERROR: TunnelState
TUNNEL_PROTOCOL_HTTP: TunnelProtocol
TUNNEL_PROTOCOL_HTTPS: TunnelProtocol
TUNNEL_PROTOCOL_TCP: TunnelProtocol

class TunnelCreate(_message.Message):
    __slots__ = ("tunnel_id", "local_address", "protocol", "subdomain")
    TUNNEL_ID_FIELD_NUMBER: _ClassVar[int]
    LOCAL_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    SUBDOMAIN_FIELD_NUMBER: _ClassVar[int]
    tunnel_id: str
    local_address: str
    protocol: TunnelProtocol
    subdomain: str
    def __init__(self, tunnel_id: _Optional[str] = ..., local_address: _Optional[str] = ..., protocol: _Optional[_Union[TunnelProtocol, str]] = ..., subdomain: _Optional[str] = ...) -> None: ...

class TunnelData(_message.Message):
    __slots__ = ("tunnel_id", "connection_id", "data", "sequence", "is_request", "is_close", "method", "path", "status_code", "headers")
    class HeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TUNNEL_ID_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    IS_REQUEST_FIELD_NUMBER: _ClassVar[int]
    IS_CLOSE_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    tunnel_id: str
    connection_id: str
    data: bytes
    sequence: int
    is_request: bool
    is_close: bool
    method: str
    path: str
    status_code: int
    headers: _containers.ScalarMap[str, str]
    def __init__(self, tunnel_id: _Optional[str] = ..., connection_id: _Optional[str] = ..., data: _Optional[bytes] = ..., sequence: _Optional[int] = ..., is_request: bool = ..., is_close: bool = ..., method: _Optional[str] = ..., path: _Optional[str] = ..., status_code: _Optional[int] = ..., headers: _Optional[_Mapping[str, str]] = ...) -> None: ...

class TunnelClose(_message.Message):
    __slots__ = ("tunnel_id", "reason")
    TUNNEL_ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    tunnel_id: str
    reason: str
    def __init__(self, tunnel_id: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...

class TunnelCreated(_message.Message):
    __slots__ = ("tunnel_id", "success", "error", "public_url")
    TUNNEL_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_URL_FIELD_NUMBER: _ClassVar[int]
    tunnel_id: str
    success: bool
    error: str
    public_url: str
    def __init__(self, tunnel_id: _Optional[str] = ..., success: bool = ..., error: _Optional[str] = ..., public_url: _Optional[str] = ...) -> None: ...

class TunnelClosed(_message.Message):
    __slots__ = ("tunnel_id",)
    TUNNEL_ID_FIELD_NUMBER: _ClassVar[int]
    tunnel_id: str
    def __init__(self, tunnel_id: _Optional[str] = ...) -> None: ...

class TunnelError(_message.Message):
    __slots__ = ("tunnel_id", "connection_id", "error_code", "message", "is_fatal")
    TUNNEL_ID_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    IS_FATAL_FIELD_NUMBER: _ClassVar[int]
    tunnel_id: str
    connection_id: str
    error_code: str
    message: str
    is_fatal: bool
    def __init__(self, tunnel_id: _Optional[str] = ..., connection_id: _Optional[str] = ..., error_code: _Optional[str] = ..., message: _Optional[str] = ..., is_fatal: bool = ...) -> None: ...

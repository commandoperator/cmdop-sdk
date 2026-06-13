from cmdop.core.v1 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TunnelView(_message.Message):
    __slots__ = ("tunnel_id", "fleet_id", "session_id", "subdomain", "local_host", "local_port", "protocol", "created_at", "public_url")
    TUNNEL_ID_FIELD_NUMBER: _ClassVar[int]
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SUBDOMAIN_FIELD_NUMBER: _ClassVar[int]
    LOCAL_HOST_FIELD_NUMBER: _ClassVar[int]
    LOCAL_PORT_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_URL_FIELD_NUMBER: _ClassVar[int]
    tunnel_id: str
    fleet_id: str
    session_id: str
    subdomain: str
    local_host: str
    local_port: int
    protocol: str
    created_at: str
    public_url: str
    def __init__(self, tunnel_id: _Optional[str] = ..., fleet_id: _Optional[str] = ..., session_id: _Optional[str] = ..., subdomain: _Optional[str] = ..., local_host: _Optional[str] = ..., local_port: _Optional[int] = ..., protocol: _Optional[str] = ..., created_at: _Optional[str] = ..., public_url: _Optional[str] = ...) -> None: ...

class ConnectedSessionOption(_message.Message):
    __slots__ = ("session_id", "machine_id", "hostname", "label", "status")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MACHINE_ID_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    machine_id: str
    hostname: str
    label: str
    status: str
    def __init__(self, session_id: _Optional[str] = ..., machine_id: _Optional[str] = ..., hostname: _Optional[str] = ..., label: _Optional[str] = ..., status: _Optional[str] = ...) -> None: ...

class OpenTunnelRequest(_message.Message):
    __slots__ = ("session_id", "protocol", "local_host", "local_port", "subdomain", "options")
    class OptionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    LOCAL_HOST_FIELD_NUMBER: _ClassVar[int]
    LOCAL_PORT_FIELD_NUMBER: _ClassVar[int]
    SUBDOMAIN_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    protocol: str
    local_host: str
    local_port: int
    subdomain: str
    options: _containers.ScalarMap[str, str]
    def __init__(self, session_id: _Optional[str] = ..., protocol: _Optional[str] = ..., local_host: _Optional[str] = ..., local_port: _Optional[int] = ..., subdomain: _Optional[str] = ..., options: _Optional[_Mapping[str, str]] = ...) -> None: ...

class CloseTunnelRequest(_message.Message):
    __slots__ = ("tunnel_id",)
    TUNNEL_ID_FIELD_NUMBER: _ClassVar[int]
    tunnel_id: str
    def __init__(self, tunnel_id: _Optional[str] = ...) -> None: ...

class ListTunnelsRequest(_message.Message):
    __slots__ = ("page",)
    PAGE_FIELD_NUMBER: _ClassVar[int]
    page: _common_pb2.OffsetPage
    def __init__(self, page: _Optional[_Union[_common_pb2.OffsetPage, _Mapping]] = ...) -> None: ...

class GetTunnelRequest(_message.Message):
    __slots__ = ("tunnel_id",)
    TUNNEL_ID_FIELD_NUMBER: _ClassVar[int]
    tunnel_id: str
    def __init__(self, tunnel_id: _Optional[str] = ...) -> None: ...

class ListSessionsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TunnelList(_message.Message):
    __slots__ = ("items", "offset", "per_page", "total")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    PER_PAGE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[TunnelView]
    offset: int
    per_page: int
    total: int
    def __init__(self, items: _Optional[_Iterable[_Union[TunnelView, _Mapping]]] = ..., offset: _Optional[int] = ..., per_page: _Optional[int] = ..., total: _Optional[int] = ...) -> None: ...

class SessionList(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[ConnectedSessionOption]
    def __init__(self, items: _Optional[_Iterable[_Union[ConnectedSessionOption, _Mapping]]] = ...) -> None: ...

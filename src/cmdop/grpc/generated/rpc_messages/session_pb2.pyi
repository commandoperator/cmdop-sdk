import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
import common_types_pb2 as _common_types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateSessionRequest(_message.Message):
    __slots__ = ("user_id", "name", "config")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    name: str
    config: _common_types_pb2.SessionConfig
    def __init__(self, user_id: _Optional[str] = ..., name: _Optional[str] = ..., config: _Optional[_Union[_common_types_pb2.SessionConfig, _Mapping]] = ...) -> None: ...

class CreateSessionResponse(_message.Message):
    __slots__ = ("success", "session_id", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    session_id: str
    error: str
    def __init__(self, success: bool = ..., session_id: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class CloseSessionRequest(_message.Message):
    __slots__ = ("session_id", "reason", "force")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    reason: str
    force: bool
    def __init__(self, session_id: _Optional[str] = ..., reason: _Optional[str] = ..., force: bool = ...) -> None: ...

class CloseSessionResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class GetSessionStatusRequest(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class GetSessionStatusResponse(_message.Message):
    __slots__ = ("exists", "status", "agent_hostname", "connected_at", "last_heartbeat_at", "commands_count")
    EXISTS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    AGENT_HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    CONNECTED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_HEARTBEAT_AT_FIELD_NUMBER: _ClassVar[int]
    COMMANDS_COUNT_FIELD_NUMBER: _ClassVar[int]
    exists: bool
    status: _common_types_pb2.SessionStatus
    agent_hostname: str
    connected_at: _timestamp_pb2.Timestamp
    last_heartbeat_at: _timestamp_pb2.Timestamp
    commands_count: int
    def __init__(self, exists: bool = ..., status: _Optional[_Union[_common_types_pb2.SessionStatus, str]] = ..., agent_hostname: _Optional[str] = ..., connected_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., last_heartbeat_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., commands_count: _Optional[int] = ...) -> None: ...

class ListSessionsRequest(_message.Message):
    __slots__ = ("hostname_filter", "status_filter", "limit", "offset")
    HOSTNAME_FILTER_FIELD_NUMBER: _ClassVar[int]
    STATUS_FILTER_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    hostname_filter: str
    status_filter: str
    limit: int
    offset: int
    def __init__(self, hostname_filter: _Optional[str] = ..., status_filter: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class SessionInfoItem(_message.Message):
    __slots__ = ("session_id", "machine_hostname", "machine_name", "status", "os", "agent_version", "heartbeat_age_seconds", "has_shell", "shell", "working_directory", "connected_at")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MACHINE_HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    MACHINE_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    OS_FIELD_NUMBER: _ClassVar[int]
    AGENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_AGE_SECONDS_FIELD_NUMBER: _ClassVar[int]
    HAS_SHELL_FIELD_NUMBER: _ClassVar[int]
    SHELL_FIELD_NUMBER: _ClassVar[int]
    WORKING_DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    CONNECTED_AT_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    machine_hostname: str
    machine_name: str
    status: str
    os: str
    agent_version: str
    heartbeat_age_seconds: int
    has_shell: bool
    shell: str
    working_directory: str
    connected_at: _timestamp_pb2.Timestamp
    def __init__(self, session_id: _Optional[str] = ..., machine_hostname: _Optional[str] = ..., machine_name: _Optional[str] = ..., status: _Optional[str] = ..., os: _Optional[str] = ..., agent_version: _Optional[str] = ..., heartbeat_age_seconds: _Optional[int] = ..., has_shell: bool = ..., shell: _Optional[str] = ..., working_directory: _Optional[str] = ..., connected_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ListSessionsResponse(_message.Message):
    __slots__ = ("sessions", "total", "workspace_name", "error")
    SESSIONS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    sessions: _containers.RepeatedCompositeFieldContainer[SessionInfoItem]
    total: int
    workspace_name: str
    error: str
    def __init__(self, sessions: _Optional[_Iterable[_Union[SessionInfoItem, _Mapping]]] = ..., total: _Optional[int] = ..., workspace_name: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class GetSessionByHostnameRequest(_message.Message):
    __slots__ = ("hostname", "partial_match")
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_MATCH_FIELD_NUMBER: _ClassVar[int]
    hostname: str
    partial_match: bool
    def __init__(self, hostname: _Optional[str] = ..., partial_match: bool = ...) -> None: ...

class GetSessionByHostnameResponse(_message.Message):
    __slots__ = ("found", "session_id", "machine_hostname", "machine_name", "status", "error", "connected_at", "heartbeat_age_seconds", "has_shell", "shell", "working_directory", "ambiguous", "matches_count", "os", "agent_version")
    FOUND_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MACHINE_HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    MACHINE_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    CONNECTED_AT_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_AGE_SECONDS_FIELD_NUMBER: _ClassVar[int]
    HAS_SHELL_FIELD_NUMBER: _ClassVar[int]
    SHELL_FIELD_NUMBER: _ClassVar[int]
    WORKING_DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    AMBIGUOUS_FIELD_NUMBER: _ClassVar[int]
    MATCHES_COUNT_FIELD_NUMBER: _ClassVar[int]
    OS_FIELD_NUMBER: _ClassVar[int]
    AGENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    found: bool
    session_id: str
    machine_hostname: str
    machine_name: str
    status: str
    error: str
    connected_at: _timestamp_pb2.Timestamp
    heartbeat_age_seconds: int
    has_shell: bool
    shell: str
    working_directory: str
    ambiguous: bool
    matches_count: int
    os: str
    agent_version: str
    def __init__(self, found: bool = ..., session_id: _Optional[str] = ..., machine_hostname: _Optional[str] = ..., machine_name: _Optional[str] = ..., status: _Optional[str] = ..., error: _Optional[str] = ..., connected_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., heartbeat_age_seconds: _Optional[int] = ..., has_shell: bool = ..., shell: _Optional[str] = ..., working_directory: _Optional[str] = ..., ambiguous: bool = ..., matches_count: _Optional[int] = ..., os: _Optional[str] = ..., agent_version: _Optional[str] = ...) -> None: ...

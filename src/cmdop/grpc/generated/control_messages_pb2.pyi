import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
import common_types_pb2 as _common_types_pb2
import file_operations_pb2 as _file_operations_pb2
from file_operations import common_pb2 as _common_pb2
from file_operations import directory_pb2 as _directory_pb2
from file_operations import file_crud_pb2 as _file_crud_pb2
from file_operations import archive_pb2 as _archive_pb2
from file_operations import search_pb2 as _search_pb2
from file_operations import transfer_pb2 as _transfer_pb2
from file_operations import hls_pb2 as _hls_pb2
from file_operations import changes_pb2 as _changes_pb2
from file_operations import requests_pb2 as _requests_pb2
import tunnel_pb2 as _tunnel_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NotificationMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NOTIFICATION_METHOD_AUTO: _ClassVar[NotificationMethod]
    NOTIFICATION_METHOD_VISUAL: _ClassVar[NotificationMethod]
    NOTIFICATION_METHOD_AUDIO: _ClassVar[NotificationMethod]
    NOTIFICATION_METHOD_BOTH: _ClassVar[NotificationMethod]

class AgentType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AGENT_TYPE_CHAT: _ClassVar[AgentType]
    AGENT_TYPE_TERMINAL: _ClassVar[AgentType]
    AGENT_TYPE_COMMAND: _ClassVar[AgentType]
    AGENT_TYPE_ROUTER: _ClassVar[AgentType]
    AGENT_TYPE_PLANNER: _ClassVar[AgentType]
NOTIFICATION_METHOD_AUTO: NotificationMethod
NOTIFICATION_METHOD_VISUAL: NotificationMethod
NOTIFICATION_METHOD_AUDIO: NotificationMethod
NOTIFICATION_METHOD_BOTH: NotificationMethod
AGENT_TYPE_CHAT: AgentType
AGENT_TYPE_TERMINAL: AgentType
AGENT_TYPE_COMMAND: AgentType
AGENT_TYPE_ROUTER: AgentType
AGENT_TYPE_PLANNER: AgentType

class ControlMessage(_message.Message):
    __slots__ = ("command_id", "timestamp", "input", "resize", "start_session", "close_session", "signal", "cancel", "ping", "config_update", "file_operation", "push_notification", "streaming_relay_chunk", "tunnel_create", "tunnel_data", "tunnel_close", "refresh_permissions", "agent_run", "agent_cancel", "skill_list", "skill_show", "skill_run")
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    RESIZE_FIELD_NUMBER: _ClassVar[int]
    START_SESSION_FIELD_NUMBER: _ClassVar[int]
    CLOSE_SESSION_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_FIELD_NUMBER: _ClassVar[int]
    CANCEL_FIELD_NUMBER: _ClassVar[int]
    PING_FIELD_NUMBER: _ClassVar[int]
    CONFIG_UPDATE_FIELD_NUMBER: _ClassVar[int]
    FILE_OPERATION_FIELD_NUMBER: _ClassVar[int]
    PUSH_NOTIFICATION_FIELD_NUMBER: _ClassVar[int]
    STREAMING_RELAY_CHUNK_FIELD_NUMBER: _ClassVar[int]
    TUNNEL_CREATE_FIELD_NUMBER: _ClassVar[int]
    TUNNEL_DATA_FIELD_NUMBER: _ClassVar[int]
    TUNNEL_CLOSE_FIELD_NUMBER: _ClassVar[int]
    REFRESH_PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    AGENT_RUN_FIELD_NUMBER: _ClassVar[int]
    AGENT_CANCEL_FIELD_NUMBER: _ClassVar[int]
    SKILL_LIST_FIELD_NUMBER: _ClassVar[int]
    SKILL_SHOW_FIELD_NUMBER: _ClassVar[int]
    SKILL_RUN_FIELD_NUMBER: _ClassVar[int]
    command_id: str
    timestamp: _timestamp_pb2.Timestamp
    input: TerminalInput
    resize: ResizeCommand
    start_session: StartSessionCommand
    close_session: CloseSessionCommand
    signal: SignalCommand
    cancel: CancelCommand
    ping: PingCommand
    config_update: ConfigUpdateCommand
    file_operation: _requests_pb2.FileOperationRequest
    push_notification: PushNotification
    streaming_relay_chunk: _transfer_pb2.StreamingRelayChunk
    tunnel_create: _tunnel_pb2.TunnelCreate
    tunnel_data: _tunnel_pb2.TunnelData
    tunnel_close: _tunnel_pb2.TunnelClose
    refresh_permissions: RefreshPermissionsCommand
    agent_run: AgentRunCommand
    agent_cancel: AgentCancelCommand
    skill_list: SkillListCommand
    skill_show: SkillShowCommand
    skill_run: SkillRunCommand
    def __init__(self, command_id: _Optional[str] = ..., timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., input: _Optional[_Union[TerminalInput, _Mapping]] = ..., resize: _Optional[_Union[ResizeCommand, _Mapping]] = ..., start_session: _Optional[_Union[StartSessionCommand, _Mapping]] = ..., close_session: _Optional[_Union[CloseSessionCommand, _Mapping]] = ..., signal: _Optional[_Union[SignalCommand, _Mapping]] = ..., cancel: _Optional[_Union[CancelCommand, _Mapping]] = ..., ping: _Optional[_Union[PingCommand, _Mapping]] = ..., config_update: _Optional[_Union[ConfigUpdateCommand, _Mapping]] = ..., file_operation: _Optional[_Union[_requests_pb2.FileOperationRequest, _Mapping]] = ..., push_notification: _Optional[_Union[PushNotification, _Mapping]] = ..., streaming_relay_chunk: _Optional[_Union[_transfer_pb2.StreamingRelayChunk, _Mapping]] = ..., tunnel_create: _Optional[_Union[_tunnel_pb2.TunnelCreate, _Mapping]] = ..., tunnel_data: _Optional[_Union[_tunnel_pb2.TunnelData, _Mapping]] = ..., tunnel_close: _Optional[_Union[_tunnel_pb2.TunnelClose, _Mapping]] = ..., refresh_permissions: _Optional[_Union[RefreshPermissionsCommand, _Mapping]] = ..., agent_run: _Optional[_Union[AgentRunCommand, _Mapping]] = ..., agent_cancel: _Optional[_Union[AgentCancelCommand, _Mapping]] = ..., skill_list: _Optional[_Union[SkillListCommand, _Mapping]] = ..., skill_show: _Optional[_Union[SkillShowCommand, _Mapping]] = ..., skill_run: _Optional[_Union[SkillRunCommand, _Mapping]] = ...) -> None: ...

class PushNotification(_message.Message):
    __slots__ = ("id", "type", "title", "message", "data", "priority", "silent", "method")
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    SILENT_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    title: str
    message: str
    data: _containers.ScalarMap[str, str]
    priority: int
    silent: bool
    method: NotificationMethod
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ..., title: _Optional[str] = ..., message: _Optional[str] = ..., data: _Optional[_Mapping[str, str]] = ..., priority: _Optional[int] = ..., silent: bool = ..., method: _Optional[_Union[NotificationMethod, str]] = ...) -> None: ...

class TerminalInput(_message.Message):
    __slots__ = ("data", "sequence")
    DATA_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    sequence: int
    def __init__(self, data: _Optional[bytes] = ..., sequence: _Optional[int] = ...) -> None: ...

class ResizeCommand(_message.Message):
    __slots__ = ("size",)
    SIZE_FIELD_NUMBER: _ClassVar[int]
    size: _common_types_pb2.TerminalSize
    def __init__(self, size: _Optional[_Union[_common_types_pb2.TerminalSize, _Mapping]] = ...) -> None: ...

class StartSessionCommand(_message.Message):
    __slots__ = ("config", "web_terminal_url", "expires_at")
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    WEB_TERMINAL_URL_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    config: _common_types_pb2.SessionConfig
    web_terminal_url: str
    expires_at: _timestamp_pb2.Timestamp
    def __init__(self, config: _Optional[_Union[_common_types_pb2.SessionConfig, _Mapping]] = ..., web_terminal_url: _Optional[str] = ..., expires_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CloseSessionCommand(_message.Message):
    __slots__ = ("reason", "force")
    REASON_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    reason: str
    force: bool
    def __init__(self, reason: _Optional[str] = ..., force: bool = ...) -> None: ...

class SignalCommand(_message.Message):
    __slots__ = ("signal",)
    SIGNAL_FIELD_NUMBER: _ClassVar[int]
    signal: int
    def __init__(self, signal: _Optional[int] = ...) -> None: ...

class CancelCommand(_message.Message):
    __slots__ = ("command_id",)
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    command_id: str
    def __init__(self, command_id: _Optional[str] = ...) -> None: ...

class PingCommand(_message.Message):
    __slots__ = ("sequence",)
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    sequence: int
    def __init__(self, sequence: _Optional[int] = ...) -> None: ...

class ConfigUpdateCommand(_message.Message):
    __slots__ = ("config",)
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: _common_types_pb2.SessionConfig
    def __init__(self, config: _Optional[_Union[_common_types_pb2.SessionConfig, _Mapping]] = ...) -> None: ...

class RefreshPermissionsCommand(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AgentRunCommand(_message.Message):
    __slots__ = ("request_id", "prompt", "agent_type", "options", "stream_events", "output_schema")
    class OptionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    AGENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    STREAM_EVENTS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    prompt: str
    agent_type: AgentType
    options: _containers.ScalarMap[str, str]
    stream_events: bool
    output_schema: str
    def __init__(self, request_id: _Optional[str] = ..., prompt: _Optional[str] = ..., agent_type: _Optional[_Union[AgentType, str]] = ..., options: _Optional[_Mapping[str, str]] = ..., stream_events: bool = ..., output_schema: _Optional[str] = ...) -> None: ...

class AgentCancelCommand(_message.Message):
    __slots__ = ("request_id", "reason")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    reason: str
    def __init__(self, request_id: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...

class SkillListCommand(_message.Message):
    __slots__ = ("request_id",)
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    def __init__(self, request_id: _Optional[str] = ...) -> None: ...

class SkillShowCommand(_message.Message):
    __slots__ = ("request_id", "skill_name")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SKILL_NAME_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    skill_name: str
    def __init__(self, request_id: _Optional[str] = ..., skill_name: _Optional[str] = ...) -> None: ...

class SkillRunCommand(_message.Message):
    __slots__ = ("request_id", "skill_name", "prompt", "options", "timeout_seconds", "output_schema")
    class OptionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SKILL_NAME_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    skill_name: str
    prompt: str
    options: _containers.ScalarMap[str, str]
    timeout_seconds: int
    output_schema: str
    def __init__(self, request_id: _Optional[str] = ..., skill_name: _Optional[str] = ..., prompt: _Optional[str] = ..., options: _Optional[_Mapping[str, str]] = ..., timeout_seconds: _Optional[int] = ..., output_schema: _Optional[str] = ...) -> None: ...

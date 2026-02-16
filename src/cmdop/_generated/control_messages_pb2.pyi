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

class BrowserCommandType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BROWSER_CMD_CREATE_SESSION: _ClassVar[BrowserCommandType]
    BROWSER_CMD_CLOSE_SESSION: _ClassVar[BrowserCommandType]
    BROWSER_CMD_NAVIGATE: _ClassVar[BrowserCommandType]
    BROWSER_CMD_CLICK: _ClassVar[BrowserCommandType]
    BROWSER_CMD_TYPE: _ClassVar[BrowserCommandType]
    BROWSER_CMD_WAIT: _ClassVar[BrowserCommandType]
    BROWSER_CMD_EXTRACT: _ClassVar[BrowserCommandType]
    BROWSER_CMD_EXTRACT_REGEX: _ClassVar[BrowserCommandType]
    BROWSER_CMD_GET_HTML: _ClassVar[BrowserCommandType]
    BROWSER_CMD_GET_TEXT: _ClassVar[BrowserCommandType]
    BROWSER_CMD_EXECUTE_SCRIPT: _ClassVar[BrowserCommandType]
    BROWSER_CMD_SCREENSHOT: _ClassVar[BrowserCommandType]
    BROWSER_CMD_GET_STATE: _ClassVar[BrowserCommandType]
    BROWSER_CMD_SET_COOKIES: _ClassVar[BrowserCommandType]
    BROWSER_CMD_GET_COOKIES: _ClassVar[BrowserCommandType]
    BROWSER_CMD_VALIDATE_SELECTORS: _ClassVar[BrowserCommandType]
    BROWSER_CMD_EXTRACT_DATA: _ClassVar[BrowserCommandType]

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
    AGENT_TYPE_BROWSER: _ClassVar[AgentType]
    AGENT_TYPE_SCRAPER: _ClassVar[AgentType]
    AGENT_TYPE_FORM_FILLER: _ClassVar[AgentType]
BROWSER_CMD_CREATE_SESSION: BrowserCommandType
BROWSER_CMD_CLOSE_SESSION: BrowserCommandType
BROWSER_CMD_NAVIGATE: BrowserCommandType
BROWSER_CMD_CLICK: BrowserCommandType
BROWSER_CMD_TYPE: BrowserCommandType
BROWSER_CMD_WAIT: BrowserCommandType
BROWSER_CMD_EXTRACT: BrowserCommandType
BROWSER_CMD_EXTRACT_REGEX: BrowserCommandType
BROWSER_CMD_GET_HTML: BrowserCommandType
BROWSER_CMD_GET_TEXT: BrowserCommandType
BROWSER_CMD_EXECUTE_SCRIPT: BrowserCommandType
BROWSER_CMD_SCREENSHOT: BrowserCommandType
BROWSER_CMD_GET_STATE: BrowserCommandType
BROWSER_CMD_SET_COOKIES: BrowserCommandType
BROWSER_CMD_GET_COOKIES: BrowserCommandType
BROWSER_CMD_VALIDATE_SELECTORS: BrowserCommandType
BROWSER_CMD_EXTRACT_DATA: BrowserCommandType
NOTIFICATION_METHOD_AUTO: NotificationMethod
NOTIFICATION_METHOD_VISUAL: NotificationMethod
NOTIFICATION_METHOD_AUDIO: NotificationMethod
NOTIFICATION_METHOD_BOTH: NotificationMethod
AGENT_TYPE_CHAT: AgentType
AGENT_TYPE_TERMINAL: AgentType
AGENT_TYPE_COMMAND: AgentType
AGENT_TYPE_ROUTER: AgentType
AGENT_TYPE_PLANNER: AgentType
AGENT_TYPE_BROWSER: AgentType
AGENT_TYPE_SCRAPER: AgentType
AGENT_TYPE_FORM_FILLER: AgentType

class ControlMessage(_message.Message):
    __slots__ = ("command_id", "timestamp", "input", "resize", "start_session", "close_session", "signal", "cancel", "ping", "config_update", "get_history", "file_operation", "push_notification", "streaming_relay_chunk", "tunnel_create", "tunnel_data", "tunnel_close", "refresh_permissions", "agent_run", "agent_cancel", "browser")
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
    GET_HISTORY_FIELD_NUMBER: _ClassVar[int]
    FILE_OPERATION_FIELD_NUMBER: _ClassVar[int]
    PUSH_NOTIFICATION_FIELD_NUMBER: _ClassVar[int]
    STREAMING_RELAY_CHUNK_FIELD_NUMBER: _ClassVar[int]
    TUNNEL_CREATE_FIELD_NUMBER: _ClassVar[int]
    TUNNEL_DATA_FIELD_NUMBER: _ClassVar[int]
    TUNNEL_CLOSE_FIELD_NUMBER: _ClassVar[int]
    REFRESH_PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    AGENT_RUN_FIELD_NUMBER: _ClassVar[int]
    AGENT_CANCEL_FIELD_NUMBER: _ClassVar[int]
    BROWSER_FIELD_NUMBER: _ClassVar[int]
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
    get_history: GetHistoryCommand
    file_operation: _requests_pb2.FileOperationRequest
    push_notification: PushNotification
    streaming_relay_chunk: _transfer_pb2.StreamingRelayChunk
    tunnel_create: _tunnel_pb2.TunnelCreate
    tunnel_data: _tunnel_pb2.TunnelData
    tunnel_close: _tunnel_pb2.TunnelClose
    refresh_permissions: RefreshPermissionsCommand
    agent_run: AgentRunCommand
    agent_cancel: AgentCancelCommand
    browser: BrowserCommand
    def __init__(self, command_id: _Optional[str] = ..., timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., input: _Optional[_Union[TerminalInput, _Mapping]] = ..., resize: _Optional[_Union[ResizeCommand, _Mapping]] = ..., start_session: _Optional[_Union[StartSessionCommand, _Mapping]] = ..., close_session: _Optional[_Union[CloseSessionCommand, _Mapping]] = ..., signal: _Optional[_Union[SignalCommand, _Mapping]] = ..., cancel: _Optional[_Union[CancelCommand, _Mapping]] = ..., ping: _Optional[_Union[PingCommand, _Mapping]] = ..., config_update: _Optional[_Union[ConfigUpdateCommand, _Mapping]] = ..., get_history: _Optional[_Union[GetHistoryCommand, _Mapping]] = ..., file_operation: _Optional[_Union[_requests_pb2.FileOperationRequest, _Mapping]] = ..., push_notification: _Optional[_Union[PushNotification, _Mapping]] = ..., streaming_relay_chunk: _Optional[_Union[_transfer_pb2.StreamingRelayChunk, _Mapping]] = ..., tunnel_create: _Optional[_Union[_tunnel_pb2.TunnelCreate, _Mapping]] = ..., tunnel_data: _Optional[_Union[_tunnel_pb2.TunnelData, _Mapping]] = ..., tunnel_close: _Optional[_Union[_tunnel_pb2.TunnelClose, _Mapping]] = ..., refresh_permissions: _Optional[_Union[RefreshPermissionsCommand, _Mapping]] = ..., agent_run: _Optional[_Union[AgentRunCommand, _Mapping]] = ..., agent_cancel: _Optional[_Union[AgentCancelCommand, _Mapping]] = ..., browser: _Optional[_Union[BrowserCommand, _Mapping]] = ...) -> None: ...

class BrowserCommand(_message.Message):
    __slots__ = ("request_id", "type", "payload_json")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_JSON_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    type: BrowserCommandType
    payload_json: str
    def __init__(self, request_id: _Optional[str] = ..., type: _Optional[_Union[BrowserCommandType, str]] = ..., payload_json: _Optional[str] = ...) -> None: ...

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

class GetHistoryCommand(_message.Message):
    __slots__ = ("limit", "offset", "source")
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    limit: int
    offset: int
    source: str
    def __init__(self, limit: _Optional[int] = ..., offset: _Optional[int] = ..., source: _Optional[str] = ...) -> None: ...

class RefreshPermissionsCommand(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AgentRunCommand(_message.Message):
    __slots__ = ("request_id", "prompt", "agent_type", "options", "stream_events", "output_schema", "browser_options")
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
    BROWSER_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    prompt: str
    agent_type: AgentType
    options: _containers.ScalarMap[str, str]
    stream_events: bool
    output_schema: str
    browser_options: BrowserAgentOptions
    def __init__(self, request_id: _Optional[str] = ..., prompt: _Optional[str] = ..., agent_type: _Optional[_Union[AgentType, str]] = ..., options: _Optional[_Mapping[str, str]] = ..., stream_events: bool = ..., output_schema: _Optional[str] = ..., browser_options: _Optional[_Union[BrowserAgentOptions, _Mapping]] = ...) -> None: ...

class BrowserAgentOptions(_message.Message):
    __slots__ = ("session_type", "profile_id", "start_url", "use_axtree", "use_diff", "max_tokens", "stealth_level", "use_proxy", "proxy_url", "max_actions", "navigation_timeout_ms", "action_timeout_ms", "screenshot_on_action", "screenshot_fullpage", "screenshot_format")
    SESSION_TYPE_FIELD_NUMBER: _ClassVar[int]
    PROFILE_ID_FIELD_NUMBER: _ClassVar[int]
    START_URL_FIELD_NUMBER: _ClassVar[int]
    USE_AXTREE_FIELD_NUMBER: _ClassVar[int]
    USE_DIFF_FIELD_NUMBER: _ClassVar[int]
    MAX_TOKENS_FIELD_NUMBER: _ClassVar[int]
    STEALTH_LEVEL_FIELD_NUMBER: _ClassVar[int]
    USE_PROXY_FIELD_NUMBER: _ClassVar[int]
    PROXY_URL_FIELD_NUMBER: _ClassVar[int]
    MAX_ACTIONS_FIELD_NUMBER: _ClassVar[int]
    NAVIGATION_TIMEOUT_MS_FIELD_NUMBER: _ClassVar[int]
    ACTION_TIMEOUT_MS_FIELD_NUMBER: _ClassVar[int]
    SCREENSHOT_ON_ACTION_FIELD_NUMBER: _ClassVar[int]
    SCREENSHOT_FULLPAGE_FIELD_NUMBER: _ClassVar[int]
    SCREENSHOT_FORMAT_FIELD_NUMBER: _ClassVar[int]
    session_type: str
    profile_id: str
    start_url: str
    use_axtree: bool
    use_diff: bool
    max_tokens: int
    stealth_level: str
    use_proxy: bool
    proxy_url: str
    max_actions: int
    navigation_timeout_ms: int
    action_timeout_ms: int
    screenshot_on_action: bool
    screenshot_fullpage: bool
    screenshot_format: str
    def __init__(self, session_type: _Optional[str] = ..., profile_id: _Optional[str] = ..., start_url: _Optional[str] = ..., use_axtree: bool = ..., use_diff: bool = ..., max_tokens: _Optional[int] = ..., stealth_level: _Optional[str] = ..., use_proxy: bool = ..., proxy_url: _Optional[str] = ..., max_actions: _Optional[int] = ..., navigation_timeout_ms: _Optional[int] = ..., action_timeout_ms: _Optional[int] = ..., screenshot_on_action: bool = ..., screenshot_fullpage: bool = ..., screenshot_format: _Optional[str] = ...) -> None: ...

class AgentCancelCommand(_message.Message):
    __slots__ = ("request_id", "reason")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    reason: str
    def __init__(self, request_id: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...

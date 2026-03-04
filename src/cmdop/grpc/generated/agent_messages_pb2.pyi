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
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PermissionAccessStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PERMISSION_GRANTED: _ClassVar[PermissionAccessStatus]
    PERMISSION_DENIED: _ClassVar[PermissionAccessStatus]
    PERMISSION_PENDING: _ClassVar[PermissionAccessStatus]
    PERMISSION_UNKNOWN: _ClassVar[PermissionAccessStatus]

class AgentEventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AGENT_EVENT_TOKEN: _ClassVar[AgentEventType]
    AGENT_EVENT_TOOL_START: _ClassVar[AgentEventType]
    AGENT_EVENT_TOOL_END: _ClassVar[AgentEventType]
    AGENT_EVENT_THINKING: _ClassVar[AgentEventType]
    AGENT_EVENT_ERROR: _ClassVar[AgentEventType]
    AGENT_EVENT_HANDOFF: _ClassVar[AgentEventType]
    AGENT_EVENT_CANCELLED: _ClassVar[AgentEventType]
PERMISSION_GRANTED: PermissionAccessStatus
PERMISSION_DENIED: PermissionAccessStatus
PERMISSION_PENDING: PermissionAccessStatus
PERMISSION_UNKNOWN: PermissionAccessStatus
AGENT_EVENT_TOKEN: AgentEventType
AGENT_EVENT_TOOL_START: AgentEventType
AGENT_EVENT_TOOL_END: AgentEventType
AGENT_EVENT_THINKING: AgentEventType
AGENT_EVENT_ERROR: AgentEventType
AGENT_EVENT_HANDOFF: AgentEventType
AGENT_EVENT_CANCELLED: AgentEventType

class AgentMessage(_message.Message):
    __slots__ = ("session_id", "message_id", "timestamp", "register", "heartbeat", "output", "command_complete", "status", "error", "ack", "file_operation_result", "tunnel_created", "tunnel_data", "tunnel_closed", "tunnel_error", "permission_status", "agent_result", "agent_event", "skill_list_result", "skill_show_result", "skill_run_result")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REGISTER_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    COMMAND_COMPLETE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ACK_FIELD_NUMBER: _ClassVar[int]
    FILE_OPERATION_RESULT_FIELD_NUMBER: _ClassVar[int]
    TUNNEL_CREATED_FIELD_NUMBER: _ClassVar[int]
    TUNNEL_DATA_FIELD_NUMBER: _ClassVar[int]
    TUNNEL_CLOSED_FIELD_NUMBER: _ClassVar[int]
    TUNNEL_ERROR_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_STATUS_FIELD_NUMBER: _ClassVar[int]
    AGENT_RESULT_FIELD_NUMBER: _ClassVar[int]
    AGENT_EVENT_FIELD_NUMBER: _ClassVar[int]
    SKILL_LIST_RESULT_FIELD_NUMBER: _ClassVar[int]
    SKILL_SHOW_RESULT_FIELD_NUMBER: _ClassVar[int]
    SKILL_RUN_RESULT_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    message_id: str
    timestamp: _timestamp_pb2.Timestamp
    register: RegisterRequest
    heartbeat: HeartbeatUpdate
    output: TerminalOutput
    command_complete: CommandComplete
    status: StatusUpdate
    error: ErrorReport
    ack: CommandAck
    file_operation_result: _requests_pb2.FileOperationResult
    tunnel_created: _tunnel_pb2.TunnelCreated
    tunnel_data: _tunnel_pb2.TunnelData
    tunnel_closed: _tunnel_pb2.TunnelClosed
    tunnel_error: _tunnel_pb2.TunnelError
    permission_status: PermissionStatus
    agent_result: AgentResult
    agent_event: AgentStreamEvent
    skill_list_result: SkillListResult
    skill_show_result: SkillShowResult
    skill_run_result: SkillRunResult
    def __init__(self, session_id: _Optional[str] = ..., message_id: _Optional[str] = ..., timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., register: _Optional[_Union[RegisterRequest, _Mapping]] = ..., heartbeat: _Optional[_Union[HeartbeatUpdate, _Mapping]] = ..., output: _Optional[_Union[TerminalOutput, _Mapping]] = ..., command_complete: _Optional[_Union[CommandComplete, _Mapping]] = ..., status: _Optional[_Union[StatusUpdate, _Mapping]] = ..., error: _Optional[_Union[ErrorReport, _Mapping]] = ..., ack: _Optional[_Union[CommandAck, _Mapping]] = ..., file_operation_result: _Optional[_Union[_requests_pb2.FileOperationResult, _Mapping]] = ..., tunnel_created: _Optional[_Union[_tunnel_pb2.TunnelCreated, _Mapping]] = ..., tunnel_data: _Optional[_Union[_tunnel_pb2.TunnelData, _Mapping]] = ..., tunnel_closed: _Optional[_Union[_tunnel_pb2.TunnelClosed, _Mapping]] = ..., tunnel_error: _Optional[_Union[_tunnel_pb2.TunnelError, _Mapping]] = ..., permission_status: _Optional[_Union[PermissionStatus, _Mapping]] = ..., agent_result: _Optional[_Union[AgentResult, _Mapping]] = ..., agent_event: _Optional[_Union[AgentStreamEvent, _Mapping]] = ..., skill_list_result: _Optional[_Union[SkillListResult, _Mapping]] = ..., skill_show_result: _Optional[_Union[SkillShowResult, _Mapping]] = ..., skill_run_result: _Optional[_Union[SkillRunResult, _Mapping]] = ...) -> None: ...

class RegisterRequest(_message.Message):
    __slots__ = ("version", "hostname", "platform", "supported_shells", "initial_size", "architecture", "device_id", "device_type", "has_shell", "device_model", "public_ip", "local_ips", "username", "uid", "is_root", "home_dir", "os_version", "kernel_version", "cpu_model", "cpu_count", "total_ram", "uptime_seconds")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    SUPPORTED_SHELLS_FIELD_NUMBER: _ClassVar[int]
    INITIAL_SIZE_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_TYPE_FIELD_NUMBER: _ClassVar[int]
    HAS_SHELL_FIELD_NUMBER: _ClassVar[int]
    DEVICE_MODEL_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_IP_FIELD_NUMBER: _ClassVar[int]
    LOCAL_IPS_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    IS_ROOT_FIELD_NUMBER: _ClassVar[int]
    HOME_DIR_FIELD_NUMBER: _ClassVar[int]
    OS_VERSION_FIELD_NUMBER: _ClassVar[int]
    KERNEL_VERSION_FIELD_NUMBER: _ClassVar[int]
    CPU_MODEL_FIELD_NUMBER: _ClassVar[int]
    CPU_COUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_RAM_FIELD_NUMBER: _ClassVar[int]
    UPTIME_SECONDS_FIELD_NUMBER: _ClassVar[int]
    version: str
    hostname: str
    platform: str
    supported_shells: _containers.RepeatedScalarFieldContainer[str]
    initial_size: _common_types_pb2.TerminalSize
    architecture: str
    device_id: str
    device_type: str
    has_shell: bool
    device_model: str
    public_ip: str
    local_ips: _containers.RepeatedScalarFieldContainer[str]
    username: str
    uid: int
    is_root: bool
    home_dir: str
    os_version: str
    kernel_version: str
    cpu_model: str
    cpu_count: int
    total_ram: int
    uptime_seconds: int
    def __init__(self, version: _Optional[str] = ..., hostname: _Optional[str] = ..., platform: _Optional[str] = ..., supported_shells: _Optional[_Iterable[str]] = ..., initial_size: _Optional[_Union[_common_types_pb2.TerminalSize, _Mapping]] = ..., architecture: _Optional[str] = ..., device_id: _Optional[str] = ..., device_type: _Optional[str] = ..., has_shell: bool = ..., device_model: _Optional[str] = ..., public_ip: _Optional[str] = ..., local_ips: _Optional[_Iterable[str]] = ..., username: _Optional[str] = ..., uid: _Optional[int] = ..., is_root: bool = ..., home_dir: _Optional[str] = ..., os_version: _Optional[str] = ..., kernel_version: _Optional[str] = ..., cpu_model: _Optional[str] = ..., cpu_count: _Optional[int] = ..., total_ram: _Optional[int] = ..., uptime_seconds: _Optional[int] = ...) -> None: ...

class HeartbeatUpdate(_message.Message):
    __slots__ = ("metrics",)
    METRICS_FIELD_NUMBER: _ClassVar[int]
    metrics: _common_types_pb2.SystemMetrics
    def __init__(self, metrics: _Optional[_Union[_common_types_pb2.SystemMetrics, _Mapping]] = ...) -> None: ...

class TerminalOutput(_message.Message):
    __slots__ = ("data", "is_stderr", "sequence")
    DATA_FIELD_NUMBER: _ClassVar[int]
    IS_STDERR_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    is_stderr: bool
    sequence: int
    def __init__(self, data: _Optional[bytes] = ..., is_stderr: bool = ..., sequence: _Optional[int] = ...) -> None: ...

class CommandComplete(_message.Message):
    __slots__ = ("command_id", "exit_code", "duration_ms")
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    EXIT_CODE_FIELD_NUMBER: _ClassVar[int]
    DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    command_id: str
    exit_code: int
    duration_ms: int
    def __init__(self, command_id: _Optional[str] = ..., exit_code: _Optional[int] = ..., duration_ms: _Optional[int] = ...) -> None: ...

class StatusUpdate(_message.Message):
    __slots__ = ("old_status", "new_status", "reason", "working_directory")
    OLD_STATUS_FIELD_NUMBER: _ClassVar[int]
    NEW_STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    WORKING_DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    old_status: _common_types_pb2.SessionStatus
    new_status: _common_types_pb2.SessionStatus
    reason: str
    working_directory: str
    def __init__(self, old_status: _Optional[_Union[_common_types_pb2.SessionStatus, str]] = ..., new_status: _Optional[_Union[_common_types_pb2.SessionStatus, str]] = ..., reason: _Optional[str] = ..., working_directory: _Optional[str] = ...) -> None: ...

class ErrorReport(_message.Message):
    __slots__ = ("error_code", "message", "stack_trace", "is_fatal", "suggestions", "can_retry")
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STACK_TRACE_FIELD_NUMBER: _ClassVar[int]
    IS_FATAL_FIELD_NUMBER: _ClassVar[int]
    SUGGESTIONS_FIELD_NUMBER: _ClassVar[int]
    CAN_RETRY_FIELD_NUMBER: _ClassVar[int]
    error_code: str
    message: str
    stack_trace: str
    is_fatal: bool
    suggestions: _containers.RepeatedScalarFieldContainer[str]
    can_retry: bool
    def __init__(self, error_code: _Optional[str] = ..., message: _Optional[str] = ..., stack_trace: _Optional[str] = ..., is_fatal: bool = ..., suggestions: _Optional[_Iterable[str]] = ..., can_retry: bool = ...) -> None: ...

class CommandAck(_message.Message):
    __slots__ = ("command_id", "success", "message")
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    command_id: str
    success: bool
    message: str
    def __init__(self, command_id: _Optional[str] = ..., success: bool = ..., message: _Optional[str] = ...) -> None: ...

class PermissionStatus(_message.Message):
    __slots__ = ("directories", "platform", "checked_at")
    DIRECTORIES_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    CHECKED_AT_FIELD_NUMBER: _ClassVar[int]
    directories: _containers.RepeatedCompositeFieldContainer[DirectoryPermission]
    platform: str
    checked_at: int
    def __init__(self, directories: _Optional[_Iterable[_Union[DirectoryPermission, _Mapping]]] = ..., platform: _Optional[str] = ..., checked_at: _Optional[int] = ...) -> None: ...

class DirectoryPermission(_message.Message):
    __slots__ = ("path", "status", "error_message", "is_sensitive")
    PATH_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    IS_SENSITIVE_FIELD_NUMBER: _ClassVar[int]
    path: str
    status: PermissionAccessStatus
    error_message: str
    is_sensitive: bool
    def __init__(self, path: _Optional[str] = ..., status: _Optional[_Union[PermissionAccessStatus, str]] = ..., error_message: _Optional[str] = ..., is_sensitive: bool = ...) -> None: ...

class AgentResult(_message.Message):
    __slots__ = ("request_id", "success", "text", "error", "tool_results", "usage", "duration_ms", "output_json")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    TOOL_RESULTS_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_JSON_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    success: bool
    text: str
    error: str
    tool_results: _containers.RepeatedCompositeFieldContainer[AgentToolResult]
    usage: AgentUsage
    duration_ms: int
    output_json: str
    def __init__(self, request_id: _Optional[str] = ..., success: bool = ..., text: _Optional[str] = ..., error: _Optional[str] = ..., tool_results: _Optional[_Iterable[_Union[AgentToolResult, _Mapping]]] = ..., usage: _Optional[_Union[AgentUsage, _Mapping]] = ..., duration_ms: _Optional[int] = ..., output_json: _Optional[str] = ...) -> None: ...

class AgentToolResult(_message.Message):
    __slots__ = ("tool_name", "tool_call_id", "success", "result", "error", "duration_ms")
    TOOL_NAME_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALL_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    tool_name: str
    tool_call_id: str
    success: bool
    result: str
    error: str
    duration_ms: int
    def __init__(self, tool_name: _Optional[str] = ..., tool_call_id: _Optional[str] = ..., success: bool = ..., result: _Optional[str] = ..., error: _Optional[str] = ..., duration_ms: _Optional[int] = ...) -> None: ...

class AgentUsage(_message.Message):
    __slots__ = ("prompt_tokens", "completion_tokens", "total_tokens")
    PROMPT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    COMPLETION_TOKENS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TOKENS_FIELD_NUMBER: _ClassVar[int]
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    def __init__(self, prompt_tokens: _Optional[int] = ..., completion_tokens: _Optional[int] = ..., total_tokens: _Optional[int] = ...) -> None: ...

class AgentStreamEvent(_message.Message):
    __slots__ = ("request_id", "type", "payload", "timestamp")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    type: AgentEventType
    payload: str
    timestamp: int
    def __init__(self, request_id: _Optional[str] = ..., type: _Optional[_Union[AgentEventType, str]] = ..., payload: _Optional[str] = ..., timestamp: _Optional[int] = ...) -> None: ...

class SkillInfoItem(_message.Message):
    __slots__ = ("name", "description", "author", "version", "model", "origin", "required_bins", "required_env")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_BINS_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_ENV_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    author: str
    version: str
    model: str
    origin: str
    required_bins: _containers.RepeatedScalarFieldContainer[str]
    required_env: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., author: _Optional[str] = ..., version: _Optional[str] = ..., model: _Optional[str] = ..., origin: _Optional[str] = ..., required_bins: _Optional[_Iterable[str]] = ..., required_env: _Optional[_Iterable[str]] = ...) -> None: ...

class SkillListResult(_message.Message):
    __slots__ = ("request_id", "skills")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SKILLS_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    skills: _containers.RepeatedCompositeFieldContainer[SkillInfoItem]
    def __init__(self, request_id: _Optional[str] = ..., skills: _Optional[_Iterable[_Union[SkillInfoItem, _Mapping]]] = ...) -> None: ...

class SkillShowResult(_message.Message):
    __slots__ = ("request_id", "found", "info", "content", "source", "error")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    FOUND_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    found: bool
    info: SkillInfoItem
    content: str
    source: str
    error: str
    def __init__(self, request_id: _Optional[str] = ..., found: bool = ..., info: _Optional[_Union[SkillInfoItem, _Mapping]] = ..., content: _Optional[str] = ..., source: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class SkillRunResult(_message.Message):
    __slots__ = ("request_id", "success", "text", "error", "tool_results", "usage", "duration_ms", "output_json")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    TOOL_RESULTS_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_JSON_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    success: bool
    text: str
    error: str
    tool_results: _containers.RepeatedCompositeFieldContainer[AgentToolResult]
    usage: AgentUsage
    duration_ms: int
    output_json: str
    def __init__(self, request_id: _Optional[str] = ..., success: bool = ..., text: _Optional[str] = ..., error: _Optional[str] = ..., tool_results: _Optional[_Iterable[_Union[AgentToolResult, _Mapping]]] = ..., usage: _Optional[_Union[AgentUsage, _Mapping]] = ..., duration_ms: _Optional[int] = ..., output_json: _Optional[str] = ...) -> None: ...

from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AgentEventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AGENT_EVENT_TYPE_UNSPECIFIED: _ClassVar[AgentEventType]
    AGENT_EVENT_TYPE_TOKEN: _ClassVar[AgentEventType]
    AGENT_EVENT_TYPE_TOOL_START: _ClassVar[AgentEventType]
    AGENT_EVENT_TYPE_TOOL_END: _ClassVar[AgentEventType]
    AGENT_EVENT_TYPE_THINKING: _ClassVar[AgentEventType]
    AGENT_EVENT_TYPE_ERROR: _ClassVar[AgentEventType]
    AGENT_EVENT_TYPE_CANCELLED: _ClassVar[AgentEventType]
    AGENT_EVENT_TYPE_MEDIA: _ClassVar[AgentEventType]
    AGENT_EVENT_TYPE_PLAN_UPDATE: _ClassVar[AgentEventType]
    AGENT_EVENT_TYPE_VERIFY: _ClassVar[AgentEventType]
    AGENT_EVENT_TYPE_SUB_AGENT: _ClassVar[AgentEventType]
    AGENT_EVENT_TYPE_DIFF: _ClassVar[AgentEventType]
    AGENT_EVENT_TYPE_NOTICE: _ClassVar[AgentEventType]
    AGENT_EVENT_TYPE_ASK_USER: _ClassVar[AgentEventType]

class AskStreamErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ASK_STREAM_ERROR_CODE_UNSPECIFIED: _ClassVar[AskStreamErrorCode]
    ASK_STREAM_ERROR_CODE_MACHINE_OFFLINE: _ClassVar[AskStreamErrorCode]
    ASK_STREAM_ERROR_CODE_NO_TARGETS: _ClassVar[AskStreamErrorCode]
    ASK_STREAM_ERROR_CODE_INTERNAL: _ClassVar[AskStreamErrorCode]
    ASK_STREAM_ERROR_CODE_PIN_DENIED: _ClassVar[AskStreamErrorCode]

class ErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ERROR_CODE_UNSPECIFIED: _ClassVar[ErrorCode]
    ERROR_CODE_INVALID_ARGUMENT: _ClassVar[ErrorCode]
    ERROR_CODE_UNAUTHENTICATED: _ClassVar[ErrorCode]
    ERROR_CODE_PERMISSION_DENIED: _ClassVar[ErrorCode]
    ERROR_CODE_NOT_FOUND: _ClassVar[ErrorCode]
    ERROR_CODE_CONFLICT: _ClassVar[ErrorCode]
    ERROR_CODE_RATE_LIMITED: _ClassVar[ErrorCode]
    ERROR_CODE_INTERNAL: _ClassVar[ErrorCode]
    ERROR_CODE_UNAVAILABLE: _ClassVar[ErrorCode]
    ERROR_CODE_DEADLINE_EXCEEDED: _ClassVar[ErrorCode]
    ERROR_CODE_TRANSPORT: _ClassVar[ErrorCode]
    ERROR_CODE_UNSUPPORTED: _ClassVar[ErrorCode]
    ERROR_CODE_PROTOCOL: _ClassVar[ErrorCode]
AGENT_EVENT_TYPE_UNSPECIFIED: AgentEventType
AGENT_EVENT_TYPE_TOKEN: AgentEventType
AGENT_EVENT_TYPE_TOOL_START: AgentEventType
AGENT_EVENT_TYPE_TOOL_END: AgentEventType
AGENT_EVENT_TYPE_THINKING: AgentEventType
AGENT_EVENT_TYPE_ERROR: AgentEventType
AGENT_EVENT_TYPE_CANCELLED: AgentEventType
AGENT_EVENT_TYPE_MEDIA: AgentEventType
AGENT_EVENT_TYPE_PLAN_UPDATE: AgentEventType
AGENT_EVENT_TYPE_VERIFY: AgentEventType
AGENT_EVENT_TYPE_SUB_AGENT: AgentEventType
AGENT_EVENT_TYPE_DIFF: AgentEventType
AGENT_EVENT_TYPE_NOTICE: AgentEventType
AGENT_EVENT_TYPE_ASK_USER: AgentEventType
ASK_STREAM_ERROR_CODE_UNSPECIFIED: AskStreamErrorCode
ASK_STREAM_ERROR_CODE_MACHINE_OFFLINE: AskStreamErrorCode
ASK_STREAM_ERROR_CODE_NO_TARGETS: AskStreamErrorCode
ASK_STREAM_ERROR_CODE_INTERNAL: AskStreamErrorCode
ASK_STREAM_ERROR_CODE_PIN_DENIED: AskStreamErrorCode
ERROR_CODE_UNSPECIFIED: ErrorCode
ERROR_CODE_INVALID_ARGUMENT: ErrorCode
ERROR_CODE_UNAUTHENTICATED: ErrorCode
ERROR_CODE_PERMISSION_DENIED: ErrorCode
ERROR_CODE_NOT_FOUND: ErrorCode
ERROR_CODE_CONFLICT: ErrorCode
ERROR_CODE_RATE_LIMITED: ErrorCode
ERROR_CODE_INTERNAL: ErrorCode
ERROR_CODE_UNAVAILABLE: ErrorCode
ERROR_CODE_DEADLINE_EXCEEDED: ErrorCode
ERROR_CODE_TRANSPORT: ErrorCode
ERROR_CODE_UNSUPPORTED: ErrorCode
ERROR_CODE_PROTOCOL: ErrorCode

class Envelope(_message.Message):
    __slots__ = ("id", "kind", "system_bootstrap_req", "system_bootstrap_resp", "list_machines_req", "machine_roster_snapshot", "ask_machine_req", "ask_event", "ask_done", "ask_stream_error", "list_machine_messages_req", "machine_message_list", "error")
    class Kind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KIND_UNSPECIFIED: _ClassVar[Envelope.Kind]
        KIND_REQUEST: _ClassVar[Envelope.Kind]
        KIND_RESPONSE: _ClassVar[Envelope.Kind]
        KIND_EVENT: _ClassVar[Envelope.Kind]
        KIND_DONE: _ClassVar[Envelope.Kind]
        KIND_ERROR: _ClassVar[Envelope.Kind]
    KIND_UNSPECIFIED: Envelope.Kind
    KIND_REQUEST: Envelope.Kind
    KIND_RESPONSE: Envelope.Kind
    KIND_EVENT: Envelope.Kind
    KIND_DONE: Envelope.Kind
    KIND_ERROR: Envelope.Kind
    ID_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_BOOTSTRAP_REQ_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_BOOTSTRAP_RESP_FIELD_NUMBER: _ClassVar[int]
    LIST_MACHINES_REQ_FIELD_NUMBER: _ClassVar[int]
    MACHINE_ROSTER_SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    ASK_MACHINE_REQ_FIELD_NUMBER: _ClassVar[int]
    ASK_EVENT_FIELD_NUMBER: _ClassVar[int]
    ASK_DONE_FIELD_NUMBER: _ClassVar[int]
    ASK_STREAM_ERROR_FIELD_NUMBER: _ClassVar[int]
    LIST_MACHINE_MESSAGES_REQ_FIELD_NUMBER: _ClassVar[int]
    MACHINE_MESSAGE_LIST_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    id: int
    kind: Envelope.Kind
    system_bootstrap_req: SystemBootstrapRequest
    system_bootstrap_resp: SystemBootstrapResponse
    list_machines_req: ListMachinesRequest
    machine_roster_snapshot: MachineRosterSnapshot
    ask_machine_req: AskMachineRequest
    ask_event: AskEvent
    ask_done: AskDone
    ask_stream_error: AskStreamError
    list_machine_messages_req: ListMachineMessagesRequest
    machine_message_list: MachineMessageList
    error: ErrorInfo
    def __init__(self, id: _Optional[int] = ..., kind: _Optional[_Union[Envelope.Kind, str]] = ..., system_bootstrap_req: _Optional[_Union[SystemBootstrapRequest, _Mapping]] = ..., system_bootstrap_resp: _Optional[_Union[SystemBootstrapResponse, _Mapping]] = ..., list_machines_req: _Optional[_Union[ListMachinesRequest, _Mapping]] = ..., machine_roster_snapshot: _Optional[_Union[MachineRosterSnapshot, _Mapping]] = ..., ask_machine_req: _Optional[_Union[AskMachineRequest, _Mapping]] = ..., ask_event: _Optional[_Union[AskEvent, _Mapping]] = ..., ask_done: _Optional[_Union[AskDone, _Mapping]] = ..., ask_stream_error: _Optional[_Union[AskStreamError, _Mapping]] = ..., list_machine_messages_req: _Optional[_Union[ListMachineMessagesRequest, _Mapping]] = ..., machine_message_list: _Optional[_Union[MachineMessageList, _Mapping]] = ..., error: _Optional[_Union[ErrorInfo, _Mapping]] = ...) -> None: ...

class SystemBootstrapRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebContractRange(_message.Message):
    __slots__ = ("current", "min_client", "max_client")
    CURRENT_FIELD_NUMBER: _ClassVar[int]
    MIN_CLIENT_FIELD_NUMBER: _ClassVar[int]
    MAX_CLIENT_FIELD_NUMBER: _ClassVar[int]
    current: int
    min_client: int
    max_client: int
    def __init__(self, current: _Optional[int] = ..., min_client: _Optional[int] = ..., max_client: _Optional[int] = ...) -> None: ...

class BootstrapUpdate(_message.Message):
    __slots__ = ("phase", "current_version", "new_version")
    PHASE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    NEW_VERSION_FIELD_NUMBER: _ClassVar[int]
    phase: str
    current_version: str
    new_version: str
    def __init__(self, phase: _Optional[str] = ..., current_version: _Optional[str] = ..., new_version: _Optional[str] = ...) -> None: ...

class SystemBootstrapResponse(_message.Message):
    __slots__ = ("version", "bundle_id", "web_contract", "capabilities", "update")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    BUNDLE_ID_FIELD_NUMBER: _ClassVar[int]
    WEB_CONTRACT_FIELD_NUMBER: _ClassVar[int]
    CAPABILITIES_FIELD_NUMBER: _ClassVar[int]
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    version: str
    bundle_id: str
    web_contract: WebContractRange
    capabilities: _containers.RepeatedScalarFieldContainer[str]
    update: BootstrapUpdate
    def __init__(self, version: _Optional[str] = ..., bundle_id: _Optional[str] = ..., web_contract: _Optional[_Union[WebContractRange, _Mapping]] = ..., capabilities: _Optional[_Iterable[str]] = ..., update: _Optional[_Union[BootstrapUpdate, _Mapping]] = ...) -> None: ...

class ListMachinesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MachineRosterSnapshot(_message.Message):
    __slots__ = ("epoch", "sequence", "machines")
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    MACHINES_FIELD_NUMBER: _ClassVar[int]
    epoch: str
    sequence: int
    machines: _containers.RepeatedCompositeFieldContainer[MachineListItem]
    def __init__(self, epoch: _Optional[str] = ..., sequence: _Optional[int] = ..., machines: _Optional[_Iterable[_Union[MachineListItem, _Mapping]]] = ...) -> None: ...

class MachineListItem(_message.Message):
    __slots__ = ("machine_id", "display_name", "portable_name", "fleet_id", "connected", "requires_pin", "last_seen_at", "unread", "last_message_failed", "os", "architecture", "agent_version", "public_key_fingerprint", "public_key_status", "presence", "model_alias", "metrics_reported", "metrics_collected_at", "cpu_percent", "memory_percent", "memory_total_bytes", "disk_percent", "disk_total_bytes", "os_version", "ip_address", "uptime_seconds", "virtual", "is_coordinator", "is_this_device")
    MACHINE_ID_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    PORTABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    CONNECTED_FIELD_NUMBER: _ClassVar[int]
    REQUIRES_PIN_FIELD_NUMBER: _ClassVar[int]
    LAST_SEEN_AT_FIELD_NUMBER: _ClassVar[int]
    UNREAD_FIELD_NUMBER: _ClassVar[int]
    LAST_MESSAGE_FAILED_FIELD_NUMBER: _ClassVar[int]
    OS_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    AGENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_FINGERPRINT_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_STATUS_FIELD_NUMBER: _ClassVar[int]
    PRESENCE_FIELD_NUMBER: _ClassVar[int]
    MODEL_ALIAS_FIELD_NUMBER: _ClassVar[int]
    METRICS_REPORTED_FIELD_NUMBER: _ClassVar[int]
    METRICS_COLLECTED_AT_FIELD_NUMBER: _ClassVar[int]
    CPU_PERCENT_FIELD_NUMBER: _ClassVar[int]
    MEMORY_PERCENT_FIELD_NUMBER: _ClassVar[int]
    MEMORY_TOTAL_BYTES_FIELD_NUMBER: _ClassVar[int]
    DISK_PERCENT_FIELD_NUMBER: _ClassVar[int]
    DISK_TOTAL_BYTES_FIELD_NUMBER: _ClassVar[int]
    OS_VERSION_FIELD_NUMBER: _ClassVar[int]
    IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    UPTIME_SECONDS_FIELD_NUMBER: _ClassVar[int]
    VIRTUAL_FIELD_NUMBER: _ClassVar[int]
    IS_COORDINATOR_FIELD_NUMBER: _ClassVar[int]
    IS_THIS_DEVICE_FIELD_NUMBER: _ClassVar[int]
    machine_id: str
    display_name: str
    portable_name: str
    fleet_id: str
    connected: bool
    requires_pin: bool
    last_seen_at: str
    unread: int
    last_message_failed: bool
    os: str
    architecture: str
    agent_version: str
    public_key_fingerprint: str
    public_key_status: str
    presence: str
    model_alias: str
    metrics_reported: bool
    metrics_collected_at: str
    cpu_percent: float
    memory_percent: float
    memory_total_bytes: int
    disk_percent: float
    disk_total_bytes: int
    os_version: str
    ip_address: str
    uptime_seconds: int
    virtual: bool
    is_coordinator: bool
    is_this_device: bool
    def __init__(self, machine_id: _Optional[str] = ..., display_name: _Optional[str] = ..., portable_name: _Optional[str] = ..., fleet_id: _Optional[str] = ..., connected: _Optional[bool] = ..., requires_pin: _Optional[bool] = ..., last_seen_at: _Optional[str] = ..., unread: _Optional[int] = ..., last_message_failed: _Optional[bool] = ..., os: _Optional[str] = ..., architecture: _Optional[str] = ..., agent_version: _Optional[str] = ..., public_key_fingerprint: _Optional[str] = ..., public_key_status: _Optional[str] = ..., presence: _Optional[str] = ..., model_alias: _Optional[str] = ..., metrics_reported: _Optional[bool] = ..., metrics_collected_at: _Optional[str] = ..., cpu_percent: _Optional[float] = ..., memory_percent: _Optional[float] = ..., memory_total_bytes: _Optional[int] = ..., disk_percent: _Optional[float] = ..., disk_total_bytes: _Optional[int] = ..., os_version: _Optional[str] = ..., ip_address: _Optional[str] = ..., uptime_seconds: _Optional[int] = ..., virtual: _Optional[bool] = ..., is_coordinator: _Optional[bool] = ..., is_this_device: _Optional[bool] = ...) -> None: ...

class AskOptions(_message.Message):
    __slots__ = ("pin", "session", "attachment_ids", "engine", "working_dir", "project_root_id", "model")
    PIN_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    ATTACHMENT_IDS_FIELD_NUMBER: _ClassVar[int]
    ENGINE_FIELD_NUMBER: _ClassVar[int]
    WORKING_DIR_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ROOT_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    pin: str
    session: str
    attachment_ids: _containers.RepeatedScalarFieldContainer[str]
    engine: str
    working_dir: str
    project_root_id: str
    model: str
    def __init__(self, pin: _Optional[str] = ..., session: _Optional[str] = ..., attachment_ids: _Optional[_Iterable[str]] = ..., engine: _Optional[str] = ..., working_dir: _Optional[str] = ..., project_root_id: _Optional[str] = ..., model: _Optional[str] = ...) -> None: ...

class AskMachineRequest(_message.Message):
    __slots__ = ("machine_id", "prompt", "options")
    MACHINE_ID_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    machine_id: str
    prompt: str
    options: AskOptions
    def __init__(self, machine_id: _Optional[str] = ..., prompt: _Optional[str] = ..., options: _Optional[_Union[AskOptions, _Mapping]] = ...) -> None: ...

class AskEvent(_message.Message):
    __slots__ = ("event_type", "payload_json", "machine_id")
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_JSON_FIELD_NUMBER: _ClassVar[int]
    MACHINE_ID_FIELD_NUMBER: _ClassVar[int]
    event_type: AgentEventType
    payload_json: str
    machine_id: str
    def __init__(self, event_type: _Optional[_Union[AgentEventType, str]] = ..., payload_json: _Optional[str] = ..., machine_id: _Optional[str] = ...) -> None: ...

class AskDone(_message.Message):
    __slots__ = ("success", "text", "error", "upstream_status", "provider", "detail", "machine_id", "input_tokens", "output_tokens", "total_tokens", "cache_read_tokens", "cache_write_tokens", "cost_usd", "cost_source", "engine", "model")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_STATUS_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    MACHINE_ID_FIELD_NUMBER: _ClassVar[int]
    INPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TOKENS_FIELD_NUMBER: _ClassVar[int]
    CACHE_READ_TOKENS_FIELD_NUMBER: _ClassVar[int]
    CACHE_WRITE_TOKENS_FIELD_NUMBER: _ClassVar[int]
    COST_USD_FIELD_NUMBER: _ClassVar[int]
    COST_SOURCE_FIELD_NUMBER: _ClassVar[int]
    ENGINE_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    success: bool
    text: str
    error: str
    upstream_status: int
    provider: str
    detail: str
    machine_id: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    cost_usd: float
    cost_source: str
    engine: str
    model: str
    def __init__(self, success: _Optional[bool] = ..., text: _Optional[str] = ..., error: _Optional[str] = ..., upstream_status: _Optional[int] = ..., provider: _Optional[str] = ..., detail: _Optional[str] = ..., machine_id: _Optional[str] = ..., input_tokens: _Optional[int] = ..., output_tokens: _Optional[int] = ..., total_tokens: _Optional[int] = ..., cache_read_tokens: _Optional[int] = ..., cache_write_tokens: _Optional[int] = ..., cost_usd: _Optional[float] = ..., cost_source: _Optional[str] = ..., engine: _Optional[str] = ..., model: _Optional[str] = ...) -> None: ...

class AskStreamError(_message.Message):
    __slots__ = ("code", "message")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: AskStreamErrorCode
    message: str
    def __init__(self, code: _Optional[_Union[AskStreamErrorCode, str]] = ..., message: _Optional[str] = ...) -> None: ...

class ListMachineMessagesRequest(_message.Message):
    __slots__ = ("machine_id", "session", "limit")
    MACHINE_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    machine_id: str
    session: str
    limit: int
    def __init__(self, machine_id: _Optional[str] = ..., session: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class MachineMessageList(_message.Message):
    __slots__ = ("messages",)
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    messages: _containers.RepeatedCompositeFieldContainer[ChatMessage]
    def __init__(self, messages: _Optional[_Iterable[_Union[ChatMessage, _Mapping]]] = ...) -> None: ...

class ChatAttachment(_message.Message):
    __slots__ = ("id", "url", "name", "mime_type", "size_bytes", "type")
    ID_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    url: str
    name: str
    mime_type: str
    size_bytes: int
    type: str
    def __init__(self, id: _Optional[str] = ..., url: _Optional[str] = ..., name: _Optional[str] = ..., mime_type: _Optional[str] = ..., size_bytes: _Optional[int] = ..., type: _Optional[str] = ...) -> None: ...

class ChatMessage(_message.Message):
    __slots__ = ("id", "seq", "author_kind", "author_id", "role", "content", "created_at", "tool_call_id", "event_type", "attachments")
    ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_KIND_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALL_ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    ATTACHMENTS_FIELD_NUMBER: _ClassVar[int]
    id: str
    seq: int
    author_kind: str
    author_id: str
    role: str
    content: str
    created_at: int
    tool_call_id: str
    event_type: int
    attachments: _containers.RepeatedCompositeFieldContainer[ChatAttachment]
    def __init__(self, id: _Optional[str] = ..., seq: _Optional[int] = ..., author_kind: _Optional[str] = ..., author_id: _Optional[str] = ..., role: _Optional[str] = ..., content: _Optional[str] = ..., created_at: _Optional[int] = ..., tool_call_id: _Optional[str] = ..., event_type: _Optional[int] = ..., attachments: _Optional[_Iterable[_Union[ChatAttachment, _Mapping]]] = ...) -> None: ...

class ErrorInfo(_message.Message):
    __slots__ = ("code", "message", "http_status", "retryable", "details_json")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    HTTP_STATUS_FIELD_NUMBER: _ClassVar[int]
    RETRYABLE_FIELD_NUMBER: _ClassVar[int]
    DETAILS_JSON_FIELD_NUMBER: _ClassVar[int]
    code: ErrorCode
    message: str
    http_status: int
    retryable: bool
    details_json: str
    def __init__(self, code: _Optional[_Union[ErrorCode, str]] = ..., message: _Optional[str] = ..., http_status: _Optional[int] = ..., retryable: _Optional[bool] = ..., details_json: _Optional[str] = ...) -> None: ...

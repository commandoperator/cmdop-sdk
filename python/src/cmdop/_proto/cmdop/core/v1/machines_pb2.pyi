from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MachineSummary(_message.Message):
    __slots__ = ("id", "name", "hostname", "os", "os_version", "architecture", "agent_version", "last_heartbeat_at", "presence", "public_key_fingerprint", "public_key_status", "disabled_at", "created_at", "fleets", "specs", "is_jarvis")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    OS_FIELD_NUMBER: _ClassVar[int]
    OS_VERSION_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    AGENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    LAST_HEARTBEAT_AT_FIELD_NUMBER: _ClassVar[int]
    PRESENCE_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_FINGERPRINT_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_STATUS_FIELD_NUMBER: _ClassVar[int]
    DISABLED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    FLEETS_FIELD_NUMBER: _ClassVar[int]
    SPECS_FIELD_NUMBER: _ClassVar[int]
    IS_JARVIS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    hostname: str
    os: str
    os_version: str
    architecture: str
    agent_version: str
    last_heartbeat_at: str
    presence: str
    public_key_fingerprint: str
    public_key_status: str
    disabled_at: str
    created_at: str
    fleets: _containers.RepeatedCompositeFieldContainer[MachineFleetRef]
    specs: MachineSpecs
    is_jarvis: bool
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., hostname: _Optional[str] = ..., os: _Optional[str] = ..., os_version: _Optional[str] = ..., architecture: _Optional[str] = ..., agent_version: _Optional[str] = ..., last_heartbeat_at: _Optional[str] = ..., presence: _Optional[str] = ..., public_key_fingerprint: _Optional[str] = ..., public_key_status: _Optional[str] = ..., disabled_at: _Optional[str] = ..., created_at: _Optional[str] = ..., fleets: _Optional[_Iterable[_Union[MachineFleetRef, _Mapping]]] = ..., specs: _Optional[_Union[MachineSpecs, _Mapping]] = ..., is_jarvis: _Optional[bool] = ...) -> None: ...

class MachineFleetRef(_message.Message):
    __slots__ = ("fleet_id", "slug", "name", "role")
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    SLUG_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    fleet_id: str
    slug: str
    name: str
    role: str
    def __init__(self, fleet_id: _Optional[str] = ..., slug: _Optional[str] = ..., name: _Optional[str] = ..., role: _Optional[str] = ...) -> None: ...

class MachineSpecs(_message.Message):
    __slots__ = ("cpu_model", "cpu_count", "total_ram_bytes", "home_dir", "uid", "device_type", "device_model")
    CPU_MODEL_FIELD_NUMBER: _ClassVar[int]
    CPU_COUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_RAM_BYTES_FIELD_NUMBER: _ClassVar[int]
    HOME_DIR_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_TYPE_FIELD_NUMBER: _ClassVar[int]
    DEVICE_MODEL_FIELD_NUMBER: _ClassVar[int]
    cpu_model: str
    cpu_count: int
    total_ram_bytes: int
    home_dir: str
    uid: int
    device_type: str
    device_model: str
    def __init__(self, cpu_model: _Optional[str] = ..., cpu_count: _Optional[int] = ..., total_ram_bytes: _Optional[int] = ..., home_dir: _Optional[str] = ..., uid: _Optional[int] = ..., device_type: _Optional[str] = ..., device_model: _Optional[str] = ...) -> None: ...

class MachineDetail(_message.Message):
    __slots__ = ("summary", "is_root", "username", "device_id", "public_key", "public_key_version", "public_key_registered_at", "created_by_id", "live_metrics")
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    IS_ROOT_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_VERSION_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_REGISTERED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_ID_FIELD_NUMBER: _ClassVar[int]
    LIVE_METRICS_FIELD_NUMBER: _ClassVar[int]
    summary: MachineSummary
    is_root: bool
    username: str
    device_id: str
    public_key: str
    public_key_version: int
    public_key_registered_at: str
    created_by_id: str
    live_metrics: LiveMetrics
    def __init__(self, summary: _Optional[_Union[MachineSummary, _Mapping]] = ..., is_root: _Optional[bool] = ..., username: _Optional[str] = ..., device_id: _Optional[str] = ..., public_key: _Optional[str] = ..., public_key_version: _Optional[int] = ..., public_key_registered_at: _Optional[str] = ..., created_by_id: _Optional[str] = ..., live_metrics: _Optional[_Union[LiveMetrics, _Mapping]] = ...) -> None: ...

class LiveMetrics(_message.Message):
    __slots__ = ("cpu_usage", "memory_usage", "memory_total_gb", "disk_usage", "disk_total_gb", "battery_level", "is_charging", "is_on_ac_power", "uptime_seconds", "process_count", "recorded_at")
    CPU_USAGE_FIELD_NUMBER: _ClassVar[int]
    MEMORY_USAGE_FIELD_NUMBER: _ClassVar[int]
    MEMORY_TOTAL_GB_FIELD_NUMBER: _ClassVar[int]
    DISK_USAGE_FIELD_NUMBER: _ClassVar[int]
    DISK_TOTAL_GB_FIELD_NUMBER: _ClassVar[int]
    BATTERY_LEVEL_FIELD_NUMBER: _ClassVar[int]
    IS_CHARGING_FIELD_NUMBER: _ClassVar[int]
    IS_ON_AC_POWER_FIELD_NUMBER: _ClassVar[int]
    UPTIME_SECONDS_FIELD_NUMBER: _ClassVar[int]
    PROCESS_COUNT_FIELD_NUMBER: _ClassVar[int]
    RECORDED_AT_FIELD_NUMBER: _ClassVar[int]
    cpu_usage: float
    memory_usage: float
    memory_total_gb: float
    disk_usage: float
    disk_total_gb: float
    battery_level: float
    is_charging: bool
    is_on_ac_power: bool
    uptime_seconds: int
    process_count: int
    recorded_at: str
    def __init__(self, cpu_usage: _Optional[float] = ..., memory_usage: _Optional[float] = ..., memory_total_gb: _Optional[float] = ..., disk_usage: _Optional[float] = ..., disk_total_gb: _Optional[float] = ..., battery_level: _Optional[float] = ..., is_charging: _Optional[bool] = ..., is_on_ac_power: _Optional[bool] = ..., uptime_seconds: _Optional[int] = ..., process_count: _Optional[int] = ..., recorded_at: _Optional[str] = ...) -> None: ...

class ListMachinesRequest(_message.Message):
    __slots__ = ("presence", "q", "limit", "cursor")
    PRESENCE_FIELD_NUMBER: _ClassVar[int]
    Q_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    presence: str
    q: str
    limit: int
    cursor: str
    def __init__(self, presence: _Optional[str] = ..., q: _Optional[str] = ..., limit: _Optional[int] = ..., cursor: _Optional[str] = ...) -> None: ...

class MachineList(_message.Message):
    __slots__ = ("items", "next_cursor", "has_more")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    NEXT_CURSOR_FIELD_NUMBER: _ClassVar[int]
    HAS_MORE_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[MachineSummary]
    next_cursor: str
    has_more: bool
    def __init__(self, items: _Optional[_Iterable[_Union[MachineSummary, _Mapping]]] = ..., next_cursor: _Optional[str] = ..., has_more: _Optional[bool] = ...) -> None: ...

class GetMachineRequest(_message.Message):
    __slots__ = ("machine_id",)
    MACHINE_ID_FIELD_NUMBER: _ClassVar[int]
    machine_id: str
    def __init__(self, machine_id: _Optional[str] = ...) -> None: ...

class MachineInfoRequest(_message.Message):
    __slots__ = ("machine_id",)
    MACHINE_ID_FIELD_NUMBER: _ClassVar[int]
    machine_id: str
    def __init__(self, machine_id: _Optional[str] = ...) -> None: ...

class MachineIdentity(_message.Message):
    __slots__ = ("hostname", "os", "os_version", "kernel_version", "agent_version")
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    OS_FIELD_NUMBER: _ClassVar[int]
    OS_VERSION_FIELD_NUMBER: _ClassVar[int]
    KERNEL_VERSION_FIELD_NUMBER: _ClassVar[int]
    AGENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    hostname: str
    os: str
    os_version: str
    kernel_version: str
    agent_version: str
    def __init__(self, hostname: _Optional[str] = ..., os: _Optional[str] = ..., os_version: _Optional[str] = ..., kernel_version: _Optional[str] = ..., agent_version: _Optional[str] = ...) -> None: ...

class MachineHardware(_message.Message):
    __slots__ = ("cpu", "cpu_cores", "memory_total_gb", "disk_total_gb", "gpu")
    CPU_FIELD_NUMBER: _ClassVar[int]
    CPU_CORES_FIELD_NUMBER: _ClassVar[int]
    MEMORY_TOTAL_GB_FIELD_NUMBER: _ClassVar[int]
    DISK_TOTAL_GB_FIELD_NUMBER: _ClassVar[int]
    GPU_FIELD_NUMBER: _ClassVar[int]
    cpu: str
    cpu_cores: int
    memory_total_gb: float
    disk_total_gb: float
    gpu: str
    def __init__(self, cpu: _Optional[str] = ..., cpu_cores: _Optional[int] = ..., memory_total_gb: _Optional[float] = ..., disk_total_gb: _Optional[float] = ..., gpu: _Optional[str] = ...) -> None: ...

class MachineLiveState(_message.Message):
    __slots__ = ("cpu_usage", "memory_usage", "memory_total_gb", "memory_free_gb", "disk_usage", "disk_total_gb", "disk_free_gb", "battery_level", "is_charging", "is_on_ac_power", "uptime_seconds", "process_count", "recorded_at", "stale")
    CPU_USAGE_FIELD_NUMBER: _ClassVar[int]
    MEMORY_USAGE_FIELD_NUMBER: _ClassVar[int]
    MEMORY_TOTAL_GB_FIELD_NUMBER: _ClassVar[int]
    MEMORY_FREE_GB_FIELD_NUMBER: _ClassVar[int]
    DISK_USAGE_FIELD_NUMBER: _ClassVar[int]
    DISK_TOTAL_GB_FIELD_NUMBER: _ClassVar[int]
    DISK_FREE_GB_FIELD_NUMBER: _ClassVar[int]
    BATTERY_LEVEL_FIELD_NUMBER: _ClassVar[int]
    IS_CHARGING_FIELD_NUMBER: _ClassVar[int]
    IS_ON_AC_POWER_FIELD_NUMBER: _ClassVar[int]
    UPTIME_SECONDS_FIELD_NUMBER: _ClassVar[int]
    PROCESS_COUNT_FIELD_NUMBER: _ClassVar[int]
    RECORDED_AT_FIELD_NUMBER: _ClassVar[int]
    STALE_FIELD_NUMBER: _ClassVar[int]
    cpu_usage: float
    memory_usage: float
    memory_total_gb: float
    memory_free_gb: float
    disk_usage: float
    disk_total_gb: float
    disk_free_gb: float
    battery_level: float
    is_charging: bool
    is_on_ac_power: bool
    uptime_seconds: int
    process_count: int
    recorded_at: str
    stale: bool
    def __init__(self, cpu_usage: _Optional[float] = ..., memory_usage: _Optional[float] = ..., memory_total_gb: _Optional[float] = ..., memory_free_gb: _Optional[float] = ..., disk_usage: _Optional[float] = ..., disk_total_gb: _Optional[float] = ..., disk_free_gb: _Optional[float] = ..., battery_level: _Optional[float] = ..., is_charging: _Optional[bool] = ..., is_on_ac_power: _Optional[bool] = ..., uptime_seconds: _Optional[int] = ..., process_count: _Optional[int] = ..., recorded_at: _Optional[str] = ..., stale: _Optional[bool] = ...) -> None: ...

class MachineSessionInfo(_message.Message):
    __slots__ = ("connected_at", "last_heartbeat_at", "reconnect_count_24h", "token_expires_at", "tunnel_count_active")
    CONNECTED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_HEARTBEAT_AT_FIELD_NUMBER: _ClassVar[int]
    RECONNECT_COUNT_24H_FIELD_NUMBER: _ClassVar[int]
    TOKEN_EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    TUNNEL_COUNT_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    connected_at: str
    last_heartbeat_at: str
    reconnect_count_24h: int
    token_expires_at: str
    tunnel_count_active: int
    def __init__(self, connected_at: _Optional[str] = ..., last_heartbeat_at: _Optional[str] = ..., reconnect_count_24h: _Optional[int] = ..., token_expires_at: _Optional[str] = ..., tunnel_count_active: _Optional[int] = ...) -> None: ...

class MachinePresence(_message.Message):
    __slots__ = ("status", "last_seen_at", "freshness_seconds")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LAST_SEEN_AT_FIELD_NUMBER: _ClassVar[int]
    FRESHNESS_SECONDS_FIELD_NUMBER: _ClassVar[int]
    status: str
    last_seen_at: str
    freshness_seconds: int
    def __init__(self, status: _Optional[str] = ..., last_seen_at: _Optional[str] = ..., freshness_seconds: _Optional[int] = ...) -> None: ...

class MachineFingerprint(_message.Message):
    __slots__ = ("public_key_fingerprint", "public_key_status", "public_key_version")
    PUBLIC_KEY_FINGERPRINT_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_STATUS_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_VERSION_FIELD_NUMBER: _ClassVar[int]
    public_key_fingerprint: str
    public_key_status: str
    public_key_version: int
    def __init__(self, public_key_fingerprint: _Optional[str] = ..., public_key_status: _Optional[str] = ..., public_key_version: _Optional[int] = ...) -> None: ...

class MachineInfoResponse(_message.Message):
    __slots__ = ("identity", "hardware", "live_state", "session", "presence", "fingerprint")
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    HARDWARE_FIELD_NUMBER: _ClassVar[int]
    LIVE_STATE_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    PRESENCE_FIELD_NUMBER: _ClassVar[int]
    FINGERPRINT_FIELD_NUMBER: _ClassVar[int]
    identity: MachineIdentity
    hardware: MachineHardware
    live_state: MachineLiveState
    session: MachineSessionInfo
    presence: MachinePresence
    fingerprint: MachineFingerprint
    def __init__(self, identity: _Optional[_Union[MachineIdentity, _Mapping]] = ..., hardware: _Optional[_Union[MachineHardware, _Mapping]] = ..., live_state: _Optional[_Union[MachineLiveState, _Mapping]] = ..., session: _Optional[_Union[MachineSessionInfo, _Mapping]] = ..., presence: _Optional[_Union[MachinePresence, _Mapping]] = ..., fingerprint: _Optional[_Union[MachineFingerprint, _Mapping]] = ...) -> None: ...

class UpdateMachineRequest(_message.Message):
    __slots__ = ("machine_id", "name")
    MACHINE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    machine_id: str
    name: str
    def __init__(self, machine_id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class DisableMachineRequest(_message.Message):
    __slots__ = ("machine_id",)
    MACHINE_ID_FIELD_NUMBER: _ClassVar[int]
    machine_id: str
    def __init__(self, machine_id: _Optional[str] = ...) -> None: ...

class MachineSpendRequest(_message.Message):
    __slots__ = ("machine_id", "window")
    MACHINE_ID_FIELD_NUMBER: _ClassVar[int]
    WINDOW_FIELD_NUMBER: _ClassVar[int]
    machine_id: str
    window: str
    def __init__(self, machine_id: _Optional[str] = ..., window: _Optional[str] = ...) -> None: ...

class TopModel(_message.Message):
    __slots__ = ("model", "usd", "pct")
    MODEL_FIELD_NUMBER: _ClassVar[int]
    USD_FIELD_NUMBER: _ClassVar[int]
    PCT_FIELD_NUMBER: _ClassVar[int]
    model: str
    usd: float
    pct: float
    def __init__(self, model: _Optional[str] = ..., usd: _Optional[float] = ..., pct: _Optional[float] = ...) -> None: ...

class MachineSpend(_message.Message):
    __slots__ = ("window", "total_usd", "delta_usd", "delta_pct", "tokens_in", "tokens_out", "calls", "ocr_pages", "top_models")
    WINDOW_FIELD_NUMBER: _ClassVar[int]
    TOTAL_USD_FIELD_NUMBER: _ClassVar[int]
    DELTA_USD_FIELD_NUMBER: _ClassVar[int]
    DELTA_PCT_FIELD_NUMBER: _ClassVar[int]
    TOKENS_IN_FIELD_NUMBER: _ClassVar[int]
    TOKENS_OUT_FIELD_NUMBER: _ClassVar[int]
    CALLS_FIELD_NUMBER: _ClassVar[int]
    OCR_PAGES_FIELD_NUMBER: _ClassVar[int]
    TOP_MODELS_FIELD_NUMBER: _ClassVar[int]
    window: str
    total_usd: float
    delta_usd: float
    delta_pct: float
    tokens_in: int
    tokens_out: int
    calls: int
    ocr_pages: int
    top_models: _containers.RepeatedCompositeFieldContainer[TopModel]
    def __init__(self, window: _Optional[str] = ..., total_usd: _Optional[float] = ..., delta_usd: _Optional[float] = ..., delta_pct: _Optional[float] = ..., tokens_in: _Optional[int] = ..., tokens_out: _Optional[int] = ..., calls: _Optional[int] = ..., ocr_pages: _Optional[int] = ..., top_models: _Optional[_Iterable[_Union[TopModel, _Mapping]]] = ...) -> None: ...

class AskRequest(_message.Message):
    __slots__ = ("machine_id", "session_id", "prompt", "agent_type", "timeout_seconds", "options", "pin")
    class OptionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    MACHINE_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    AGENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    PIN_FIELD_NUMBER: _ClassVar[int]
    machine_id: str
    session_id: str
    prompt: str
    agent_type: str
    timeout_seconds: int
    options: _containers.ScalarMap[str, str]
    pin: str
    def __init__(self, machine_id: _Optional[str] = ..., session_id: _Optional[str] = ..., prompt: _Optional[str] = ..., agent_type: _Optional[str] = ..., timeout_seconds: _Optional[int] = ..., options: _Optional[_Mapping[str, str]] = ..., pin: _Optional[str] = ...) -> None: ...

class AskFrame(_message.Message):
    __slots__ = ("event", "confirm_required", "pin_required", "pin_denied")
    EVENT_FIELD_NUMBER: _ClassVar[int]
    CONFIRM_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    PIN_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    PIN_DENIED_FIELD_NUMBER: _ClassVar[int]
    event: StreamEvent
    confirm_required: StreamConfirm
    pin_required: PinRequired
    pin_denied: PinDenied
    def __init__(self, event: _Optional[_Union[StreamEvent, _Mapping]] = ..., confirm_required: _Optional[_Union[StreamConfirm, _Mapping]] = ..., pin_required: _Optional[_Union[PinRequired, _Mapping]] = ..., pin_denied: _Optional[_Union[PinDenied, _Mapping]] = ...) -> None: ...

class StreamEvent(_message.Message):
    __slots__ = ("event_type", "payload_json")
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_JSON_FIELD_NUMBER: _ClassVar[int]
    event_type: int
    payload_json: str
    def __init__(self, event_type: _Optional[int] = ..., payload_json: _Optional[str] = ...) -> None: ...

class DoneInfo(_message.Message):
    __slots__ = ("success", "text", "error", "duration_ms")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    text: str
    error: str
    duration_ms: int
    def __init__(self, success: _Optional[bool] = ..., text: _Optional[str] = ..., error: _Optional[str] = ..., duration_ms: _Optional[int] = ...) -> None: ...

class ErrorInfo(_message.Message):
    __slots__ = ("code", "message")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: str
    message: str
    def __init__(self, code: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class StreamConfirm(_message.Message):
    __slots__ = ("token", "plan", "danger_level")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    PLAN_FIELD_NUMBER: _ClassVar[int]
    DANGER_LEVEL_FIELD_NUMBER: _ClassVar[int]
    token: str
    plan: str
    danger_level: str
    def __init__(self, token: _Optional[str] = ..., plan: _Optional[str] = ..., danger_level: _Optional[str] = ...) -> None: ...

class PinRequired(_message.Message):
    __slots__ = ("challenge_id", "label")
    CHALLENGE_ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    challenge_id: str
    label: str
    def __init__(self, challenge_id: _Optional[str] = ..., label: _Optional[str] = ...) -> None: ...

class PinDenied(_message.Message):
    __slots__ = ("challenge_id", "reason")
    CHALLENGE_ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    challenge_id: str
    reason: str
    def __init__(self, challenge_id: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...

class ConfirmRequired(_message.Message):
    __slots__ = ("token", "plan", "danger_level")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    PLAN_FIELD_NUMBER: _ClassVar[int]
    DANGER_LEVEL_FIELD_NUMBER: _ClassVar[int]
    token: str
    plan: str
    danger_level: str
    def __init__(self, token: _Optional[str] = ..., plan: _Optional[str] = ..., danger_level: _Optional[str] = ...) -> None: ...

class PinAnswer(_message.Message):
    __slots__ = ("challenge_id", "pin")
    CHALLENGE_ID_FIELD_NUMBER: _ClassVar[int]
    PIN_FIELD_NUMBER: _ClassVar[int]
    challenge_id: str
    pin: str
    def __init__(self, challenge_id: _Optional[str] = ..., pin: _Optional[str] = ...) -> None: ...

class ConfirmAnswer(_message.Message):
    __slots__ = ("token", "accept")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    ACCEPT_FIELD_NUMBER: _ClassVar[int]
    token: str
    accept: bool
    def __init__(self, token: _Optional[str] = ..., accept: _Optional[bool] = ...) -> None: ...

class MessagesRequest(_message.Message):
    __slots__ = ("machine_id", "limit")
    MACHINE_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    machine_id: str
    limit: int
    def __init__(self, machine_id: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class MessagesResponse(_message.Message):
    __slots__ = ("agent_session_id", "messages")
    AGENT_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    agent_session_id: str
    messages: _containers.RepeatedCompositeFieldContainer[HistoryMessage]
    def __init__(self, agent_session_id: _Optional[str] = ..., messages: _Optional[_Iterable[_Union[HistoryMessage, _Mapping]]] = ...) -> None: ...

class HistoryMessage(_message.Message):
    __slots__ = ("role", "text", "created_at", "request_id", "success", "error", "duration_ms")
    ROLE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    role: str
    text: str
    created_at: str
    request_id: str
    success: bool
    error: str
    duration_ms: int
    def __init__(self, role: _Optional[str] = ..., text: _Optional[str] = ..., created_at: _Optional[str] = ..., request_id: _Optional[str] = ..., success: _Optional[bool] = ..., error: _Optional[str] = ..., duration_ms: _Optional[int] = ...) -> None: ...

class ClearMessagesRequest(_message.Message):
    __slots__ = ("machine_id",)
    MACHINE_ID_FIELD_NUMBER: _ClassVar[int]
    machine_id: str
    def __init__(self, machine_id: _Optional[str] = ...) -> None: ...

class ClearMessagesResponse(_message.Message):
    __slots__ = ("agent_session_id", "deleted")
    AGENT_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    DELETED_FIELD_NUMBER: _ClassVar[int]
    agent_session_id: str
    deleted: int
    def __init__(self, agent_session_id: _Optional[str] = ..., deleted: _Optional[int] = ...) -> None: ...

class ActiveSessionRequest(_message.Message):
    __slots__ = ("machine_id",)
    MACHINE_ID_FIELD_NUMBER: _ClassVar[int]
    machine_id: str
    def __init__(self, machine_id: _Optional[str] = ...) -> None: ...

class ActiveSessionResponse(_message.Message):
    __slots__ = ("agent_session_id",)
    AGENT_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    agent_session_id: str
    def __init__(self, agent_session_id: _Optional[str] = ...) -> None: ...

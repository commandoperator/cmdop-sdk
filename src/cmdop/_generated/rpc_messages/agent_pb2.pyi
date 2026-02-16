import control_messages_pb2 as _control_messages_pb2
import agent_messages_pb2 as _agent_messages_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RunAgentRequest(_message.Message):
    __slots__ = ("session_id", "request_id", "prompt", "agent_type", "options", "timeout_seconds", "output_schema")
    class OptionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    AGENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    request_id: str
    prompt: str
    agent_type: _control_messages_pb2.AgentType
    options: _containers.ScalarMap[str, str]
    timeout_seconds: int
    output_schema: str
    def __init__(self, session_id: _Optional[str] = ..., request_id: _Optional[str] = ..., prompt: _Optional[str] = ..., agent_type: _Optional[_Union[_control_messages_pb2.AgentType, str]] = ..., options: _Optional[_Mapping[str, str]] = ..., timeout_seconds: _Optional[int] = ..., output_schema: _Optional[str] = ...) -> None: ...

class RunAgentResponse(_message.Message):
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
    tool_results: _containers.RepeatedCompositeFieldContainer[_agent_messages_pb2.AgentToolResult]
    usage: _agent_messages_pb2.AgentUsage
    duration_ms: int
    output_json: str
    def __init__(self, request_id: _Optional[str] = ..., success: bool = ..., text: _Optional[str] = ..., error: _Optional[str] = ..., tool_results: _Optional[_Iterable[_Union[_agent_messages_pb2.AgentToolResult, _Mapping]]] = ..., usage: _Optional[_Union[_agent_messages_pb2.AgentUsage, _Mapping]] = ..., duration_ms: _Optional[int] = ..., output_json: _Optional[str] = ...) -> None: ...

class CancelAgentRequest(_message.Message):
    __slots__ = ("session_id", "request_id", "reason")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    request_id: str
    reason: str
    def __init__(self, session_id: _Optional[str] = ..., request_id: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...

class CancelAgentResponse(_message.Message):
    __slots__ = ("success", "error", "partial_text", "usage")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_TEXT_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    partial_text: str
    usage: _agent_messages_pb2.AgentUsage
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., partial_text: _Optional[str] = ..., usage: _Optional[_Union[_agent_messages_pb2.AgentUsage, _Mapping]] = ...) -> None: ...

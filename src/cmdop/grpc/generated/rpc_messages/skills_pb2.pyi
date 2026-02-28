import agent_messages_pb2 as _agent_messages_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SkillInfo(_message.Message):
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

class SkillListRequest(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class SkillListResponse(_message.Message):
    __slots__ = ("skills", "error")
    SKILLS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    skills: _containers.RepeatedCompositeFieldContainer[SkillInfo]
    error: str
    def __init__(self, skills: _Optional[_Iterable[_Union[SkillInfo, _Mapping]]] = ..., error: _Optional[str] = ...) -> None: ...

class SkillShowRequest(_message.Message):
    __slots__ = ("session_id", "skill_name")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SKILL_NAME_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    skill_name: str
    def __init__(self, session_id: _Optional[str] = ..., skill_name: _Optional[str] = ...) -> None: ...

class SkillShowResponse(_message.Message):
    __slots__ = ("found", "info", "content", "source", "error")
    FOUND_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    found: bool
    info: SkillInfo
    content: str
    source: str
    error: str
    def __init__(self, found: bool = ..., info: _Optional[_Union[SkillInfo, _Mapping]] = ..., content: _Optional[str] = ..., source: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class SkillRunRequest(_message.Message):
    __slots__ = ("session_id", "request_id", "skill_name", "prompt", "options", "timeout_seconds", "output_schema")
    class OptionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SKILL_NAME_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    request_id: str
    skill_name: str
    prompt: str
    options: _containers.ScalarMap[str, str]
    timeout_seconds: int
    output_schema: str
    def __init__(self, session_id: _Optional[str] = ..., request_id: _Optional[str] = ..., skill_name: _Optional[str] = ..., prompt: _Optional[str] = ..., options: _Optional[_Mapping[str, str]] = ..., timeout_seconds: _Optional[int] = ..., output_schema: _Optional[str] = ...) -> None: ...

class SkillRunResponse(_message.Message):
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

from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExtractErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EXTRACT_ERROR_NONE: _ClassVar[ExtractErrorCode]
    EXTRACT_ERROR_INVALID_SCHEMA: _ClassVar[ExtractErrorCode]
    EXTRACT_ERROR_EXTRACTION_FAILED: _ClassVar[ExtractErrorCode]
    EXTRACT_ERROR_VALIDATION_FAILED: _ClassVar[ExtractErrorCode]
    EXTRACT_ERROR_TIMEOUT: _ClassVar[ExtractErrorCode]
    EXTRACT_ERROR_LLM_ERROR: _ClassVar[ExtractErrorCode]
    EXTRACT_ERROR_TOOL_ERROR: _ClassVar[ExtractErrorCode]
    EXTRACT_ERROR_CANCELLED: _ClassVar[ExtractErrorCode]
    EXTRACT_ERROR_SCHEMA_TOO_LARGE: _ClassVar[ExtractErrorCode]
EXTRACT_ERROR_NONE: ExtractErrorCode
EXTRACT_ERROR_INVALID_SCHEMA: ExtractErrorCode
EXTRACT_ERROR_EXTRACTION_FAILED: ExtractErrorCode
EXTRACT_ERROR_VALIDATION_FAILED: ExtractErrorCode
EXTRACT_ERROR_TIMEOUT: ExtractErrorCode
EXTRACT_ERROR_LLM_ERROR: ExtractErrorCode
EXTRACT_ERROR_TOOL_ERROR: ExtractErrorCode
EXTRACT_ERROR_CANCELLED: ExtractErrorCode
EXTRACT_ERROR_SCHEMA_TOO_LARGE: ExtractErrorCode

class ExtractRequest(_message.Message):
    __slots__ = ("prompt", "json_schema", "options")
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    JSON_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    prompt: str
    json_schema: str
    options: ExtractOptions
    def __init__(self, prompt: _Optional[str] = ..., json_schema: _Optional[str] = ..., options: _Optional[_Union[ExtractOptions, _Mapping]] = ...) -> None: ...

class ExtractOptions(_message.Message):
    __slots__ = ("model", "temperature", "max_tokens", "max_retries", "timeout_seconds", "working_directory", "enabled_tools")
    MODEL_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    MAX_TOKENS_FIELD_NUMBER: _ClassVar[int]
    MAX_RETRIES_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    WORKING_DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    ENABLED_TOOLS_FIELD_NUMBER: _ClassVar[int]
    model: str
    temperature: float
    max_tokens: int
    max_retries: int
    timeout_seconds: int
    working_directory: str
    enabled_tools: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, model: _Optional[str] = ..., temperature: _Optional[float] = ..., max_tokens: _Optional[int] = ..., max_retries: _Optional[int] = ..., timeout_seconds: _Optional[int] = ..., working_directory: _Optional[str] = ..., enabled_tools: _Optional[_Iterable[str]] = ...) -> None: ...

class ExtractResponse(_message.Message):
    __slots__ = ("success", "error", "error_code", "reasoning", "result_json", "metrics")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    REASONING_FIELD_NUMBER: _ClassVar[int]
    RESULT_JSON_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    error_code: ExtractErrorCode
    reasoning: str
    result_json: str
    metrics: ExtractMetrics
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., error_code: _Optional[_Union[ExtractErrorCode, str]] = ..., reasoning: _Optional[str] = ..., result_json: _Optional[str] = ..., metrics: _Optional[_Union[ExtractMetrics, _Mapping]] = ...) -> None: ...

class ExtractMetrics(_message.Message):
    __slots__ = ("duration_ms", "llm_duration_ms", "tool_duration_ms", "llm_calls", "tool_calls", "retries", "tokens")
    DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    LLM_DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    TOOL_DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    LLM_CALLS_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALLS_FIELD_NUMBER: _ClassVar[int]
    RETRIES_FIELD_NUMBER: _ClassVar[int]
    TOKENS_FIELD_NUMBER: _ClassVar[int]
    duration_ms: int
    llm_duration_ms: int
    tool_duration_ms: int
    llm_calls: int
    tool_calls: int
    retries: int
    tokens: ExtractTokenUsage
    def __init__(self, duration_ms: _Optional[int] = ..., llm_duration_ms: _Optional[int] = ..., tool_duration_ms: _Optional[int] = ..., llm_calls: _Optional[int] = ..., tool_calls: _Optional[int] = ..., retries: _Optional[int] = ..., tokens: _Optional[_Union[ExtractTokenUsage, _Mapping]] = ...) -> None: ...

class ExtractTokenUsage(_message.Message):
    __slots__ = ("prompt_tokens", "completion_tokens", "total_tokens")
    PROMPT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    COMPLETION_TOKENS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TOKENS_FIELD_NUMBER: _ClassVar[int]
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    def __init__(self, prompt_tokens: _Optional[int] = ..., completion_tokens: _Optional[int] = ..., total_tokens: _Optional[int] = ...) -> None: ...

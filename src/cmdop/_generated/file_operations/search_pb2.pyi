from file_operations import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SearchMatchType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MATCH_TYPE_UNSPECIFIED: _ClassVar[SearchMatchType]
    MATCH_FILENAME: _ClassVar[SearchMatchType]
    MATCH_CONTENT: _ClassVar[SearchMatchType]
MATCH_TYPE_UNSPECIFIED: SearchMatchType
MATCH_FILENAME: SearchMatchType
MATCH_CONTENT: SearchMatchType

class FileSearchRequest(_message.Message):
    __slots__ = ("path", "filename_pattern", "content_pattern", "case_sensitive", "include_hidden", "max_results", "max_depth", "context_lines", "visibility_mode")
    PATH_FIELD_NUMBER: _ClassVar[int]
    FILENAME_PATTERN_FIELD_NUMBER: _ClassVar[int]
    CONTENT_PATTERN_FIELD_NUMBER: _ClassVar[int]
    CASE_SENSITIVE_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_HIDDEN_FIELD_NUMBER: _ClassVar[int]
    MAX_RESULTS_FIELD_NUMBER: _ClassVar[int]
    MAX_DEPTH_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_LINES_FIELD_NUMBER: _ClassVar[int]
    VISIBILITY_MODE_FIELD_NUMBER: _ClassVar[int]
    path: str
    filename_pattern: str
    content_pattern: str
    case_sensitive: bool
    include_hidden: bool
    max_results: int
    max_depth: int
    context_lines: int
    visibility_mode: _common_pb2.FileVisibilityMode
    def __init__(self, path: _Optional[str] = ..., filename_pattern: _Optional[str] = ..., content_pattern: _Optional[str] = ..., case_sensitive: bool = ..., include_hidden: bool = ..., max_results: _Optional[int] = ..., max_depth: _Optional[int] = ..., context_lines: _Optional[int] = ..., visibility_mode: _Optional[_Union[_common_pb2.FileVisibilityMode, str]] = ...) -> None: ...

class FileSearchMatch(_message.Message):
    __slots__ = ("entry", "match_type", "content_matches")
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    MATCH_TYPE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_MATCHES_FIELD_NUMBER: _ClassVar[int]
    entry: _common_pb2.StreamFileEntry
    match_type: SearchMatchType
    content_matches: _containers.RepeatedCompositeFieldContainer[ContentMatch]
    def __init__(self, entry: _Optional[_Union[_common_pb2.StreamFileEntry, _Mapping]] = ..., match_type: _Optional[_Union[SearchMatchType, str]] = ..., content_matches: _Optional[_Iterable[_Union[ContentMatch, _Mapping]]] = ...) -> None: ...

class ContentMatch(_message.Message):
    __slots__ = ("line_number", "line", "column_start", "column_end", "context_before", "context_after")
    LINE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    LINE_FIELD_NUMBER: _ClassVar[int]
    COLUMN_START_FIELD_NUMBER: _ClassVar[int]
    COLUMN_END_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_BEFORE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_AFTER_FIELD_NUMBER: _ClassVar[int]
    line_number: int
    line: str
    column_start: int
    column_end: int
    context_before: _containers.RepeatedScalarFieldContainer[str]
    context_after: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, line_number: _Optional[int] = ..., line: _Optional[str] = ..., column_start: _Optional[int] = ..., column_end: _Optional[int] = ..., context_before: _Optional[_Iterable[str]] = ..., context_after: _Optional[_Iterable[str]] = ...) -> None: ...

class FileSearchResult(_message.Message):
    __slots__ = ("matches", "total_matches", "truncated", "search_path", "files_scanned", "duration_ms")
    MATCHES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_MATCHES_FIELD_NUMBER: _ClassVar[int]
    TRUNCATED_FIELD_NUMBER: _ClassVar[int]
    SEARCH_PATH_FIELD_NUMBER: _ClassVar[int]
    FILES_SCANNED_FIELD_NUMBER: _ClassVar[int]
    DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    matches: _containers.RepeatedCompositeFieldContainer[FileSearchMatch]
    total_matches: int
    truncated: bool
    search_path: str
    files_scanned: int
    duration_ms: int
    def __init__(self, matches: _Optional[_Iterable[_Union[FileSearchMatch, _Mapping]]] = ..., total_matches: _Optional[int] = ..., truncated: bool = ..., search_path: _Optional[str] = ..., files_scanned: _Optional[int] = ..., duration_ms: _Optional[int] = ...) -> None: ...

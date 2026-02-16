from file_operations import directory_pb2 as _directory_pb2
from file_operations import file_crud_pb2 as _file_crud_pb2
from file_operations import archive_pb2 as _archive_pb2
from file_operations import search_pb2 as _search_pb2
from file_operations import hls_pb2 as _hls_pb2
from file_operations import changes_pb2 as _changes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FileOperationRequest(_message.Message):
    __slots__ = ("request_id", "list_directory", "read_file", "write_file", "create_directory", "delete_file", "move_file", "copy_file", "get_info", "create_archive", "search", "get_changes", "hls_get_playlist", "hls_get_segment", "hls_stop_session")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    LIST_DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    READ_FILE_FIELD_NUMBER: _ClassVar[int]
    WRITE_FILE_FIELD_NUMBER: _ClassVar[int]
    CREATE_DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    DELETE_FILE_FIELD_NUMBER: _ClassVar[int]
    MOVE_FILE_FIELD_NUMBER: _ClassVar[int]
    COPY_FILE_FIELD_NUMBER: _ClassVar[int]
    GET_INFO_FIELD_NUMBER: _ClassVar[int]
    CREATE_ARCHIVE_FIELD_NUMBER: _ClassVar[int]
    SEARCH_FIELD_NUMBER: _ClassVar[int]
    GET_CHANGES_FIELD_NUMBER: _ClassVar[int]
    HLS_GET_PLAYLIST_FIELD_NUMBER: _ClassVar[int]
    HLS_GET_SEGMENT_FIELD_NUMBER: _ClassVar[int]
    HLS_STOP_SESSION_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    list_directory: _directory_pb2.FileListDirectoryRequest
    read_file: _file_crud_pb2.FileReadRequest
    write_file: _file_crud_pb2.FileWriteRequest
    create_directory: _directory_pb2.FileCreateDirectoryRequest
    delete_file: _file_crud_pb2.FileDeleteRequest
    move_file: _file_crud_pb2.FileMoveRequest
    copy_file: _file_crud_pb2.FileCopyRequest
    get_info: _file_crud_pb2.FileGetInfoRequest
    create_archive: _archive_pb2.FileCreateArchiveRequest
    search: _search_pb2.FileSearchRequest
    get_changes: _changes_pb2.FileGetChangesRequest
    hls_get_playlist: _hls_pb2.HlsGetPlaylistRequest
    hls_get_segment: _hls_pb2.HlsGetSegmentRequest
    hls_stop_session: _hls_pb2.HlsStopSessionRequest
    def __init__(self, request_id: _Optional[str] = ..., list_directory: _Optional[_Union[_directory_pb2.FileListDirectoryRequest, _Mapping]] = ..., read_file: _Optional[_Union[_file_crud_pb2.FileReadRequest, _Mapping]] = ..., write_file: _Optional[_Union[_file_crud_pb2.FileWriteRequest, _Mapping]] = ..., create_directory: _Optional[_Union[_directory_pb2.FileCreateDirectoryRequest, _Mapping]] = ..., delete_file: _Optional[_Union[_file_crud_pb2.FileDeleteRequest, _Mapping]] = ..., move_file: _Optional[_Union[_file_crud_pb2.FileMoveRequest, _Mapping]] = ..., copy_file: _Optional[_Union[_file_crud_pb2.FileCopyRequest, _Mapping]] = ..., get_info: _Optional[_Union[_file_crud_pb2.FileGetInfoRequest, _Mapping]] = ..., create_archive: _Optional[_Union[_archive_pb2.FileCreateArchiveRequest, _Mapping]] = ..., search: _Optional[_Union[_search_pb2.FileSearchRequest, _Mapping]] = ..., get_changes: _Optional[_Union[_changes_pb2.FileGetChangesRequest, _Mapping]] = ..., hls_get_playlist: _Optional[_Union[_hls_pb2.HlsGetPlaylistRequest, _Mapping]] = ..., hls_get_segment: _Optional[_Union[_hls_pb2.HlsGetSegmentRequest, _Mapping]] = ..., hls_stop_session: _Optional[_Union[_hls_pb2.HlsStopSessionRequest, _Mapping]] = ...) -> None: ...

class FileOperationResult(_message.Message):
    __slots__ = ("request_id", "success", "error_code", "error_message", "suggestions", "can_retry", "list_directory", "read_file", "write_file", "create_directory", "delete_file", "move_file", "copy_file", "get_info", "create_archive", "search", "get_changes", "hls_get_playlist", "hls_get_segment", "hls_stop_session")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUGGESTIONS_FIELD_NUMBER: _ClassVar[int]
    CAN_RETRY_FIELD_NUMBER: _ClassVar[int]
    LIST_DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    READ_FILE_FIELD_NUMBER: _ClassVar[int]
    WRITE_FILE_FIELD_NUMBER: _ClassVar[int]
    CREATE_DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    DELETE_FILE_FIELD_NUMBER: _ClassVar[int]
    MOVE_FILE_FIELD_NUMBER: _ClassVar[int]
    COPY_FILE_FIELD_NUMBER: _ClassVar[int]
    GET_INFO_FIELD_NUMBER: _ClassVar[int]
    CREATE_ARCHIVE_FIELD_NUMBER: _ClassVar[int]
    SEARCH_FIELD_NUMBER: _ClassVar[int]
    GET_CHANGES_FIELD_NUMBER: _ClassVar[int]
    HLS_GET_PLAYLIST_FIELD_NUMBER: _ClassVar[int]
    HLS_GET_SEGMENT_FIELD_NUMBER: _ClassVar[int]
    HLS_STOP_SESSION_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    success: bool
    error_code: str
    error_message: str
    suggestions: _containers.RepeatedScalarFieldContainer[str]
    can_retry: bool
    list_directory: _directory_pb2.FileListDirectoryResult
    read_file: _file_crud_pb2.FileReadResult
    write_file: _file_crud_pb2.FileWriteResult
    create_directory: _directory_pb2.FileCreateDirectoryResult
    delete_file: _file_crud_pb2.FileDeleteResult
    move_file: _file_crud_pb2.FileMoveResult
    copy_file: _file_crud_pb2.FileCopyResult
    get_info: _file_crud_pb2.FileGetInfoResult
    create_archive: _archive_pb2.FileCreateArchiveResult
    search: _search_pb2.FileSearchResult
    get_changes: _changes_pb2.FileGetChangesResult
    hls_get_playlist: _hls_pb2.HlsGetPlaylistResult
    hls_get_segment: _hls_pb2.HlsGetSegmentResult
    hls_stop_session: _hls_pb2.HlsStopSessionResult
    def __init__(self, request_id: _Optional[str] = ..., success: bool = ..., error_code: _Optional[str] = ..., error_message: _Optional[str] = ..., suggestions: _Optional[_Iterable[str]] = ..., can_retry: bool = ..., list_directory: _Optional[_Union[_directory_pb2.FileListDirectoryResult, _Mapping]] = ..., read_file: _Optional[_Union[_file_crud_pb2.FileReadResult, _Mapping]] = ..., write_file: _Optional[_Union[_file_crud_pb2.FileWriteResult, _Mapping]] = ..., create_directory: _Optional[_Union[_directory_pb2.FileCreateDirectoryResult, _Mapping]] = ..., delete_file: _Optional[_Union[_file_crud_pb2.FileDeleteResult, _Mapping]] = ..., move_file: _Optional[_Union[_file_crud_pb2.FileMoveResult, _Mapping]] = ..., copy_file: _Optional[_Union[_file_crud_pb2.FileCopyResult, _Mapping]] = ..., get_info: _Optional[_Union[_file_crud_pb2.FileGetInfoResult, _Mapping]] = ..., create_archive: _Optional[_Union[_archive_pb2.FileCreateArchiveResult, _Mapping]] = ..., search: _Optional[_Union[_search_pb2.FileSearchResult, _Mapping]] = ..., get_changes: _Optional[_Union[_changes_pb2.FileGetChangesResult, _Mapping]] = ..., hls_get_playlist: _Optional[_Union[_hls_pb2.HlsGetPlaylistResult, _Mapping]] = ..., hls_get_segment: _Optional[_Union[_hls_pb2.HlsGetSegmentResult, _Mapping]] = ..., hls_stop_session: _Optional[_Union[_hls_pb2.HlsStopSessionResult, _Mapping]] = ...) -> None: ...

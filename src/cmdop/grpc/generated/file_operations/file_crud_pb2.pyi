from file_operations import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FileReadRequest(_message.Message):
    __slots__ = ("path", "offset", "length", "transcode")
    PATH_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    TRANSCODE_FIELD_NUMBER: _ClassVar[int]
    path: str
    offset: int
    length: int
    transcode: bool
    def __init__(self, path: _Optional[str] = ..., offset: _Optional[int] = ..., length: _Optional[int] = ..., transcode: bool = ...) -> None: ...

class FileReadResult(_message.Message):
    __slots__ = ("content", "encoding", "total_size", "mime_type", "is_truncated", "viewer_type", "is_transcoded", "transcode_complete")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    ENCODING_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SIZE_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_TRUNCATED_FIELD_NUMBER: _ClassVar[int]
    VIEWER_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_TRANSCODED_FIELD_NUMBER: _ClassVar[int]
    TRANSCODE_COMPLETE_FIELD_NUMBER: _ClassVar[int]
    content: bytes
    encoding: str
    total_size: int
    mime_type: str
    is_truncated: bool
    viewer_type: _common_pb2.ViewerType
    is_transcoded: bool
    transcode_complete: bool
    def __init__(self, content: _Optional[bytes] = ..., encoding: _Optional[str] = ..., total_size: _Optional[int] = ..., mime_type: _Optional[str] = ..., is_truncated: bool = ..., viewer_type: _Optional[_Union[_common_pb2.ViewerType, str]] = ..., is_transcoded: bool = ..., transcode_complete: bool = ...) -> None: ...

class FileWriteRequest(_message.Message):
    __slots__ = ("path", "content", "overwrite", "create_parents")
    PATH_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    CREATE_PARENTS_FIELD_NUMBER: _ClassVar[int]
    path: str
    content: bytes
    overwrite: bool
    create_parents: bool
    def __init__(self, path: _Optional[str] = ..., content: _Optional[bytes] = ..., overwrite: bool = ..., create_parents: bool = ...) -> None: ...

class FileWriteResult(_message.Message):
    __slots__ = ("bytes_written", "entry")
    BYTES_WRITTEN_FIELD_NUMBER: _ClassVar[int]
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    bytes_written: int
    entry: _common_pb2.StreamFileEntry
    def __init__(self, bytes_written: _Optional[int] = ..., entry: _Optional[_Union[_common_pb2.StreamFileEntry, _Mapping]] = ...) -> None: ...

class FileDeleteRequest(_message.Message):
    __slots__ = ("path", "recursive")
    PATH_FIELD_NUMBER: _ClassVar[int]
    RECURSIVE_FIELD_NUMBER: _ClassVar[int]
    path: str
    recursive: bool
    def __init__(self, path: _Optional[str] = ..., recursive: bool = ...) -> None: ...

class FileDeleteResult(_message.Message):
    __slots__ = ("deleted_path", "files_deleted", "dirs_deleted")
    DELETED_PATH_FIELD_NUMBER: _ClassVar[int]
    FILES_DELETED_FIELD_NUMBER: _ClassVar[int]
    DIRS_DELETED_FIELD_NUMBER: _ClassVar[int]
    deleted_path: str
    files_deleted: int
    dirs_deleted: int
    def __init__(self, deleted_path: _Optional[str] = ..., files_deleted: _Optional[int] = ..., dirs_deleted: _Optional[int] = ...) -> None: ...

class FileMoveRequest(_message.Message):
    __slots__ = ("source_path", "destination_path", "overwrite")
    SOURCE_PATH_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_PATH_FIELD_NUMBER: _ClassVar[int]
    OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    source_path: str
    destination_path: str
    overwrite: bool
    def __init__(self, source_path: _Optional[str] = ..., destination_path: _Optional[str] = ..., overwrite: bool = ...) -> None: ...

class FileMoveResult(_message.Message):
    __slots__ = ("entry",)
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    entry: _common_pb2.StreamFileEntry
    def __init__(self, entry: _Optional[_Union[_common_pb2.StreamFileEntry, _Mapping]] = ...) -> None: ...

class FileCopyRequest(_message.Message):
    __slots__ = ("source_path", "destination_path", "overwrite", "recursive")
    SOURCE_PATH_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_PATH_FIELD_NUMBER: _ClassVar[int]
    OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    RECURSIVE_FIELD_NUMBER: _ClassVar[int]
    source_path: str
    destination_path: str
    overwrite: bool
    recursive: bool
    def __init__(self, source_path: _Optional[str] = ..., destination_path: _Optional[str] = ..., overwrite: bool = ..., recursive: bool = ...) -> None: ...

class FileCopyResult(_message.Message):
    __slots__ = ("entry", "bytes_copied")
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    BYTES_COPIED_FIELD_NUMBER: _ClassVar[int]
    entry: _common_pb2.StreamFileEntry
    bytes_copied: int
    def __init__(self, entry: _Optional[_Union[_common_pb2.StreamFileEntry, _Mapping]] = ..., bytes_copied: _Optional[int] = ...) -> None: ...

class FileGetInfoRequest(_message.Message):
    __slots__ = ("path",)
    PATH_FIELD_NUMBER: _ClassVar[int]
    path: str
    def __init__(self, path: _Optional[str] = ...) -> None: ...

class FileGetInfoResult(_message.Message):
    __slots__ = ("entry",)
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    entry: _common_pb2.StreamFileEntry
    def __init__(self, entry: _Optional[_Union[_common_pb2.StreamFileEntry, _Mapping]] = ...) -> None: ...

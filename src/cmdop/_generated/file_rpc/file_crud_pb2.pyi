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
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FileReadRpcRequest(_message.Message):
    __slots__ = ("session_id", "path", "offset", "length", "transcode")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    TRANSCODE_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    path: str
    offset: int
    length: int
    transcode: bool
    def __init__(self, session_id: _Optional[str] = ..., path: _Optional[str] = ..., offset: _Optional[int] = ..., length: _Optional[int] = ..., transcode: bool = ...) -> None: ...

class FileReadRpcResponse(_message.Message):
    __slots__ = ("success", "error", "result")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    result: _file_crud_pb2.FileReadResult
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., result: _Optional[_Union[_file_crud_pb2.FileReadResult, _Mapping]] = ...) -> None: ...

class FileWriteRpcRequest(_message.Message):
    __slots__ = ("session_id", "path", "content", "overwrite", "create_parents")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    CREATE_PARENTS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    path: str
    content: bytes
    overwrite: bool
    create_parents: bool
    def __init__(self, session_id: _Optional[str] = ..., path: _Optional[str] = ..., content: _Optional[bytes] = ..., overwrite: bool = ..., create_parents: bool = ...) -> None: ...

class FileWriteRpcResponse(_message.Message):
    __slots__ = ("success", "error", "result")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    result: _file_crud_pb2.FileWriteResult
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., result: _Optional[_Union[_file_crud_pb2.FileWriteResult, _Mapping]] = ...) -> None: ...

class FileCreateDirectoryRpcRequest(_message.Message):
    __slots__ = ("session_id", "path", "create_parents")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    CREATE_PARENTS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    path: str
    create_parents: bool
    def __init__(self, session_id: _Optional[str] = ..., path: _Optional[str] = ..., create_parents: bool = ...) -> None: ...

class FileCreateDirectoryRpcResponse(_message.Message):
    __slots__ = ("success", "error", "result")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    result: _directory_pb2.FileCreateDirectoryResult
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., result: _Optional[_Union[_directory_pb2.FileCreateDirectoryResult, _Mapping]] = ...) -> None: ...

class FileDeleteRpcRequest(_message.Message):
    __slots__ = ("session_id", "path", "recursive")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    RECURSIVE_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    path: str
    recursive: bool
    def __init__(self, session_id: _Optional[str] = ..., path: _Optional[str] = ..., recursive: bool = ...) -> None: ...

class FileDeleteRpcResponse(_message.Message):
    __slots__ = ("success", "error", "result")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    result: _file_crud_pb2.FileDeleteResult
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., result: _Optional[_Union[_file_crud_pb2.FileDeleteResult, _Mapping]] = ...) -> None: ...

class FileMoveRpcRequest(_message.Message):
    __slots__ = ("session_id", "source_path", "destination_path", "overwrite")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_PATH_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_PATH_FIELD_NUMBER: _ClassVar[int]
    OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    source_path: str
    destination_path: str
    overwrite: bool
    def __init__(self, session_id: _Optional[str] = ..., source_path: _Optional[str] = ..., destination_path: _Optional[str] = ..., overwrite: bool = ...) -> None: ...

class FileMoveRpcResponse(_message.Message):
    __slots__ = ("success", "error", "result")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    result: _file_crud_pb2.FileMoveResult
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., result: _Optional[_Union[_file_crud_pb2.FileMoveResult, _Mapping]] = ...) -> None: ...

class FileCopyRpcRequest(_message.Message):
    __slots__ = ("session_id", "source_path", "destination_path", "overwrite", "recursive")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_PATH_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_PATH_FIELD_NUMBER: _ClassVar[int]
    OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    RECURSIVE_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    source_path: str
    destination_path: str
    overwrite: bool
    recursive: bool
    def __init__(self, session_id: _Optional[str] = ..., source_path: _Optional[str] = ..., destination_path: _Optional[str] = ..., overwrite: bool = ..., recursive: bool = ...) -> None: ...

class FileCopyRpcResponse(_message.Message):
    __slots__ = ("success", "error", "result")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    result: _file_crud_pb2.FileCopyResult
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., result: _Optional[_Union[_file_crud_pb2.FileCopyResult, _Mapping]] = ...) -> None: ...

class FileGetInfoRpcRequest(_message.Message):
    __slots__ = ("session_id", "path")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    path: str
    def __init__(self, session_id: _Optional[str] = ..., path: _Optional[str] = ...) -> None: ...

class FileGetInfoRpcResponse(_message.Message):
    __slots__ = ("success", "error", "result")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    result: _file_crud_pb2.FileGetInfoResult
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., result: _Optional[_Union[_file_crud_pb2.FileGetInfoResult, _Mapping]] = ...) -> None: ...

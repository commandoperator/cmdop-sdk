from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StreamingRelayState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RELAY_STATE_UNSPECIFIED: _ClassVar[StreamingRelayState]
    RELAY_INITIATED: _ClassVar[StreamingRelayState]
    RELAY_STREAMING: _ClassVar[StreamingRelayState]
    RELAY_COMPLETED: _ClassVar[StreamingRelayState]
    RELAY_FAILED: _ClassVar[StreamingRelayState]
    RELAY_CANCELLED: _ClassVar[StreamingRelayState]
RELAY_STATE_UNSPECIFIED: StreamingRelayState
RELAY_INITIATED: StreamingRelayState
RELAY_STREAMING: StreamingRelayState
RELAY_COMPLETED: StreamingRelayState
RELAY_FAILED: StreamingRelayState
RELAY_CANCELLED: StreamingRelayState

class FileChunk(_message.Message):
    __slots__ = ("transfer_id", "chunk_index", "total_chunks", "data", "checksum", "offset", "is_last")
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_INDEX_FIELD_NUMBER: _ClassVar[int]
    TOTAL_CHUNKS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    CHECKSUM_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_FIELD_NUMBER: _ClassVar[int]
    transfer_id: str
    chunk_index: int
    total_chunks: int
    data: bytes
    checksum: str
    offset: int
    is_last: bool
    def __init__(self, transfer_id: _Optional[str] = ..., chunk_index: _Optional[int] = ..., total_chunks: _Optional[int] = ..., data: _Optional[bytes] = ..., checksum: _Optional[str] = ..., offset: _Optional[int] = ..., is_last: bool = ...) -> None: ...

class ChunkedUploadRequest(_message.Message):
    __slots__ = ("session_id", "transfer_id", "path", "total_size", "chunk_size", "file_checksum")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SIZE_FIELD_NUMBER: _ClassVar[int]
    CHUNK_SIZE_FIELD_NUMBER: _ClassVar[int]
    FILE_CHECKSUM_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    transfer_id: str
    path: str
    total_size: int
    chunk_size: int
    file_checksum: str
    def __init__(self, session_id: _Optional[str] = ..., transfer_id: _Optional[str] = ..., path: _Optional[str] = ..., total_size: _Optional[int] = ..., chunk_size: _Optional[int] = ..., file_checksum: _Optional[str] = ...) -> None: ...

class ChunkedUploadResponse(_message.Message):
    __slots__ = ("transfer_id", "success", "error", "expected_chunks")
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_CHUNKS_FIELD_NUMBER: _ClassVar[int]
    transfer_id: str
    success: bool
    error: str
    expected_chunks: int
    def __init__(self, transfer_id: _Optional[str] = ..., success: bool = ..., error: _Optional[str] = ..., expected_chunks: _Optional[int] = ...) -> None: ...

class ChunkedDownloadRequest(_message.Message):
    __slots__ = ("session_id", "transfer_id", "path", "total_size", "chunk_size", "file_checksum")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SIZE_FIELD_NUMBER: _ClassVar[int]
    CHUNK_SIZE_FIELD_NUMBER: _ClassVar[int]
    FILE_CHECKSUM_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    transfer_id: str
    path: str
    total_size: int
    chunk_size: int
    file_checksum: str
    def __init__(self, session_id: _Optional[str] = ..., transfer_id: _Optional[str] = ..., path: _Optional[str] = ..., total_size: _Optional[int] = ..., chunk_size: _Optional[int] = ..., file_checksum: _Optional[str] = ...) -> None: ...

class ChunkedDownloadResponse(_message.Message):
    __slots__ = ("transfer_id", "success", "error")
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    transfer_id: str
    success: bool
    error: str
    def __init__(self, transfer_id: _Optional[str] = ..., success: bool = ..., error: _Optional[str] = ...) -> None: ...

class TransferProgress(_message.Message):
    __slots__ = ("transfer_id", "bytes_transferred", "total_bytes", "percentage", "speed_bps", "eta_seconds")
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    BYTES_TRANSFERRED_FIELD_NUMBER: _ClassVar[int]
    TOTAL_BYTES_FIELD_NUMBER: _ClassVar[int]
    PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    SPEED_BPS_FIELD_NUMBER: _ClassVar[int]
    ETA_SECONDS_FIELD_NUMBER: _ClassVar[int]
    transfer_id: str
    bytes_transferred: int
    total_bytes: int
    percentage: float
    speed_bps: float
    eta_seconds: int
    def __init__(self, transfer_id: _Optional[str] = ..., bytes_transferred: _Optional[int] = ..., total_bytes: _Optional[int] = ..., percentage: _Optional[float] = ..., speed_bps: _Optional[float] = ..., eta_seconds: _Optional[int] = ...) -> None: ...

class TransferComplete(_message.Message):
    __slots__ = ("transfer_id", "success", "error", "chunks_transferred", "bytes_transferred", "final_checksum")
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    CHUNKS_TRANSFERRED_FIELD_NUMBER: _ClassVar[int]
    BYTES_TRANSFERRED_FIELD_NUMBER: _ClassVar[int]
    FINAL_CHECKSUM_FIELD_NUMBER: _ClassVar[int]
    transfer_id: str
    success: bool
    error: str
    chunks_transferred: int
    bytes_transferred: int
    final_checksum: str
    def __init__(self, transfer_id: _Optional[str] = ..., success: bool = ..., error: _Optional[str] = ..., chunks_transferred: _Optional[int] = ..., bytes_transferred: _Optional[int] = ..., final_checksum: _Optional[str] = ...) -> None: ...

class BrokerDownloadRequest(_message.Message):
    __slots__ = ("transfer_id", "target_path", "total_size", "file_checksum", "chunk_size")
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_PATH_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SIZE_FIELD_NUMBER: _ClassVar[int]
    FILE_CHECKSUM_FIELD_NUMBER: _ClassVar[int]
    CHUNK_SIZE_FIELD_NUMBER: _ClassVar[int]
    transfer_id: str
    target_path: str
    total_size: int
    file_checksum: str
    chunk_size: int
    def __init__(self, transfer_id: _Optional[str] = ..., target_path: _Optional[str] = ..., total_size: _Optional[int] = ..., file_checksum: _Optional[str] = ..., chunk_size: _Optional[int] = ...) -> None: ...

class BrokerChunkRequest(_message.Message):
    __slots__ = ("transfer_id", "chunk_index", "chunk_size")
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_INDEX_FIELD_NUMBER: _ClassVar[int]
    CHUNK_SIZE_FIELD_NUMBER: _ClassVar[int]
    transfer_id: str
    chunk_index: int
    chunk_size: int
    def __init__(self, transfer_id: _Optional[str] = ..., chunk_index: _Optional[int] = ..., chunk_size: _Optional[int] = ...) -> None: ...

class BrokerChunkResponse(_message.Message):
    __slots__ = ("transfer_id", "chunk_index", "data", "checksum", "is_last")
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_INDEX_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    CHECKSUM_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_FIELD_NUMBER: _ClassVar[int]
    transfer_id: str
    chunk_index: int
    data: bytes
    checksum: str
    is_last: bool
    def __init__(self, transfer_id: _Optional[str] = ..., chunk_index: _Optional[int] = ..., data: _Optional[bytes] = ..., checksum: _Optional[str] = ..., is_last: bool = ...) -> None: ...

class StreamingRelayRequest(_message.Message):
    __slots__ = ("transfer_id", "source_session_id", "target_session_ids", "file_name", "source_path", "target_path", "file_size", "file_checksum", "chunk_size")
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_SESSION_IDS_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    SOURCE_PATH_FIELD_NUMBER: _ClassVar[int]
    TARGET_PATH_FIELD_NUMBER: _ClassVar[int]
    FILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    FILE_CHECKSUM_FIELD_NUMBER: _ClassVar[int]
    CHUNK_SIZE_FIELD_NUMBER: _ClassVar[int]
    transfer_id: str
    source_session_id: str
    target_session_ids: _containers.RepeatedScalarFieldContainer[str]
    file_name: str
    source_path: str
    target_path: str
    file_size: int
    file_checksum: str
    chunk_size: int
    def __init__(self, transfer_id: _Optional[str] = ..., source_session_id: _Optional[str] = ..., target_session_ids: _Optional[_Iterable[str]] = ..., file_name: _Optional[str] = ..., source_path: _Optional[str] = ..., target_path: _Optional[str] = ..., file_size: _Optional[int] = ..., file_checksum: _Optional[str] = ..., chunk_size: _Optional[int] = ...) -> None: ...

class StreamingRelayResponse(_message.Message):
    __slots__ = ("transfer_id", "success", "error", "total_chunks", "connected_targets", "offline_targets")
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    TOTAL_CHUNKS_FIELD_NUMBER: _ClassVar[int]
    CONNECTED_TARGETS_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_TARGETS_FIELD_NUMBER: _ClassVar[int]
    transfer_id: str
    success: bool
    error: str
    total_chunks: int
    connected_targets: _containers.RepeatedScalarFieldContainer[str]
    offline_targets: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, transfer_id: _Optional[str] = ..., success: bool = ..., error: _Optional[str] = ..., total_chunks: _Optional[int] = ..., connected_targets: _Optional[_Iterable[str]] = ..., offline_targets: _Optional[_Iterable[str]] = ...) -> None: ...

class StreamingRelayChunk(_message.Message):
    __slots__ = ("transfer_id", "source_session_id", "target_session_ids", "chunk_index", "total_chunks", "data", "chunk_checksum", "offset", "is_first", "is_last")
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_SESSION_IDS_FIELD_NUMBER: _ClassVar[int]
    CHUNK_INDEX_FIELD_NUMBER: _ClassVar[int]
    TOTAL_CHUNKS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    CHUNK_CHECKSUM_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    IS_FIRST_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_FIELD_NUMBER: _ClassVar[int]
    transfer_id: str
    source_session_id: str
    target_session_ids: _containers.RepeatedScalarFieldContainer[str]
    chunk_index: int
    total_chunks: int
    data: bytes
    chunk_checksum: str
    offset: int
    is_first: bool
    is_last: bool
    def __init__(self, transfer_id: _Optional[str] = ..., source_session_id: _Optional[str] = ..., target_session_ids: _Optional[_Iterable[str]] = ..., chunk_index: _Optional[int] = ..., total_chunks: _Optional[int] = ..., data: _Optional[bytes] = ..., chunk_checksum: _Optional[str] = ..., offset: _Optional[int] = ..., is_first: bool = ..., is_last: bool = ...) -> None: ...

class StreamingRelayAck(_message.Message):
    __slots__ = ("transfer_id", "session_id", "chunk_index", "success", "error")
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_INDEX_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    transfer_id: str
    session_id: str
    chunk_index: int
    success: bool
    error: str
    def __init__(self, transfer_id: _Optional[str] = ..., session_id: _Optional[str] = ..., chunk_index: _Optional[int] = ..., success: bool = ..., error: _Optional[str] = ...) -> None: ...

class StreamingRelayStatus(_message.Message):
    __slots__ = ("transfer_id", "state", "overall_progress", "target_progress", "target_chunks_acked", "chunks_sent", "total_chunks", "error", "file_name", "file_size")
    class TargetProgressEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    class TargetChunksAckedEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    OVERALL_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    TARGET_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    TARGET_CHUNKS_ACKED_FIELD_NUMBER: _ClassVar[int]
    CHUNKS_SENT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_CHUNKS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    FILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    transfer_id: str
    state: StreamingRelayState
    overall_progress: float
    target_progress: _containers.ScalarMap[str, float]
    target_chunks_acked: _containers.ScalarMap[str, int]
    chunks_sent: int
    total_chunks: int
    error: str
    file_name: str
    file_size: int
    def __init__(self, transfer_id: _Optional[str] = ..., state: _Optional[_Union[StreamingRelayState, str]] = ..., overall_progress: _Optional[float] = ..., target_progress: _Optional[_Mapping[str, float]] = ..., target_chunks_acked: _Optional[_Mapping[str, int]] = ..., chunks_sent: _Optional[int] = ..., total_chunks: _Optional[int] = ..., error: _Optional[str] = ..., file_name: _Optional[str] = ..., file_size: _Optional[int] = ...) -> None: ...

class StreamingRelayStatusRequest(_message.Message):
    __slots__ = ("transfer_id",)
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    transfer_id: str
    def __init__(self, transfer_id: _Optional[str] = ...) -> None: ...

class StreamingRelayCancelRequest(_message.Message):
    __slots__ = ("transfer_id", "reason")
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    transfer_id: str
    reason: str
    def __init__(self, transfer_id: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...

class StreamingRelayCancelResponse(_message.Message):
    __slots__ = ("transfer_id", "success", "error")
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    transfer_id: str
    success: bool
    error: str
    def __init__(self, transfer_id: _Optional[str] = ..., success: bool = ..., error: _Optional[str] = ...) -> None: ...

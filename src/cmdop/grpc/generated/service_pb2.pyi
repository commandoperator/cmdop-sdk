import agent_messages_pb2 as _agent_messages_pb2
import control_messages_pb2 as _control_messages_pb2
import rpc_messages_pb2 as _rpc_messages_pb2
from rpc_messages import session_pb2 as _session_pb2
from rpc_messages import terminal_pb2 as _terminal_pb2
from rpc_messages import history_pb2 as _history_pb2
from rpc_messages import device_pb2 as _device_pb2
from rpc_messages import lifecycle_pb2 as _lifecycle_pb2
from rpc_messages import health_pb2 as _health_pb2
from rpc_messages import push_pb2 as _push_pb2
from rpc_messages import extract_pb2 as _extract_pb2
from rpc_messages import agent_pb2 as _agent_pb2
from rpc_messages import skills_pb2 as _skills_pb2
import file_rpc_pb2 as _file_rpc_pb2
from file_rpc import directory_pb2 as _directory_pb2
from file_rpc import file_crud_pb2 as _file_crud_pb2
from file_rpc import archive_pb2 as _archive_pb2
from file_rpc import search_pb2 as _search_pb2
from file_rpc import hls_pb2 as _hls_pb2
import file_operations_pb2 as _file_operations_pb2
from file_operations import common_pb2 as _common_pb2
from file_operations import directory_pb2 as _directory_pb2_1
from file_operations import file_crud_pb2 as _file_crud_pb2_1
from file_operations import archive_pb2 as _archive_pb2_1
from file_operations import search_pb2 as _search_pb2_1
from file_operations import transfer_pb2 as _transfer_pb2
from file_operations import hls_pb2 as _hls_pb2_1
from file_operations import changes_pb2 as _changes_pb2
from file_operations import requests_pb2 as _requests_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GetChallengeRequest(_message.Message):
    __slots__ = ("workspace_id", "session_id")
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    workspace_id: str
    session_id: str
    def __init__(self, workspace_id: _Optional[str] = ..., session_id: _Optional[str] = ...) -> None: ...

class GetChallengeResponse(_message.Message):
    __slots__ = ("nonce", "expires_at", "required_methods")
    NONCE_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_METHODS_FIELD_NUMBER: _ClassVar[int]
    nonce: bytes
    expires_at: int
    required_methods: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, nonce: _Optional[bytes] = ..., expires_at: _Optional[int] = ..., required_methods: _Optional[_Iterable[str]] = ...) -> None: ...

from cmdop.core.v1 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ApiKeySummary(_message.Message):
    __slots__ = ("id", "fleet_id", "name", "key_prefix", "created_at", "expires_at", "last_used_at", "revoked_at", "created_by_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    KEY_PREFIX_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_USED_AT_FIELD_NUMBER: _ClassVar[int]
    REVOKED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    fleet_id: str
    name: str
    key_prefix: str
    created_at: str
    expires_at: str
    last_used_at: str
    revoked_at: str
    created_by_id: str
    def __init__(self, id: _Optional[str] = ..., fleet_id: _Optional[str] = ..., name: _Optional[str] = ..., key_prefix: _Optional[str] = ..., created_at: _Optional[str] = ..., expires_at: _Optional[str] = ..., last_used_at: _Optional[str] = ..., revoked_at: _Optional[str] = ..., created_by_id: _Optional[str] = ...) -> None: ...

class ListKeysRequest(_message.Message):
    __slots__ = ("fleet_id", "page")
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    fleet_id: str
    page: _common_pb2.OffsetPage
    def __init__(self, fleet_id: _Optional[str] = ..., page: _Optional[_Union[_common_pb2.OffsetPage, _Mapping]] = ...) -> None: ...

class ApiKeyList(_message.Message):
    __slots__ = ("items", "offset", "per_page", "total")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    PER_PAGE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[ApiKeySummary]
    offset: int
    per_page: int
    total: int
    def __init__(self, items: _Optional[_Iterable[_Union[ApiKeySummary, _Mapping]]] = ..., offset: _Optional[int] = ..., per_page: _Optional[int] = ..., total: _Optional[int] = ...) -> None: ...

class IssueKeyRequest(_message.Message):
    __slots__ = ("fleet_id", "name", "expires_in_days")
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_IN_DAYS_FIELD_NUMBER: _ClassVar[int]
    fleet_id: str
    name: str
    expires_in_days: int
    def __init__(self, fleet_id: _Optional[str] = ..., name: _Optional[str] = ..., expires_in_days: _Optional[int] = ...) -> None: ...

class IssueKeyResponse(_message.Message):
    __slots__ = ("id", "fleet_id", "name", "raw_token", "expires_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    RAW_TOKEN_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    fleet_id: str
    name: str
    raw_token: str
    expires_at: str
    def __init__(self, id: _Optional[str] = ..., fleet_id: _Optional[str] = ..., name: _Optional[str] = ..., raw_token: _Optional[str] = ..., expires_at: _Optional[str] = ...) -> None: ...

class RevokeKeyRequest(_message.Message):
    __slots__ = ("fleet_id", "key_id")
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    KEY_ID_FIELD_NUMBER: _ClassVar[int]
    fleet_id: str
    key_id: str
    def __init__(self, fleet_id: _Optional[str] = ..., key_id: _Optional[str] = ...) -> None: ...

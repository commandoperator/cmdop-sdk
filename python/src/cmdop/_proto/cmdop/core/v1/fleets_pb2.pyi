from cmdop.core.v1 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FleetSummary(_message.Message):
    __slots__ = ("id", "name", "slug", "mfa_required", "role", "created_at", "disabled_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SLUG_FIELD_NUMBER: _ClassVar[int]
    MFA_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    DISABLED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    slug: str
    mfa_required: _common_pb2.MfaRequirement
    role: str
    created_at: str
    disabled_at: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., slug: _Optional[str] = ..., mfa_required: _Optional[_Union[_common_pb2.MfaRequirement, str]] = ..., role: _Optional[str] = ..., created_at: _Optional[str] = ..., disabled_at: _Optional[str] = ...) -> None: ...

class ListFleetsRequest(_message.Message):
    __slots__ = ("page",)
    PAGE_FIELD_NUMBER: _ClassVar[int]
    page: _common_pb2.OffsetPage
    def __init__(self, page: _Optional[_Union[_common_pb2.OffsetPage, _Mapping]] = ...) -> None: ...

class FleetList(_message.Message):
    __slots__ = ("items", "offset", "per_page", "total")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    PER_PAGE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[FleetSummary]
    offset: int
    per_page: int
    total: int
    def __init__(self, items: _Optional[_Iterable[_Union[FleetSummary, _Mapping]]] = ..., offset: _Optional[int] = ..., per_page: _Optional[int] = ..., total: _Optional[int] = ...) -> None: ...

class GetFleetRequest(_message.Message):
    __slots__ = ("fleet_id",)
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    fleet_id: str
    def __init__(self, fleet_id: _Optional[str] = ...) -> None: ...

class CreateFleetRequest(_message.Message):
    __slots__ = ("name", "slug", "mfa_required")
    NAME_FIELD_NUMBER: _ClassVar[int]
    SLUG_FIELD_NUMBER: _ClassVar[int]
    MFA_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    name: str
    slug: str
    mfa_required: _common_pb2.MfaRequirement
    def __init__(self, name: _Optional[str] = ..., slug: _Optional[str] = ..., mfa_required: _Optional[_Union[_common_pb2.MfaRequirement, str]] = ...) -> None: ...

class UpdateFleetRequest(_message.Message):
    __slots__ = ("fleet_id", "name", "mfa_required")
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MFA_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    fleet_id: str
    name: str
    mfa_required: _common_pb2.MfaRequirement
    def __init__(self, fleet_id: _Optional[str] = ..., name: _Optional[str] = ..., mfa_required: _Optional[_Union[_common_pb2.MfaRequirement, str]] = ...) -> None: ...

class DisableFleetRequest(_message.Message):
    __slots__ = ("fleet_id",)
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    fleet_id: str
    def __init__(self, fleet_id: _Optional[str] = ...) -> None: ...

class MemberInfo(_message.Message):
    __slots__ = ("user_id", "email", "display_name", "role", "joined_at", "invited_by_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    JOINED_AT_FIELD_NUMBER: _ClassVar[int]
    INVITED_BY_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    email: str
    display_name: str
    role: str
    joined_at: str
    invited_by_id: str
    def __init__(self, user_id: _Optional[str] = ..., email: _Optional[str] = ..., display_name: _Optional[str] = ..., role: _Optional[str] = ..., joined_at: _Optional[str] = ..., invited_by_id: _Optional[str] = ...) -> None: ...

class ListMembersRequest(_message.Message):
    __slots__ = ("fleet_id", "page")
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    fleet_id: str
    page: _common_pb2.OffsetPage
    def __init__(self, fleet_id: _Optional[str] = ..., page: _Optional[_Union[_common_pb2.OffsetPage, _Mapping]] = ...) -> None: ...

class MemberList(_message.Message):
    __slots__ = ("items", "offset", "per_page", "total")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    PER_PAGE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[MemberInfo]
    offset: int
    per_page: int
    total: int
    def __init__(self, items: _Optional[_Iterable[_Union[MemberInfo, _Mapping]]] = ..., offset: _Optional[int] = ..., per_page: _Optional[int] = ..., total: _Optional[int] = ...) -> None: ...

class AddMemberRequest(_message.Message):
    __slots__ = ("fleet_id", "email", "role")
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    fleet_id: str
    email: str
    role: str
    def __init__(self, fleet_id: _Optional[str] = ..., email: _Optional[str] = ..., role: _Optional[str] = ...) -> None: ...

class SetMemberRoleRequest(_message.Message):
    __slots__ = ("fleet_id", "user_id", "role")
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    fleet_id: str
    user_id: str
    role: str
    def __init__(self, fleet_id: _Optional[str] = ..., user_id: _Optional[str] = ..., role: _Optional[str] = ...) -> None: ...

class RemoveMemberRequest(_message.Message):
    __slots__ = ("fleet_id", "user_id")
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    fleet_id: str
    user_id: str
    def __init__(self, fleet_id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class ListFleetMachinesRequest(_message.Message):
    __slots__ = ("fleet_id", "presence", "q", "limit", "cursor")
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    PRESENCE_FIELD_NUMBER: _ClassVar[int]
    Q_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    fleet_id: str
    presence: str
    q: str
    limit: int
    cursor: str
    def __init__(self, fleet_id: _Optional[str] = ..., presence: _Optional[str] = ..., q: _Optional[str] = ..., limit: _Optional[int] = ..., cursor: _Optional[str] = ...) -> None: ...

class AttachMachineRequest(_message.Message):
    __slots__ = ("fleet_id", "machine_id")
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    MACHINE_ID_FIELD_NUMBER: _ClassVar[int]
    fleet_id: str
    machine_id: str
    def __init__(self, fleet_id: _Optional[str] = ..., machine_id: _Optional[str] = ...) -> None: ...

class DetachMachineRequest(_message.Message):
    __slots__ = ("fleet_id", "machine_id")
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    MACHINE_ID_FIELD_NUMBER: _ClassVar[int]
    fleet_id: str
    machine_id: str
    def __init__(self, fleet_id: _Optional[str] = ..., machine_id: _Optional[str] = ...) -> None: ...

class MachineFleetLink(_message.Message):
    __slots__ = ("machine_id", "fleet_id", "joined_at", "added_by_id")
    MACHINE_ID_FIELD_NUMBER: _ClassVar[int]
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    JOINED_AT_FIELD_NUMBER: _ClassVar[int]
    ADDED_BY_ID_FIELD_NUMBER: _ClassVar[int]
    machine_id: str
    fleet_id: str
    joined_at: str
    added_by_id: str
    def __init__(self, machine_id: _Optional[str] = ..., fleet_id: _Optional[str] = ..., joined_at: _Optional[str] = ..., added_by_id: _Optional[str] = ...) -> None: ...

from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class MfaRequirement(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MFA_REQUIREMENT_UNSPECIFIED: _ClassVar[MfaRequirement]
    MFA_REQUIREMENT_NONE: _ClassVar[MfaRequirement]
    MFA_REQUIREMENT_OPTIONAL: _ClassVar[MfaRequirement]
    MFA_REQUIREMENT_REQUIRED: _ClassVar[MfaRequirement]

class ScheduleTargetKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SCHEDULE_TARGET_KIND_UNSPECIFIED: _ClassVar[ScheduleTargetKind]
    SCHEDULE_TARGET_KIND_ALL_FLEET_MACHINES: _ClassVar[ScheduleTargetKind]
    SCHEDULE_TARGET_KIND_SPECIFIC_MACHINES: _ClassVar[ScheduleTargetKind]

class ScheduleRunStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SCHEDULE_RUN_STATUS_UNSPECIFIED: _ClassVar[ScheduleRunStatus]
    SCHEDULE_RUN_STATUS_PENDING: _ClassVar[ScheduleRunStatus]
    SCHEDULE_RUN_STATUS_RUNNING: _ClassVar[ScheduleRunStatus]
    SCHEDULE_RUN_STATUS_SUCCESS: _ClassVar[ScheduleRunStatus]
    SCHEDULE_RUN_STATUS_FAILED: _ClassVar[ScheduleRunStatus]
MFA_REQUIREMENT_UNSPECIFIED: MfaRequirement
MFA_REQUIREMENT_NONE: MfaRequirement
MFA_REQUIREMENT_OPTIONAL: MfaRequirement
MFA_REQUIREMENT_REQUIRED: MfaRequirement
SCHEDULE_TARGET_KIND_UNSPECIFIED: ScheduleTargetKind
SCHEDULE_TARGET_KIND_ALL_FLEET_MACHINES: ScheduleTargetKind
SCHEDULE_TARGET_KIND_SPECIFIC_MACHINES: ScheduleTargetKind
SCHEDULE_RUN_STATUS_UNSPECIFIED: ScheduleRunStatus
SCHEDULE_RUN_STATUS_PENDING: ScheduleRunStatus
SCHEDULE_RUN_STATUS_RUNNING: ScheduleRunStatus
SCHEDULE_RUN_STATUS_SUCCESS: ScheduleRunStatus
SCHEDULE_RUN_STATUS_FAILED: ScheduleRunStatus

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class OffsetPage(_message.Message):
    __slots__ = ("offset", "per_page")
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    PER_PAGE_FIELD_NUMBER: _ClassVar[int]
    offset: int
    per_page: int
    def __init__(self, offset: _Optional[int] = ..., per_page: _Optional[int] = ...) -> None: ...

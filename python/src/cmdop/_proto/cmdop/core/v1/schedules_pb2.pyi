from cmdop.core.v1 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ScheduleView(_message.Message):
    __slots__ = ("id", "fleet_id", "name", "description", "cron_expr", "timezone", "command", "target_kind", "is_enabled", "machine_ids", "created_at", "updated_at", "last_run_at", "next_run_at", "last_status")
    ID_FIELD_NUMBER: _ClassVar[int]
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CRON_EXPR_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    TARGET_KIND_FIELD_NUMBER: _ClassVar[int]
    IS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    MACHINE_IDS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_RUN_AT_FIELD_NUMBER: _ClassVar[int]
    NEXT_RUN_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_STATUS_FIELD_NUMBER: _ClassVar[int]
    id: str
    fleet_id: str
    name: str
    description: str
    cron_expr: str
    timezone: str
    command: str
    target_kind: _common_pb2.ScheduleTargetKind
    is_enabled: bool
    machine_ids: _containers.RepeatedScalarFieldContainer[str]
    created_at: str
    updated_at: str
    last_run_at: str
    next_run_at: str
    last_status: _common_pb2.ScheduleRunStatus
    def __init__(self, id: _Optional[str] = ..., fleet_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., cron_expr: _Optional[str] = ..., timezone: _Optional[str] = ..., command: _Optional[str] = ..., target_kind: _Optional[_Union[_common_pb2.ScheduleTargetKind, str]] = ..., is_enabled: _Optional[bool] = ..., machine_ids: _Optional[_Iterable[str]] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ..., last_run_at: _Optional[str] = ..., next_run_at: _Optional[str] = ..., last_status: _Optional[_Union[_common_pb2.ScheduleRunStatus, str]] = ...) -> None: ...

class ScheduleRunView(_message.Message):
    __slots__ = ("id", "schedule_id", "fleet_id", "status", "started_at", "finished_at", "duration_seconds", "error", "command_count")
    ID_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_ID_FIELD_NUMBER: _ClassVar[int]
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    DURATION_SECONDS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    COMMAND_COUNT_FIELD_NUMBER: _ClassVar[int]
    id: str
    schedule_id: str
    fleet_id: str
    status: _common_pb2.ScheduleRunStatus
    started_at: str
    finished_at: str
    duration_seconds: float
    error: str
    command_count: int
    def __init__(self, id: _Optional[str] = ..., schedule_id: _Optional[str] = ..., fleet_id: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.ScheduleRunStatus, str]] = ..., started_at: _Optional[str] = ..., finished_at: _Optional[str] = ..., duration_seconds: _Optional[float] = ..., error: _Optional[str] = ..., command_count: _Optional[int] = ...) -> None: ...

class ListSchedulesRequest(_message.Message):
    __slots__ = ("fleet_id", "page")
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    fleet_id: str
    page: _common_pb2.OffsetPage
    def __init__(self, fleet_id: _Optional[str] = ..., page: _Optional[_Union[_common_pb2.OffsetPage, _Mapping]] = ...) -> None: ...

class ScheduleList(_message.Message):
    __slots__ = ("items", "offset", "per_page", "total")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    PER_PAGE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[ScheduleView]
    offset: int
    per_page: int
    total: int
    def __init__(self, items: _Optional[_Iterable[_Union[ScheduleView, _Mapping]]] = ..., offset: _Optional[int] = ..., per_page: _Optional[int] = ..., total: _Optional[int] = ...) -> None: ...

class GetScheduleRequest(_message.Message):
    __slots__ = ("fleet_id", "schedule_id")
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_ID_FIELD_NUMBER: _ClassVar[int]
    fleet_id: str
    schedule_id: str
    def __init__(self, fleet_id: _Optional[str] = ..., schedule_id: _Optional[str] = ...) -> None: ...

class CreateScheduleRequest(_message.Message):
    __slots__ = ("fleet_id", "name", "description", "cron_expr", "timezone", "command", "target_kind", "is_enabled", "machine_ids")
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CRON_EXPR_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    TARGET_KIND_FIELD_NUMBER: _ClassVar[int]
    IS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    MACHINE_IDS_FIELD_NUMBER: _ClassVar[int]
    fleet_id: str
    name: str
    description: str
    cron_expr: str
    timezone: str
    command: str
    target_kind: _common_pb2.ScheduleTargetKind
    is_enabled: bool
    machine_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, fleet_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., cron_expr: _Optional[str] = ..., timezone: _Optional[str] = ..., command: _Optional[str] = ..., target_kind: _Optional[_Union[_common_pb2.ScheduleTargetKind, str]] = ..., is_enabled: _Optional[bool] = ..., machine_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class UpdateScheduleRequest(_message.Message):
    __slots__ = ("fleet_id", "schedule_id", "name", "description", "cron_expr", "timezone", "command", "target_kind", "is_enabled", "machine_ids")
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CRON_EXPR_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    TARGET_KIND_FIELD_NUMBER: _ClassVar[int]
    IS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    MACHINE_IDS_FIELD_NUMBER: _ClassVar[int]
    fleet_id: str
    schedule_id: str
    name: str
    description: str
    cron_expr: str
    timezone: str
    command: str
    target_kind: _common_pb2.ScheduleTargetKind
    is_enabled: bool
    machine_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, fleet_id: _Optional[str] = ..., schedule_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., cron_expr: _Optional[str] = ..., timezone: _Optional[str] = ..., command: _Optional[str] = ..., target_kind: _Optional[_Union[_common_pb2.ScheduleTargetKind, str]] = ..., is_enabled: _Optional[bool] = ..., machine_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class DeleteScheduleRequest(_message.Message):
    __slots__ = ("fleet_id", "schedule_id")
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_ID_FIELD_NUMBER: _ClassVar[int]
    fleet_id: str
    schedule_id: str
    def __init__(self, fleet_id: _Optional[str] = ..., schedule_id: _Optional[str] = ...) -> None: ...

class TriggerScheduleRequest(_message.Message):
    __slots__ = ("fleet_id", "schedule_id")
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_ID_FIELD_NUMBER: _ClassVar[int]
    fleet_id: str
    schedule_id: str
    def __init__(self, fleet_id: _Optional[str] = ..., schedule_id: _Optional[str] = ...) -> None: ...

class ManualTriggerResponse(_message.Message):
    __slots__ = ("queued", "job_id")
    QUEUED_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    queued: bool
    job_id: str
    def __init__(self, queued: _Optional[bool] = ..., job_id: _Optional[str] = ...) -> None: ...

class ScheduleRunsRequest(_message.Message):
    __slots__ = ("fleet_id", "schedule_id", "limit", "cursor")
    FLEET_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    fleet_id: str
    schedule_id: str
    limit: int
    cursor: str
    def __init__(self, fleet_id: _Optional[str] = ..., schedule_id: _Optional[str] = ..., limit: _Optional[int] = ..., cursor: _Optional[str] = ...) -> None: ...

class ScheduleRunList(_message.Message):
    __slots__ = ("items", "next_cursor")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    NEXT_CURSOR_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[ScheduleRunView]
    next_cursor: str
    def __init__(self, items: _Optional[_Iterable[_Union[ScheduleRunView, _Mapping]]] = ..., next_cursor: _Optional[str] = ...) -> None: ...

"""Curated re-exports of the generated protobuf message classes.

Users import these from ``cmdop.types`` (or the top-level package), never
from ``cmdop._proto`` directly — exactly like the archived REST wrapper
re-exported its curated DTOs from ``cmdop.types`` rather than
``cmdop._generated.models``. If a regen renames a proto symbol, the alias is
absorbed here in one place.
"""

from __future__ import annotations

from cmdop._proto.cmdop.core.v1.fleets_pb2 import (
    FleetList,
    FleetSummary,
    MachineFleetLink,
    MemberInfo,
    MemberList,
)
from cmdop._proto.cmdop.core.v1.keys_pb2 import (
    ApiKeyList,
    ApiKeySummary,
    IssueKeyResponse,
)
from cmdop._proto.cmdop.core.v1.machines_pb2 import (
    ActiveSessionResponse,
    ClearMessagesResponse,
    HistoryMessage,
    LiveMetrics,
    MachineDetail,
    MachineInfoResponse,
    MachineList,
    MachineSpecs,
    MachineSummary,
    MessagesResponse,
)
from cmdop._proto.cmdop.core.v1.schedules_pb2 import (
    ManualTriggerResponse,
    ScheduleList,
    ScheduleRunList,
    ScheduleRunView,
    ScheduleView,
)
from cmdop._proto.cmdop.core.v1.skills_pb2 import (
    SkillCategory,
    SkillCategoryList,
    SkillCreated,
    SkillDetail,
    SkillFile,
    SkillInstall,
    SkillListPage,
    SkillMeta,
    SkillPackages,
    SkillReview,
    SkillReviewPage,
    SkillsPublishResponse,
    SkillsPublishStatusResponse,
    SkillStar,
    SkillSummary,
    SkillTag,
    SkillTagList,
    SkillUpdated,
    SkillVersion,
    SkillVersionList,
)
from cmdop._proto.cmdop.core.v1.tunnels_pb2 import (
    ConnectedSessionOption,
    SessionList,
    TunnelList,
    TunnelView,
)

__all__ = [
    "ActiveSessionResponse",
    "ApiKeyList",
    "ApiKeySummary",
    "ClearMessagesResponse",
    "ConnectedSessionOption",
    "FleetList",
    "FleetSummary",
    "HistoryMessage",
    "IssueKeyResponse",
    "LiveMetrics",
    "MachineDetail",
    "MachineFleetLink",
    "MachineInfoResponse",
    "MachineList",
    "MachineSpecs",
    "MachineSummary",
    "ManualTriggerResponse",
    "MemberInfo",
    "MemberList",
    "MessagesResponse",
    "ScheduleList",
    "ScheduleRunList",
    "ScheduleRunView",
    "ScheduleView",
    "SessionList",
    "SkillCategory",
    "SkillCategoryList",
    "SkillCreated",
    "SkillDetail",
    "SkillFile",
    "SkillInstall",
    "SkillListPage",
    "SkillMeta",
    "SkillPackages",
    "SkillReview",
    "SkillReviewPage",
    "SkillStar",
    "SkillSummary",
    "SkillTag",
    "SkillTagList",
    "SkillUpdated",
    "SkillVersion",
    "SkillVersionList",
    "SkillsPublishResponse",
    "SkillsPublishStatusResponse",
    "TunnelList",
    "TunnelView",
]

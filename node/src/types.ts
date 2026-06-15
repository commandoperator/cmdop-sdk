/**
 * Curated re-exports of the generated protobuf message types.
 *
 * Users import these from `@cmdop/sdk` (under the `types` namespace), never from
 * `./_proto` directly — the mirror of the archived REST wrapper exposing curated
 * DTOs. If a regen renames a proto symbol, the alias is absorbed here.
 */

export type {
  FleetList,
  FleetSummary,
  MachineFleetLink,
  MemberInfo,
  MemberList,
} from "./_proto/cmdop/core/v1/fleets_pb";
export type {
  ApiKeyList,
  ApiKeySummary,
  IssueKeyResponse,
} from "./_proto/cmdop/core/v1/keys_pb";
export type {
  ActiveSessionResponse,
  ClearMessagesResponse,
  HistoryMessage,
  LiveMetrics,
  MachineDetail,
  MachineInfoResponse,
  MachineList,
  MachineSpecs,
  MachineSpend,
  MachineSummary,
  MessagesResponse,
} from "./_proto/cmdop/core/v1/machines_pb";
export type {
  ManualTriggerResponse,
  ScheduleList,
  ScheduleRunList,
  ScheduleRunView,
  ScheduleView,
} from "./_proto/cmdop/core/v1/schedules_pb";
export type {
  ConnectedSessionOption,
  SessionList,
  TunnelList,
  TunnelView,
} from "./_proto/cmdop/core/v1/tunnels_pb";
export type {
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
} from "./_proto/cmdop/core/v1/skills_pb";

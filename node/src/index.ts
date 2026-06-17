/**
 * `@cmdop/sdk` — typed Node SDK for CMDOP.
 *
 * A **thin** client: it spawns the baked-in `cmdop-core` Go binary and speaks a
 * protobuf-length-delimited `Envelope` protocol over its stdio. All relay logic
 * (REST, the `/ask` SSE stream, pin/confirm side-channels, retries, error
 * mapping) lives in the Go core; this package is the typed surface + transport.
 *
 *     import { Client } from "@cmdop/sdk";
 *
 *     const c = new Client({ token: "..." });
 *     const page = await c.machines.list({ presence: "online" });
 *     const text = await c.machines.ask(machineId, "uptime").collect();
 *     await c.close();
 */

export { Client, type ClientOptions } from "./client";
export {
  type ClientConfig,
  DEFAULT_BASE_URL,
  DEFAULT_TIMEOUT_MS,
  resolveConfig,
} from "./config";

// Error hierarchy + mapper.
export {
  AgentStreamError,
  AuthError,
  CmdopError,
  ConflictError,
  ConnectionError,
  mapCoreError,
  NotFoundError,
  PermissionError,
  PinDeniedError,
  PinTimeoutError,
  RateLimitError,
  ServerError,
  TimeoutError,
  UnavailableError,
  ValidationError,
} from "./errors";

// Streaming surface.
export { type AskFrame, AskStream } from "./streaming";

// Resource option shapes that appear in public signatures.
export type { AskOptions, ListMachinesOptions } from "./resources/machines";
export type { ListPageOptions } from "./resources/base";
export type { OpenTunnelOptions } from "./resources/tunnels";
export type {
  CreateScheduleOptions,
  RunsOptions,
  UpdateScheduleOptions,
} from "./resources/schedules";
export type {
  SkillsListOptions,
  SkillsMyOptions,
  SkillsPublishOptions,
  SkillsReviewsOptions,
  SkillsUpdateOptions,
  TaxonomyOptions,
} from "./resources/skills";

// Curated generated DTO types — re-exported as a namespace.
export * as types from "./types";

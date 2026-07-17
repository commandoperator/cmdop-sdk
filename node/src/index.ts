/** Typed Node SDK for the current Cmdop relay. */

export { Client, type ClientOptions } from "./client";
export { type ClientConfig, DEFAULT_TIMEOUT_MS, resolveConfig } from "./config";
export {
  AgentStreamError,
  AuthError,
  CmdopError,
  ConflictError,
  ConnectionError,
  NotFoundError,
  PermissionError,
  ProtocolError,
  RateLimitError,
  ServerError,
  TimeoutError,
  UnavailableError,
  UnsupportedError,
  ValidationError,
} from "./errors";
export { type AskFrame, AskStream } from "./streaming";
export type { AskOptions, MessageOptions } from "./resources/machines";
export * as types from "./types";

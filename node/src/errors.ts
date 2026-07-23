import { ErrorCode, type ErrorInfo } from "./_proto/cmdop/core/v2/contract_pb";

export class CmdopError extends Error {
  readonly retryable: boolean;
  constructor(
    message: string,
    readonly code = "internal",
    readonly status?: number,
    retryable = false,
    readonly details?: unknown,
  ) {
    super(message);
    this.name = new.target.name;
    this.retryable = retryable;
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class AuthError extends CmdopError {}
export class PermissionError extends CmdopError {}
export class NotFoundError extends CmdopError {}
export class ConflictError extends CmdopError {}
export class ValidationError extends CmdopError {}
export class RateLimitError extends CmdopError {}
export class ServerError extends CmdopError {}
export class ConnectionError extends CmdopError {}
export class TimeoutError extends ConnectionError {}
export class UnavailableError extends CmdopError {}
export class UnsupportedError extends CmdopError {}
export class ProtocolError extends CmdopError {}
export class AgentStreamError extends CmdopError {}

const NAMES: Record<number, string> = {
  [ErrorCode.UNSPECIFIED]: "unspecified",
  [ErrorCode.INVALID_ARGUMENT]: "invalid_argument",
  [ErrorCode.UNAUTHENTICATED]: "unauthenticated",
  [ErrorCode.PERMISSION_DENIED]: "permission_denied",
  [ErrorCode.NOT_FOUND]: "not_found",
  [ErrorCode.CONFLICT]: "conflict",
  [ErrorCode.RATE_LIMITED]: "rate_limited",
  [ErrorCode.INTERNAL]: "internal",
  [ErrorCode.UNAVAILABLE]: "unavailable",
  [ErrorCode.DEADLINE_EXCEEDED]: "deadline_exceeded",
  [ErrorCode.TRANSPORT]: "transport",
  [ErrorCode.UNSUPPORTED]: "unsupported",
  [ErrorCode.PROTOCOL]: "protocol",
};

const TYPES: Record<string, typeof CmdopError> = {
  invalid_argument: ValidationError,
  unauthenticated: AuthError,
  permission_denied: PermissionError,
  not_found: NotFoundError,
  conflict: ConflictError,
  rate_limited: RateLimitError,
  internal: ServerError,
  unavailable: UnavailableError,
  deadline_exceeded: TimeoutError,
  transport: ConnectionError,
  unsupported: UnsupportedError,
  protocol: ProtocolError,
};

export function mapCoreError(info: ErrorInfo): CmdopError {
  const code = NAMES[info.code] ?? "internal";
  let details: unknown = info.detailsJson;
  if (info.detailsJson) {
    try {
      details = JSON.parse(info.detailsJson);
    } catch {
      // Preserve the redacted diagnostic string.
    }
  }
  const ErrorType = TYPES[code] ?? CmdopError;
  return new ErrorType(
    info.message || code.replaceAll("_", " "),
    code,
    info.httpStatus,
    info.retryable,
    details,
  );
}

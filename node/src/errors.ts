/**
 * Error hierarchy + `ErrorInfo.code` -> typed error mapper.
 *
 * Mirror of the Python `CmdopError` tree. The Go core emits a terminal `ERROR`
 * frame carrying an `ErrorInfo{code, message}`; {@link mapCoreError} maps that
 * `code` to the right typed exception. Codes are owned by the core
 * (`internal/core/errmap.go`): `auth / permission / not_found / conflict /
 * validation / rate_limit / server / connection` (+ catch-alls).
 */

export class CmdopError extends Error {
  readonly status?: number;
  readonly code?: string;
  readonly body?: unknown;

  constructor(message: string, status?: number, code?: string, body?: unknown) {
    super(message);
    this.name = new.target.name;
    this.status = status;
    this.code = code;
    this.body = body;
    // Restore prototype chain for instanceof across transpile targets.
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class AuthError extends CmdopError {}
export class PermissionError extends CmdopError {}
export class NotFoundError extends CmdopError {}
export class ConflictError extends CmdopError {}
export class ValidationError extends CmdopError {}

export class RateLimitError extends CmdopError {
  readonly retryAfter?: number;
  constructor(message: string, code?: string, retryAfter?: number, body?: unknown) {
    super(message, undefined, code, body);
    this.retryAfter = retryAfter;
  }
}

export class ServerError extends CmdopError {}
export class ConnectionError extends CmdopError {}

/** An `error` outcome from `machines.ask` (machine_offline/timeout/internal). */
export class AgentStreamError extends CmdopError {
  constructor(code: string, message: string) {
    super(message, undefined, code);
  }
}

type CmdopErrorCtor = new (
  message: string,
  status?: number,
  code?: string,
  body?: unknown,
) => CmdopError;

const CODE_MAP: Record<string, CmdopErrorCtor> = {
  auth: AuthError,
  permission: PermissionError,
  not_found: NotFoundError,
  conflict: ConflictError,
  validation: ValidationError,
  server: ServerError,
  connection: ConnectionError,
};

/** Map a core `ErrorInfo{code, message}` to a typed {@link CmdopError}. */
export function mapCoreError(code: string, message: string): CmdopError {
  if (code === "rate_limit") {
    return new RateLimitError(message, code);
  }
  const Ctor = CODE_MAP[code];
  if (Ctor) {
    return new Ctor(message, undefined, code);
  }
  // internal / unknown_op / unsupported / anything new -> base error.
  return new CmdopError(message, undefined, code);
}

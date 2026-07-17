/** Immutable configuration for the local cmdop-core process. */

export const DEFAULT_TIMEOUT_MS = 30_000;

export interface ClientConfig {
  token?: string;
  baseUrl?: string;
  timeoutMs: number;
}

/** `new Client()` works locally; cmdop-core owns local config discovery. */
export function resolveConfig(opts: Partial<ClientConfig> = {}): ClientConfig {
  const env = typeof process !== "undefined" && process.env ? process.env : {};
  const timeoutMs =
    opts.timeoutMs ??
    (env.CMDOP_TIMEOUT_MS ? Number(env.CMDOP_TIMEOUT_MS) : DEFAULT_TIMEOUT_MS);
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
    throw new Error("timeoutMs must be greater than zero");
  }
  const rawBase = opts.baseUrl ?? env.CMDOP_BASE_URL;
  return {
    token: opts.token ?? env.CMDOP_TOKEN ?? undefined,
    baseUrl: rawBase ? rawBase.replace(/\/+$/, "") : undefined,
    timeoutMs,
  };
}

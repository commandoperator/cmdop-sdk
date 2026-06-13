/**
 * Client configuration + env-var resolution.
 *
 * Precedence for every field: explicit > env > default — the exact mirror of the
 * Python `ClientConfig.resolve()`. The resolved credentials + base URLs are passed
 * to the spawned `cmdop-core` over env (never a port):
 *   - relay plane: `CMDOP_TOKEN` / `CMDOP_BASE_URL` (machines, fleets, …)
 *   - Django platform plane: `CMDOP_API_KEY` / `CMDOP_API_BASE_URL` (skills)
 * The two credentials are SEPARATE and must not be conflated.
 */

export const DEFAULT_BASE_URL = "https://cloud.cmdop.com";
export const DEFAULT_API_BASE_URL = "https://api.cmdop.com";
export const DEFAULT_TIMEOUT_MS = 30_000;

export interface ClientConfig {
  token: string;
  baseUrl: string;
  fleetId?: string;
  timeoutMs: number;
  /** Django platform plane (skills) — UserAPIKey / X-Api-Key. Separate credential. */
  apiKey?: string;
  /** Django platform plane base URL — separate from the relay `baseUrl`. */
  apiBaseUrl: string;
}

/**
 * Resolve a {@link ClientConfig} from explicit options, environment, then defaults.
 *
 * Relay token sources (token wins if both set): `CMDOP_TOKEN`, then `CMDOP_API_KEY`.
 * Throws if no token can be resolved. The skills plane reads `apiKey` from
 * `CMDOP_API_KEY` independently.
 */
export function resolveConfig(opts: Partial<ClientConfig> = {}): ClientConfig {
  const env = typeof process !== "undefined" && process.env ? process.env : {};

  const token = opts.token ?? env.CMDOP_TOKEN ?? env.CMDOP_API_KEY;
  if (!token) {
    throw new Error(
      "No token. Pass token or set CMDOP_TOKEN (or CMDOP_API_KEY).",
    );
  }

  const baseUrl = stripTrailingSlash(
    opts.baseUrl ?? env.CMDOP_BASE_URL ?? DEFAULT_BASE_URL,
  );

  const fleetId = opts.fleetId ?? env.CMDOP_FLEET_ID ?? undefined;

  const timeoutMs =
    opts.timeoutMs ??
    (env.CMDOP_TIMEOUT_MS ? Number(env.CMDOP_TIMEOUT_MS) : DEFAULT_TIMEOUT_MS);

  const apiKey = opts.apiKey ?? env.CMDOP_API_KEY ?? undefined;

  const apiBaseUrl = stripTrailingSlash(
    opts.apiBaseUrl ?? env.CMDOP_API_BASE_URL ?? DEFAULT_API_BASE_URL,
  );

  return { token, baseUrl, fleetId, timeoutMs, apiKey, apiBaseUrl };
}

function stripTrailingSlash(url: string): string {
  return url.endsWith("/") ? url.slice(0, -1) : url;
}

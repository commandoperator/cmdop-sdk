import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  DEFAULT_BASE_URL,
  DEFAULT_TIMEOUT_MS,
  resolveConfig,
} from "../src/config";

const ENV_KEYS = [
  "CMDOP_TOKEN",
  "CMDOP_API_KEY",
  "CMDOP_BASE_URL",
  "CMDOP_FLEET_ID",
  "CMDOP_TIMEOUT_MS",
];

describe("resolveConfig precedence", () => {
  const saved: Record<string, string | undefined> = {};
  beforeEach(() => {
    for (const k of ENV_KEYS) {
      saved[k] = process.env[k];
      delete process.env[k];
    }
  });
  afterEach(() => {
    for (const k of ENV_KEYS) {
      if (saved[k] === undefined) delete process.env[k];
      else process.env[k] = saved[k];
    }
  });

  it("explicit token wins over env", () => {
    process.env.CMDOP_TOKEN = "from-env";
    expect(resolveConfig({ token: "explicit" }).token).toBe("explicit");
  });

  it("falls back to CMDOP_TOKEN", () => {
    process.env.CMDOP_TOKEN = "env-token";
    expect(resolveConfig().token).toBe("env-token");
  });

  it("CMDOP_TOKEN wins over CMDOP_API_KEY", () => {
    process.env.CMDOP_TOKEN = "the-token";
    process.env.CMDOP_API_KEY = "the-api-key";
    expect(resolveConfig().token).toBe("the-token");
  });

  it("uses CMDOP_API_KEY when token absent", () => {
    process.env.CMDOP_API_KEY = "the-api-key";
    expect(resolveConfig().token).toBe("the-api-key");
  });

  it("throws when no token", () => {
    expect(() => resolveConfig()).toThrow(/No token/);
  });

  it("defaults", () => {
    const cfg = resolveConfig({ token: "t" });
    expect(cfg.baseUrl).toBe(DEFAULT_BASE_URL);
    expect(cfg.fleetId).toBeUndefined();
    expect(cfg.timeoutMs).toBe(DEFAULT_TIMEOUT_MS);
  });

  it("base url precedence + trailing slash strip", () => {
    process.env.CMDOP_BASE_URL = "https://env.example.com";
    expect(resolveConfig({ token: "t" }).baseUrl).toBe("https://env.example.com");
    expect(resolveConfig({ token: "t", baseUrl: "https://x.example.com/" }).baseUrl).toBe(
      "https://x.example.com",
    );
  });

  it("fleet + timeout from env", () => {
    process.env.CMDOP_FLEET_ID = "fleet-123";
    process.env.CMDOP_TIMEOUT_MS = "5000";
    const cfg = resolveConfig({ token: "t" });
    expect(cfg.fleetId).toBe("fleet-123");
    expect(cfg.timeoutMs).toBe(5000);
  });
});

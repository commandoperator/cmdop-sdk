import { afterEach, describe, expect, it } from "vitest";
import { DEFAULT_TIMEOUT_MS, resolveConfig } from "../src/config";

const saved = { ...process.env };
afterEach(() => {
  process.env = { ...saved };
});

describe("v2 config", () => {
  it("needs no explicit local configuration", () => {
    delete process.env.CMDOP_TOKEN;
    delete process.env.CMDOP_BASE_URL;
    expect(resolveConfig()).toEqual({ token: undefined, baseUrl: undefined, timeoutMs: DEFAULT_TIMEOUT_MS });
  });

  it("uses explicit values before environment", () => {
    process.env.CMDOP_TOKEN = "env";
    expect(resolveConfig({ token: "arg", baseUrl: "https://relay///", timeoutMs: 99 })).toEqual({
      token: "arg",
      baseUrl: "https://relay",
      timeoutMs: 99,
    });
  });

  it("never treats the platform API key as a relay token", () => {
    delete process.env.CMDOP_TOKEN;
    process.env.CMDOP_API_KEY = "platform-only";
    expect(resolveConfig().token).toBeUndefined();
  });

  it("rejects a non-positive timeout", () => {
    expect(() => resolveConfig({ timeoutMs: 0 })).toThrow(/greater than zero/);
  });
});

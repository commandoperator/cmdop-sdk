import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { expect, it } from "vitest";
import { actualSurface } from "../src/_parity";

it("matches shipped v2 capabilities", () => {
  const path = fileURLToPath(new URL("../../../core/parity/capabilities.v2.json", import.meta.url));
  const capabilities = JSON.parse(readFileSync(path, "utf8")).capabilities as Array<{
    id: string;
    status: string;
  }>;
  const expected: Record<string, string[]> = {};
  for (const capability of capabilities.filter(({ status }) => status === "shipped")) {
    const [namespace, method] = capability.id.split(".");
    (expected[namespace] ??= []).push(method);
  }
  for (const methods of Object.values(expected)) methods.sort();
  expect(actualSurface()).toEqual(expected);
});

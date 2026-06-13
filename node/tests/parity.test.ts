/**
 * Cross-language parity gate (Node half, Phase 5 §5.3).
 *
 * Introspects the Node SDK's actual resource surface and asserts it equals the
 * checked-in `parity/manifest.json`. The Python SDK runs the mirror test
 * (`sdk/python/tests/test_parity.py`); `parity/check.py` runs both. Any namespace or
 * method that exists in one language but not the other — or drifts from the
 * manifest — fails CI. camelCase is normalised to snake_case in `_parity.ts`.
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { actualSurface } from "../src/_parity";

const manifestPath = fileURLToPath(new URL("../../../core/parity/manifest.json", import.meta.url));
const manifest = JSON.parse(readFileSync(manifestPath, "utf8")).namespaces as Record<
  string,
  string[]
>;

const surface = actualSurface();

describe("cross-language parity: node surface == manifest", () => {
  it("exposes exactly the manifest namespaces", () => {
    expect(Object.keys(surface).sort()).toEqual(Object.keys(manifest).sort());
  });

  for (const [ns, methods] of Object.entries(manifest)) {
    it(`namespace "${ns}" has exactly the manifest methods`, () => {
      expect(surface[ns]).toBeDefined();
      expect(surface[ns]).toEqual([...methods].sort());
    });
  }
});

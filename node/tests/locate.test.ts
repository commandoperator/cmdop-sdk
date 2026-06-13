/**
 * Binary-locate tests for the single fat-package model: the `CMDOP_CORE_BINARY`
 * override path, defensive chmod, and the actionable error when neither override
 * nor a baked `bin/cmdop-core-<os>-<arch>` binary is present. In the dev tree the
 * `bin/` dir is not staged (stage_packages.py bakes it at release time), so the
 * resolver throws an actionable error pointing at CMDOP_CORE_BINARY.
 */

import { chmodSync, mkdtempSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { locateBinary } from "../src/locate";

describe("locateBinary", () => {
  let saved: string | undefined;
  beforeEach(() => {
    saved = process.env.CMDOP_CORE_BINARY;
    delete process.env.CMDOP_CORE_BINARY;
  });
  afterEach(() => {
    if (saved === undefined) delete process.env.CMDOP_CORE_BINARY;
    else process.env.CMDOP_CORE_BINARY = saved;
  });

  it("override resolves and is made executable", () => {
    const dir = mkdtempSync(join(tmpdir(), "cmdop-locate-"));
    const bin = join(dir, "cmdop-core");
    writeFileSync(bin, "#!/bin/sh\nexit 0\n");
    chmodSync(bin, 0o644); // strip exec bit; locate must re-add it
    process.env.CMDOP_CORE_BINARY = bin;

    const resolved = locateBinary();
    expect(resolved).toBe(bin);
    if (process.platform !== "win32") {
      expect(statSync(resolved).mode & 0o100).toBeTruthy(); // owner-exec bit set
    }
  });

  it("override pointing at a missing file throws", () => {
    process.env.CMDOP_CORE_BINARY = join(tmpdir(), "definitely-not-here-xyz");
    expect(() => locateBinary()).toThrow(/points at a missing file/);
  });

  it("no override + no baked binary throws an actionable error", () => {
    // In the dev tree the bin/ dir is not staged, so locate must tell the user
    // to set CMDOP_CORE_BINARY (or that the platform is unbuilt).
    expect(() => locateBinary()).toThrow(/CMDOP_CORE_BINARY|prebuilt binary/);
  });

  it("the not-found error names the host's per-platform binary", () => {
    // Fat model: the resolver looks for cmdop-core-<platform>-<arch>[.exe]. For
    // a supported host the error mentions that exact filename (proving the slug
    // is computed from process.platform/process.arch, not hardcoded).
    const key = `${process.platform}-${process.arch}`;
    const supported = new Set([
      "darwin-arm64",
      "darwin-x64",
      "linux-x64",
      "linux-arm64",
      "win32-x64",
    ]);
    if (supported.has(key)) {
      const exe = process.platform === "win32" ? ".exe" : "";
      expect(() => locateBinary()).toThrow(
        new RegExp(`cmdop-core-${key}${exe.replace(".", "\\.")}`),
      );
    } else {
      // Unsupported platform: a clear "no prebuilt binary for <key>" error.
      expect(() => locateBinary()).toThrow(/no prebuilt binary/);
    }
  });
});

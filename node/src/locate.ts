/**
 * Locate the `cmdop-core` binary the client spawns.
 *
 * Single fat-package model (report 01 §5): all 5 prebuilt binaries are baked
 * into `@cmdop/sdk/bin/cmdop-core-<os>-<arch>[.exe]`. There are no per-platform
 * sub-packages and no `optionalDependencies` — the runtime resolver below picks
 * the host's binary from the local `bin/` dir, so we are structurally immune to
 * npm's optionalDependencies lockfile-pruning bug class (#4828).
 *
 * Resolution order:
 *   1. `CMDOP_CORE_BINARY` env override (dev / local tests / offline escape
 *      hatch — point it at a `go build`'d binary).
 *   2. `bin/cmdop-core-${process.platform}-${process.arch}${.exe}` resolved
 *      relative to THIS package's root (found robustly for ESM + CJS).
 *
 * The binary is `chmod`'d +x defensively (npm/pnpm/umask or a CI artifact
 * upload can strip the exec bit) and the Windows `.exe` suffix is honoured.
 */

import { chmodSync, existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

/**
 * Supported `${process.platform}-${process.arch}` keys, kept in lockstep with
 * `core/scripts/stage_packages.py` TARGETS. process.arch is already x64/arm64
 * and process.platform is already darwin/linux/win32, so the key maps 1:1 to a
 * baked binary name (`cmdop-core-<key>`).
 */
const SUPPORTED_PLATFORMS = new Set([
  "darwin-arm64",
  "darwin-x64",
  "linux-x64",
  "linux-arm64",
  "win32-x64",
]);

function binaryName(): string {
  const key = `${process.platform}-${process.arch}`;
  const exe = process.platform === "win32" ? ".exe" : "";
  return `cmdop-core-${key}${exe}`;
}

/**
 * The directory of THIS module, resolved for both ESM (`import.meta.url`) and
 * CJS (`__dirname`). Anchoring to the module file — never `process.cwd()` —
 * means the binary is found wherever the package is installed, including
 * workspaces and symlinked installs.
 */
function moduleDir(): string {
  // CJS bundle: tsup emits `__dirname`. ESM bundle: reconstruct from the URL.
  // Guard `import.meta` access so the CJS build (where it is undefined) does
  // not throw — tsup rewrites one branch per format, but be defensive.
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const metaUrl = (import.meta as any)?.url as string | undefined;
    if (metaUrl) return dirname(fileURLToPath(metaUrl));
  } catch {
    /* not ESM — fall through to __dirname */
  }
  if (typeof __dirname !== "undefined") return __dirname;
  // Last resort: resolve relative to cwd (should never be reached in practice).
  return resolve(".");
}

/**
 * Find the package root (the dir containing `bin/`). The built bundle lives in
 * `dist/`, so the package root is one level up; but be robust to either layout
 * by checking `./bin` and `../bin` relative to the module dir.
 */
function packageBinDir(): string {
  const here = moduleDir();
  const candidates = [
    join(here, "bin"), // module sits at package root (unbundled / tests)
    join(here, "..", "bin"), // module sits in dist/ (the published bundle)
    join(here, "..", "..", "bin"),
  ];
  for (const c of candidates) {
    if (existsSync(c)) return c;
  }
  // Default to the dist/.. layout even if the dir does not yet exist, so the
  // error below names a sensible path.
  return join(here, "..", "bin");
}

export function locateBinary(): string {
  const override = process.env.CMDOP_CORE_BINARY;
  if (override) {
    if (!existsSync(override)) {
      throw new Error(`CMDOP_CORE_BINARY points at a missing file: ${override}`);
    }
    makeExecutable(override);
    return override;
  }

  const key = `${process.platform}-${process.arch}`;
  if (!SUPPORTED_PLATFORMS.has(key)) {
    throw new Error(
      `cmdop-core has no prebuilt binary for ${key}. ` +
        "Set CMDOP_CORE_BINARY to a `go build -o /path/cmdop-core ./cmd/cmdop-core` output.",
    );
  }

  const binPath = join(packageBinDir(), binaryName());
  if (!existsSync(binPath)) {
    throw new Error(
      `cmdop-core binary not found at ${binPath}. ` +
        "Reinstall @cmdop/sdk (the 5 baked binaries ship in its bin/ dir), " +
        "or set CMDOP_CORE_BINARY to a local `go build` output.",
    );
  }
  makeExecutable(binPath);
  return binPath;
}

function makeExecutable(path: string): void {
  if (process.platform === "win32") return;
  try {
    chmodSync(path, 0o755);
  } catch {
    /* read-only store; the bit may already be set */
  }
}

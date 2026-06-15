import { defineConfig } from "vitest/config";

// Live e2e for the Node SDK. Lives in sdk/node (so vitest + @bufbuild/protobuf
// resolve from its node_modules) but targets the repo-level e2e/node/ suite,
// which imports the client from ../../sdk/node/src directly. Separate from
// vitest.config.ts (the offline unit suite). Run via `make e2e-node`.
export default defineConfig({
  test: {
    environment: "node",
    include: ["../../e2e/node/**/*.e2e.test.ts"],
    testTimeout: 60_000,
    hookTimeout: 60_000,
    // The live relay occasionally stalls a TLS handshake — retry once so that
    // infrastructure noise doesn't flake the suite. A real bug fails both tries
    // (deterministic); only transient network blips recover on the retry.
    retry: 1,
    // One process: the harness memoizes the validated token across files.
    fileParallelism: false,
  },
});

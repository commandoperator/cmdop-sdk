import { defineConfig } from "tsup";

export default defineConfig({
  entry: ["src/index.ts"],
  format: ["cjs", "esm"],
  dts: true,
  treeshake: true,
  clean: true,
  sourcemap: true,
  target: "es2022",
  outDir: "dist",
});

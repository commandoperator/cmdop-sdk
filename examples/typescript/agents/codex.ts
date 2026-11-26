import { main, question } from "./shared.js";

export const CODEX = { agent: "codex", ...question } as const;
await main(CODEX);

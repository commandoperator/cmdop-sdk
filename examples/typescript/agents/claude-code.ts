import { main, question } from "./shared.js";

export const CLAUDE_CODE = { agent: "claude-code", ...question } as const;
await main(CLAUDE_CODE);

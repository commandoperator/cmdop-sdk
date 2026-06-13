/**
 * Print the Node SDK's actual public surface as JSON to stdout. Consumed by the
 * top-level cross-language parity orchestrator (`parity/check.py`, run via
 * `tsx`). Keep stdout JSON-only.
 */
import { actualSurface } from "../src/_parity";

process.stdout.write(JSON.stringify(actualSurface()));

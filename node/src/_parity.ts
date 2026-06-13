/**
 * Parity introspection: the actual public method surface of every resource
 * namespace, as a `{ namespace: [methods] }` map, with camelCase normalised to
 * snake_case so it compares directly against `parity/manifest.json`.
 *
 * This is the Node half of the cross-language parity gate (Phase 5 §5.3). It is
 * imported by `tests/parity.test.ts` and printed as JSON by the top-level
 * `parity/check.py` orchestrator (run via `tsx`). Pagination helpers
 * (`iter`/`pages`/`iterRuns`/`pagesRuns`) are stripped here: they are ergonomic
 * extras that are not part of the wire surface the manifest locks.
 */

import { FleetsResource, FleetMachinesResource, FleetMembersResource } from "./resources/fleets";
import { KeysResource } from "./resources/keys";
import { MachinesResource } from "./resources/machines";
import { SchedulesResource } from "./resources/schedules";
import { SkillsResource } from "./resources/skills";
import { TunnelsResource } from "./resources/tunnels";

/** Non-canonical ergonomic helpers excluded from the locked surface. */
const PAGINATION_HELPERS = new Set(["iter", "pages", "iterRuns", "pagesRuns"]);

/** camelCase -> snake_case (activeSession -> active_session, setRole -> set_role). */
function toSnake(name: string): string {
  return name.replace(/[A-Z]/g, (c) => `_${c.toLowerCase()}`);
}

/** Public, non-pagination instance methods of a resource class, snake_cased. */
function methodsOf(cls: { prototype: object }): string[] {
  return Object.getOwnPropertyNames(cls.prototype)
    .filter((n) => n !== "constructor")
    .filter((n) => !n.startsWith("_") && !n.startsWith("#"))
    .filter((n) => !PAGINATION_HELPERS.has(n))
    // sub-resource accessors (`members`, `machines`) live on FleetsResource as
    // getters, not methods — they are namespaces, surfaced separately below.
    .filter((n) => {
      const d = Object.getOwnPropertyDescriptor(cls.prototype, n);
      return typeof d?.value === "function";
    })
    .map(toSnake)
    .sort();
}

/** The actual Node SDK surface, keyed by namespace path. */
export function actualSurface(): Record<string, string[]> {
  return {
    machines: methodsOf(MachinesResource),
    fleets: methodsOf(FleetsResource),
    "fleets.members": methodsOf(FleetMembersResource),
    "fleets.machines": methodsOf(FleetMachinesResource),
    tunnels: methodsOf(TunnelsResource),
    schedules: methodsOf(SchedulesResource),
    keys: methodsOf(KeysResource),
    skills: methodsOf(SkillsResource),
  };
}

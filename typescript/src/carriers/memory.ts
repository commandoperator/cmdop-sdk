/**
 * The in-memory carrier: the contract with no channel at all, for tests and the conformance suite. `serve` plays the
 * door: it gets each request and the caller's signal, and yields what the door would (pieces, then the answer).
 */

import type { Answer, CallRequest, StreamLine } from "../generated/call.gen.ts";
import { CarrierError, type Carrier, type MachineRow } from "./carrier.ts";

export interface MemoryDoor {
  serve(req: CallRequest, signal: AbortSignal | undefined): AsyncIterable<StreamLine>;
  machines?: MachineRow[];
}

const isAnswer = (l: StreamLine): l is Answer => "ok" in l || "error" in l || "sealed" in l;

export function memoryCarrier(door: MemoryDoor): Carrier {
  return {
    name: "memory",
    async call(req, o) {
      let last: Answer | undefined;
      for await (const l of this.stream(req, o)) if (isAnswer(l)) last = l;
      if (!last) throw new CarrierError("memory", "the door gave no answer");
      return last;
    },
    async *stream(req, o) {
      try {
        yield* door.serve(req, o.signal);
      } catch (e) {
        // The caller's own abort stays theirs; anything else is the channel breaking.
        if (o.signal?.aborted) throw e;
        throw new CarrierError("memory", `the door broke: ${String(e)}`);
      }
    },
    async machines() {
      return { ok: door.machines ?? [] };
    },
    async close() {},
  };
}

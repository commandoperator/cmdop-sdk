/**
 * The client-door seam (developer SDK plan, section 4): the one interface between the client and a channel. The client
 * knows the call contract (`generated/call.gen.ts`) and nothing about the channel; an adapter moves the contract's
 * shapes and nothing else. A carrier defines no semantics: codes, deadlines, cancel and the order of pieces come from
 * the contract, and the shared vectors (`exports/sdk/vectors/carrier`) hold every adapter to it.
 */

import type { Answer, CallRequest, StreamLine } from "../generated/call.gen.ts";

export interface CallOptions {
  /** Aborting it cancels the call: the adapter tells the door, the door tells the machine. */
  signal?: AbortSignal;
}

/** One machine as the server lists it. Only the fields the client reads. */
export interface MachineRow {
  id: string;
  name: string;
  online: boolean;
  os?: string;
  last_seen?: number | null;
  /** The machine's box key and its signature by the machine's id, for end-to-end calls. */
  box_key?: string | null;
  box_sig?: string | null;
  tools?: string[];
}

export interface Carrier {
  /** `"http"`, `"memory"`; later `"ws"`, `"grpc"`. */
  readonly name: string;
  /** One call, answered once. A refusal is an `Answer` with `error`, never a throw. */
  call(req: CallRequest, o: CallOptions): Promise<Answer>;
  /** One call, its pieces as they come, its answer as the last line. */
  stream(req: CallRequest, o: CallOptions): AsyncIterable<StreamLine>;
  /** The machines of the contour, a server-answered operation: `ok` is a `MachineRow[]`. */
  machines(o: CallOptions): Promise<Answer>;
  close(): Promise<void>;
}

/** A carrier could not reach the door or read what came back: not a contract answer. */
export class CarrierError extends Error {
  /** Written without parameter properties, so Node can run the sources with its own type stripping. */
  readonly carrier: string;
  constructor(carrier: string, message: string) {
    super(`${carrier}: ${message}`);
    this.name = "CarrierError";
    this.carrier = carrier;
  }
}

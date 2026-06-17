/**
 * `machines.ask` streaming: the typed frame union + {@link AskStream}.
 *
 * The Go core drives the relay's SSE `/ask` + the `/pin` + `/confirm`
 * side-channel POSTs and projects each onto an `Envelope` on the call's id
 * (report 13 §4.1). This module turns those envelopes into a typed discriminated
 * union and exposes the archived wrapper's ergonomics: `for await (const frame of
 * stream)`, `stream.pin(...)`, `stream.confirm(...)`, `stream.collect()`.
 *
 * The mid-stream answer (pin/confirm) writes an `ANSWER` envelope on the **same
 * id**; the core resumes the stream.
 */

import { create } from "@bufbuild/protobuf";
import { AgentStreamError, type CmdopError, mapCoreError } from "./errors";
import {
  type Envelope,
  Envelope_Kind,
  EnvelopeSchema,
} from "./_proto/cmdop/core/v1/envelope_pb";

/** Discriminated union of frames surfaced by `machines.ask`. */
export type AskFrame =
  | { type: "event"; eventType: number; payload: unknown }
  | { type: "done"; success: boolean; text: string; error: string; durationMs: number }
  | { type: "confirm_required"; token: string; plan: string; dangerLevel: string }
  | { type: "pin_required"; challengeId: string; label: string }
  | { type: "pin_denied"; challengeId: string; reason: string }
  | { type: "unknown"; raw: string };

/** What `call_stream` registers a stream with: a transport-driven frame source. */
export interface StreamSource {
  /** Allocated correlation id (set once the stream is started). */
  readonly id: number;
  /** Async-iterate the raw envelopes for this stream (terminates on done). */
  envelopes(): AsyncGenerator<Envelope>;
  /** Write an ANSWER envelope on this stream's id. */
  answer(env: Envelope): Promise<void>;
}

/**
 * Stream-terminal `error` codes that surface as their typed exception (not the
 * generic {@link AgentStreamError}) — the connection-PIN gate's verdicts.
 * Everything else keeps the established AgentStreamError stream contract.
 */
const TYPED_STREAM_ERROR_CODES = new Set(["pin_denied", "pin_required_timeout"]);

/**
 * Build the error to throw for a stream-terminal ERROR frame: the typed PIN
 * exception for a PIN-gate verdict, else the generic {@link AgentStreamError}.
 */
function streamError(code: string, message: string): CmdopError {
  if (TYPED_STREAM_ERROR_CODES.has(code)) {
    return mapCoreError(code, message);
  }
  return new AgentStreamError(code || "internal", message || "");
}

function frameFromEnvelope(env: Envelope): AskFrame {
  switch (env.kind) {
    case Envelope_Kind.DONE: {
      const d = env.payload.case === "done" ? env.payload.value : undefined;
      return {
        type: "done",
        success: d?.success ?? false,
        text: d?.text ?? "",
        error: d?.error ?? "",
        durationMs: Number(d?.durationMs ?? 0),
      };
    }
    case Envelope_Kind.CALLBACK: {
      if (env.payload.case === "pinRequired") {
        const pr = env.payload.value;
        return { type: "pin_required", challengeId: pr.challengeId, label: pr.label };
      }
      if (env.payload.case === "confirmRequired") {
        const cr = env.payload.value;
        return {
          type: "confirm_required",
          token: cr.token,
          plan: cr.plan,
          dangerLevel: cr.dangerLevel || "medium",
        };
      }
      return { type: "unknown", raw: env.payload.case ?? "" };
    }
    case Envelope_Kind.EVENT: {
      if (env.payload.case !== "askFrame") return { type: "unknown", raw: env.payload.case ?? "" };
      const f = env.payload.value.frame;
      if (f.case === "event") {
        let payload: unknown = undefined;
        if (f.value.payloadJson) {
          try {
            payload = JSON.parse(f.value.payloadJson);
          } catch {
            payload = f.value.payloadJson;
          }
        }
        return { type: "event", eventType: f.value.eventType, payload };
      }
      if (f.case === "pinDenied") {
        return { type: "pin_denied", challengeId: f.value.challengeId, reason: f.value.reason };
      }
      return { type: "unknown", raw: f.case ?? "" };
    }
    default:
      return { type: "unknown", raw: String(env.kind) };
  }
}

/**
 * Async-iterable of {@link AskFrame} with `pin()` / `confirm()` / `collect()`.
 *
 * Iterating starts the streaming call; a terminal ERROR envelope is thrown as an
 * {@link AgentStreamError}.
 */
export class AskStream implements AsyncIterable<AskFrame> {
  constructor(private readonly source: StreamSource) {}

  async *[Symbol.asyncIterator](): AsyncIterator<AskFrame> {
    for await (const env of this.source.envelopes()) {
      if (env.kind === Envelope_Kind.ERROR) {
        const info = env.payload.case === "error" ? env.payload.value : undefined;
        // PIN-gate verdicts surface as PinDeniedError / PinTimeoutError.
        throw streamError(info?.code || "", info?.message || "");
      }
      yield frameFromEnvelope(env);
    }
  }

  /** Answer a `pin_required` frame with the entered connection PIN. */
  async pin(challengeId: string, pin: string): Promise<void> {
    await this.source.answer(
      create(EnvelopeSchema, {
        id: this.source.id,
        kind: Envelope_Kind.ANSWER,
        payload: { case: "pinAnswer", value: { challengeId, pin } },
      }),
    );
  }

  /**
   * Answer a `confirm_required` frame. `accept=true` resumes the stream onto the
   * same id; `accept=false` ends it with a rejected `done`.
   */
  async confirm(token: string, accept: boolean): Promise<void> {
    await this.source.answer(
      create(EnvelopeSchema, {
        id: this.source.id,
        kind: Envelope_Kind.ANSWER,
        payload: { case: "confirmAnswer", value: { token, accept } },
      }),
    );
  }

  /**
   * Drain to the final text (the `done` frame's text, else accumulated event
   * deltas). Throws {@link AgentStreamError} on an error outcome.
   */
  async collect(): Promise<string> {
    let text = "";
    for await (const f of this) {
      if (f.type === "event") {
        const p = f.payload as { delta?: string; text?: string } | undefined;
        text += p?.delta ?? p?.text ?? "";
      } else if (f.type === "done") {
        return f.text || text;
      }
    }
    return text;
  }
}

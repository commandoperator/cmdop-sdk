import {
  AskStreamErrorCode,
  type Envelope,
  Envelope_Kind,
} from "./_proto/cmdop/core/v2/contract_pb";
import { AgentStreamError, TimeoutError } from "./errors";

export type AskFrame =
  | { type: "event"; eventType: number; payload: unknown; machineId?: string }
  | { type: "error"; code: string; message: string }
  | {
      type: "done";
      success: boolean;
      text: string;
      error?: string;
      upstreamStatus?: number;
      provider?: string;
      detail?: string;
      inputTokens?: bigint;
      outputTokens?: bigint;
      totalTokens?: bigint;
      cacheReadTokens?: bigint;
      cacheWriteTokens?: bigint;
      costUsd?: number;
      costSource?: string;
      engine?: string;
      model?: string;
    };

export interface StreamSource {
  envelopes(): AsyncGenerator<Envelope>;
}

const STREAM_ERROR_NAMES: Record<number, string> = {
  [AskStreamErrorCode.UNSPECIFIED]: "unspecified",
  [AskStreamErrorCode.MACHINE_OFFLINE]: "machine_offline",
  [AskStreamErrorCode.NO_TARGETS]: "no_targets",
  [AskStreamErrorCode.INTERNAL]: "internal",
  [AskStreamErrorCode.PIN_DENIED]: "pin_denied",
};

export class AskStream implements AsyncIterable<AskFrame> {
  #consumed = false;

  constructor(
    private readonly source: StreamSource,
    private readonly timeoutMs: number,
  ) {}

  async *[Symbol.asyncIterator](): AsyncIterator<AskFrame> {
    if (this.#consumed) throw new Error("an AskStream can only be consumed once");
    this.#consumed = true;
    const iterator = this.source.envelopes();
    for (;;) {
      const result = await withTimeout(iterator.next(), this.timeoutMs);
      if (result.done) return;
      const env = result.value;
      if (env.kind === Envelope_Kind.EVENT && env.payload.case === "askEvent") {
        let payload: unknown = env.payload.value.payloadJson;
        try {
          payload = JSON.parse(env.payload.value.payloadJson);
        } catch {
          // Preserve a non-JSON payload verbatim.
        }
        yield {
          type: "event",
          eventType: env.payload.value.eventType,
          payload,
          machineId: env.payload.value.machineId,
        };
      } else if (env.kind === Envelope_Kind.EVENT && env.payload.case === "askStreamError") {
        yield {
          type: "error",
          code: STREAM_ERROR_NAMES[env.payload.value.code] ?? "internal",
          message: env.payload.value.message,
        };
      } else if (env.kind === Envelope_Kind.DONE && env.payload.case === "askDone") {
        const value = env.payload.value;
        yield { type: "done", ...value };
      }
    }
  }

  async collect(): Promise<string> {
    let text = "";
    let streamError: Extract<AskFrame, { type: "error" }> | undefined;
    for await (const frame of this) {
      if (frame.type === "event") {
        const payload = frame.payload as { delta?: string; text?: string } | undefined;
        text += payload?.delta ?? payload?.text ?? "";
      } else if (frame.type === "error") {
        streamError = frame;
      } else if (!frame.success) {
        throw new AgentStreamError(
          frame.error ?? streamError?.message ?? "agent run failed",
          streamError?.code ?? "internal",
          frame.upstreamStatus,
        );
      } else {
        return frame.text || text;
      }
    }
    return text;
  }
}

async function withTimeout<T>(promise: Promise<T>, timeoutMs: number): Promise<T> {
  let timer: ReturnType<typeof setTimeout> | undefined;
  try {
    return await Promise.race([
      promise,
      new Promise<never>((_, reject) => {
        timer = setTimeout(
          () => reject(new TimeoutError("agent stream timed out", "deadline_exceeded", undefined, true)),
          timeoutMs,
        );
      }),
    ]);
  } finally {
    if (timer) clearTimeout(timer);
  }
}

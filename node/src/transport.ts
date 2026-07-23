import { type ChildProcessWithoutNullStreams, spawn } from "node:child_process";
import type { Readable, Writable } from "node:stream";
import {
  sizeDelimitedDecodeStream,
  sizeDelimitedEncode,
} from "@bufbuild/protobuf/wire";
import { toBinary } from "@bufbuild/protobuf";
import type { ClientConfig } from "./config";
import { ConnectionError, TimeoutError, mapCoreError } from "./errors";
import { AskStream, type StreamSource } from "./streaming";
import {
  type Envelope,
  Envelope_Kind,
  EnvelopeSchema,
} from "./_proto/cmdop/core/v2/contract_pb";

const MAX_QUEUED_FRAMES = 256;
const MAX_REQUEST_FRAME_BYTES = 4 * 1024 * 1024;

interface UnaryPending {
  kind: "unary";
  resolve: (envelope: Envelope) => void;
  reject: (error: Error) => void;
  timer: ReturnType<typeof setTimeout>;
}

interface StreamPending {
  kind: "stream";
  queue: FrameQueue;
}

class FrameQueue {
  #frames: Envelope[] = [];
  #wait?: (result: IteratorResult<Envelope>) => void;
  #done = false;
  #error?: Error;

  push(envelope: Envelope): void {
    if (this.#done) return;
    if (this.#wait) {
      const waiter = this.#wait;
      this.#wait = undefined;
      waiter({ value: envelope, done: false });
      return;
    }
    if (this.#frames.length >= MAX_QUEUED_FRAMES) {
      this.fail(new ConnectionError("agent stream consumer is too slow", "transport"));
      return;
    }
    this.#frames.push(envelope);
  }

  end(): void {
    this.#done = true;
    this.#wakeDone();
  }

  fail(error: Error): void {
    this.#error = error;
    this.#done = true;
    this.#wakeDone();
  }

  #wakeDone(): void {
    if (this.#wait) {
      const waiter = this.#wait;
      this.#wait = undefined;
      waiter({ value: undefined as never, done: true });
    }
  }

  async *iterate(): AsyncGenerator<Envelope> {
    for (;;) {
      if (this.#error) throw this.#error;
      if (this.#frames.length) {
        yield this.#frames.shift()!;
        continue;
      }
      if (this.#done) return;
      const result = await new Promise<IteratorResult<Envelope>>((resolve) => {
        this.#wait = resolve;
      });
      if (this.#error) throw this.#error;
      if (result.done) return;
      yield result.value;
    }
  }
}

export class Transport {
  #child?: ChildProcessWithoutNullStreams;
  #stdin?: Writable;
  #pending = new Map<bigint, UnaryPending | StreamPending>();
  #nextId = 1n;
  #closed = false;
  #starting?: Promise<void>;

  constructor(
    private readonly config: ClientConfig,
    private readonly binaryPath: string,
  ) {}

  /** @internal test seam */
  attachStreamsForTest(stdin: Writable, stdout: Readable): void {
    this.#stdin = stdin;
    this.#child = { stdin } as unknown as ChildProcessWithoutNullStreams;
    this.#startReader(stdout);
  }

  async #ensureStarted(): Promise<void> {
    if (this.#child) return;
    if (this.#starting) return this.#starting;
    this.#starting = this.#spawn();
    try {
      await this.#starting;
    } finally {
      this.#starting = undefined;
    }
  }

  async #spawn(): Promise<void> {
    const env = { ...process.env };
    if (this.config.token) env.CMDOP_TOKEN = this.config.token;
    else delete env.CMDOP_TOKEN;
    if (this.config.baseUrl) env.CMDOP_BASE_URL = this.config.baseUrl;
    else delete env.CMDOP_BASE_URL;
    const child = spawn(this.binaryPath, ["--stdio"], {
      stdio: ["pipe", "pipe", "pipe"],
      env,
      windowsHide: true,
    });
    this.#child = child;
    this.#stdin = child.stdin;
    child.stderr.on("data", () => {});
    child.on("exit", () => this.#failAll(new ConnectionError("cmdop-core exited", "transport")));
    child.on("error", (error) =>
      this.#failAll(new ConnectionError(`cmdop-core spawn failed: ${error.message}`, "transport")),
    );
    this.#startReader(child.stdout);
  }

  #startReader(stdout: Readable): void {
    void (async () => {
      try {
        for await (const envelope of sizeDelimitedDecodeStream(EnvelopeSchema, stdout)) {
          this.#dispatch(envelope);
        }
        this.#failAll(new ConnectionError("cmdop-core stdout closed", "transport"));
      } catch (error) {
        this.#failAll(
          new ConnectionError(
            `core read failed: ${error instanceof Error ? error.message : String(error)}`,
            "transport",
          ),
        );
      }
    })();
  }

  #dispatch(envelope: Envelope): void {
    const pending = this.#pending.get(envelope.id);
    if (!pending) return;
    if (pending.kind === "unary") {
      if (envelope.kind === Envelope_Kind.RESPONSE) {
        this.#pending.delete(envelope.id);
        clearTimeout(pending.timer);
        pending.resolve(envelope);
      } else if (envelope.kind === Envelope_Kind.ERROR && envelope.payload.case === "error") {
        this.#pending.delete(envelope.id);
        clearTimeout(pending.timer);
        pending.reject(mapCoreError(envelope.payload.value));
      }
      return;
    }
    if (envelope.kind === Envelope_Kind.EVENT) {
      pending.queue.push(envelope);
    } else if (envelope.kind === Envelope_Kind.DONE) {
      this.#pending.delete(envelope.id);
      pending.queue.push(envelope);
      pending.queue.end();
    } else if (envelope.kind === Envelope_Kind.ERROR && envelope.payload.case === "error") {
      this.#pending.delete(envelope.id);
      pending.queue.fail(mapCoreError(envelope.payload.value));
    }
  }

  #failAll(error: Error): void {
    const pending = this.#pending;
    this.#pending = new Map();
    for (const call of pending.values()) {
      if (call.kind === "unary") {
        clearTimeout(call.timer);
        call.reject(error);
      } else {
        call.queue.fail(error);
      }
    }
  }

  #write(envelope: Envelope): void {
    if (!this.#stdin) throw new ConnectionError("cmdop-core is not running", "transport");
    if (toBinary(EnvelopeSchema, envelope).byteLength > MAX_REQUEST_FRAME_BYTES) {
      throw new ConnectionError(
        `request frame exceeds ${MAX_REQUEST_FRAME_BYTES} bytes`,
        "transport",
      );
    }
    this.#stdin.write(sizeDelimitedEncode(EnvelopeSchema, envelope));
  }

  async callUnary(request: Envelope): Promise<Envelope> {
    await this.#ensureStarted();
    request.id = this.#nextId++;
    request.kind = Envelope_Kind.REQUEST;
    return new Promise<Envelope>((resolve, reject) => {
      const timer = setTimeout(() => {
        this.#pending.delete(request.id);
        reject(new TimeoutError("cmdop-core request timed out", "deadline_exceeded", undefined, true));
      }, this.config.timeoutMs);
      this.#pending.set(request.id, { kind: "unary", resolve, reject, timer });
      try {
        this.#write(request);
      } catch (error) {
        clearTimeout(timer);
        this.#pending.delete(request.id);
        reject(error);
      }
    });
  }

  callStream(request: Envelope): AskStream {
    const transport = this;
    let started = false;
    const source: StreamSource = {
      async *envelopes() {
        if (started) throw new Error("an AskStream can only be consumed once");
        started = true;
        await transport.#ensureStarted();
        request.id = transport.#nextId++;
        request.kind = Envelope_Kind.REQUEST;
        const queue = new FrameQueue();
        transport.#pending.set(request.id, { kind: "stream", queue });
        try {
          transport.#write(request);
          yield* queue.iterate();
        } finally {
          transport.#pending.delete(request.id);
        }
      },
    };
    return new AskStream(source, this.config.timeoutMs);
  }

  async close(): Promise<void> {
    if (this.#closed) return;
    this.#closed = true;
    const child = this.#child;
    if (!child) return;
    this.#stdin?.end();
    if (typeof child.once === "function" && typeof child.kill === "function") {
      await new Promise<void>((resolve) => {
        let finished = false;
        const done = () => {
          if (!finished) {
            finished = true;
            resolve();
          }
        };
        child.once("exit", done);
        setTimeout(() => {
          if (!finished) child.kill();
          done();
        }, 5000);
      });
    }
    this.#failAll(new ConnectionError("client closed", "transport"));
  }
}

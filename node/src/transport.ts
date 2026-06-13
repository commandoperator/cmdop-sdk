/**
 * Stdio transport: spawn `cmdop-core`, frame protobuf Envelopes over its
 * stdin/stdout, demux by `Envelope.id`.
 *
 * This is the hand-written transport runtime (report 11 §0) — written once,
 * untouched when methods are added. Each generated resource method is ~3 lines
 * calling {@link Transport.callUnary} / {@link Transport.callStream}.
 *
 * Framing (report 13 §1.3): `@bufbuild/protobuf/wire`'s `sizeDelimitedEncode` /
 * `sizeDelimitedDecodeStream`. `sizeDelimitedDecodeStream` is *already* a
 * chunk-to-message async-iterator over `child.stdout` — it reassembles frames
 * split across chunk boundaries for us, so there is no hand-rolled buffering.
 *
 * Demux (report 11 §1.4): a `Map<number, Pending>` keyed by id. A unary call
 * resolves/rejects a Promise; a streaming call pushes EVENT/CALLBACK frames into
 * a bounded push→pull queue and ends on DONE (or rejects on ERROR).
 */

import { type ChildProcessWithoutNullStreams, spawn } from "node:child_process";
import type { Readable, Writable } from "node:stream";
import {
  sizeDelimitedDecodeStream,
  sizeDelimitedEncode,
} from "@bufbuild/protobuf/wire";
import type { ClientConfig } from "./config";
import { ConnectionError, mapCoreError } from "./errors";
import { AskStream, type StreamSource } from "./streaming";
import {
  type Envelope,
  Envelope_Kind,
  EnvelopeSchema,
} from "./_proto/cmdop/core/v1/envelope_pb";

interface UnaryPending {
  kind: "unary";
  resolve: (env: Envelope) => void;
  reject: (err: Error) => void;
}

interface StreamPending {
  kind: "stream";
  push: (env: Envelope) => void;
  end: () => void;
  fail: (err: Error) => void;
}

type Pending = UnaryPending | StreamPending;

/**
 * A bounded push→pull async-iterator: bridges the demux's push of frames into a
 * `for await` consumer (the canonical "queueable" pattern, report 11 §1.4).
 */
class FrameQueue {
  #q: Envelope[] = [];
  #wait?: (r: IteratorResult<Envelope>) => void;
  #done = false;
  #err?: Error;

  push(env: Envelope): void {
    if (this.#wait) {
      const w = this.#wait;
      this.#wait = undefined;
      w({ value: env, done: false });
    } else {
      this.#q.push(env);
    }
  }

  end(): void {
    this.#done = true;
    if (this.#wait) {
      const w = this.#wait;
      this.#wait = undefined;
      w({ value: undefined as never, done: true });
    }
  }

  fail(err: Error): void {
    this.#err = err;
    if (this.#wait) {
      const w = this.#wait;
      this.#wait = undefined;
      // surface on next() via the stored error
      w({ value: undefined as never, done: true });
    }
  }

  async *iterate(): AsyncGenerator<Envelope> {
    for (;;) {
      if (this.#err) throw this.#err;
      if (this.#q.length) {
        yield this.#q.shift()!;
        continue;
      }
      if (this.#done) return;
      const r = await new Promise<IteratorResult<Envelope>>((res) => {
        this.#wait = res;
      });
      if (this.#err) throw this.#err;
      if (r.done) return;
      yield r.value;
    }
  }
}

export class Transport {
  #child?: ChildProcessWithoutNullStreams;
  #stdin?: Writable;
  #pending = new Map<number, Pending>();
  #nextId = 1;
  #closed = false;
  #starting?: Promise<void>;

  constructor(
    private readonly cfg: ClientConfig,
    private readonly binPath: string,
  ) {}

  /**
   * @internal Test seam: drive the demux off a provided stdin/stdout pair
   * instead of spawning a binary. Used by the transport unit tests, mirroring
   * the Python test that injects a fake process.
   */
  attachStreamsForTest(stdin: Writable, stdout: Readable): void {
    this.#stdin = stdin;
    this.#starting = Promise.resolve();
    this.#child = { stdin } as unknown as ChildProcessWithoutNullStreams;
    this.#startReader(stdout);
  }

  // -- lifecycle ---------------------------------------------------------

  private async ensureStarted(): Promise<void> {
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
    const child = spawn(this.binPath, ["--stdio"], {
      stdio: ["pipe", "pipe", "pipe"],
      env: {
        ...process.env,
        CMDOP_TOKEN: this.cfg.token,
        CMDOP_BASE_URL: this.cfg.baseUrl,
        // Django platform plane (skills) — separate credential + base URL.
        CMDOP_API_BASE_URL: this.cfg.apiBaseUrl,
        ...(this.cfg.apiKey ? { CMDOP_API_KEY: this.cfg.apiKey } : {}),
      },
      windowsHide: true,
    });
    this.#child = child;
    this.#stdin = child.stdin;

    // stderr is NOT part of the protocol — drain it so it never blocks/corrupts
    // the pipe (the core logs to a file when CMDOP_DEBUG=1).
    child.stderr.on("data", () => {});

    child.on("exit", () => {
      this.#failAll(new ConnectionError("cmdop-core exited"));
    });
    child.on("error", (err) => {
      this.#failAll(new ConnectionError(`cmdop-core spawn failed: ${err.message}`));
    });

    this.#startReader(child.stdout);
  }

  /**
   * Reader: `sizeDelimitedDecodeStream` consumes the stdout (an
   * `AsyncIterable<Uint8Array>`) and yields fully-assembled Envelopes,
   * reassembling frames split across chunk boundaries for us.
   */
  #startReader(stdout: Readable): void {
    void (async () => {
      try {
        for await (const env of sizeDelimitedDecodeStream(EnvelopeSchema, stdout)) {
          this.#dispatch(env);
        }
        this.#failAll(new ConnectionError("cmdop-core stdout closed"));
      } catch (err) {
        this.#failAll(
          new ConnectionError(
            `core read loop failed: ${err instanceof Error ? err.message : String(err)}`,
          ),
        );
      }
    })();
  }

  #dispatch(env: Envelope): void {
    const p = this.#pending.get(env.id);
    if (!p) return;

    if (p.kind === "unary") {
      if (env.kind === Envelope_Kind.ERROR) {
        this.#pending.delete(env.id);
        p.reject(this.#toError(env));
      } else if (env.kind === Envelope_Kind.RESPONSE) {
        this.#pending.delete(env.id);
        p.resolve(env);
      }
      return;
    }

    // stream
    switch (env.kind) {
      case Envelope_Kind.EVENT:
      case Envelope_Kind.CALLBACK:
        p.push(env);
        break;
      case Envelope_Kind.DONE:
        this.#pending.delete(env.id);
        p.push(env);
        p.end();
        break;
      case Envelope_Kind.ERROR:
        // Push the raw ERROR envelope so AskStream raises an AgentStreamError
        // (ask stream's error-frame semantics), then end.
        this.#pending.delete(env.id);
        p.push(env);
        p.end();
        break;
      case Envelope_Kind.RESPONSE:
        this.#pending.delete(env.id);
        p.push(env);
        p.end();
        break;
    }
  }

  #toError(env: Envelope): Error {
    const info = env.payload.case === "error" ? env.payload.value : undefined;
    return mapCoreError(info?.code || "internal", info?.message || "");
  }

  #failAll(err: Error): void {
    const pending = this.#pending;
    this.#pending = new Map();
    for (const p of pending.values()) {
      if (p.kind === "unary") p.reject(err);
      else p.fail(err);
    }
  }

  async close(): Promise<void> {
    if (this.#closed) return;
    this.#closed = true;
    const child = this.#child;
    const stdin = this.#stdin;
    if (!child) return;
    try {
      stdin?.end(); // EOF → core drains gracefully
    } catch {
      /* ignore */
    }
    // A real spawned child emits 'exit'; a test-injected fake child does not, so
    // resolve immediately when the lifecycle hooks are absent.
    if (typeof child.once === "function" && typeof child.kill === "function") {
      await new Promise<void>((resolve) => {
        let done = false;
        const finish = () => {
          if (done) return;
          done = true;
          resolve();
        };
        child.once("exit", finish);
        setTimeout(() => {
          if (!done) {
            child.kill();
            finish();
          }
        }, 5000);
      });
    }
    this.#failAll(new ConnectionError("client closed"));
  }

  // -- write path --------------------------------------------------------

  #write(env: Envelope): void {
    const stdin = this.#stdin;
    if (!stdin) throw new ConnectionError("cmdop-core not running");
    stdin.write(sizeDelimitedEncode(EnvelopeSchema, env));
  }

  // -- call entry points (used by generated resources) -------------------

  /**
   * Send a REQUEST envelope, await the RESPONSE/ERROR on its id. `req` carries
   * the oneof payload arm; `id`/`kind` are filled here.
   */
  async callUnary(req: Envelope): Promise<Envelope> {
    await this.ensureStarted();
    req.id = this.#nextId++;
    req.kind = Envelope_Kind.REQUEST;
    return new Promise<Envelope>((resolve, reject) => {
      this.#pending.set(req.id, { kind: "unary", resolve, reject });
      try {
        this.#write(req);
      } catch (err) {
        this.#pending.delete(req.id);
        reject(err instanceof Error ? err : new Error(String(err)));
      }
    });
  }

  /** Open a streaming call (machines.ask). Returns an {@link AskStream}. */
  callStream(req: Envelope): AskStream {
    const queue = new FrameQueue();
    let started = false;
    let id = 0;
    const transport = this;

    const source: StreamSource = {
      get id() {
        return id;
      },
      async *envelopes() {
        if (!started) {
          started = true;
          await transport.ensureStarted();
          id = transport.#nextId++;
          req.id = id;
          req.kind = Envelope_Kind.REQUEST;
          transport.#pending.set(id, {
            kind: "stream",
            push: (e) => queue.push(e),
            end: () => queue.end(),
            fail: (e) => queue.fail(e),
          });
          transport.#write(req);
        }
        yield* queue.iterate();
      },
      async answer(env: Envelope) {
        await transport.ensureStarted();
        transport.#write(env);
      },
    };

    return new AskStream(source);
  }
}

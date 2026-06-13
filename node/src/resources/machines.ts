/**
 * `client.machines` — list / get / update / disable / info / spend + the `ask`
 * stream and the chat-history side-channel (messages / clearMessages /
 * activeSession). `disable` is soft-disable; `spend` takes a `window`.
 */

import { create } from "@bufbuild/protobuf";
import type { AskStream } from "../streaming";
import type {
  ClearMessagesResponse,
  MachineDetail,
  MachineList,
  MachineSpend,
  MachineSummary,
  MessagesResponse,
} from "../_proto/cmdop/core/v1/machines_pb";
import { AskRequestSchema } from "../_proto/cmdop/core/v1/machines_pb";
import { BaseResource } from "./base";

export interface ListMachinesOptions {
  presence?: string;
  q?: string;
  limit?: number;
  cursor?: string;
}

export interface AskOptions {
  sessionId?: string;
  agentType?: string;
  timeoutSeconds?: number;
  options?: Record<string, string>;
}

export class MachinesResource extends BaseResource {
  async list(opts: ListMachinesOptions = {}): Promise<MachineList> {
    const env = await this.unary(
      this.req({
        case: "listMachinesReq",
        value: {
          presence: opts.presence ?? "any",
          q: opts.q ?? "",
          limit: opts.limit ?? 100,
          cursor: opts.cursor ?? "",
        },
      }),
    );
    return env.payload.value as MachineList;
  }

  async get(machineId: string): Promise<MachineDetail> {
    const env = await this.unary(this.req({ case: "getMachineReq", value: { machineId } }));
    return env.payload.value as MachineDetail;
  }

  async update(machineId: string, body: { name?: string } = {}): Promise<MachineSummary> {
    const env = await this.unary(
      this.req({ case: "updateMachineReq", value: { machineId, name: body.name ?? "" } }),
    );
    return env.payload.value as MachineSummary;
  }

  /** Soft-disable (not delete). */
  async disable(machineId: string): Promise<void> {
    await this.unary(this.req({ case: "disableMachineReq", value: { machineId } }));
  }

  async info(machineId: string): Promise<MachineDetail> {
    const env = await this.unary(this.req({ case: "machineInfoReq", value: { machineId } }));
    return env.payload.value as MachineDetail;
  }

  async spend(machineId: string, opts: { window?: string } = {}): Promise<MachineSpend> {
    const env = await this.unary(
      this.req({ case: "machineSpendReq", value: { machineId, window: opts.window ?? "7d" } }),
    );
    return env.payload.value as MachineSpend;
  }

  // -- pagination --------------------------------------------------------

  iter(opts: ListMachinesOptions = {}): AsyncGenerator<MachineSummary> {
    return this.paginateCursor((cursor) => this.list({ ...opts, cursor }));
  }

  pages(opts: ListMachinesOptions = {}): AsyncGenerator<MachineList> {
    return this.pagesCursor((cursor) => this.list({ ...opts, cursor }));
  }

  // -- stream ------------------------------------------------------------

  /** Talk to the machine's AI agent. Returns an {@link AskStream}. */
  ask(machineId: string, prompt: string, opts: AskOptions = {}): AskStream {
    const askReq = create(AskRequestSchema, {
      machineId,
      sessionId: opts.sessionId ?? randomId(),
      prompt,
      options: opts.options ?? {},
    });
    if (opts.agentType !== undefined) askReq.agentType = opts.agentType;
    if (opts.timeoutSeconds !== undefined) askReq.timeoutSeconds = opts.timeoutSeconds;
    return this.t.callStream(this.req({ case: "askReq", value: askReq }));
  }

  // -- chat history ------------------------------------------------------

  async messages(machineId: string, opts: { limit?: number } = {}): Promise<MessagesResponse> {
    const env = await this.unary(
      this.req({ case: "messagesReq", value: { machineId, limit: opts.limit ?? 50 } }),
    );
    return env.payload.value as MessagesResponse;
  }

  async clearMessages(machineId: string): Promise<ClearMessagesResponse> {
    const env = await this.unary(this.req({ case: "clearMessagesReq", value: { machineId } }));
    return env.payload.value as ClearMessagesResponse;
  }

  /** The live agent session id (empty string if none). */
  async activeSession(machineId: string): Promise<string> {
    const env = await this.unary(this.req({ case: "activeSessionReq", value: { machineId } }));
    const resp = env.payload.value as { agentSessionId: string };
    return resp.agentSessionId;
  }
}

function randomId(): string {
  if (typeof globalThis.crypto?.randomUUID === "function") {
    return globalThis.crypto.randomUUID().replace(/-/g, "");
  }
  return Date.now().toString(36) + Math.random().toString(36).slice(2);
}

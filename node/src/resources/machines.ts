import type { MachineMessageList, MachineRosterSnapshot } from "../_proto/cmdop/core/v2/contract_pb";
import type { AskStream } from "../streaming";
import { BaseResource } from "./base";

export interface AskOptions {
  pin?: string;
  session?: string;
  attachmentIds?: readonly string[];
  engine?: string;
  workingDir?: string;
  projectRootId?: string;
  model?: string;
}

export interface MessageOptions {
  session?: string;
  limit?: number;
}

export class MachinesResource extends BaseResource {
  async list(): Promise<MachineRosterSnapshot> {
    const response = await this.unary(
      this.request({ case: "listMachinesReq", value: {} }),
    );
    if (response.payload.case !== "machineRosterSnapshot") {
      throw new Error("cmdop-core returned the wrong roster response arm");
    }
    return response.payload.value;
  }

  ask(machineId: string, prompt = "", options: AskOptions = {}): AskStream {
    const attachmentIds = [...(options.attachmentIds ?? [])];
    if (!prompt && attachmentIds.length === 0) {
      throw new Error("prompt or at least one attachmentId is required");
    }
    return this.t.callStream(
      this.request({
        case: "askMachineReq",
        value: {
          machineId,
          prompt,
          options: {
            pin: options.pin,
            session: options.session,
            attachmentIds,
            engine: options.engine,
            workingDir: options.workingDir,
            projectRootId: options.projectRootId,
            model: options.model,
          },
        },
      }),
    );
  }

  async messages(machineId: string, options: MessageOptions = {}): Promise<MachineMessageList> {
    if (options.limit !== undefined && (options.limit < 1 || options.limit > 500)) {
      throw new Error("limit must be between 1 and 500");
    }
    const response = await this.unary(
      this.request({
        case: "listMachineMessagesReq",
        value: { machineId, session: options.session, limit: options.limit },
      }),
    );
    if (response.payload.case !== "machineMessageList") {
      throw new Error("cmdop-core returned the wrong messages response arm");
    }
    return response.payload.value;
  }
}

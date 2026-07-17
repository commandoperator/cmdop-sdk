import { create, type MessageInitShape } from "@bufbuild/protobuf";
import type { Client } from "../client";
import type { Transport } from "../transport";
import { type Envelope, EnvelopeSchema } from "../_proto/cmdop/core/v2/contract_pb";

type Payload = MessageInitShape<typeof EnvelopeSchema>["payload"];

export abstract class BaseResource {
  protected readonly t: Transport;

  constructor(protected readonly client: Client) {
    this.t = client._t;
  }

  protected unary(request: Envelope): Promise<Envelope> {
    return this.t.callUnary(request);
  }

  protected request(payload: Payload): Envelope {
    return create(EnvelopeSchema, { payload });
  }
}

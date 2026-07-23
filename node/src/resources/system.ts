import type { SystemBootstrapResponse } from "../_proto/cmdop/core/v2/contract_pb";
import { BaseResource } from "./base";

export class SystemResource extends BaseResource {
  async bootstrap(): Promise<SystemBootstrapResponse> {
    const response = await this.unary(
      this.request({ case: "systemBootstrapReq", value: {} }),
    );
    if (response.payload.case !== "systemBootstrapResp") {
      throw new Error("cmdop-core returned the wrong bootstrap response arm");
    }
    return response.payload.value;
  }
}

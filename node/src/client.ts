import { type ClientConfig, resolveConfig } from "./config";
import { locateBinary } from "./locate";
import { MachinesResource } from "./resources/machines";
import { SystemResource } from "./resources/system";
import { Transport } from "./transport";

export interface ClientOptions extends Partial<ClientConfig> {
  binaryPath?: string;
}

export class Client {
  readonly config: ClientConfig;
  /** @internal */
  readonly _t: Transport;

  constructor(opts: ClientOptions | string = {}) {
    const resolved = typeof opts === "string" ? { token: opts } : opts;
    this.config = resolveConfig(resolved);
    this._t = new Transport(this.config, resolved.binaryPath ?? locateBinary());
  }

  static fromEnv(): Client {
    return new Client();
  }

  get baseUrl(): string | undefined {
    return this.config.baseUrl;
  }

  #system?: SystemResource;
  get system(): SystemResource {
    return (this.#system ??= new SystemResource(this));
  }

  #machines?: MachinesResource;
  get machines(): MachinesResource {
    return (this.#machines ??= new MachinesResource(this));
  }

  async close(): Promise<void> {
    await this._t.close();
  }

  async [Symbol.asyncDispose](): Promise<void> {
    await this.close();
  }
}

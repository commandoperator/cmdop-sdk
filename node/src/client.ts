/**
 * The public `Client` — owns config, spawns one persistent `cmdop-core`
 * subprocess (on first call), and exposes lazy resource accessors.
 *
 * Mirror of the Python async `Client`: `Client.fromEnv()`, default-fleet
 * fallback, `Symbol.asyncDispose` for `await using`.
 */

import { type ClientConfig, resolveConfig } from "./config";
import { locateBinary } from "./locate";
import { FleetsResource } from "./resources/fleets";
import { KeysResource } from "./resources/keys";
import { MachinesResource } from "./resources/machines";
import { SchedulesResource } from "./resources/schedules";
import { SkillsResource } from "./resources/skills";
import { TunnelsResource } from "./resources/tunnels";
import { Transport } from "./transport";

export interface ClientOptions extends Partial<ClientConfig> {
  /** Override the located binary (otherwise CMDOP_CORE_BINARY / baked binary). */
  binaryPath?: string;
}

export class Client {
  readonly config: ClientConfig;
  /** @internal Shared stdio transport (never exposed publicly). */
  readonly _t: Transport;

  constructor(opts: ClientOptions | string = {}) {
    const o = typeof opts === "string" ? { token: opts } : opts;
    this.config = resolveConfig(o);
    this._t = new Transport(this.config, o.binaryPath ?? locateBinary());
  }

  /** Build a client purely from the environment (`CMDOP_*`). */
  static fromEnv(): Client {
    return new Client();
  }

  get fleetId(): string | undefined {
    return this.config.fleetId;
  }

  get baseUrl(): string {
    return this.config.baseUrl;
  }

  #machines?: MachinesResource;
  get machines(): MachinesResource {
    return (this.#machines ??= new MachinesResource(this));
  }

  #fleets?: FleetsResource;
  get fleets(): FleetsResource {
    return (this.#fleets ??= new FleetsResource(this));
  }

  #tunnels?: TunnelsResource;
  get tunnels(): TunnelsResource {
    return (this.#tunnels ??= new TunnelsResource(this));
  }

  #schedules?: SchedulesResource;
  get schedules(): SchedulesResource {
    return (this.#schedules ??= new SchedulesResource(this));
  }

  #keys?: KeysResource;
  get keys(): KeysResource {
    return (this.#keys ??= new KeysResource(this));
  }

  #skills?: SkillsResource;
  get skills(): SkillsResource {
    return (this.#skills ??= new SkillsResource(this));
  }

  /** Close stdin (graceful drain) and reap the core process. */
  async close(): Promise<void> {
    await this._t.close();
  }

  async [Symbol.asyncDispose](): Promise<void> {
    await this.close();
  }
}

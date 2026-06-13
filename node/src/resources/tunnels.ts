/**
 * `client.tunnels` — open / close / list / get / sessions.
 */

import type {
  ConnectedSessionOption,
  TunnelList,
  TunnelView,
} from "../_proto/cmdop/core/v1/tunnels_pb";
import { BaseResource, type ListPageOptions } from "./base";

export interface OpenTunnelOptions {
  protocol?: string;
  localHost?: string;
  localPort: number;
  subdomain?: string;
  options?: Record<string, string>;
}

export class TunnelsResource extends BaseResource {
  async open(sessionId: string, opts: OpenTunnelOptions): Promise<TunnelView> {
    const env = await this.unary(
      this.req({
        case: "openTunnelReq",
        value: {
          sessionId,
          protocol: opts.protocol ?? "http",
          localHost: opts.localHost ?? "127.0.0.1",
          localPort: opts.localPort,
          subdomain: opts.subdomain ?? "",
          options: opts.options ?? {},
        },
      }),
    );
    return env.payload.value as TunnelView;
  }

  /** Close a tunnel (idempotent). */
  async close(tunnelId: string): Promise<void> {
    await this.unary(this.req({ case: "closeTunnelReq", value: { tunnelId } }));
  }

  async list(opts: ListPageOptions = {}): Promise<TunnelList> {
    const env = await this.unary(
      this.req({ case: "listTunnelsReq", value: { page: this.offsetPage(opts.page, opts.perPage) } }),
    );
    return env.payload.value as TunnelList;
  }

  iter(opts: ListPageOptions = {}): AsyncGenerator<TunnelView> {
    return this.paginateOffset((page) => this.list({ page, perPage: opts.perPage }));
  }

  pages(opts: ListPageOptions = {}): AsyncGenerator<TunnelList> {
    return this.pagesOffset((page) => this.list({ page, perPage: opts.perPage }));
  }

  async get(tunnelId: string): Promise<TunnelView> {
    const env = await this.unary(this.req({ case: "getTunnelReq", value: { tunnelId } }));
    return env.payload.value as TunnelView;
  }

  /** Connected-session picker for opening tunnels. */
  async sessions(): Promise<ConnectedSessionOption[]> {
    const env = await this.unary(this.req({ case: "listSessionsReq", value: {} }));
    const list = env.payload.value as { items: ConnectedSessionOption[] };
    return list.items;
  }
}

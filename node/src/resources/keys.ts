/**
 * `client.keys` — api-keys list / issue / revoke. Fleet-scoped (default-fleet
 * fallback).
 */

import type {
  ApiKeyList,
  ApiKeySummary,
  IssueKeyResponse,
} from "../_proto/cmdop/core/v1/keys_pb";
import { BaseResource, type ListPageOptions } from "./base";

type KeysListOptions = ListPageOptions & { fleetId?: string };

export class KeysResource extends BaseResource {
  async list(opts: ListPageOptions & { fleetId?: string } = {}): Promise<ApiKeyList> {
    const fid = this.fleet(opts.fleetId);
    const env = await this.unary(
      this.req({
        case: "listKeysReq",
        value: { fleetId: fid, page: this.offsetPage(opts.page, opts.perPage) },
      }),
    );
    return env.payload.value as ApiKeyList;
  }

  iter(opts: KeysListOptions = {}): AsyncGenerator<ApiKeySummary> {
    return this.paginateOffset((page) =>
      this.list({ page, perPage: opts.perPage, fleetId: opts.fleetId }),
    );
  }

  pages(opts: KeysListOptions = {}): AsyncGenerator<ApiKeyList> {
    return this.pagesOffset((page) =>
      this.list({ page, perPage: opts.perPage, fleetId: opts.fleetId }),
    );
  }

  /** Mint a key — `rawToken` is returned only here. */
  async issue(opts: { name: string; expiresInDays?: number; fleetId?: string }): Promise<IssueKeyResponse> {
    const fid = this.fleet(opts.fleetId);
    const env = await this.unary(
      this.req({
        case: "issueKeyReq",
        value: { fleetId: fid, name: opts.name, expiresInDays: opts.expiresInDays ?? 0 },
      }),
    );
    return env.payload.value as IssueKeyResponse;
  }

  async revoke(keyId: string, opts: { fleetId?: string } = {}): Promise<void> {
    const fid = this.fleet(opts.fleetId);
    await this.unary(this.req({ case: "revokeKeyReq", value: { fleetId: fid, keyId } }));
  }
}

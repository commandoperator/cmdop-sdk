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
    // `expiresInDays` is an optional proto field the server requires to be >= 1
    // when present. Only set it when the caller passed one — sending 0 marks the
    // optional field present and 422s the request.
    const value: { fleetId: string; name: string; expiresInDays?: number } = {
      fleetId: fid,
      name: opts.name,
    };
    if (opts.expiresInDays !== undefined) value.expiresInDays = opts.expiresInDays;
    const env = await this.unary(this.req({ case: "issueKeyReq", value }));
    return env.payload.value as IssueKeyResponse;
  }

  async revoke(keyId: string, opts: { fleetId?: string } = {}): Promise<void> {
    const fid = this.fleet(opts.fleetId);
    await this.unary(this.req({ case: "revokeKeyReq", value: { fleetId: fid, keyId } }));
  }
}

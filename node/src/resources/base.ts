/**
 * Shared resource plumbing: the transport handle, fleet-default fallback, the
 * `OffsetPage{offset, per_page}` request helper, and the two pagination helpers.
 *
 * Every resource method builds a request `Envelope` (one oneof arm), calls the
 * transport, and reads the typed response arm back out.
 */

import { create, type MessageInitShape } from "@bufbuild/protobuf";
import type { Client } from "../client";
import type { Transport } from "../transport";
import {
  type Envelope,
  EnvelopeSchema,
} from "../_proto/cmdop/core/v1/envelope_pb";
import {
  type OffsetPage,
  OffsetPageSchema,
} from "../_proto/cmdop/core/v1/common_pb";

/** The `{ case, value }` init form of the Envelope's `payload` oneof. */
type PayloadInit = MessageInitShape<typeof EnvelopeSchema>["payload"];

/** A cursor-paginated list (`MachineList`, `ScheduleRunList`). */
interface CursorList<T> {
  items: T[];
  nextCursor?: string;
  hasMore?: boolean;
}

/** An offset-paginated list (`FleetList`/`MemberList`/`TunnelList`/...). */
interface OffsetList<T> {
  items: T[];
  offset: number;
  perPage: number;
  total: number;
}

export interface ListPageOptions {
  page?: number;
  perPage?: number;
}

export abstract class BaseResource {
  protected readonly t: Transport;
  protected readonly client: Client;

  constructor(client: Client) {
    this.client = client;
    this.t = client._t;
  }

  /** Resolve the effective fleet id (explicit arg, else the client default). */
  protected fleet(fleetId?: string): string {
    const fid = fleetId ?? this.client.fleetId;
    if (!fid) {
      throw new Error(
        "No fleetId; pass one or set a default on the client (CMDOP_FLEET_ID).",
      );
    }
    return fid;
  }

  /** Build the proto `OffsetPage{offset, per_page}` from a 1-based page number. */
  protected offsetPage(page = 1, perPage?: number): OffsetPage {
    const pp = perPage ?? 0;
    const offset = pp ? (Math.max(page, 1) - 1) * pp : 0;
    return create(OffsetPageSchema, { offset, perPage: pp });
  }

  /** Send a unary REQUEST envelope; the typed arm is read by the caller. */
  protected unary(req: Envelope): Promise<Envelope> {
    return this.t.callUnary(req);
  }

  /** Convenience: construct a REQUEST envelope from a oneof payload init. */
  protected req(payload: PayloadInit): Envelope {
    return create(EnvelopeSchema, { payload });
  }

  // -- pagination helpers ------------------------------------------------

  protected async *paginateCursor<T, P extends CursorList<T>>(
    fetchPage: (cursor: string | undefined) => Promise<P>,
  ): AsyncGenerator<T> {
    let cursor: string | undefined;
    for (;;) {
      const page = await fetchPage(cursor);
      for (const item of page.items) yield item;
      const next = page.nextCursor || undefined;
      if (!next) return;
      if (page.hasMore === false) return;
      cursor = next;
    }
  }

  protected async *pagesCursor<T, P extends CursorList<T>>(
    fetchPage: (cursor: string | undefined) => Promise<P>,
  ): AsyncGenerator<P> {
    let cursor: string | undefined;
    for (;;) {
      const page = await fetchPage(cursor);
      yield page;
      const next = page.nextCursor || undefined;
      if (!next) return;
      if (page.hasMore === false) return;
      cursor = next;
    }
  }

  protected async *paginateOffset<T, P extends OffsetList<T>>(
    fetchPage: (page: number) => Promise<P>,
  ): AsyncGenerator<T> {
    let page = 1;
    for (;;) {
      const p = await fetchPage(page);
      for (const item of p.items) yield item;
      if (p.items.length === 0) return;
      if (p.total > 0 && p.offset + p.items.length >= p.total) return;
      if (p.total === 0) return;
      page += 1;
    }
  }

  protected async *pagesOffset<T, P extends OffsetList<T>>(
    fetchPage: (page: number) => Promise<P>,
  ): AsyncGenerator<P> {
    let page = 1;
    for (;;) {
      const p = await fetchPage(page);
      yield p;
      if (p.items.length === 0) return;
      if (p.total > 0 && p.offset + p.items.length >= p.total) return;
      if (p.total === 0) return;
      page += 1;
    }
  }
}

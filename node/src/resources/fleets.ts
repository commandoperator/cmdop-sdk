/**
 * `client.fleets` — list / get / create / update / disable, plus `members` and
 * `machines` sub-resources (lazy getters). `get` scans `list` client-side;
 * `disable` is soft-disable.
 */

import { MfaRequirement } from "../_proto/cmdop/core/v1/common_pb";
import type {
  FleetList,
  FleetSummary,
  MachineFleetLink,
  MemberInfo,
  MemberList,
} from "../_proto/cmdop/core/v1/fleets_pb";
import type { MachineList, MachineSummary } from "../_proto/cmdop/core/v1/machines_pb";
import { BaseResource, type ListPageOptions } from "./base";
import type { ListMachinesOptions } from "./machines";

const MFA: Record<string, MfaRequirement> = {
  none: MfaRequirement.NONE,
  optional: MfaRequirement.OPTIONAL,
  required: MfaRequirement.REQUIRED,
};

export class FleetsResource extends BaseResource {
  #members?: FleetMembersResource;
  get members(): FleetMembersResource {
    return (this.#members ??= new FleetMembersResource(this.client));
  }

  #machines?: FleetMachinesResource;
  get machines(): FleetMachinesResource {
    return (this.#machines ??= new FleetMachinesResource(this.client));
  }

  async list(opts: ListPageOptions = {}): Promise<FleetList> {
    const env = await this.unary(
      this.req({ case: "listFleetsReq", value: { page: this.offsetPage(opts.page, opts.perPage) } }),
    );
    return env.payload.value as FleetList;
  }

  iter(opts: ListPageOptions = {}): AsyncGenerator<FleetSummary> {
    return this.paginateOffset((page) => this.list({ page, perPage: opts.perPage }));
  }

  pages(opts: ListPageOptions = {}): AsyncGenerator<FleetList> {
    return this.pagesOffset((page) => this.list({ page, perPage: opts.perPage }));
  }

  /** Get a single fleet by scanning the (offset-paginated) list. */
  async get(fleetId: string): Promise<FleetSummary> {
    for await (const f of this.iter()) {
      if (f.id === fleetId) return f;
    }
    const { NotFoundError } = await import("../errors");
    throw new NotFoundError(`Fleet ${fleetId} not found`, undefined, "not_found");
  }

  async create(body: {
    name: string;
    slug: string;
    mfaRequired?: string;
  }): Promise<FleetSummary> {
    const env = await this.unary(
      this.req({
        case: "createFleetReq",
        value: {
          name: body.name,
          slug: body.slug,
          mfaRequired: MFA[body.mfaRequired ?? "none"] ?? MfaRequirement.NONE,
        },
      }),
    );
    return env.payload.value as FleetSummary;
  }

  async update(
    fleetId: string,
    body: { name?: string; mfaRequired?: string } = {},
  ): Promise<FleetSummary> {
    const value: { fleetId: string; name: string; mfaRequired?: MfaRequirement } = {
      fleetId,
      name: body.name ?? "",
    };
    if (body.mfaRequired !== undefined) {
      value.mfaRequired = MFA[body.mfaRequired] ?? MfaRequirement.NONE;
    }
    const env = await this.unary(this.req({ case: "updateFleetReq", value }));
    return env.payload.value as FleetSummary;
  }

  /** Soft-disable (not delete). */
  async disable(fleetId: string): Promise<void> {
    await this.unary(this.req({ case: "disableFleetReq", value: { fleetId } }));
  }
}

export class FleetMembersResource extends BaseResource {
  async list(fleetId?: string, opts: ListPageOptions = {}): Promise<MemberList> {
    const fid = this.fleet(fleetId);
    const env = await this.unary(
      this.req({
        case: "listMembersReq",
        value: { fleetId: fid, page: this.offsetPage(opts.page, opts.perPage) },
      }),
    );
    return env.payload.value as MemberList;
  }

  iter(fleetId?: string, opts: ListPageOptions = {}): AsyncGenerator<MemberInfo> {
    return this.paginateOffset((page) => this.list(fleetId, { page, perPage: opts.perPage }));
  }

  async add(
    body: { email: string; role?: string },
    opts: { fleetId?: string } = {},
  ): Promise<MemberInfo> {
    const fid = this.fleet(opts.fleetId);
    const env = await this.unary(
      this.req({ case: "addMemberReq", value: { fleetId: fid, email: body.email, role: body.role ?? "member" } }),
    );
    return env.payload.value as MemberInfo;
  }

  async setRole(userId: string, role: string, opts: { fleetId?: string } = {}): Promise<MemberInfo> {
    const fid = this.fleet(opts.fleetId);
    const env = await this.unary(
      this.req({ case: "setMemberRoleReq", value: { fleetId: fid, userId, role } }),
    );
    return env.payload.value as MemberInfo;
  }

  async remove(userId: string, opts: { fleetId?: string } = {}): Promise<void> {
    const fid = this.fleet(opts.fleetId);
    await this.unary(this.req({ case: "removeMemberReq", value: { fleetId: fid, userId } }));
  }
}

export class FleetMachinesResource extends BaseResource {
  async list(fleetId?: string, opts: ListMachinesOptions = {}): Promise<MachineList> {
    const fid = this.fleet(fleetId);
    const env = await this.unary(
      this.req({
        case: "listFleetMachinesReq",
        value: {
          fleetId: fid,
          presence: opts.presence ?? "any",
          q: opts.q ?? "",
          limit: opts.limit ?? 100,
          cursor: opts.cursor ?? "",
        },
      }),
    );
    return env.payload.value as MachineList;
  }

  iter(fleetId?: string, opts: ListMachinesOptions = {}): AsyncGenerator<MachineSummary> {
    return this.paginateCursor((cursor) => this.list(fleetId, { ...opts, cursor }));
  }

  async attach(machineId: string, opts: { fleetId?: string } = {}): Promise<MachineFleetLink> {
    const fid = this.fleet(opts.fleetId);
    const env = await this.unary(
      this.req({ case: "attachMachineReq", value: { fleetId: fid, machineId } }),
    );
    return env.payload.value as MachineFleetLink;
  }

  async detach(machineId: string, opts: { fleetId?: string } = {}): Promise<void> {
    const fid = this.fleet(opts.fleetId);
    await this.unary(this.req({ case: "detachMachineReq", value: { fleetId: fid, machineId } }));
  }
}

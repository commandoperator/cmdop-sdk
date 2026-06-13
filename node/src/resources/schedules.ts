/**
 * `client.schedules` — list / get / create / update / delete / trigger / runs.
 * Fleet-scoped (default-fleet fallback). `delete` (not disable). `runs` is
 * cursor-paginated; `list` is offset-paginated.
 */

import { ScheduleTargetKind } from "../_proto/cmdop/core/v1/common_pb";
import { UpdateScheduleRequestSchema } from "../_proto/cmdop/core/v1/schedules_pb";
import type {
  ManualTriggerResponse,
  ScheduleList,
  ScheduleRunList,
  ScheduleRunView,
  ScheduleView,
} from "../_proto/cmdop/core/v1/schedules_pb";
import { create } from "@bufbuild/protobuf";
import { BaseResource, type ListPageOptions } from "./base";

const TARGET: Record<string, ScheduleTargetKind> = {
  all_fleet_machines: ScheduleTargetKind.ALL_FLEET_MACHINES,
  specific_machines: ScheduleTargetKind.SPECIFIC_MACHINES,
};

export interface CreateScheduleOptions {
  name: string;
  cronExpr: string;
  command: string;
  description?: string;
  timezone?: string;
  targetKind?: string;
  isEnabled?: boolean;
  machineIds?: string[];
  fleetId?: string;
}

export interface UpdateScheduleOptions {
  name?: string;
  cronExpr?: string;
  command?: string;
  description?: string;
  timezone?: string;
  targetKind?: string;
  isEnabled?: boolean;
  machineIds?: string[];
  fleetId?: string;
}

export interface RunsOptions {
  fleetId?: string;
  limit?: number;
  cursor?: string;
}

export class SchedulesResource extends BaseResource {
  async list(opts: ListPageOptions & { fleetId?: string } = {}): Promise<ScheduleList> {
    const fid = this.fleet(opts.fleetId);
    const env = await this.unary(
      this.req({
        case: "listSchedulesReq",
        value: { fleetId: fid, page: this.offsetPage(opts.page, opts.perPage) },
      }),
    );
    return env.payload.value as ScheduleList;
  }

  iter(opts: ListPageOptions & { fleetId?: string } = {}): AsyncGenerator<ScheduleView> {
    return this.paginateOffset((page) =>
      this.list({ page, perPage: opts.perPage, fleetId: opts.fleetId }),
    );
  }

  pages(opts: ListPageOptions & { fleetId?: string } = {}): AsyncGenerator<ScheduleList> {
    return this.pagesOffset((page) =>
      this.list({ page, perPage: opts.perPage, fleetId: opts.fleetId }),
    );
  }

  async get(scheduleId: string, opts: { fleetId?: string } = {}): Promise<ScheduleView> {
    const fid = this.fleet(opts.fleetId);
    const env = await this.unary(
      this.req({ case: "getScheduleReq", value: { fleetId: fid, scheduleId } }),
    );
    return env.payload.value as ScheduleView;
  }

  async create(opts: CreateScheduleOptions): Promise<ScheduleView> {
    const fid = this.fleet(opts.fleetId);
    const env = await this.unary(
      this.req({
        case: "createScheduleReq",
        value: {
          fleetId: fid,
          name: opts.name,
          cronExpr: opts.cronExpr,
          command: opts.command,
          description: opts.description ?? "",
          timezone: opts.timezone ?? "UTC",
          targetKind: TARGET[opts.targetKind ?? "all_fleet_machines"] ?? ScheduleTargetKind.ALL_FLEET_MACHINES,
          isEnabled: opts.isEnabled ?? true,
          machineIds: opts.machineIds ?? [],
        },
      }),
    );
    return env.payload.value as ScheduleView;
  }

  async update(scheduleId: string, opts: UpdateScheduleOptions): Promise<ScheduleView> {
    const fid = this.fleet(opts.fleetId);
    const body = create(UpdateScheduleRequestSchema, { fleetId: fid, scheduleId });
    if (opts.name !== undefined) body.name = opts.name;
    if (opts.description !== undefined) body.description = opts.description;
    if (opts.cronExpr !== undefined) body.cronExpr = opts.cronExpr;
    if (opts.timezone !== undefined) body.timezone = opts.timezone;
    if (opts.command !== undefined) body.command = opts.command;
    if (opts.targetKind !== undefined) {
      body.targetKind = TARGET[opts.targetKind] ?? ScheduleTargetKind.ALL_FLEET_MACHINES;
    }
    if (opts.isEnabled !== undefined) body.isEnabled = opts.isEnabled;
    if (opts.machineIds !== undefined) body.machineIds = opts.machineIds;
    const env = await this.unary(this.req({ case: "updateScheduleReq", value: body }));
    return env.payload.value as ScheduleView;
  }

  async delete(scheduleId: string, opts: { fleetId?: string } = {}): Promise<void> {
    const fid = this.fleet(opts.fleetId);
    await this.unary(this.req({ case: "deleteScheduleReq", value: { fleetId: fid, scheduleId } }));
  }

  /** Run now. */
  async trigger(scheduleId: string, opts: { fleetId?: string } = {}): Promise<ManualTriggerResponse> {
    const fid = this.fleet(opts.fleetId);
    const env = await this.unary(
      this.req({ case: "triggerScheduleReq", value: { fleetId: fid, scheduleId } }),
    );
    return env.payload.value as ManualTriggerResponse;
  }

  /** Run history (cursor-paginated, newest first). */
  async runs(scheduleId: string, opts: RunsOptions = {}): Promise<ScheduleRunList> {
    const fid = this.fleet(opts.fleetId);
    const env = await this.unary(
      this.req({
        case: "scheduleRunsReq",
        value: { fleetId: fid, scheduleId, limit: opts.limit ?? 50, cursor: opts.cursor ?? "" },
      }),
    );
    return env.payload.value as ScheduleRunList;
  }

  iterRuns(scheduleId: string, opts: Omit<RunsOptions, "cursor"> = {}): AsyncGenerator<ScheduleRunView> {
    return this.paginateCursor((cursor) =>
      this.runs(scheduleId, { ...opts, cursor }).then((p) => ({
        items: p.items,
        nextCursor: p.nextCursor,
        hasMore: p.nextCursor != null && p.nextCursor !== "",
      })),
    );
  }

  pagesRuns(scheduleId: string, opts: Omit<RunsOptions, "cursor"> = {}): AsyncGenerator<ScheduleRunList> {
    return this.pagesCursor((cursor) =>
      this.runs(scheduleId, { ...opts, cursor }).then((p) => ({
        items: p.items,
        nextCursor: p.nextCursor,
        hasMore: p.nextCursor != null && p.nextCursor !== "",
      })),
    ) as AsyncGenerator<ScheduleRunList>;
  }
}

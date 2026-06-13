/**
 * `client.skills` — the marketplace surface (Django platform plane).
 *
 * Skills live on Django (`UserAPIKey` / `X-Api-Key`), NOT the relay — the
 * spawned `cmdop-core` reaches them with `CMDOP_API_KEY` (passed through at
 * spawn), distinct from the relay `CMDOP_TOKEN` that drives machines/fleets.
 *
 * Browse / install / publish / manage your own skills + the read-only taxonomy
 * (categories, tags). Mirrors the Python `cmdop_skill` framework's marketplace
 * operations, baked into the Go core so any language gets them.
 */

import type {
  SkillCategoryList,
  SkillCreated,
  SkillDetail,
  SkillInstall,
  SkillListPage,
  SkillReviewPage,
  SkillsPublishResponse,
  SkillsPublishStatusResponse,
  SkillStar,
  SkillTagList,
  SkillUpdated,
  SkillVersionList,
} from "../_proto/cmdop/core/v1/skills_pb";
import { BaseResource } from "./base";

export interface SkillsListOptions {
  category?: string;
  tag?: string;
  search?: string;
  lang?: string;
  ordering?: string;
  page?: number;
  pageSize?: number;
}

export interface SkillsMyOptions {
  search?: string;
  ordering?: string;
  page?: number;
  pageSize?: number;
}

export interface SkillsReviewsOptions {
  search?: string;
  ordering?: string;
  page?: number;
  pageSize?: number;
}

export interface SkillsUpdateOptions {
  name?: string;
  category?: string;
  visibility?: string;
  status?: string;
  icon?: string;
  cover?: string;
  repositoryUrl?: string;
}

export interface SkillsPublishOptions {
  skillMd?: string;
  readme?: string;
  changelog?: string;
}

export interface TaxonomyOptions {
  search?: string;
  ordering?: string;
}

export class SkillsResource extends BaseResource {
  // -- browse / detail ---------------------------------------------------

  async list(opts: SkillsListOptions = {}): Promise<SkillListPage> {
    const env = await this.unary(
      this.req({ case: "skillsListReq", value: { ...opts } }),
    );
    return env.payload.value as SkillListPage;
  }

  async get(slug: string, opts: { lang?: string } = {}): Promise<SkillDetail> {
    const env = await this.unary(
      this.req({ case: "skillsGetReq", value: { slug, lang: opts.lang } }),
    );
    return env.payload.value as SkillDetail;
  }

  async my(opts: SkillsMyOptions = {}): Promise<SkillListPage> {
    const env = await this.unary(
      this.req({ case: "skillsMyReq", value: { ...opts } }),
    );
    return env.payload.value as SkillListPage;
  }

  // -- install / star ----------------------------------------------------

  async install(slug: string): Promise<SkillInstall> {
    const env = await this.unary(this.req({ case: "skillsInstallReq", value: { slug } }));
    return env.payload.value as SkillInstall;
  }

  async star(slug: string): Promise<SkillStar> {
    const env = await this.unary(this.req({ case: "skillsStarReq", value: { slug } }));
    return env.payload.value as SkillStar;
  }

  // -- versions / reviews ------------------------------------------------

  async versions(slug: string): Promise<SkillVersionList> {
    const env = await this.unary(this.req({ case: "skillsVersionsReq", value: { slug } }));
    return env.payload.value as SkillVersionList;
  }

  async reviews(slug: string, opts: SkillsReviewsOptions = {}): Promise<SkillReviewPage> {
    const env = await this.unary(
      this.req({ case: "skillsReviewsReq", value: { slug, ...opts } }),
    );
    return env.payload.value as SkillReviewPage;
  }

  // -- create / update / delete ------------------------------------------

  async create(name: string): Promise<SkillCreated> {
    const env = await this.unary(this.req({ case: "skillsCreateReq", value: { name } }));
    return env.payload.value as SkillCreated;
  }

  async update(slug: string, opts: SkillsUpdateOptions = {}): Promise<SkillUpdated> {
    const env = await this.unary(
      this.req({ case: "skillsUpdateReq", value: { slug, ...opts } }),
    );
    return env.payload.value as SkillUpdated;
  }

  async delete(slug: string): Promise<void> {
    await this.unary(this.req({ case: "skillsDeleteReq", value: { slug } }));
  }

  // -- publish (async) ---------------------------------------------------

  async publish(
    slug: string,
    rawManifest: string,
    opts: SkillsPublishOptions = {},
  ): Promise<SkillsPublishResponse> {
    const env = await this.unary(
      this.req({ case: "skillsPublishReq", value: { slug, rawManifest, ...opts } }),
    );
    return env.payload.value as SkillsPublishResponse;
  }

  async publishStatus(slug: string): Promise<SkillsPublishStatusResponse> {
    const env = await this.unary(
      this.req({ case: "skillsPublishStatusReq", value: { slug } }),
    );
    return env.payload.value as SkillsPublishStatusResponse;
  }

  // -- taxonomy ----------------------------------------------------------

  async categories(opts: TaxonomyOptions = {}): Promise<SkillCategoryList> {
    const env = await this.unary(this.req({ case: "skillsCategoriesReq", value: { ...opts } }));
    return env.payload.value as SkillCategoryList;
  }

  async tags(opts: TaxonomyOptions = {}): Promise<SkillTagList> {
    const env = await this.unary(this.req({ case: "skillsTagsReq", value: { ...opts } }));
    return env.payload.value as SkillTagList;
  }
}

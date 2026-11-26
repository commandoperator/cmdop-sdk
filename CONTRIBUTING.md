# Contributing to the CMDOP SDK

For a bug, include your package version, runtime, tool name, error code and a small reproducer.
Remove tokens, computer identifiers and personal data. You can
[open an issue](https://github.com/commandoperator/cmdop-sdk/issues) with a documentation correction
or a useful workflow as well. Generated SDK/reference changes are routed to their source by maintainers.

## Editorial updates

Read [AGENTS.md](AGENTS.md). The editorial paths are `README.md`, `showcase/*.md` (including
subdirectories) and approved assets under `assets/`. Everything else is maintainer-owned.

Start from an up-to-date public checkout and capture its commit before editing:

```bash
git fetch origin
git switch -c content/my-change origin/main
CONTENT_BASE=$(git rev-parse HEAD)
```

Edit the requested material, then run the dependency-free check with Node.js 20+:

```bash
node tools/content-check.mjs --base "$CONTENT_BASE"
git diff --check
git diff --stat "$CONTENT_BASE"
```

The check covers changed paths (both sides of renames), local links/anchors and images, alt text,
approved asset hashes, size/type limits and common secret/private-data patterns. It also refuses
changed executable code fences: ask a maintainer to validate an example update against the released
SDK rather than adding unverified code during a copy change. It does not execute examples, access
computers, verify product claims or prove that a campaign worked.

Inspect the actual diff. Stage and commit only the exact files you changed:

```bash
git add -- README.md
git diff --cached --stat
git commit -m "docs: clarify the first useful outcome" -- README.md
node tools/content-check.mjs --base "$CONTENT_BASE"
git push -u origin content/my-change
```

Adjust the explicit file list and branch name to the task. Open a pull request when your assigned
workflow uses review. Direct pushes require the access/policy assigned by the maintainer; these
instructions grant no credentials. If public main advances during your work, fetch it, reapply
your own change on the fresh tip and rerun the check. Do not force push over other writers.

No SDK build, version bump, npm/PyPI login, release tag or GitHub release is part of this procedure.
Technical guides in `docs/` are exported; propose their correction to maintainers instead of
hand-editing the snapshot. Public editorial content survives subsequent SDK releases.

## Maintainer checks

`node --test tools/content-check.test.mjs` runs isolated filesystem/Git fixtures without network
or package dependencies. `node tools/content-check.mjs --audit` audits current editorial text and
links without claiming to validate an editorial diff. Maintainers use separate source, example
and snapshot checks for code changes and generated documentation publication.

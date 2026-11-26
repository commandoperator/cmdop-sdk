import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { mkdirSync, mkdtempSync, readFileSync, renameSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { test } from "node:test";
import { checkContent } from "./content-check.mjs";

const git = (root, ...args) => execFileSync("git", args, { cwd: root, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }).trim();
const put = (root, file, value) => { mkdirSync(path.dirname(path.join(root, file)), { recursive: true }); writeFileSync(path.join(root, file), value); };
function fixture(t) {
  const root = mkdtempSync(path.join(tmpdir(), "sdk-content-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  git(root, "init"); git(root, "config", "user.email", "fixture@example.invalid"); git(root, "config", "user.name", "Fixture");
  put(root, "README.md", '# SDK\n\n[Guide](docs/README.md#next)\n\n```ts\nimport cmdop from "example";\n```\n');
  put(root, "docs/README.md", "# Guide\n\n## Next\n");
  put(root, "LICENSE", "license\n");
  put(root, "tools/approved-assets.json", JSON.stringify({ schema: 1, sha256: {} }));
  git(root, "add", "."); git(root, "commit", "-m", "baseline");
  return { root, base: git(root, "rev-parse", "HEAD") };
}

test("copy changes and a new linked showcase need no SDK build", (t) => {
  const { root, base } = fixture(t);
  const text = readFileSync(path.join(root, "README.md"), "utf8");
  put(root, "README.md", text + "\n[Story](showcase/build.md)\n");
  put(root, "showcase/build.md", "# A useful build\n\n[Try it](../docs/README.md#next)\n");
  const result = checkContent(root, { base });
  assert.deepEqual(result.findings, []); assert.equal(result.changedPaths, 2);
  git(root, "add", "README.md", "showcase/build.md"); git(root, "commit", "-m", "copy");
  assert.deepEqual(checkContent(root, { base }).findings, []);
  assert.equal(result.liveCalls, "not run"); assert.equal(result.snippetTypecheck, "not run");
});

test("both sides of a rename and untracked code/control edits are detected", (t) => {
  const { root, base } = fixture(t);
  mkdirSync(path.join(root, "showcase")); renameSync(path.join(root, "LICENSE"), path.join(root, "showcase/license.md"));
  put(root, "python/new.py", "print('foreign')\n");
  const result = checkContent(root, { base });
  assert(result.findings.some((x) => x.startsWith("LICENSE: outside")));
  assert(result.findings.some((x) => x.startsWith("python/new.py: outside")));
  rmSync(path.join(root, "README.md"));
  assert(checkContent(root, { base }).findings.some((x) => x.includes("root README is required")));
});

test("examples are compared to the captured base, including after committing", (t) => {
  const { root, base } = fixture(t);
  const file = path.join(root, "README.md");
  put(root, "README.md", readFileSync(file, "utf8").replace('import cmdop from "example";', "const changed = 1;"));
  git(root, "add", "README.md"); git(root, "commit", "-m", "example");
  assert(checkContent(root, { base }).findings.some((x) => x.includes("executable examples changed")));
});

test("links, code-fence heading impostors, references and image alt text are checked", (t) => {
  const { root, base } = fixture(t);
  put(root, "showcase/broken.md", '# Story\n\n[Missing](../missing.md)\n[Anchor](../docs/README.md#inside-code)\n![ ](../assets/no.png)\n[ref][missing-ref]\n<img src="../assets/no.png" alt="">\n');
  put(root, "docs/README.md", "# Guide\n\n## Next\n\n```text\n## Inside code\n```\n");
  const result = checkContent(root, { base });
  for (const text of ["missing link target", "missing anchor", "image needs useful alt", "unresolved link reference", "HTML image"]) {
    assert(result.findings.some((x) => x.includes(text)), text);
  }
});

test("approved images pass and changed images require an exact maintainer hash", (t) => {
  const { root } = fixture(t);
  const svg = '<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0"/></svg>';
  put(root, "tools/approved-assets.json", JSON.stringify({ schema: 1, sha256: { "assets/mark.svg": createHash("sha256").update(svg).digest("hex") } }));
  git(root, "add", "tools/approved-assets.json"); git(root, "commit", "-m", "approval");
  const base = git(root, "rev-parse", "HEAD");
  put(root, "assets/mark.svg", svg); put(root, "showcase/logo.md", "# Logo\n\n![CMDOP](../assets/mark.svg)\n");
  assert.deepEqual(checkContent(root, { base }).findings, []);
  put(root, "assets/mark.svg", svg + " ");
  assert(checkContent(root, { base }).findings.some((x) => x.includes("not maintainer-approved")));
  put(root, "assets/oversize.png", Buffer.alloc(1024 * 1024 + 1));
  assert(checkContent(root, { base }).findings.some((x) => x.includes("exceeds 1 MiB")));
});

test("privacy, escaping links, remote images and symlinks fail without exposing content", (t) => {
  const { root, base } = fixture(t);
  put(root, "showcase/private.md", "# Private\n\n" + "ghp_" + "x".repeat(40) + "\n![remote](https://example.invalid/a.png)\n[escape](../../outside.md)\n");
  symlinkSync(path.join(root, "LICENSE"), path.join(root, "showcase/symlink.md"));
  const result = checkContent(root, { base });
  for (const text of ["GitHub token", "remote image", "escapes repository", "regular file"]) assert(result.findings.some((x) => x.includes(text)), text);
  assert(!JSON.stringify(result).includes("x".repeat(40)));
  assert.throws(() => checkContent(root), /--base/);
});

import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { existsSync, lstatSync, readFileSync, readdirSync, realpathSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const imageTypes = new Set([".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"]);
const executable = new Set(["ts", "typescript", "js", "javascript", "python", "py", "sh", "bash", "shell"]);
const secretPatterns = [
  ["private key", /-----BEGIN [A-Z ]*PRIVATE KEY-----/],
  ["GitHub token", /\bgh[pousr]_[A-Za-z0-9]{30,}/],
  ["npm token", /\bnpm_[A-Za-z0-9]{30,}/],
  ["PyPI token", /\bpypi-[A-Za-z0-9_-]{50,}/],
  ["credential assignment", /(?:CMDOP_TOKEN|api_key)\s*[=:]\s*["']?[A-Za-z0-9_-]{24,}/i],
  ["personal filesystem path", /\/(?:Users|home)\/[a-z][a-z0-9_-]+\//i],
  ["private network address", /\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b/],
];
const git = (root, ...args) => execFileSync("git", args, { cwd: root, encoding: "utf8", maxBuffer: 8 * 1024 * 1024 });
const markdown = (file) => file === "README.md" || /^showcase\/.+\.md$/.test(file);
const allowed = (file) => markdown(file) || (file.startsWith("assets/") && imageTypes.has(path.extname(file).toLowerCase()));
const withoutCode = (text) => text.replace(/^([ \t]*)(`{3,}|~{3,})[^\n]*\n[\s\S]*?^\1\2[^\n]*$/gm, "");

function codeBlocks(text) {
  const blocks = []; let active = null;
  for (const line of text.split("\n")) {
    if (!active) {
      const start = /^\s*(`{3,}|~{3,})([\w+-]*)/.exec(line);
      if (start) active = { mark: start[1][0], size: start[1].length, lang: start[2].toLowerCase(), lines: [] };
    } else if (new RegExp(`^\\s*${active.mark}{${active.size},}\\s*$`).test(line)) {
      if (executable.has(active.lang)) blocks.push([active.lang, active.lines.join("\n")]);
      active = null;
    } else active.lines.push(line);
  }
  if (active) throw new Error("Unclosed code fence");
  return JSON.stringify(blocks);
}

function anchors(text) {
  const source = withoutCode(text), out = new Set(), counts = new Map();
  for (const match of source.matchAll(/^#{1,6}\s+(.+?)\s*#*$/gm)) {
    const slug = match[1].replace(/<[^>]*>/g, "").toLowerCase().replace(/[^\p{L}\p{N}_ -]/gu, "").replace(/ /g, "-");
    const n = counts.get(slug) ?? 0; counts.set(slug, n + 1);
    out.add(n ? `${slug}-${n}` : slug);
  }
  for (const match of source.matchAll(/\b(?:id|name)=["']([^"']+)["']/g)) out.add(match[1]);
  return out;
}

function walk(root, prefix) {
  if (!existsSync(path.join(root, prefix))) return [];
  return readdirSync(path.join(root, prefix)).flatMap((name) => {
    const file = `${prefix}/${name}`, stat = lstatSync(path.join(root, file));
    return stat.isDirectory() && !stat.isSymbolicLink() ? walk(root, file) : [file];
  });
}

export function checkContent(directory, { base, audit = false } = {}) {
  const root = realpathSync(directory), findings = [];
  const fail = (file, reason) => findings.push(`${file}: ${reason}`);
  if (!existsSync(path.join(root, "README.md"))) fail("README.md", "root README is required");
  let revision, changed = [];
  if (!audit) {
    if (!base || base.startsWith("-")) throw new Error("Supply --base with the public commit captured before editing");
    revision = git(root, "rev-parse", "--verify", "--end-of-options", `${base}^{commit}`).trim();
    changed = [...new Set([
      ...git(root, "diff", "--name-only", "--no-renames", "-z", revision, "--").split("\0"),
      ...git(root, "ls-files", "--others", "--exclude-standard", "-z").split("\0"),
    ].filter(Boolean))];
    for (const file of changed) if (!allowed(file)) fail(file, "outside editorial ownership");
  }
  const approved = JSON.parse(readFileSync(path.join(root, "tools/approved-assets.json"), "utf8"));
  if (approved.schema !== 1 || !approved.sha256 || typeof approved.sha256 !== "object") throw new Error("Invalid approved asset registry");
  const inspected = [...new Set(["README.md", ...walk(root, "showcase").filter(markdown), ...changed.filter(allowed)])];
  for (const file of inspected) {
    const abs = path.join(root, file);
    const stat = lstatSync(abs, { throwIfNoEntry: false });
    if (!stat) continue; // Deletions are checked by inbound links below.
    if (!stat.isFile() || stat.isSymbolicLink()) { fail(file, "expected a regular file"); continue; }
    if (!realpathSync(abs).startsWith(root + path.sep)) { fail(file, "file resolves outside repository"); continue; }
    const bytes = readFileSync(abs);
    const isImage = file.startsWith("assets/");
    if (isImage) {
      if (bytes.length > 1024 * 1024) fail(file, "image exceeds 1 MiB");
      if (changed.includes(file) && approved.sha256[file] !== createHash("sha256").update(bytes).digest("hex")) fail(file, "image hash is not maintainer-approved");
      if (path.extname(file).toLowerCase() !== ".svg") continue;
    } else if (bytes.length > 128 * 1024) fail(file, "Markdown exceeds 128 KiB");
    const text = bytes.toString("utf8");
    for (const [label, pattern] of secretPatterns) if (pattern.test(text)) fail(file, label);
    if (isImage) {
      if (/<(?:script|foreignObject)\b|\bon\w+\s*=|(?:href|src)=["'](?:https?:|javascript:|data:)/i.test(text)) fail(file, "SVG contains active or external content");
      continue;
    }
    if (!audit && changed.includes(file)) {
      const existsBefore = git(root, "ls-tree", "--name-only", revision, "--", file).trim() !== "";
      const before = existsBefore ? git(root, "show", `${revision}:${file}`) : "";
      try { if (codeBlocks(text) !== codeBlocks(before)) fail(file, "executable examples changed; requires maintainer validation against the released SDK"); }
      catch (e) { fail(file, e.message); }
    }
    const source = withoutCode(text);
    const refs = new Map([...source.matchAll(/^\s*\[([^\]]+)\]:\s*(<[^>]+>|\S+)/gm)].map((m) => [m[1].toLowerCase(), m[2].replace(/^<|>$/g, "")]));
    const links = [...source.matchAll(/(!?)\[([^\]]*)\]\((<[^>]+>|[^\s)]+)(?:\s+["'][^\n]*?["'])?\)/g)].map((m) => ({ image: Boolean(m[1]), alt: m[2], href: m[3].replace(/^<|>$/g, "") }));
    for (const m of source.matchAll(/(!?)\[([^\]]*)\]\[([^\]]*)\]/g)) {
      const href = refs.get((m[3] || m[2]).toLowerCase());
      if (href) links.push({ image: Boolean(m[1]), alt: m[2], href });
      else fail(file, `unresolved link reference: ${m[3] || m[2]}`);
    }
    for (const m of source.matchAll(/<(?:a|img|source)\b[^>]*>/gi)) {
      const tag = m[0], isImg = /^<img\b/i.test(tag);
      if (isImg && !/\balt=["']([^"']*)["']/i.exec(tag)?.[1].trim()) fail(file, "HTML image needs useful alt text");
      for (const attr of tag.matchAll(/\b(href|src|srcset)=["']([^"']+)["']/gi)) {
        const targets = attr[1].toLowerCase() === "srcset" ? attr[2].split(",").map((s) => s.trim().split(/\s+/)[0]) : [attr[2]];
        for (const href of targets) links.push({ image: attr[1].toLowerCase() !== "href", alt: "HTML image", href });
      }
    }
    for (const link of links) {
      if (link.image && !link.alt.trim()) fail(file, "image needs useful alt text");
      if (/^(?:https?:|mailto:)/i.test(link.href)) {
        if (link.image) fail(file, "use a local approved image instead of a remote image");
        continue;
      }
      if (/^[a-z][a-z0-9+.-]*:|^\/\//i.test(link.href)) { fail(file, "unsupported link scheme"); continue; }
      let target, fragment;
      try {
        const [name, hash] = link.href.split("#");
        fragment = hash === undefined ? undefined : decodeURIComponent(hash);
        target = name ? path.resolve(path.dirname(abs), decodeURIComponent(name)) : abs;
      } catch { fail(file, "malformed local link"); continue; }
      if (target !== root && !target.startsWith(root + path.sep)) { fail(file, "link escapes repository"); continue; }
      if (!existsSync(target)) { fail(file, `missing link target: ${link.href}`); continue; }
      if (!realpathSync(target).startsWith(root + path.sep) && realpathSync(target) !== root) { fail(file, "link follows a symlink outside repository"); continue; }
      if (fragment && target.endsWith(".md") && !anchors(readFileSync(target, "utf8")).has(fragment)) fail(file, `missing anchor: ${link.href}`);
    }
  }
  return { mode: audit ? "maintainer audit" : "editorial diff", base: revision ?? null, changedPaths: changed.length, inspectedFiles: inspected.length, findings,
    examples: audit ? "not compared; maintainer audit only" : "changed executable fences require maintainer validation", liveCalls: "not run", snippetTypecheck: "not run" };
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  try {
    const args = process.argv.slice(2);
    const audit = args.length === 1 && args[0] === "--audit";
    if (!audit && !(args.length === 2 && args[0] === "--base")) throw new Error("Usage: node tools/content-check.mjs --base <commit> | --audit");
    const result = checkContent(process.cwd(), { base: audit ? undefined : args[1], audit });
    console.log(JSON.stringify(result, null, 2));
    if (result.findings.length) process.exitCode = 1;
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}

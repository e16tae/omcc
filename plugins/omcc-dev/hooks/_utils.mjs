// Common utilities for omcc-dev continuity hooks.
// Pure Node.js built-ins — no external dependencies.
// See continuity-protocol.md for the contract this file implements.

import { readFile, rename, chmod, unlink, open } from "node:fs/promises";
import { openSync, closeSync, existsSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { resolve } from "node:path";

export const SANITIZE_CAP = 512;
const CTRL_CHARS = /[\x00-\x08\x0b-\x1f\x7f]/g;

export const WORKFLOW_ID_REGEX =
  /^(start|fix|audit)-\d{8}T\d{6}Z-(migrated-)?[0-9a-f]{6}$/;

export const TERMINAL_PHASES = ["commit-complete", "summary-complete"];

export const KNOWN_WORKFLOW_TYPES = ["start", "fix", "audit"];

// Schema version this hook layer understands. Files with higher
// `schema` are skipped with a stderr diagnostic per
// continuity-protocol.md §Parser rules.
export const SUPPORTED_SCHEMA_VERSION = 1;

export const COMMIT_SUBJECT_REGEX = {
  start: /^feat(\([^)]+\))?!?:/,
  fix: /^fix(\([^)]+\))?!?:/,
  audit: null,
};

export function sanitize(value, cap = SANITIZE_CAP) {
  if (typeof value !== "string") return "";
  let s = value.replace(CTRL_CHARS, "").replace(/`/g, "");
  if (s.length > cap) s = s.slice(0, cap);
  return s;
}

export function isValidWorkflowId(id) {
  return typeof id === "string" && WORKFLOW_ID_REGEX.test(id);
}

export function readStdinJson(timeoutMs = 100) {
  return new Promise((resolvePromise) => {
    let data = "";
    let resolved = false;
    const finish = () => {
      if (resolved) return;
      resolved = true;
      try { resolvePromise(data ? JSON.parse(data) : null); }
      catch { resolvePromise(null); }
    };
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (c) => { data += c; });
    process.stdin.on("end", finish);
    process.stdin.on("error", finish);
    setTimeout(finish, timeoutMs);
  });
}

// Parse YAML frontmatter. Returns { prefix, fmBody, suffix, body, fields }
// where `fields` holds top-level scalar string values only. Nested maps and
// lists must be extracted via getNestedMap or getListBlock.
export function parseFrontmatter(content) {
  const m = content.match(/^(---\s*\n)([\s\S]*?)(\n---\s*(?:\n|$))([\s\S]*)$/);
  if (!m) return null;
  const fields = {};
  for (const line of m[2].split("\n")) {
    if (!/^[a-zA-Z_]/.test(line)) continue;
    const kv = line.match(/^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$/);
    if (!kv) continue;
    const val = kv[2].trim();
    if (!val || val.startsWith("#")) continue;
    fields[kv[1]] = val.replace(/^"(.*)"$/, "$1").replace(/^'(.*)'$/, "$1");
  }
  return { prefix: m[1], fmBody: m[2], suffix: m[3], body: m[4], fields };
}

export function getNestedMap(fmBody, topKey) {
  const lines = fmBody.split("\n");
  const out = {};
  let inside = false;
  for (const line of lines) {
    if (!inside) {
      if (new RegExp(`^${topKey}:\\s*$`).test(line)) inside = true;
      continue;
    }
    if (/^\S/.test(line)) break;
    const kv = line.match(/^\s+([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$/);
    if (kv) {
      out[kv[1]] = kv[2].trim()
        .replace(/^"(.*)"$/, "$1")
        .replace(/^'(.*)'$/, "$1");
    }
  }
  return out;
}

// Parse active.md's `active:` list into [{id, type, phase, parent, children, originating_finding}]
export function parseActiveRegistry(content) {
  const parsed = parseFrontmatter(content);
  if (!parsed) return [];
  const m = parsed.fmBody.match(/(?:^|\n)active:\s*(?:\n([\s\S]*))?$/);
  if (!m || !m[1]) return [];
  const entries = [];
  let current = null;
  let inChildren = false;
  for (const line of m[1].split("\n")) {
    if (/^\S/.test(line) || line.trim() === "---") break;
    const idLine = line.match(/^\s*-\s*id:\s*(\S+)/);
    if (idLine) {
      if (current) entries.push(current);
      current = { id: idLine[1], children: [] };
      inChildren = false;
      continue;
    }
    if (!current) continue;
    const listItem = line.match(/^\s{6,}-\s*(\S+)/);
    if (inChildren && listItem) {
      current.children.push(listItem[1]);
      continue;
    }
    const kv = line.match(/^\s+([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$/);
    if (!kv) continue;
    const [, key, rawVal] = kv;
    inChildren = false;
    let val = rawVal.trim();
    if (key === "children") {
      inChildren = true;
      if (val === "[]") current.children = [];
      continue;
    }
    if (val === "null" || val === "") val = null;
    current[key] = val;
  }
  if (current) entries.push(current);
  return entries;
}

export function getGitInfo(cwd) {
  const env = { ...process.env, LC_ALL: "C" };
  const opts = { cwd, env, encoding: "utf8" };
  try {
    const branch = execFileSync("git", ["branch", "--show-current"], opts).trim();
    const head = execFileSync("git", ["rev-parse", "HEAD"], opts).trim();
    // --porcelain=v1 -z per continuity-protocol.md §Execution contract.
    // NUL-separated; unambiguous handling of filenames containing newlines
    // or quotes.
    const status = execFileSync("git", ["status", "--porcelain=v1", "-z"], opts);
    return { branch, head, status };
  } catch {
    return null;
  }
}

const SENSITIVE_FILE_PATTERNS = [/\.env/, /\.pem$/, /\.key$/, /id_rsa/, /\.p12$/, /\.pfx$/];

// Input: NUL-separated status output from `git status --porcelain=v1 -z`.
// Output: newline-joined "XY path" lines (or bare path for rename-from
// continuations), with any entry whose path component matches a
// SENSITIVE_FILE_PATTERNS regex removed.
//
// Rename/copy records in -z format span two NUL-separated tokens:
//   "R  new-path\0old-path\0"
// If EITHER path is sensitive, the ENTIRE entry (both tokens) is dropped
// — otherwise a sensitive companion path leaks into the snapshot.
export function filterSensitiveStatus(statusZ) {
  const tokens = statusZ.split("\0").filter(Boolean);
  const out = [];
  let i = 0;
  while (i < tokens.length) {
    const tok = tokens[i];
    const hasXY = /^[ MADRCU?!][ MADRCU?!] /.test(tok);
    const statusChar = hasXY ? tok.charAt(0) : " ";
    const path = hasXY ? tok.slice(3) : tok;
    const isRenameCopy = hasXY && (statusChar === "R" || statusChar === "C");
    // For rename/copy, the next token is the previous path and belongs to
    // the same entry. Consume it here.
    const companion = isRenameCopy && i + 1 < tokens.length ? tokens[i + 1] : null;
    const allPaths = companion ? [path, companion] : [path];
    const sensitive = allPaths.some(
      (p) => SENSITIVE_FILE_PATTERNS.some((r) => r.test(p))
    );
    if (!sensitive) {
      out.push(tok);
      if (companion !== null) out.push(companion);
    }
    i += companion !== null ? 2 : 1;
  }
  return out.join("\n");
}

export async function acquireLock(lockPath, timeoutMs = 5000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const fd = openSync(lockPath, "wx");
      closeSync(fd);
      return true;
    } catch (e) {
      if (e.code === "EEXIST") {
        await new Promise((r) => setTimeout(r, 100));
        continue;
      }
      return false;
    }
  }
  return false;
}

export async function releaseLock(lockPath) {
  try { await unlink(lockPath); } catch {}
}

// atomicModifyFile: read-modify-write under advisory lock.
// mutator signature: async (current: string | null) => string | null | undefined
//   - receives null when target does not exist
//   - returns new content to write, or null/undefined for no-op
// The full read → mutate → write sequence runs inside one lock acquisition,
// preventing lost updates between read and write. Errors from mutator
// release the lock and re-throw.
export async function atomicModifyFile(filePath, mutator) {
  const lockPath = `${filePath}.lock`;
  const acquired = await acquireLock(lockPath);
  if (!acquired) throw new Error(`lock timeout: ${filePath}`);
  try {
    const current = existsSync(filePath)
      ? await readFile(filePath, "utf8")
      : null;
    const next = await mutator(current);
    if (next === null || next === undefined) return;
    const tmp = `${filePath}.tmp`;
    const bak = `${filePath}.bak`;
    // Remove any stale tempfile (e.g., symlink planted by another process)
    // before exclusive-create. unlink ignores ENOENT.
    try { await unlink(tmp); } catch {}
    // Open with O_WRONLY|O_CREAT|O_EXCL, mode 0600 — fails on any
    // pre-existing file (regular OR symlink), defeating follow-symlink
    // write redirection. fsync before rename is required per
    // continuity-protocol.md §Atomic write discipline.
    const fh = await open(tmp, "wx", 0o600);
    try {
      await fh.writeFile(next, { encoding: "utf8" });
      await fh.sync();
    } finally {
      await fh.close();
    }
    if (existsSync(filePath)) {
      await rename(filePath, bak);
    }
    await rename(tmp, filePath);
    await chmod(filePath, 0o600);
  } finally {
    await releaseLock(lockPath);
  }
}

// Thin wrapper: atomic write with pre-computed content. Equivalent to
// atomicModifyFile(path, async () => newContent). Retained for callers
// that compute content outside the lock; see atomicModifyFile for RMW.
export async function atomicUpdateFile(filePath, newContent) {
  return atomicModifyFile(filePath, async () => newContent);
}

export function resolveActivePath(cwd) {
  return resolve(cwd, ".claude", "omcc-dev", "active.md");
}
export function resolveWorkflowPath(cwd, id) {
  return resolve(cwd, ".claude", "omcc-dev", "workflows", `${id}.md`);
}
export function resolveArchivePath(cwd, id) {
  return resolve(cwd, ".claude", "omcc-dev", "archive", `${id}.md`);
}

export function updateUpdatedAt(fmBody, isoTimestamp) {
  if (/^(\s*updated_at:\s*).*$/m.test(fmBody)) {
    return fmBody.replace(/^(\s*updated_at:\s*).*$/m, `$1${isoTimestamp}`);
  }
  return fmBody;
}

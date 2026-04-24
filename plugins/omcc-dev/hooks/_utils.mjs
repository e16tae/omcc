// Common utilities for omcc-dev continuity hooks.
// Pure Node.js built-ins — no external dependencies.
// See continuity-protocol.md for the contract this file implements.

import {
  readFile, rename, chmod, unlink, open, writeFile,
} from "node:fs/promises";
import { openSync, closeSync, existsSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { resolve } from "node:path";

export const SANITIZE_CAP = 512;
const CTRL_CHARS = /[\x00-\x08\x0b-\x1f\x7f]/g;

export const WORKFLOW_ID_REGEX =
  /^(start|fix|audit)-\d{8}T\d{6}Z-(migrated-)?[0-9a-f]{6}$/;

export const TERMINAL_PHASES = ["commit-complete", "summary-complete"];

export const KNOWN_WORKFLOW_TYPES = ["start", "fix", "audit"];

// Schema version this hook layer understands. Files with `schema`
// either higher (future) or lower (legacy) are skipped with a stderr
// diagnostic per continuity-protocol.md §Parser rules. Legacy schema
// files are carried across the migration window — `/omcc-dev:resume`
// offers the user an Import / Archive / Abort choice to migrate them.
export const SUPPORTED_SCHEMA_VERSION = 2;

// Returns true if the file's schema version is not actively supported
// (either legacy `schema < SUPPORTED` or future `schema > SUPPORTED`).
// Writes a one-line stderr diagnostic identifying the workflow and the
// calling hook. Callers should skip the workflow entirely when this
// returns true. `schema` may be `undefined` (field missing) — that
// case returns false so existing call sites keep their pre-schema-gate
// behavior.
export function handleLegacySchema(schema, workflowId, hookName) {
  if (typeof schema !== "number") return false;
  if (schema < SUPPORTED_SCHEMA_VERSION) {
    process.stderr.write(
      `[omcc-dev/${hookName}] workflow ${workflowId}: legacy schema ${schema}; run /omcc-dev:resume to migrate\n`
    );
    return true;
  }
  if (schema > SUPPORTED_SCHEMA_VERSION) {
    process.stderr.write(
      `[omcc-dev/${hookName}] workflow ${workflowId}: schema ${schema} newer than supported (${SUPPORTED_SCHEMA_VERSION})\n`
    );
    return true;
  }
  return false;
}

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

// Per-field length caps for sanitize() callers. Prefer sanitizeField over
// hand-picked numeric caps at call sites — the table keeps caps consistent
// across hooks and commands and makes new fields easy to register.
export const SANITIZE_FIELD_CAPS = {
  phase: 64,
  next_action: 120,
  type: 16,
  // Pre-registered for schema 2 /omcc-dev:checkpoint injection (B5.3).
  checkpoint_summary: 200,
};

export function sanitizeField(name, value) {
  const cap = Object.prototype.hasOwnProperty.call(SANITIZE_FIELD_CAPS, name)
    ? SANITIZE_FIELD_CAPS[name]
    : SANITIZE_CAP;
  return sanitize(value, cap);
}

export function isValidWorkflowId(id) {
  return typeof id === "string" && WORKFLOW_ID_REGEX.test(id);
}

// Finding IDs are audit-only keys into the parent audit's `findings[]`
// array — never used as a filesystem path component. Validated against
// a separate regex per continuity-protocol.md §Finding IDs.
export const FINDING_ID_REGEX = /^finding-[0-9]+$/;

export function isValidFindingId(id) {
  return typeof id === "string" && FINDING_ID_REGEX.test(id);
}

// Shard IDs are sibling-scoped identifiers under a sharded root at
// workflows/<root_id>/<shard_id>.md per continuity-protocol.md
// §Hierarchical workflow shards. Format pin: ^deliverable-[A-Z]$.
export const SHARD_ID_REGEX = /^deliverable-[A-Z]$/;

export function isValidShardId(id) {
  return typeof id === "string" && SHARD_ID_REGEX.test(id);
}

// Secret scrub patterns per continuity-protocol.md §Secrets hygiene.
// Applied in order; each match is replaced with "[REDACTED]".
// Patterns 1 and 2 are case-sensitive (token formats and the HTTP
// Bearer header convention respectively). Pattern 3 is
// case-insensitive via the /i flag.
export const SECRETS_SCRUB_PATTERNS = [
  {
    pattern:
      /(sk|pk|ghp|gho|ghu|ghs|ghr|github_pat|xoxb|xoxp|AKIA)[_A-Za-z0-9-]{8,}/g,
    replacement: "[REDACTED]",
  },
  {
    pattern: /Bearer\s+[A-Za-z0-9._~+/=-]+/g,
    replacement: "[REDACTED]",
  },
  {
    pattern:
      /(password|token|secret|api[_-]?key|authorization)\s*[:=]\s*\S+/gi,
    replacement: "[REDACTED]",
  },
];

// Best-effort scrub. Non-string values pass through unchanged so callers
// may chain without defensive type checks at each call site.
export function scrubSecrets(text) {
  if (typeof text !== "string") return text;
  let out = text;
  for (const { pattern, replacement } of SECRETS_SCRUB_PATTERNS) {
    out = out.replace(pattern, replacement);
  }
  return out;
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

// Return all descendants of rootId reachable via entry.parent back-pointers,
// in breadth-first topological order (each parent appears before its
// descendants). rootId itself is excluded from the result.
//
// Cycle-safe: every node is visited at most once. Self-parent edges
// (entry.parent === entry.id) are ignored. Intended for A4 transitive
// "no active children" gating under hierarchical workflows.
export function walkWorkflowTree(entries, rootId) {
  if (typeof rootId !== "string" || !Array.isArray(entries)) return [];
  // Build child index: parent_id -> [child_entry]
  const byParent = new Map();
  for (const e of entries) {
    if (!e || typeof e !== "object" || typeof e.id !== "string") continue;
    const p = e.parent;
    if (typeof p !== "string" || p === e.id) continue;
    const arr = byParent.get(p);
    if (arr) arr.push(e);
    else byParent.set(p, [e]);
  }
  const result = [];
  const visited = new Set([rootId]);
  const queue = [rootId];
  while (queue.length > 0) {
    const currentId = queue.shift();
    const children = byParent.get(currentId);
    if (!children) continue;
    for (const child of children) {
      if (visited.has(child.id)) continue;
      visited.add(child.id);
      result.push(child);
      queue.push(child.id);
    }
  }
  return result;
}

// Parse a YAML-subset list of maps from an fmBody region starting at
// `<topKey>:`. Each map is introduced by `  - id: <value>` and continues
// with `    <key>: <value>` lines until the next map or a non-indented
// line (including the `---` terminator). Nested lists for specific keys
// (e.g., `children:` under each active entry) are recognized when that
// key is listed in `innerListKeys`.
//
// Returns [] when the topKey is absent or its block is empty.
export function parseNestedList(fmBody, topKey, innerListKeys = []) {
  const pattern = new RegExp(`(?:^|\\n)${topKey}:\\s*(?:\\n([\\s\\S]*))?$`);
  const m = fmBody.match(pattern);
  if (!m || !m[1]) return [];
  const innerSet = new Set(innerListKeys);
  const entries = [];
  let current = null;
  let currentList = null; // name of the nested list currently being filled, or null
  for (const line of m[1].split("\n")) {
    if (/^\S/.test(line) || line.trim() === "---") break;
    const idLine = line.match(/^\s*-\s*id:\s*(\S+)/);
    if (idLine) {
      if (current) entries.push(current);
      current = { id: idLine[1] };
      for (const k of innerListKeys) current[k] = [];
      currentList = null;
      continue;
    }
    if (!current) continue;
    const listItem = line.match(/^\s{6,}-\s*(\S+)/);
    if (currentList && listItem) {
      current[currentList].push(listItem[1]);
      continue;
    }
    const kv = line.match(/^\s+([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$/);
    if (!kv) continue;
    const [, key, rawVal] = kv;
    currentList = null;
    let val = rawVal.trim();
    if (innerSet.has(key)) {
      currentList = key;
      if (val === "[]") current[key] = [];
      continue;
    }
    if (val === "null" || val === "") val = null;
    current[key] = val;
  }
  if (current) entries.push(current);
  return entries;
}

// Parse active.md's `active:` list into [{id, type, phase, parent, children, originating_finding}]
export function parseActiveRegistry(content) {
  const parsed = parseFrontmatter(content);
  if (!parsed) return [];
  return parseNestedList(parsed.fmBody, "active", ["children"]);
}

// Re-serialize active.md content from its schema/updated_at and the
// entries list. Fields are emitted in the canonical order
// (id, type, phase, parent, children, originating_finding) and any
// unknown scalar keys are appended verbatim after originating_finding
// so round-trip preserves fields the parser didn't anticipate.
// Active entries are sorted by `id` ASCII ascending per spec.
function serializeActiveRegistry(entries, schema, updatedAt) {
  const lines = [
    "---",
    `schema: ${schema}`,
    `updated_at: ${updatedAt}`,
    "active:",
  ];
  const sorted = [...entries].sort((a, b) =>
    a.id < b.id ? -1 : a.id > b.id ? 1 : 0
  );
  const known = new Set([
    "id", "type", "phase", "parent", "children", "originating_finding",
  ]);
  const emitScalar = (k, v) => {
    lines.push(`    ${k}: ${v === null || v === undefined ? "null" : v}`);
  };
  for (const e of sorted) {
    lines.push(`  - id: ${e.id}`);
    if ("type" in e) emitScalar("type", e.type);
    if ("phase" in e) emitScalar("phase", e.phase);
    if ("parent" in e) emitScalar("parent", e.parent);
    const children = Array.isArray(e.children) ? e.children : [];
    if (children.length === 0) {
      lines.push("    children: []");
    } else {
      lines.push("    children:");
      for (const c of children) lines.push(`      - ${c}`);
    }
    if ("originating_finding" in e) {
      emitScalar("originating_finding", e.originating_finding);
    }
    // Unknown scalars preserved at the end of the entry block
    for (const k of Object.keys(e)) {
      if (known.has(k)) continue;
      emitScalar(k, e[k]);
    }
  }
  lines.push("---");
  lines.push("");
  return lines.join("\n");
}

// Append childId to parentId's `children:` list in the active registry.
// Dedupes (no-op if already present). Maintains ASCII-ascending order
// for diff stability. No-op if the parent entry is absent or either
// id fails the workflow-id regex. Writes via atomicModifyFile so the
// read-modify-write sequence is serialized with all other writers.
export async function appendChildToParentRegistry(activePath, parentId, childId) {
  if (!isValidWorkflowId(parentId) || !isValidWorkflowId(childId)) return;
  await atomicModifyFile(activePath, async (content) => {
    if (content === null) return null;
    const parsed = parseFrontmatter(content);
    if (!parsed) return null;
    const entries = parseActiveRegistry(content);
    const parent = entries.find((e) => e.id === parentId);
    if (!parent) return null;
    const children = Array.isArray(parent.children) ? parent.children : [];
    if (children.includes(childId)) return null;
    children.push(childId);
    children.sort();
    parent.children = children;
    const schema = parsed.fields.schema ?? "2";
    const updatedAt = new Date().toISOString();
    return serializeActiveRegistry(entries, schema, updatedAt);
  });
}

// Remove childId from parentId's `children:` list. No-op if parent is
// absent, child is not currently in the list, or either id fails
// validation. When the last child is removed, the block collapses to
// the inline empty-list literal `children: []`.
export async function removeChildFromParentRegistry(activePath, parentId, childId) {
  if (!isValidWorkflowId(parentId) || !isValidWorkflowId(childId)) return;
  await atomicModifyFile(activePath, async (content) => {
    if (content === null) return null;
    const parsed = parseFrontmatter(content);
    if (!parsed) return null;
    const entries = parseActiveRegistry(content);
    const parent = entries.find((e) => e.id === parentId);
    if (!parent) return null;
    const children = Array.isArray(parent.children) ? parent.children : [];
    const idx = children.indexOf(childId);
    if (idx < 0) return null;
    children.splice(idx, 1);
    parent.children = children;
    const schema = parsed.fields.schema ?? "2";
    const updatedAt = new Date().toISOString();
    return serializeActiveRegistry(entries, schema, updatedAt);
  });
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

// Cleans up transient sibling files after a workflow file has been
// atomically renamed into archive/. Removes `<src>.bak` so orphan
// backups do not accumulate in workflows/ over time. Leaves
// `<src>.lock` intact because a concurrent writer (e.g., a PreCompact
// in another session) may still own it — deleting another process's
// lock sentinel would let a second writer enter the critical section.
export async function archiveCleanupPolicy(archivedSrcPath) {
  try { await unlink(`${archivedSrcPath}.bak`); } catch {}
}

// Resolve a shard file path. Rejects ids that fail their regex and
// confirms the resolved path stays under workflows/<root_id>/ so a
// crafted shard id cannot escape into sibling workspaces.
export function resolveShardPath(cwd, rootId, shardId) {
  if (!isValidWorkflowId(rootId)) {
    throw new Error(`invalid root workflow id: ${rootId}`);
  }
  if (!isValidShardId(shardId)) {
    throw new Error(`invalid shard id: ${shardId}`);
  }
  const rootDir = resolve(cwd, ".claude", "omcc-dev", "workflows", rootId);
  const full = resolve(rootDir, `${shardId}.md`);
  if (!full.startsWith(`${rootDir}/`)) {
    throw new Error(`resolved shard path escapes root: ${full}`);
  }
  return full;
}

export function resolveShardDirectoryPath(cwd, rootId) {
  if (!isValidWorkflowId(rootId)) {
    throw new Error(`invalid root workflow id: ${rootId}`);
  }
  return resolve(cwd, ".claude", "omcc-dev", "workflows", rootId);
}

export function resolveArchivedShardDirectoryPath(cwd, rootId) {
  if (!isValidWorkflowId(rootId)) {
    throw new Error(`invalid root workflow id: ${rootId}`);
  }
  return resolve(cwd, ".claude", "omcc-dev", "archive", rootId);
}

// Move a workflow into archive/. For flat (non-sharded) workflows this
// is a single rename of the .md file. For sharded roots both the root
// .md AND the shard directory move atomically — if the directory
// rename fails, the root file rename is rolled back so the root is
// never split across workflows/ and archive/.
// Returns true on success, false on any failure (caller may retry).
export async function moveWorkflowToArchive(cwd, workflowId) {
  if (!isValidWorkflowId(workflowId)) return false;
  const src = resolveWorkflowPath(cwd, workflowId);
  const dst = resolveArchivePath(cwd, workflowId);
  const shardDir = resolveShardDirectoryPath(cwd, workflowId);
  const archiveShardDir = resolveArchivedShardDirectoryPath(cwd, workflowId);
  try {
    await rename(src, dst);
  } catch {
    return false;
  }
  if (existsSync(shardDir)) {
    try {
      await rename(shardDir, archiveShardDir);
    } catch (dirErr) {
      // Roll back root-file move so the workflow is not split.
      try {
        await rename(dst, src);
        return false;
      } catch (rollbackErr) {
        // Double failure: leave a journal marker next to the shard
        // directory so the user can recover manually.
        try {
          await writeFile(
            `${shardDir}.journal-incomplete`,
            `pre-archive root file is at ${dst}\n` +
              `intended archive directory is ${archiveShardDir}\n` +
              `directory rename error: ${dirErr.message}\n` +
              `rollback error: ${rollbackErr.message}\n`,
            { mode: 0o600 }
          );
        } catch {
          // Best-effort journal; suppress secondary failures.
        }
        return false;
      }
    }
  }
  await archiveCleanupPolicy(src);
  return true;
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

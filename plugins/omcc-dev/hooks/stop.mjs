#!/usr/bin/env node
// Stop hook for omcc-dev continuity-protocol. Validates required state
// fields (non-blocking stderr reminder) and applies the four-condition
// auto-archive check (A1-A4) when a workflow reaches terminal state.
// Exits 0 on stop_hook_active to prevent infinite loops.

import { existsSync } from "node:fs";
import { readFile, rename } from "node:fs/promises";
import { execFileSync } from "node:child_process";
import {
  readStdinJson,
  resolveActivePath,
  resolveWorkflowPath,
  resolveArchivePath,
  parseActiveRegistry,
  parseFrontmatter,
  getNestedMap,
  atomicModifyFile,
  archiveCleanupPolicy,
  isValidWorkflowId,
  TERMINAL_PHASES,
  COMMIT_SUBJECT_REGEX,
  KNOWN_WORKFLOW_TYPES,
  SUPPORTED_SCHEMA_VERSION,
} from "./_utils.mjs";

function getCommitSubjectsInRange(cwd, baselineHead) {
  try {
    // Use `--format=%s` first and `--` separator so a baseline value
    // starting with `-` cannot be mis-parsed as a git option.
    return execFileSync(
      "git",
      ["log", "--format=%s", `${baselineHead}..HEAD`, "--"],
      { cwd, encoding: "utf8" }
    ).split("\n").filter(Boolean);
  } catch {
    return [];
  }
}

function getCurrentHead(cwd) {
  try {
    return execFileSync("git", ["rev-parse", "HEAD"], { cwd, encoding: "utf8" }).trim();
  } catch { return null; }
}

function hasActiveChildren(entries, workflowId) {
  return entries.some((e) => e.parent === workflowId);
}

async function validateFields(filePath) {
  let content = "";
  try { content = await readFile(filePath, "utf8"); }
  catch { return { valid: false }; }
  const parsed = parseFrontmatter(content);
  if (!parsed) return { valid: false };
  const { current_phase, next_action, workflow_type, schema } = parsed.fields;
  const git_baseline = getNestedMap(parsed.fmBody, "git_baseline");
  return {
    valid: !!(current_phase && next_action),
    current_phase,
    next_action,
    workflow_type,
    git_baseline,
    schema: schema !== undefined ? Number(schema) : undefined,
  };
}

async function maybeAutoArchive(cwd, entry, entries) {
  const filePath = resolveWorkflowPath(cwd, entry.id);
  if (!existsSync(filePath)) {
    // Stale-registry reconciliation only applies when the workflow has
    // actually moved to archive/. If the file is missing from BOTH
    // workflows/ and archive/, it's more likely a transient race or a
    // manual filesystem issue — preserve the registry entry so we do
    // not silently drop active work.
    const archivePath = resolveArchivePath(cwd, entry.id);
    if (existsSync(archivePath)) {
      return { archive: false, staleRegistryEntry: true };
    }
    return { archive: false };
  }
  const meta = await validateFields(filePath);
  if (!meta.valid) {
    process.stderr.write(
      `[omcc-dev/stop] workflow ${entry.id}: missing current_phase or next_action\n`
    );
    return { archive: false };
  }
  // Schema-version gate per continuity-protocol.md §Parser rules.
  if (typeof meta.schema === "number" && meta.schema > SUPPORTED_SCHEMA_VERSION) {
    process.stderr.write(
      `[omcc-dev/stop] workflow ${entry.id}: schema ${meta.schema} newer than supported (${SUPPORTED_SCHEMA_VERSION}); not archiving\n`
    );
    return { archive: false };
  }
  // A1
  if (!TERMINAL_PHASES.includes(meta.current_phase)) return { archive: false };
  const type = meta.workflow_type;
  // Fail closed on unknown/missing workflow_type — corrupt or malformed
  // state files must not be archived based on incomplete checks.
  if (!KNOWN_WORKFLOW_TYPES.includes(type)) {
    process.stderr.write(
      `[omcc-dev/stop] workflow ${entry.id}: unknown workflow_type "${type}"; not archiving\n`
    );
    return { archive: false };
  }
  if (type !== "audit") {
    // A2
    const head = getCurrentHead(cwd);
    if (!head) return { archive: false };
    if (!meta.git_baseline || head === meta.git_baseline.head) return { archive: false };
    // A3
    const re = COMMIT_SUBJECT_REGEX[type];
    // A known type with no regex (should not happen for start/fix) fails
    // closed to avoid skipping A3.
    if (!re) return { archive: false };
    const subjects = getCommitSubjectsInRange(cwd, meta.git_baseline.head);
    if (!subjects.some((s) => re.test(s))) return { archive: false };
  }
  // A4
  if (hasActiveChildren(entries, entry.id)) return { archive: false };
  return { archive: true };
}

async function moveToArchive(cwd, workflowId) {
  const src = resolveWorkflowPath(cwd, workflowId);
  const dst = resolveArchivePath(cwd, workflowId);
  try {
    await rename(src, dst);
  } catch { return false; }
  await archiveCleanupPolicy(src);
  return true;
}

async function removeFromActiveRegistry(cwd, removeId) {
  const activePath = resolveActivePath(cwd);
  if (!existsSync(activePath)) return;
  try {
    await atomicModifyFile(activePath, async (content) => {
      if (content === null) return null;
      // Line-scan: skip the `- id: removeId` block until the next `- id:` or
      // the frontmatter terminator. Blocks are identified by indentation > 2.
      const lines = content.split("\n");
      const out = [];
      let skipping = false;
      for (const line of lines) {
        const idLine = line.match(/^\s*-\s*id:\s*(\S+)/);
        if (idLine) {
          skipping = idLine[1] === removeId;
          if (!skipping) out.push(line);
          continue;
        }
        if (skipping) {
          // still inside the entry block if line has >= 4 leading spaces or
          // is a bare list continuation; otherwise we exited the entry.
          if (/^\s{4,}/.test(line) || line.trim() === "") {
            continue;
          }
          skipping = false;
        }
        out.push(line);
      }
      const nowIso = new Date().toISOString();
      let updated = out.join("\n");
      // If the `active:` list is now empty, normalize a dangling `active:`
      // scalar (which YAML reads as null) to the required empty list
      // literal `active: []`.
      updated = updated.replace(
        /(^|\n)active:\s*\n(\s*---)/,
        (_m, prefix, terminator) => `${prefix}active: []\n${terminator}`
      );
      updated = updated.replace(
        /^(\s*updated_at:\s*).*$/m,
        `$1${nowIso}`
      );
      return updated;
    });
  } catch {
    // best-effort reconciliation
  }
}

async function main() {
  const event = await readStdinJson();
  if (event && event.stop_hook_active === true) process.exit(0);
  const cwd = (event && typeof event.cwd === "string") ? event.cwd : process.cwd();
  const activePath = resolveActivePath(cwd);
  if (!existsSync(activePath)) process.exit(0);
  let activeContent = "";
  try { activeContent = await readFile(activePath, "utf8"); } catch { process.exit(0); }
  const entries = parseActiveRegistry(activeContent);
  for (const e of entries) {
    if (!isValidWorkflowId(e.id)) continue;
    const verdict = await maybeAutoArchive(cwd, e, entries).catch(() => ({ archive: false }));
    if (verdict.staleRegistryEntry) {
      // Workflow file already in archive/ — reconcile registry.
      await removeFromActiveRegistry(cwd, e.id);
      continue;
    }
    if (!verdict.archive) continue;
    const moved = await moveToArchive(cwd, e.id);
    if (moved) await removeFromActiveRegistry(cwd, e.id);
  }
  process.exit(0);
}

main().catch(() => process.exit(0));

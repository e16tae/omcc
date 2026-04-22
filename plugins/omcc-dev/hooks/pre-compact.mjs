#!/usr/bin/env node
// PreCompact hook for omcc-dev continuity-protocol. Appends a mechanical
// snapshot to each active workflow's body before compaction loses context.
// Idempotent within a 60-second window; caps body at 50 snapshots
// (oldest trimmed on overflow). All writes go through the atomic
// update sequence defined by continuity-protocol.md.

import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import {
  readStdinJson,
  resolveActivePath,
  resolveWorkflowPath,
  parseActiveRegistry,
  parseFrontmatter,
  getGitInfo,
  filterSensitiveStatus,
  atomicUpdateFile,
  updateUpdatedAt,
  isValidWorkflowId,
} from "./_utils.mjs";

const IDEMPOTENT_WINDOW_MS = 60 * 1000;
const MAX_SNAPSHOTS = 50;
const DELIM = "<!-- pre-compact snapshot -->";

function latestSnapshotMs(body) {
  const pattern = new RegExp(`${DELIM}[\\s\\S]*?timestamp:\\s*([^\\n]+)`, "g");
  let last = null, m;
  while ((m = pattern.exec(body)) !== null) last = m[1].trim();
  if (!last) return null;
  const d = new Date(last);
  return isNaN(d.getTime()) ? null : d.getTime();
}

function trimToCap(body, maxSnaps) {
  const parts = body.split(DELIM);
  if (parts.length - 1 <= maxSnaps) return body;
  const preBody = parts[0];
  const tail = parts.slice(1).slice(-maxSnaps);
  return preBody + DELIM + tail.join(DELIM);
}

async function processWorkflow(cwd, id) {
  if (!isValidWorkflowId(id)) return;
  const filePath = resolveWorkflowPath(cwd, id);
  if (!existsSync(filePath)) return;
  const content = await readFile(filePath, "utf8");
  const parsed = parseFrontmatter(content);
  if (!parsed) return;
  const now = Date.now();
  const lastMs = latestSnapshotMs(parsed.body);
  if (lastMs !== null && now - lastMs < IDEMPOTENT_WINDOW_MS) return;
  const git = getGitInfo(cwd);
  if (!git) return;
  const ts = new Date(now).toISOString();
  const filteredStatus = filterSensitiveStatus(git.status);
  const statusBlock = filteredStatus
    ? filteredStatus.split("\n").map((l) => l ? `  ${l}` : "").join("\n")
    : "  (clean)";
  const snapshotBlock =
    `\n${DELIM}\n` +
    `timestamp: ${ts}\n` +
    `branch: ${git.branch}\n` +
    `head: ${git.head}\n` +
    `status:\n${statusBlock}\n`;
  let newBody = parsed.body + snapshotBlock;
  newBody = trimToCap(newBody, MAX_SNAPSHOTS);
  const fmBodyUpdated = updateUpdatedAt(parsed.fmBody, ts);
  const newContent = parsed.prefix + fmBodyUpdated + parsed.suffix + newBody;
  try {
    await atomicUpdateFile(filePath, newContent);
  } catch {
    // best-effort; a lock timeout or write failure should not block compaction
  }
}

async function main() {
  const event = await readStdinJson();
  const cwd = (event && typeof event.cwd === "string") ? event.cwd : process.cwd();
  const activePath = resolveActivePath(cwd);
  if (!existsSync(activePath)) process.exit(0);
  let activeContent = "";
  try { activeContent = await readFile(activePath, "utf8"); } catch { process.exit(0); }
  const entries = parseActiveRegistry(activeContent);
  for (const e of entries) {
    await processWorkflow(cwd, e.id).catch(() => {});
  }
  process.exit(0);
}

main().catch(() => process.exit(0));

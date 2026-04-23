#!/usr/bin/env node
// SessionStart hook (matcher: compact) for omcc-dev continuity-protocol.
// Reads active workflows and emits a sanitized summary to stdout, which
// Claude Code injects into context after compaction. Exits 0 silently
// when no active workflows exist. All read-only — no state writes.
// See: plugins/omcc-dev/continuity-protocol.md §Hook Responsibilities.

import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import {
  readStdinJson,
  resolveActivePath,
  resolveWorkflowPath,
  parseActiveRegistry,
  parseFrontmatter,
  sanitizeField,
  isValidWorkflowId,
  SUPPORTED_SCHEMA_VERSION,
} from "./_utils.mjs";

async function main() {
  const event = await readStdinJson();
  const cwd = (event && typeof event.cwd === "string") ? event.cwd : process.cwd();
  const activePath = resolveActivePath(cwd);
  if (!existsSync(activePath)) process.exit(0);

  let activeContent = "";
  try { activeContent = await readFile(activePath, "utf8"); } catch { process.exit(0); }
  const entries = parseActiveRegistry(activeContent);
  if (!entries.length) process.exit(0);

  const lines = ["Active omcc-dev workflow(s):"];
  for (const e of entries) {
    if (!isValidWorkflowId(e.id)) continue;
    const wfPath = resolveWorkflowPath(cwd, e.id);
    let content = "";
    try { content = await readFile(wfPath, "utf8"); } catch { continue; }
    const parsed = parseFrontmatter(content);
    const fields = parsed ? parsed.fields : {};
    // Schema-version gate: skip workflows whose schema is newer than we
    // understand, rather than echoing a potentially mis-interpreted
    // summary back into Claude's context.
    const schemaRaw = fields.schema;
    const schema = schemaRaw !== undefined ? Number(schemaRaw) : undefined;
    if (schema !== undefined && schema > SUPPORTED_SCHEMA_VERSION) continue;
    const phase = sanitizeField("phase", fields.current_phase || e.phase || "unknown");
    const nextAction = sanitizeField("next_action", fields.next_action || "");
    const type = sanitizeField("type", e.type || fields.workflow_type || "?");
    lines.push(`- ${e.id} (${type}) phase=${phase} next="${nextAction}"`);
  }
  if (lines.length === 1) process.exit(0);
  lines.push("If this hook did not fire, run /omcc-dev:resume for full rehydration.");
  process.stdout.write(lines.join("\n") + "\n");
}

main().catch(() => process.exit(0));

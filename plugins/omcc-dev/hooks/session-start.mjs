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
  getNestedMap,
  sanitizeField,
  isValidWorkflowId,
  handleLegacySchema,
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
  let backtickSkipped = 0;
  for (const e of entries) {
    if (!isValidWorkflowId(e.id)) continue;
    const wfPath = resolveWorkflowPath(cwd, e.id);
    let content = "";
    try { content = await readFile(wfPath, "utf8"); } catch { continue; }
    const parsed = parseFrontmatter(content);
    const fields = parsed ? parsed.fields : {};
    // Schema-version gate: skip workflows outside the supported range
    // (legacy OR future). Legacy files are silently skipped with a
    // stderr hint suggesting /omcc-dev:resume migration.
    const schemaRaw = fields.schema;
    const schema = schemaRaw !== undefined ? Number(schemaRaw) : undefined;
    if (handleLegacySchema(schema, e.id, "session-start")) continue;
    const phase = sanitizeField("phase", fields.current_phase || e.phase || "unknown");
    const nextAction = sanitizeField("next_action", fields.next_action || "");
    const type = sanitizeField("type", e.type || fields.workflow_type || "?");
    // Optional latest_checkpoint.summary injection — user-initiated
    // digest from /omcc-dev:checkpoint, per continuity-protocol.md
    // §Conditionally-required frontmatter.
    const checkpointMap = getNestedMap(parsed.fmBody, "latest_checkpoint");
    const rawSummary = checkpointMap && checkpointMap.summary ? checkpointMap.summary : "";
    const checkpoint = rawSummary ? sanitizeField("checkpoint_summary", rawSummary) : "";
    // Backtick rule: if ANY sanitized field returned null, the value
    // contained a backtick and the whole entry is rejected per
    // continuity-protocol.md §SessionStart Backtick rule. One diag
    // per entry identifies which field triggered the reject.
    if (phase === null || nextAction === null || type === null || checkpoint === null) {
      const culprit =
        phase === null ? "phase"
        : nextAction === null ? "next_action"
        : type === null ? "type"
        : "checkpoint_summary";
      process.stderr.write(
        `[omcc-dev/session-start] workflow ${e.id}: field ${culprit} contains backticks; entry skipped\n`
      );
      backtickSkipped++;
      continue;
    }
    if (checkpoint) {
      lines.push(
        `- ${e.id} (${type}) phase=${phase} next="${nextAction}" checkpoint="${checkpoint}"`
      );
    } else {
      lines.push(`- ${e.id} (${type}) phase=${phase} next="${nextAction}"`);
    }
  }
  if (lines.length === 1) {
    // All entries filtered — if any were backtick-rejected, emit a one-line
    // summary so the operator knows why the injection is silent this time.
    if (backtickSkipped > 0) {
      process.stderr.write(
        `[omcc-dev/session-start] ${backtickSkipped} entries skipped (backtick)\n`
      );
    }
    process.exit(0);
  }
  lines.push("If this hook did not fire, run /omcc-dev:resume for full rehydration.");
  process.stdout.write(lines.join("\n") + "\n");
}

main().catch(() => process.exit(0));

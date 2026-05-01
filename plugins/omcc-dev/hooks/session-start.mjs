#!/usr/bin/env node
// SessionStart hook (matcher: compact) for omcc-dev continuity-protocol.
// Reads active workflows and emits a sanitized summary to stdout, which
// Claude Code injects into context after compaction. Exits 0 silently
// when no active workflows exist. All read-only — no state writes.
// See: plugins/omcc-dev/continuity-protocol.md §Hook Responsibilities.

import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import {
  readStdinJson,
  resolveActivePath,
  resolveWorkflowPath,
  parseActiveRegistry,
  parseFrontmatter,
  parseEnsembleResults,
  parseDeliverables,
  getNestedMap,
  sanitizeField,
  sanitizeOpaqueId,
  isValidWorkflowId,
  handleLegacySchema,
} from "./_utils.mjs";

// resume Step 5c gauntlet locals — kept inline rather than re-exported
// from _utils so the validation contract stays close to its only
// SessionStart caller. /resume Step 5c has its own copy in markdown
// prose; the schema-drift test that ties the two together lives in
// tests/test_schema_drift.py.
const RUN_ID_REGEX = /^[0-9]{8}T[0-9]{6}Z-[0-9a-f]{6}$/;
const VERDICT_ENUM = new Set(["pass", "concerns", "conflict"]);
// Workflow-type-specific phase subsets per continuity-protocol.md
// § State File Schema § Workflow-type-specific frontmatter — only
// /start and /fix produce ensemble_results; /audit uses findings.
const PHASE_ENUM_BY_TYPE = {
  start: new Set(["brainstorm", "explore", "plan", "review", "resolve"]),
  fix: new Set(["investigate", "fix-and-verify"]),
};
// Each phase emits a single ensemble_type per ensemble-protocol.md
// § Ensemble Point Types. Composite identity (phase, ensemble_type)
// must agree at write-time; readers cross-check here.
const ENSEMBLE_TYPE_BY_PHASE = {
  brainstorm: "brainstorm",
  explore: "explore",
  plan: "plan-verify",
  review: "review",
  resolve: "review",
  investigate: "investigate",
  "fix-and-verify": "fix-verify",
};

function pickActiveShard(deliverables) {
  if (!Array.isArray(deliverables) || deliverables.length === 0) return null;
  const inProgress = deliverables.find((d) => d.status === "in_progress");
  if (inProgress) return inProgress;
  const pending = deliverables.find((d) => d.status === "pending");
  if (pending) return pending;
  return null;
}

function validateEnsembleEntry(entry, workflowType) {
  if (!entry || typeof entry !== "object") return null;
  const phaseEnum = PHASE_ENUM_BY_TYPE[workflowType];
  if (!phaseEnum || !phaseEnum.has(entry.phase)) return null;
  const expectedType = ENSEMBLE_TYPE_BY_PHASE[entry.phase];
  if (!expectedType || entry.ensemble_type !== expectedType) return null;
  if (!VERDICT_ENUM.has(entry.verdict)) return null;
  if (!RUN_ID_REGEX.test(entry.run_id || "")) return null;
  const ts = Date.parse(entry.completed_at || "");
  if (!Number.isFinite(ts) || ts > Date.now()) return null;
  // Required field: non-string summary rejects the entry. Falling back
  // to "" (the prior behavior) would let a malformed row pass the
  // sanitize gate and shadow an older valid entry in the latest-overall
  // selector.
  if (typeof entry.summary !== "string") return null;
  const summary = entry.summary;
  // LF/CR are spec-rejected (multiline summary smuggling). Double-quote
  // is rejected because the line builder emits ensemble="${summary}"
  // and an embedded `"` produces malformed format-injected output that
  // could distort downstream parsing of the active-line key/value pairs.
  if (
    summary.includes("\n")
    || summary.includes("\r")
    || summary.includes('"')
  ) return null;
  const sanitized = sanitizeField("ensemble_summary", summary);
  if (sanitized === null) return null;
  if (entry.codex_session_id !== undefined) {
    const cid = sanitizeOpaqueId(entry.codex_session_id);
    if (cid === null) return null;
  }
  return { sanitizedSummary: sanitized, ts };
}

async function readEnsembleEntries(cwd, workflowId, rootFmBody) {
  const rootEntries = parseEnsembleResults(rootFmBody);
  const deliverables = parseDeliverables(rootFmBody);
  const activeShard = pickActiveShard(deliverables);
  if (!activeShard || typeof activeShard.shard_path !== "string") {
    return rootEntries;
  }
  const shardId = activeShard.shard_path.replace(/\.md$/, "");
  // Path-safety: shard id format is enforced by resolveShardPath in _utils,
  // but the SessionStart selector tolerates malformed shards by treating
  // a non-existent shard file as "no active shard" (root-only fallback).
  if (!/^deliverable-[A-Z]$/.test(shardId)) return rootEntries;
  const shardPath = resolve(
    cwd, ".claude", "omcc-dev", "workflows", workflowId, `${shardId}.md`
  );
  if (!existsSync(shardPath)) return rootEntries;
  let shardContent = "";
  try {
    shardContent = await readFile(shardPath, "utf8");
  } catch {
    return rootEntries;
  }
  const shardParsed = parseFrontmatter(shardContent);
  if (!shardParsed) return rootEntries;
  // Shard frontmatter validation: an unsupported schema (legacy or
  // future) is skipped per continuity-protocol.md §Parser rules; an
  // orphaned or corrupt shard whose shard_type / root_workflow does
  // not match must not surface its ensemble entries to SessionStart.
  const shardSchemaRaw = shardParsed.fields.schema;
  const shardSchema = shardSchemaRaw !== undefined
    ? Number(shardSchemaRaw)
    : undefined;
  if (handleLegacySchema(shardSchema, workflowId, "session-start")) {
    return rootEntries;
  }
  if (shardParsed.fields.shard_type !== "deliverable") return rootEntries;
  if (shardParsed.fields.root_workflow !== workflowId) return rootEntries;
  const shardEntries = parseEnsembleResults(shardParsed.fmBody);
  // Merge order: root first, then shard. Tie-break on completed_at is
  // root-first (deterministic source order under stable selection).
  return [...rootEntries, ...shardEntries];
}

function selectLatestEnsemble(entries, workflowType) {
  let best = null;
  for (const entry of entries) {
    const validated = validateEnsembleEntry(entry, workflowType);
    if (!validated) continue;
    // Strict > preserves root-first tie-break: when shard entry has
    // the same ts as a root entry already chosen, the root one stays.
    if (best === null || validated.ts > best.ts) {
      best = validated;
    }
  }
  return best;
}

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
    // Per-workflow try/catch defends against malformed YAML in any one
    // workflow file suppressing all other rows — Codex plan-verify R1.
    try {
      if (!isValidWorkflowId(e.id)) continue;
      const wfPath = resolveWorkflowPath(cwd, e.id);
      let content = "";
      try { content = await readFile(wfPath, "utf8"); } catch { continue; }
      const parsed = parseFrontmatter(content);
      // Corrupt or missing frontmatter: skip the entry entirely rather
      // than falling through with `fields = {}`. The prior fallback
      // bypassed the schema/version gate and surfaced a row built
      // from active-registry context — potentially stale or
      // adversarially-induced.
      if (!parsed) continue;
      const fields = parsed.fields;
      const schemaRaw = fields.schema;
      const schema = schemaRaw !== undefined ? Number(schemaRaw) : undefined;
      if (handleLegacySchema(schema, e.id, "session-start")) continue;
      const phase = sanitizeField("phase", fields.current_phase || e.phase || "unknown");
      const nextAction = sanitizeField("next_action", fields.next_action || "");
      const type = sanitizeField("type", e.type || fields.workflow_type || "?");
      const checkpointMap = parsed
        ? getNestedMap(parsed.fmBody, "latest_checkpoint")
        : {};
      const rawSummary = checkpointMap && checkpointMap.summary
        ? checkpointMap.summary : "";
      const checkpoint = rawSummary
        ? sanitizeField("checkpoint_summary", rawSummary) : "";
      // Whole-row drop for the four identity-bearing fields. The new
      // ensemble_summary follows a separate suffix-only carve-out below.
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
      // ensemble= suffix selector (Issue #100, criterion #5).
      // Suffix-only drop on validation/sanitize failure: silent degrade
      // to base row, no stderr — the suffix is informational.
      let ensembleSummary = "";
      if (parsed) {
        try {
          const workflowType = e.type || fields.workflow_type;
          const ensembleEntries = await readEnsembleEntries(cwd, e.id, parsed.fmBody);
          const latest = selectLatestEnsemble(ensembleEntries, workflowType);
          if (latest) ensembleSummary = latest.sanitizedSummary;
        } catch {
          ensembleSummary = "";
        }
      }
      // 4-state line builder per continuity-protocol.md § Hook Responsibilities
      // § SessionStart § Stdout: phase= next= [checkpoint=] [ensemble=].
      let line = `- ${e.id} (${type}) phase=${phase} next="${nextAction}"`;
      if (checkpoint) line += ` checkpoint="${checkpoint}"`;
      if (ensembleSummary) line += ` ensemble="${ensembleSummary}"`;
      lines.push(line);
    } catch (perEntryErr) {
      const msg = (perEntryErr && perEntryErr.message) || "unknown";
      process.stderr.write(
        `[omcc-dev/session-start] workflow ${e.id}: read error (${msg}); entry skipped\n`
      );
      continue;
    }
  }
  if (lines.length === 1) {
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

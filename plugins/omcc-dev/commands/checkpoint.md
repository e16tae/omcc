---
description: Write a user-initiated checkpoint into the active workflow's state as an intra-session context milestone.
argument-hint: [summary]
---

# Checkpoint

$ARGUMENTS

`/omcc-dev:checkpoint` records a user-initiated context milestone into
the `latest_checkpoint` frontmatter field of the active workflow (or
active shard) — see `continuity-protocol.md` §Conditionally-required
frontmatter. The checkpoint is consumed by two hooks:

- **SessionStart (compact matcher)** injects the checkpoint summary
  into the active-workflow summary line after compaction, so the
  user's digest is what Claude sees first on re-entry.
- **PreCompact** treats a checkpoint less than `IDEMPOTENT_WINDOW_MS`
  (60s) old as a fresh milestone and skips appending its mechanical
  git-status snapshot for that window — the user checkpoint
  supersedes the automatic one.

The checkpoint primitive is deliberately **user-initiated**. Agents MUST
NOT invoke this command automatically. An advisory prompt is offered
at `/start` deliverable boundaries (see `commands/start.md` Phase 4
Deliverable mode step 6); users may accept or decline.

---

## Step 1: Locate the target workflow

1. Read the active registry at `<cwd>/.claude/omcc-dev/active.md`.
2. If no active workflow is recorded, inform the user and exit — a
   checkpoint requires an owning workflow. Suggest `/omcc-dev:start`
   or `/omcc-dev:resume` first.
3. If multiple active workflows exist, follow the same selection UX as
   `/omcc-dev:resume` Step 1: either an explicit id in `$ARGUMENTS` or
   an interactive pick.
4. If the selected root is **sharded** (directory
   `workflows/<root_id>/` exists via `resolveShardDirectoryPath`):
   - The checkpoint writes to the **active shard** (first `in_progress`
     in `plan.deliverables[]`, else first `pending`), not the root.
     This keeps the checkpoint summary next to the narrative it
     describes, so SessionStart can reinject it on re-entry to the
     same shard.
   - If the user is working mid-deliverable and prefers to checkpoint
     a specific shard, honor the `$ARGUMENTS`-parsed `deliverable_id`
     when provided (validated via `SHARD_ID_REGEX`).

## Step 2: Compose the summary

1. If `$ARGUMENTS` contains non-empty text after the command token,
   use it as the summary verbatim (pre-sanitization).
2. Otherwise, build a summary from conversation context: last
   meaningful milestone the user and agent reached (e.g., "finished
   B4.2 helpers + tests pending", "brainstorm decision approved:
   option C"). Keep it short — ≤ 200 characters.
3. Apply `sanitizeField("checkpoint_summary", value)` per
   `hooks/_utils.mjs` (control-char strip + length cap 200).
4. **Backtick rule**: if the summary contains a backtick after
   sanitization, reject the command with a stderr diagnostic pointing
   at `continuity-protocol.md` §SessionStart Backtick rule. Ask the
   user to rephrase. Do NOT silently strip.

## Step 3: Atomic write

1. Resolve the target path (flat workflow OR active shard) via
   `resolveWorkflowPath` / `resolveShardPath`.
2. Call `atomicModifyFile(targetPath, mutator)` where `mutator`:
   - Parses the current frontmatter via `parseFrontmatter`.
   - Sets `latest_checkpoint.at = <ISO-8601 UTC now>`.
   - Sets `latest_checkpoint.summary = <sanitized summary>`.
   - Refreshes `updated_at`.
   - Returns the rebuilt content (preserves unknown fields).
3. On success, confirm to the user with the target path and the
   summary written. On lock-timeout or write failure, report and
   suggest retry.

## Idempotency

Rapid re-invocation is safe: the helper simply overwrites
`latest_checkpoint.at` and `.summary`. There is no history kept; a
checkpoint is a point-in-time bookmark, not a log. For a durable log,
use the PreCompact snapshot chain in the workflow's body (capped at
50 snapshots per `continuity-protocol.md`).

## Relation to PreCompact

A fresh checkpoint (within 60s of `PreCompact.now()`) suppresses the
next mechanical snapshot. This is the user's signal that they have
supplied a better summary than a raw `git status` dump would have
given. Outside the 60s window the mechanical snapshot resumes.

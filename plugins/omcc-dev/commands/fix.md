---
description: Systematic bug fix — investigate root cause first, fix second
argument-hint: Bug description or issue number
---

# Fix

$ARGUMENTS

Use `TaskCreate` and `TaskUpdate` to track progress across phases. Codex
ensemble runs automatically per `ensemble-protocol.md` when Ensemble Affinity
warrants it — never ask the user whether to invoke Codex, and never direct
them to run `/codex:*` commands manually.

---

## Phase 0: Continuity Check

Follow `continuity-protocol.md` Phase-boundary Write Rules, the Resume
Handoff Path contract, and the Legacy design-context.md Migration
section.

0. **Resume handoff**: if this invocation arrived via `/omcc-dev:resume`
   Step 6 delegating control back to `/fix` after having selected and
   validated an active workflow of `workflow_type: fix`, skip the
   bootstrap path. Recognize the selected workflow, advance to its
   recorded `current_phase`, and continue from the body of the
   corresponding Phase below. Do not re-prompt for resume/new/archive.
1. Read the active registry at `<cwd>/.claude/omcc-dev/active.md` if
   present. If any active workflow is listed (and this is NOT a resume
   handoff), offer the user: **resume** (hand control to
   `/omcc-dev:resume` and exit) / **start new** (continue here with a
   new workflow file alongside the existing ones) / **archive**
   (archive the chosen existing workflow, then continue).
2. If `<cwd>/.claude/design-context.md` exists (legacy artifact), apply
   the Legacy Migration rules in `continuity-protocol.md`: offer
   **import** / **archive** / **delete**. Acquire the migration lock
   sentinel per the protocol before acting.
3. Ensure `<cwd>/.claude/omcc-dev/workflows/` and
   `<cwd>/.claude/omcc-dev/archive/` exist with mode `0700` per
   `continuity-protocol.md` §Directory Layout.
4. Bootstrap write: create
   `<cwd>/.claude/omcc-dev/workflows/fix-<timestamp>-<shortid>.md`
   with the always-required frontmatter from `continuity-protocol.md`
   State File Schema. Initial values: `workflow_type: fix`,
   `current_phase: "investigate"`, `next_action` describing the Phase 1
   next step, `tasks: []`, `git_baseline` captured from `git rev-parse
   HEAD` + `git branch --show-current` + the pinned `status_digest`
   pipeline, and `task_profile` (to be populated during Phase 1
   orchestration). Apply the secrets-hygiene regex scrub to
   `$ARGUMENTS` before writing `original_request`. Write the file
   with mode `0600`.
5. If `$ARGUMENTS` indicates this `/fix` is spawned from an `/audit`
   finding (cross-workflow handoff), validate the finding id against
   the parent workflow id against the workflow-id regex. If the parent
   is an `/audit`, additionally validate the finding id against the
   finding-id regex (`^finding-[0-9]+$` per `continuity-protocol.md`
   §Finding IDs) and record `originating_finding`. Reject the handoff
   with a diagnostic and proceed as a root workflow if validation
   fails.

   Set `parent_workflow` to the parent workflow id. Dispatch the
   parent writeback by parent `workflow_type`:
   - Parent is `audit`: acquire a lock on the parent file; set
     `findings[i].decision = "fix-now"` and
     `findings[i].child_workflow = <this id>` keyed by
     `originating_finding`.
   - Parent is `start` or `fix` (non-audit): acquire a lock on the
     parent file; append
     `{child_id: <this id>, spawned_at: <ISO-8601 UTC>}` to the
     parent's `child_completions:` frontmatter list (initialize to
     `[]` if missing).

   If the parent file is in `<cwd>/.claude/omcc-dev/archive/`, **skip
   the writeback with a stderr warning** — the parent state is frozen;
   `parent_workflow` (and, for audit parents, `originating_finding`)
   are still recorded on this workflow so provenance resolution via
   the archive fallback works.
6. Add or update the entry in the active registry with all required
   fields per `continuity-protocol.md` §Active Registry: `id` = this
   workflow id, `type: fix`, `phase: "investigate"`, `parent:
   <parent_workflow if step 5 set one, else null>`, `children: []`,
   `originating_finding: <finding id if step 5 set one, else null>`.
   **If step 5 set `parent_workflow`, also call
   `appendChildToParentRegistry(activePath, parent_workflow, <this id>)`**
   so the parent's `children:` list operationally reflects this child.
7. Run `git check-ignore <cwd>/.claude/omcc-dev/` and warn if the
   directory is not gitignored (per `continuity-protocol.md` Security
   Considerations).

All subsequent phases write to this workflow file at the boundaries
listed in `continuity-protocol.md` Phase-boundary Write Rules for
`workflow_type: fix`.

---

## Phase 1: Investigate

Follow the investigate skill's command-invoked mode (`skills/investigate/SKILL.md`).

Write state per `continuity-protocol.md` Phase-boundary Write Rules:

- After hypotheses are generated (skill Step 2 spawn): write the
  `hypotheses` list to frontmatter (`text` / `verdict` / `evidence` per
  entry — snapshot the hypothesis set before it compacts out of context;
  this is a high-ROI resume anchor).
- After root cause confirmed (skill Step 4): write `root_cause`,
  `fix_approach`.

Do not proceed to Phase 2 until root cause is confirmed.

### Post-investigation assessment

After root cause is confirmed, evaluate the fix scope:

1. If the investigation identifies **2+ viable fix approaches**, invoke the brainstorm
   skill to compare approaches and wait for user approval before proceeding.
2. If the confirmed root cause requires **changes to 5+ files or architectural restructuring**,
   report this to the user and recommend transitioning to `/start`. Provide the root cause
   analysis (cause, evidence, impact scope) as context for `/start`'s brainstorm phase.
3. Otherwise, proceed to Phase 2 with the identified fix approach.

---

## Phase 2: Write Failing Test

1. Write a test that reproduces the bug
2. Run with Bash to confirm the test FAILS
3. If no test framework exists, skip this phase and inform the user

After this phase, write `failing_test` frontmatter (`path` +
`status: failing-as-expected | passing | framework-absent`) and
advance `current_phase: "failing-test"` per `continuity-protocol.md`.

---

## Phase 3: Fix and Verify

1. Apply the minimal fix targeting the confirmed root cause
2. If Phase 2 was skipped (no test framework): verify the fix manually —
   Grep for the old buggy pattern to confirm 0 remaining occurrences,
   and run the affected code path to confirm correct behavior.
   Otherwise: Run the failing test — confirm it now PASSES.
3. If test suite available: Run the full test suite — confirm no regressions.
   Without a test framework, manual verification (Steps 2 otherwise + 5) is
   sufficient; inform the user the full suite was skipped.
4. Ensemble fix verification (all affinity levels):
   - Launch Codex **fix-verify** ensemble point (background) with `--scope working-tree`
   - **Immediately after launch returns a job id**: append an entry to
     `pending_ensemble` in state per `continuity-protocol.md`
     (`job_id` from the launch result, `ensemble_type: fix-verify`,
     `dispatched_at`). If launch fails, no entry is written.
   - Collect Codex review of the patch
   - On collection: remove the entry from `pending_ensemble` by `job_id`.
   - Synthesize: merge Codex findings into fix verification
   - Report any additional concerns Codex found in the patch
5. Search for similar patterns: `Grep` for the same code pattern in other locations.
   Write `similar_pattern_grep` frontmatter (`pattern` + `matches` list) to
   state per `continuity-protocol.md` — this result is expensive to
   regenerate and is the highest-ROI resume anchor for `/fix`.
6. If similar vulnerable code exists elsewhere, report to user.

After this phase, advance `current_phase: "fix-and-verify"`.

---

## Phase 4: Commit

Create a commit with this message format:

```
fix(scope): [one-line description]

Symptom: [what was observed]
Root cause: [confirmed cause]
Fix: [what was changed]
```

After the commit:

1. Set `current_phase: "commit-complete"` and `next_action: "archive"`
   in the workflow file per `continuity-protocol.md`.
2. If this workflow has a `parent_workflow`, dispatch the terminal
   writeback by parent `workflow_type`:
   - Parent is `audit`: acquire a lock on the parent file and update
     `findings[i].resolved_commit` with the new commit SHA.
   - Parent is `start` or `fix` (non-audit): acquire a lock on the
     parent file and update the matching `child_completions[i]` entry
     (keyed by `child_id`) with `commit: <sha>` and `closed_at:
     <ISO-8601 UTC>`.
   If the parent is in `<cwd>/.claude/omcc-dev/archive/`, **skip the
   writeback with a stderr warning** — the parent state is frozen;
   the archive fallback still resolves the provenance link per
   `continuity-protocol.md` §Cross-workflow Handoff.
3. The Stop hook auto-archives when conditions A1–A4 are met (see
   `continuity-protocol.md` Archive and Completion Lifecycle). If hooks
   did not fire, the user can run `/omcc-dev:resume archive
   <workflow_id>` manually.

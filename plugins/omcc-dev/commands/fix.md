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
3. Bootstrap write: create
   `<cwd>/.claude/omcc-dev/workflows/fix-<timestamp>-<shortid>.md`
   with the always-required frontmatter from `continuity-protocol.md`
   State File Schema. Initial values: `workflow_type: fix`,
   `current_phase: "investigate"`, `next_action` describing the Phase 1
   next step, `tasks: []`, `git_baseline` captured from `git rev-parse
   HEAD` + `git branch --show-current` + the pinned `status_digest`
   pipeline, and `task_profile` (to be populated during Phase 1
   orchestration). Apply the secrets-hygiene regex scrub to
   `$ARGUMENTS` before writing `original_request`.
4. If `$ARGUMENTS` indicates this `/fix` is spawned from an `/audit`
   finding (cross-workflow handoff), set `parent_workflow` to the audit
   workflow id and `originating_finding` to the finding id per
   `continuity-protocol.md` Cross-workflow Handoff. Acquire a lock on
   the parent audit file and update its `findings[i].decision =
   "fix-now"` and `findings[i].child_workflow = <this id>`. If the
   parent file is in `<cwd>/.claude/omcc-dev/archive/`, write a warning
   and proceed without the parent update (parent state is static).
5. Add or update the entry in the active registry.
6. Run `git check-ignore <cwd>/.claude/omcc-dev/` and warn if the
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
2. If this workflow has a `parent_workflow` (spawned from `/audit`),
   acquire a lock on the parent's file and update
   `findings[i].resolved_commit` with the new commit SHA. If the parent
   is in `<cwd>/.claude/omcc-dev/archive/`, skip with a warning.
3. The Stop hook auto-archives when conditions A1–A4 are met (see
   `continuity-protocol.md` Archive and Completion Lifecycle). If hooks
   did not fire, the user can run `/omcc-dev:resume archive
   <workflow_id>` manually.

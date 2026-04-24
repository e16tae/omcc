---
description: Systematic feature development — think, explore, plan, build, review
argument-hint: Feature description or goal
---

# Start

$ARGUMENTS

Use `TaskCreate` to register each phase and `TaskUpdate` to mark progress as
the pipeline advances. Codex ensemble runs automatically per
`ensemble-protocol.md` when Ensemble Affinity warrants it — never ask the
user whether to invoke Codex, and never direct them to run `/codex:*`
commands manually.

---

## Phase 0: Continuity Check

Follow `continuity-protocol.md` Phase-boundary Write Rules, the Resume
Handoff Path contract, and the Legacy design-context.md Migration
section.

0. **Resume handoff**: if this invocation arrived via `/omcc-dev:resume`
   Step 6 delegating control back to `/start` after having selected and
   validated an active workflow of `workflow_type: start`, skip the
   bootstrap path. Recognize the selected workflow, advance to its
   recorded `current_phase`, and continue from the body of the
   corresponding Phase below. Do not re-prompt for resume/new/archive.
1. Read the active registry at `<cwd>/.claude/omcc-dev/active.md` if
   present. If any active workflow is listed (and this is NOT a resume
   handoff), offer the user: **resume** (hand control to
   `/omcc-dev:resume` and exit this command) / **start new** (continue
   here with a new workflow file alongside the existing ones) /
   **archive** (archive the chosen existing workflow, then continue).
2. If `<cwd>/.claude/design-context.md` exists (legacy artifact from an
   earlier omcc-dev version), apply the Legacy Migration rules in
   `continuity-protocol.md`: offer **import** / **archive** / **delete**.
   Acquire the migration lock sentinel per the protocol before acting.
3. Ensure `<cwd>/.claude/omcc-dev/workflows/` and
   `<cwd>/.claude/omcc-dev/archive/` exist with mode `0700` per
   `continuity-protocol.md` §Directory Layout (explicit `chmod 0700`
   after `mkdir -p`; do not rely on umask).
4. Bootstrap write: create
   `<cwd>/.claude/omcc-dev/workflows/start-<timestamp>-<shortid>.md`
   with the always-required frontmatter from `continuity-protocol.md`
   State File Schema. Initial values: `workflow_type: start`,
   `current_phase: "brainstorm"`, `next_action` describing the Phase 1
   next step, `tasks: []`, `git_baseline` captured from `git rev-parse
   HEAD` + `git branch --show-current` + the pinned `status_digest`
   pipeline, and `task_profile` (to be populated during Phase 1
   orchestration). Apply the secrets-hygiene regex scrub to
   `$ARGUMENTS` before writing `original_request`. Write the file with
   mode `0600`.
5. If `$ARGUMENTS` indicates this `/start` is spawned from a parent
   workflow (cross-workflow handoff per `continuity-protocol.md`
   §Cross-workflow Handoff) — typically a `fix-now` decision or a
   deliverable-level scope split — validate the parent workflow id
   against the workflow-id regex. If the parent is an `/audit`,
   additionally validate the finding id against the finding-id regex
   (`^finding-[0-9]+$` per `continuity-protocol.md` §Finding IDs) and
   record `originating_finding`. If validation fails at any step,
   reject the handoff with a diagnostic and proceed as a root workflow.

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
   the parent writeback with a stderr warning** — the parent state is
   frozen. `parent_workflow` (and, for audit parents,
   `originating_finding`) are still recorded on this workflow so
   provenance resolution via the archive fallback works.
6. Add or update the entry in the active registry with all required
   fields per `continuity-protocol.md` §Active Registry: `id` = this
   workflow id, `type: start`, `phase: "brainstorm"` (mirrors
   `current_phase`), `parent: <parent_workflow if step 5 set one, else
   null>`, `children: []`, `originating_finding: <finding id if step 5
   set one, else null>`. **If step 5 set `parent_workflow`, also call
   `appendChildToParentRegistry(activePath, parent_workflow, <this id>)`**
   so the parent's `children:` list operationally reflects this child
   (schema-2 requires the two-way `parent` ↔ `children` link; the
   Stop hook's transitive A4 gate walks `walkWorkflowTree` over the
   registry, but manual audit UX and cross-tooling rely on a correct
   `children:` field).
7. Run `git check-ignore <cwd>/.claude/omcc-dev/` and warn if the
   directory is not gitignored (per `continuity-protocol.md` Security
   Considerations).

All subsequent phases write to this workflow file at the boundaries
listed in `continuity-protocol.md` Phase-boundary Write Rules for
`workflow_type: start`.

---

## Phase 1: Brainstorm (no code allowed)

Follow the brainstorm skill's command-invoked mode (`skills/brainstorm/SKILL.md`).

Do not proceed until the user approves a direction.

---

## Phase 2: Explore Codebase

Follow the explore skill's command-invoked mode (`skills/explore/SKILL.md`).

---

## Phase 3: Plan and Verify

Follow the plan skill's command-invoked mode (`skills/plan/SKILL.md`).

Do not proceed until the user approves the plan.

### Workflow State Write

After plan approval, write the decision / architecture / plan into the
active workflow file at
`<cwd>/.claude/omcc-dev/workflows/<workflow_id>.md` per
`continuity-protocol.md` State File Schema. Required updates:

- `decision` (workflow-type-specific frontmatter): `chosen`, `rationale`,
  `rejected`.
- `architecture`: `patterns`, `integration_points`, `pitfalls`.
- `plan.deliverables` when deliverable mode applies (see below).
- `tasks`: populated from Phase 3's `TaskCreate`.
- `current_phase` advancing to `"plan"` (and later `"implement"` at
  phase end).

Also write human-readable summaries of the same four areas (Decision /
Architecture / Plan / Deliverable Progress) into the workflow file's
Markdown body for later re-contextualization.

Present the recorded state to the user for review — "Does this
accurately capture the decision context?"

### Deliverable assessment

Evaluate whether the plan should be executed as a single pass or in deliverables:

> "Can the full implementation be completed in one pass while maintaining context
> quality for all tasks?"

- YES → single pass (maximum coherence). Workflow stays flat:
  `workflows/<root_id>.md` only; no shards.
- NO → group tasks into independently completable deliverables,
  present grouping to user for approval. On approval, the root
  transitions to **sharded layout** per `continuity-protocol.md`
  §Hierarchical workflow shards:
  - Root's `plan.deliverables[]` is populated with one entry per
    deliverable (id = `A`, `B`, …) carrying `shard_path`, `status`,
    cached `phase`/`next_action`.
  - One shard file per deliverable is bootstrapped at
    `workflows/<root_id>/<shard_id>.md` via `resolveShardPath`, with
    frontmatter `{schema, shard_type, root_workflow, deliverable_id,
    timestamps, current_phase, next_action, tasks: []}`.
  - Each shard-file write goes through `atomicModifyFile` on the
    shard path; the root's cache update and the shard bootstrap are
    serialized by the root's `<root_id>.md.lock` to preserve the
    `continuity-protocol.md` lock-order contract (root → shard).

This is a quality judgment, not a cost optimization. Present the assessment
and reasoning to the user for final decision.

---

## Phase 4: Implement

If a task reveals a meaningful design decision with 2+ viable alternatives,
invoke the brainstorm skill first and wait for user approval before
implementing — do not code through ambiguous forks.

### Single pass mode

Execute the plan task by task:

1. For each task, follow the RED-GREEN-REFACTOR cycle:
   - **RED**: Write a failing test first and confirm failure with Bash
   - **GREEN**: Minimal implementation to pass the test
   - **REFACTOR**: Clean up while keeping tests green

   In projects without a test framework, skip the cycle, implement directly,
   and verify each task manually — inform the user about the absent framework.
2. Mark each task as completed in TaskUpdate as you go.
3. If a task reveals the plan needs adjustment — see Plan Adjustment below.

### Deliverable mode

For each deliverable (schema-2 hierarchical layout — each deliverable
owns its own shard file):

1. **Re-contextualize (shard-scoped)**:
   - Read the **active shard** file at the `shard_path` recorded in
     the root's `plan.deliverables[i]` — resolve via
     `resolveShardPath(cwd, root_id, deliverable_id)`. Load both the
     shard's frontmatter and body.
   - Read the **root file's frontmatter only** — `decision`,
     `architecture`, `plan.deliverables[]` cache. The root's body
     (pre-compact snapshots, prior deliverables' narrative) is NOT
     re-read; completed shards' detail stays in `archive/` when those
     shards have terminated, or in their own shard file when they
     are dormant.
   - Read the code files referenced in the active shard's body.
   This is the load-bearing change that makes re-contextualization
   O(shard) instead of O(root+all-shards), per Phase 2 Heavy-read
   Hotspot #1 (Codex plan-verify gap tracker).
2. **Implement**: Execute tasks in this deliverable following TDD cycle.
3. **Review**: Follow Phase 5 (full parallel-review + Codex) on the
   shard-scoped diff.
4. **Resolve**: Follow Phase 6 (Resolve & Converge).
5. **Commit**: Commit this deliverable. Update
   `plan.deliverables[i].status = "completed"` on the root (cache
   only — the shard file retains the authoritative `current_phase`).
6. **Update**: Write state via `atomicModifyFile` on the shard path;
   refresh the root's `plan.deliverables[i]` cache under the root's
   lock. Unknown fields on either file are preserved verbatim.

After all deliverables complete: proceed to Cross-deliverable Final
Review (Phase 5b). Archive of the sharded root on terminal commit is
handled by the Stop hook through `moveWorkflowToArchive`
(root .md + shard directory, atomic).

### Plan Adjustment

If a task reveals the plan needs adjustment, assess the impact:

1. **Remaining tasks only affected** (e.g., function name differs from expected):
   Report to user, adjust remaining task descriptions inline. Update the
   workflow file per `continuity-protocol.md` Phase-boundary Write Rules.
2. **Completed code also affected** (e.g., planned API doesn't support required feature):
   Report to user with impact assessment. Re-run plan skill for remaining tasks.
   Update the workflow file per `continuity-protocol.md`.
3. **Brainstorm decision itself invalidated** (e.g., chosen approach is infeasible):
   Report to user with evidence. Return to Phase 1 (Brainstorm) with the
   discovery as new context. Update the workflow file per `continuity-protocol.md`.

In all cases: present the situation and proposed response to the user for approval.

---

## Phase 5: Review

Before parallel-review, verify completion:

1. Run the full test suite (if available) — confirm all pass.
2. If the implementation transformed a pattern (rename/refactor), Grep for
   the old pattern to confirm 0 remaining occurrences.

Then follow the parallel-review skill's command-invoked mode (`skills/parallel-review/SKILL.md`).

### Phase 5b: Cross-deliverable Final Review (deliverable mode only)

After all deliverables are committed, review the entire branch:

1. `git diff [base-branch]...HEAD` for the full change set
2. Full parallel-review targeting cross-cutting concerns:
   - Architectural consistency across deliverables
   - Integration issues at deliverable boundaries
   - Patterns visible only at whole-branch scope
3. Codex review with `--scope branch`
4. If findings exist, resolve via Phase 6

---

## Phase 6: Resolve & Converge

If Phase 5 produced findings, resolve them before committing:

### Step 1: Review and fix

For each finding:
1. If the fix approach involves a meaningful choice between 2+ alternatives,
   follow the brainstorm skill to compare and wait for user approval.
2. If the fix is straightforward, present the approach and confirm with the user.
3. Apply the approved fix.

### Step 2: Re-review (Codex ensemble included)

After all findings are addressed:
1. Claude: focused review of changed files + their dependencies (side effect perspective)
2. Codex: `review --scope working-tree` (independent full patch review)
3. Run the full test suite
4. Synthesize Claude + Codex results

### Step 3: Converge

- New findings → return to Step 1
- No new findings → proceed to Phase 7
- Same finding recurring → report to user as a design-level issue,
  discuss whether to address now or defer to a separate `/fix` workflow

---

## Phase 7: Commit

Create a commit with this message format:

```
feat(scope): [one-line description]
```

If the changes warrant a PR, ask the user whether to create one.

### Cleanup

Set `current_phase: "commit-complete"` and `next_action: "archive"` in
the workflow file per `continuity-protocol.md`. If this workflow has
a `parent_workflow`, dispatch the terminal writeback by parent
`workflow_type`:

- Parent is `audit`: acquire a lock on the parent file and update
  `findings[i].resolved_commit` with the new commit SHA.
- Parent is `start` or `fix` (non-audit): acquire a lock on the parent
  file and update the matching `child_completions[i]` entry (keyed by
  `child_id`) with `commit: <sha>` and `closed_at: <ISO-8601 UTC>`.

If the parent is in `<cwd>/.claude/omcc-dev/archive/`, **skip the
writeback with a stderr warning** — the parent state is frozen; the
archive fallback still resolves the provenance link per
`continuity-protocol.md` §Cross-workflow Handoff.

The Stop hook auto-archives when all four conditions (A1–A4) are met;
no manual cleanup is needed in normal cases. If hooks did not fire,
the user can run `/omcc-dev:resume archive <workflow_id>` to archive
manually.

Handling of previous workflow files from earlier sessions is owned by
Phase 0 (Continuity Check), not this Cleanup section — a new `/start`
invocation detects them there and offers resume / start new / archive.

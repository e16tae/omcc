---
description: Systematic feature development — think, explore, plan, build, review
argument-hint: Feature description, goal, or path to a recognized artifact (DESIGN.md / research_brief.md)
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
3a. **Artifact intake (if applicable)**: inspect `$ARGUMENTS` for an
   artifact handoff from another omcc plugin. Independent of Step 5
   below — Step 3a's "single token resolving to a file" gate and
   Step 5's parent-workflow id regex match disjoint shapes; the
   `$ARGUMENTS` contract is one OR the other, never both. Mirrors the
   brief-vs-raw idiom used in the omcc-designer plugin's frontend
   skill (see that plugin's SKILL.md for the original pattern);
   structural markers chosen per artifact for i18n safety where
   applicable.

   The detection pipeline runs in two phases: a **silent gate** that
   determines whether the user even attempted a handoff, followed by
   a **committed phase** in which any failure produces a user-facing
   warning (so a typo or moved file is surfaced rather than swallowed).

   a. **Normalize `$ARGUMENTS`**: strip leading and trailing ASCII
      whitespace. Then trim one optional balanced quote pair (`'…'`
      or `"…"`). The result is the candidate path token. If the
      remaining string contains any internal whitespace (so it is
      multi-token), skip artifact intake silently — the user did not
      pass a single path.
   b. **Whitelist gate (silent)** — case-sensitive comparison on the
      basename of the candidate token (no path resolution yet, so
      case-insensitive filesystems cannot change the discriminator):
      the basename must be exactly `DESIGN.md` or *research_brief.md*.
      Other filenames — even other `.md` files — fall through to
      raw-request mode silently. (Note: only the four external-
      standard filenames `DESIGN.md`, `README.md`, `AGENTS.md`,
      `CLAUDE.md` may appear inside backticks per
      `tests/test_plugin_structure.py`; *research_brief.md* is
      rendered as italic prose for that reason.)

   From this point on, the user has explicitly attempted a handoff;
   any failure is a **warning** that surfaces the issue to the user
   (then continues with `$ARGUMENTS` treated verbatim as raw input)
   rather than a silent skip.

   c. **Resolve the path** (committed phase):
      - If the token starts with `~/` or `~<user>/`, expand `~` to
        the matching home directory.
      - If the token is relative, resolve against the current working
        directory.
      - Apply `realpath` to follow symlinks.
      - The resolved target MUST be an existing **regular file** that
        is **readable** by the current process.
      - **On any path-resolution failure** (path does not exist,
        target is a directory / device / socket / FIFO, broken
        symlink, unreadable due to permissions, realpath errors):
        emit warning "recognized artifact name <basename> but no
        readable file at <token> (resolution failed: <reason>) —
        proceeding as raw request" and continue with raw input.
   d. **Per-artifact structural marker check** (committed phase):
      - If basename = `DESIGN.md`: the file's first non-empty line
        must be exactly `---` (start of a YAML frontmatter block).
        Per the Google design.md spec the frontmatter is mandatory.
      - If basename = *research_brief.md*: the file's first non-empty
        line must start with `# ` (a markdown h1 — language-agnostic).
        The omcc-research brief spec opens with
        `# Research Brief: <topic>`, but the topic and the literal
        `Research Brief` substring may both be in the user's language;
        the structural h1 marker is the i18n-safe gate.
      - On marker mismatch: emit warning "recognized artifact name
        <basename> but the file does not match the expected shape
        (DESIGN.md needs YAML frontmatter, *research_brief.md*
        needs an h1 first line) — proceeding as raw request" and
        continue with raw input.
   e. **Outside-cwd advisory** (committed phase, non-fatal): if the
      realpath-resolved file is outside the current working directory,
      set `outside_cwd = true` and emit a one-line informational
      warning of the form "artifact <basename> resolves to a path
      outside the current project (<resolved-path>) — workflow
      provenance will reference this external location; copy the
      artifact into the project if you prefer self-contained
      provenance." Otherwise `outside_cwd = false`. Continue regardless
      — this is informational and never blocks ingestion.
   f. **Read budget guards** (apply during excerpt extraction):
      - If the file is larger than 1 MiB, do NOT embed any excerpt;
        emit informational note "artifact exceeds 1 MiB — embedding
        path only, downstream phases must Read the file directly" and
        set `artifact_excerpt = null`. (Ingestion still proceeds — the
        path is recorded so downstream phases can fetch on demand.)
      - Otherwise read the file. Per-line cap: truncate any single
        line longer than 1000 bytes to 997 bytes followed by `...`.
        Excerpt selection: full content if ≤ 60 lines; otherwise
        first 50 lines, then a separator line `...<N omitted>...`
        where N is the omitted count, then the last 10 lines.
      - **Fence-length rule**: scan the prepared excerpt for the
        longest contiguous run of backticks on any line; the outer
        fence in Step 4's body template MUST be at least one backtick
        longer than that run (and never shorter than 3). The default
        wrapper fence is therefore typically 4 or 5 backticks; bump
        further if the excerpt itself contains long fences.

   Outcomes:

   - **Detected**: record the captured fields for use by Step 4 —
     `artifact_kind` (one of `DESIGN.md` or *research_brief.md*),
     `artifact_path` (absolute, realpath-resolved),
     `outside_cwd` (boolean from Step 3a-e),
     `artifact_excerpt` (string or `null` per Step 3a-f), and
     `excerpt_fence_length` (integer ≥ 3 per Step 3a-f fence rule).
   - **Warning emitted** (path resolution or marker check failed
     after the basename gate committed the user to a handoff
     attempt): treat `$ARGUMENTS` verbatim as raw input. The warning
     is what the user sees; no artifact context is captured.
   - **Silent skip** (basename not in the whitelist, or `$ARGUMENTS`
     is multi-token / not a path-shaped token): continue with
     `$ARGUMENTS` as raw input. No warning.

   The artifact-intake whitelist is `commands/start.md`-canonical —
   `CLAUDE.md` cross-references it, but new artifact kinds MUST be
   added here.
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

   **If Step 3a detected an artifact**: in addition to the frontmatter
   above (which is unchanged — `original_request` remains the
   single-line scrubbed `$ARGUMENTS` so the YAML scalar parser in
   `hooks/_utils.mjs` is not corrupted by embedded newlines), include
   a `## Source Artifact` subsection in the workflow file's Markdown
   body using the verbatim template below, placed immediately after
   the workflow's `## Original Request` body subsection so subsequent
   phases (Phase 1 brainstorm onward) pick up the artifact context as
   part of normal workflow-body re-reading — no additional intake
   step is required downstream.

   Verbatim template (substitute the bracketed fields with the
   captured values from Step 3a; omit the `outside-cwd warning` line
   when `outside_cwd = false`; the excerpt fence in the body MUST be
   `excerpt_fence_length` backticks long per Step 3a-f's
   fence-length rule; when `artifact_excerpt = null`, replace the
   entire fenced block with the single italic line shown below):

   `````markdown
   ## Source Artifact

   - **Type**: [DESIGN.md | research_brief.md]
   - **Path**: [absolute realpath-resolved path]
   - **Outside-cwd warning**: [the warning string emitted in Step 3a-e]
   - **Excerpt**:

   <fence of `excerpt_fence_length` backticks>
   [artifact_excerpt verbatim, with Step 3a-f truncation already applied]
   <fence of `excerpt_fence_length` backticks>
   `````

   When `artifact_excerpt = null`, replace the four template lines
   from the fence-open through the fence-close with this single
   substitute line:
   `_Excerpt skipped: artifact exceeds 1 MiB; downstream phases must Read the file directly._`

   The outer template fence above uses 5 backticks so the
   `excerpt_fence_length` placeholder line and any nested 3-or-4-
   backtick fence in the spec render correctly inside this document
   itself; the actual workflow body uses whatever
   `excerpt_fence_length` Step 3a-f computed.

   When no artifact was detected, omit the `## Source Artifact`
   subsection entirely (do NOT emit an empty placeholder).
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

After Synthesize for the Codex `brainstorm` ensemble, the command
writes `ensemble_results` per `ensemble-protocol.md` §Result
Bookkeeping in the same atomic mutation that clears the matching
`pending_ensemble` row. `phase: brainstorm`,
`ensemble_type: brainstorm`, `run_id` per `continuity-protocol.md`
§Run-id format (workflow-durable token, NOT the Bash background id).

---

## Phase 2: Explore Codebase

Follow the explore skill's command-invoked mode (`skills/explore/SKILL.md`).

After Synthesize for the Codex `explore` ensemble, the command writes
`ensemble_results` per `ensemble-protocol.md` §Result Bookkeeping.
`phase: explore`, `ensemble_type: explore`, `run_id` per
`continuity-protocol.md` §Run-id format.

---

## Phase 3: Plan and Verify

Follow the plan skill's command-invoked mode (`skills/plan/SKILL.md`).

Do not proceed until the user approves the plan.

After Synthesize for the Codex `plan-verify` ensemble, the command
writes `ensemble_results` per `ensemble-protocol.md` §Result
Bookkeeping. `phase: plan`, `ensemble_type: plan-verify`, `run_id`
per `continuity-protocol.md` §Run-id format.

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
7. **Checkpoint prompt (opt-in)**: at the deliverable boundary, ask
   the user: *"A checkpoint is recommended at this deliverable
   boundary. Proceed? (y/N)"*. On `y`, invoke `/omcc-dev:checkpoint`
   with a short summary of what the deliverable accomplished —
   SessionStart will surface the digest on re-entry and PreCompact
   will suppress its mechanical snapshot for 60s. On `N` or no
   response, continue without a checkpoint. Do NOT auto-checkpoint.

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

After Synthesize for the parallel-review skill's Codex result, the
command (not the skill — see `skills/parallel-review/SKILL.md`
ownership note) writes `ensemble_results` per `ensemble-protocol.md`
§Result Bookkeeping in a single three-step atomic mutation:
(1) clear the matching `pending_ensemble` row; (2) append the new
`ensemble_results` entry; (3) invoke `pruneEnsembleResults(entries)`
from `hooks/_utils.mjs` to enforce the retention cap per
`continuity-protocol.md` §ensemble_results semantics §Retention cap.
`phase: review`, `ensemble_type: review`, `run_id` per
`continuity-protocol.md` §Run-id format.

### Phase 5b: Cross-deliverable Final Review (deliverable mode only)

After all deliverables are committed, review the entire branch:

1. `git diff [base-branch]...HEAD` for the full change set
2. Full parallel-review targeting cross-cutting concerns:
   - Architectural consistency across deliverables
   - Integration issues at deliverable boundaries
   - Patterns visible only at whole-branch scope
3. Codex review with `--scope branch`
4. If findings exist, resolve via Phase 6

The Phase 5b Codex review is also recorded to `ensemble_results` per
`ensemble-protocol.md` §Result Bookkeeping (three-step atomic
mutation: pop pending → append result → `pruneEnsembleResults`).
`phase: review`, `ensemble_type: review`, with a fresh `run_id` so
it does not collide with the Phase 5 entry. 5b writes to the **root**
file (no shard is "active" at branch-wide review).

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

The Phase 6 re-review Codex result is recorded to `ensemble_results`
per `ensemble-protocol.md` §Result Bookkeeping (three-step atomic
mutation: pop pending → append result → `pruneEnsembleResults`).
`phase: resolve`, `ensemble_type: review`, with a fresh `run_id` per
re-review pass. Multiple resolve loops produce multiple
`(phase=resolve, ensemble_type=review)` entries that differ by
`run_id` and `completed_at`. The retention cap may evict the oldest
entries across `(phase, ensemble_type)` pairs as the list grows past
`MAX_ENSEMBLE_RESULTS_PER_WORKFLOW`.

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

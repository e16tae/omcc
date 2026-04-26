---
description: Systematic codebase audit — parallel scanning across categories with remediation discussion
argument-hint: Audit scope (e.g., "security", "performance", "full")
---

# Audit

$ARGUMENTS

Use `TaskCreate` and `TaskUpdate` to track audit progress across phases.
Codex ensemble runs automatically per `ensemble-protocol.md` when Ensemble
Affinity warrants it (Phase 2 for MEDIUM/HIGH, Phase 4 for LOW) — never ask
the user whether to invoke Codex.

---

## Phase 0: Continuity Check

Follow `continuity-protocol.md` Phase-boundary Write Rules, the Resume
Handoff Path contract, and the Legacy design-context.md Migration
section.

0. **Resume handoff**: if this invocation arrived via `/omcc-dev:resume`
   Step 6 delegating control back to `/audit` after having selected and
   validated an active workflow of `workflow_type: audit`, skip the
   bootstrap path. Recognize the selected workflow, advance to its
   recorded `current_phase`, and continue from the body of the
   corresponding Phase below. Do not re-prompt for resume/new/archive.
1. Read the active registry at `<cwd>/.claude/omcc-dev/active.md` if
   present. If any active workflow is listed (and this is NOT a resume
   handoff), offer the user: **resume** (hand control to
   `/omcc-dev:resume` and exit) / **start new** / **archive** (archive
   the chosen existing workflow, then continue).
2. If `<cwd>/.claude/design-context.md` exists (legacy artifact), apply
   the Legacy Migration rules in `continuity-protocol.md`: offer
   **import** / **archive** / **delete**. Acquire the migration lock
   sentinel per the protocol before acting.
3. Ensure `<cwd>/.claude/omcc-dev/workflows/` and
   `<cwd>/.claude/omcc-dev/archive/` exist with mode `0700` per
   `continuity-protocol.md` §Directory Layout.
4. Bootstrap write: create
   `<cwd>/.claude/omcc-dev/workflows/audit-<timestamp>-<shortid>.md`
   with the always-required frontmatter from `continuity-protocol.md`
   State File Schema. Initial values: `workflow_type: audit`,
   `current_phase: "scope"`, `next_action` describing the Phase 1 next
   step, `tasks: []`, `git_baseline` captured from `git rev-parse HEAD`
   + `git branch --show-current` + the pinned `status_digest`
   pipeline, and `task_profile` (to be populated during Phase 1).
   Apply the secrets-hygiene regex scrub to `$ARGUMENTS` before
   writing `original_request`. Write the file with mode `0600`.
5. Add or update the entry in the active registry with all required
   fields per `continuity-protocol.md` §Active Registry: `id` = this
   workflow id, `type: audit`, `phase: "scope"`, `parent: null` (audit
   workflows are always root), `children: []`, `originating_finding:
   null`.
6. Run `git check-ignore <cwd>/.claude/omcc-dev/` and warn if the
   directory is not gitignored (per `continuity-protocol.md` Security
   Considerations).

Note: the workflow state file at
`<cwd>/.claude/omcc-dev/workflows/<workflow_id>.md` is distinct from
any findings report — see the clarification in Phase 4 below.

All subsequent phases write to this workflow file at the boundaries
listed in `continuity-protocol.md` Phase-boundary Write Rules for
`workflow_type: audit`.

---

## Phase 1: Determine Scope

If $ARGUMENTS specifies the audit type, use it directly. Otherwise:

1. Gather minimal context (recent git log, directory structure, project config)
2. Follow the brainstorm skill's command-invoked mode (`skills/brainstorm/SKILL.md`)
   to compare audit types and recommend the most appropriate type and scope
3. If context is insufficient, default to "full". State the reasoning.

**Audit types**: security / performance / code quality / tech debt / full (all of the above)
**Target scope**: entire codebase / specific directory or module

Build the Task Profile (`orchestration.md` Step 1), including Ensemble Affinity.

After scope is locked, write the following to state per
`continuity-protocol.md`: `audit_type`, `target_scope`, and
`task_profile` (scope / layers / risks / complexity /
ensemble_affinity). `current_phase` remains `"scope"` through this
phase and transitions to `"scan"` at Phase 2 dispatch.

---

## Phase 2: Parallel Scan

Follow `orchestration.md`, targeting Review Agents based on audit type.

### Agent selection rules for audits

**Full audit**: Always include the baseline set: **security, performance, simplicity, conventions, debt**.
These cannot be excluded — "full" guarantees complete coverage of these categories.
Then use orchestration to determine if additional specialist perspectives
(correctness, concurrency, api-design, error-resilience, migration-safety) are warranted based on the codebase's characteristics.

**Specific type**: Decompose the chosen type into distinct sub-aspects and assign one agent per sub-aspect.
Example: "security" audit → separate missions for auth/authz, input validation, secrets management.

Launch all selected agents in parallel (single message, multiple Agent calls).

Advance `current_phase: "scan"` when dispatching.

If ensemble active (Affinity MEDIUM or HIGH):
- Simultaneously launch Codex **audit-scan** ensemble point (background) per `ensemble-protocol.md`
- Focus text is derived from the audit type per `ensemble-protocol.md` audit-scan definition
- State bookkeeping per `ensemble-protocol.md` §State Bookkeeping
  (append `pending_ensemble` entry on launch with `ensemble_type:
  audit-scan`; remove on collect)

After agent results are collected, write the initial `findings` list
(one entry per finding with `id`, `severity`, `location`, and
`decision: undecided`) to state per `continuity-protocol.md`.

---

## Phase 3: Integrate Built-in Results

If the audit includes security:
- Phrase the suggestion so it degrades gracefully if the command is absent:
  "If `/security-review` is available in your Claude Code setup, it provides
  git-diff-based security analysis as a complement to this audit."
  (`/security-review` is a native Claude Code feature, not an omcc-dev command.)
- Integrate those results if the user provides them

After this phase, advance `current_phase: "integrate"` per
`continuity-protocol.md`.

---

## Phase 4: Present Findings

Collect Codex audit-scan result from Phase 2 background task (if ensemble was launched).

If ensemble active (Affinity MEDIUM or HIGH — launched in Phase 2):
- Synthesize Claude agent findings + Codex adversarial-review findings per `ensemble-protocol.md`
- Deduplicate by location
- Unify severity ratings (elevate confidence when both sides agree)
- Source-label all findings (Claude / Codex / Both)

If ensemble not active (LOW affinity):
- Launch Codex **audit-scan** ensemble point now (review-phase ensemble for LOW affinity)
- State bookkeeping per `ensemble-protocol.md` §State Bookkeeping
- Collect results
- Synthesize into findings.

Follow the Presentation Mode Protocol (`presentation-protocol.md`) before presenting.

Present findings directly in conversation, organized by severity (Critical → High → Medium → Low),
followed by positive observations. Do not generate a separate report file.

**Scope clarification**: this rule prohibits a user-facing findings
report deliverable. The workflow state file at
`<cwd>/.claude/omcc-dev/workflows/<workflow_id>.md` is distinct — it is
workflow metadata (phase, decisions, ensemble affinity, finding ids +
decision status), not a findings report. State writes continue per
`continuity-protocol.md`.

After synthesis is complete, write the finalized `findings` list
(synthesized + severity-unified + source-labeled) to state and advance
`current_phase: "present"`.

This phase is typically the workflow's first user-facing presentation
point. As soon as the user chooses batch or interview per
`presentation-protocol.md`, write `presentation_mode` to state per
`continuity-protocol.md` Conditionally-required frontmatter so a
subsequent `/omcc-dev:resume` does not re-ask.

**Observation-only short-circuit**: if every finding has
`severity: observation` (no actionable findings requiring remediation
decisions), this is the workflow's terminal point. After presenting the
observations, write `current_phase: "summary-complete"` and
`next_action: "archive"` directly and exit. The Stop hook then handles
the archive move per `continuity-protocol.md` §Archive and Completion
Lifecycle (A1 + A4 conditions for audit workflows). Observations are
exempt from the "no undecided at terminal" rule.

---

## Phase 5: Remediation Discussion

Walk through each actionable finding from Phase 4 for detailed analysis and direction decision.

If all findings are positive observations with no actionable items, the
observation-only short-circuit in Phase 4 already wrote
`summary-complete` and terminated Phase 4 (the Stop hook handles the
archive move); skip this phase entirely — it is never entered in the
observation-only case.

Use the presentation mode already chosen for this audit invocation
(per `presentation-protocol.md` timing rule — do not re-ask).

Advance `current_phase: "remediation-discussion"` when this phase
begins. If `presentation_mode` was not already persisted (e.g., Phase 4
was the first presentation and it was not recorded), write the chosen
value to state now per `continuity-protocol.md`.

### Per-finding analysis

For each finding, provide:

1. **Situation**: Explain the finding with concrete code references (file paths,
   function names, data flows) sufficient for independent verification. Cover what
   it means, why it occurs, and how far the impact reaches.

2. **Scenarios**: Describe what happens under each viable remediation approach,
   including a "do nothing" baseline. Focus on concrete consequences — specific
   failure modes, degradation paths, or maintenance costs — not abstract risk levels.

3. **Decision**: The user chooses one of:
   - **Fix now** — address in a subsequent `/fix` or `/start` workflow.
     On transition, the child command's Phase 0 sets `parent_workflow`
     to this audit's workflow id and `originating_finding` to the
     finding id per `continuity-protocol.md` Cross-workflow Handoff.
     The child's `/fix` or `/start` Phase 0 also acquires a lock on
     this audit's workflow file and sets this finding's
     `decision: "fix-now"` and `child_workflow: <child id>`.
   - **Defer** — direction is known but timing is not; record with a trigger condition
   - **Accept risk** — acknowledge and document the rationale for acceptance
   - **Investigate further** — direction itself is unknown. Invoke
     `skills/investigate/SKILL.md` in auto-activated mode for a
     hypothesis-driven investigation, or transition to `/fix` if a
     specific fault candidate has emerged from discussion. (There is
     no separate `/omcc-dev:investigate` command — investigation lives
     in the skill.)

Write each decision to state per `continuity-protocol.md`:
`findings[i].decision` is updated to the chosen value as each
discussion concludes. Actionable findings (severity critical / high /
medium / low) MUST NOT remain `undecided` before this phase
terminates. Observations (`severity: observation`) are exempt per
`continuity-protocol.md`.

When a finding reveals 2+ meaningfully different remediation paths, the
Protocol Interaction Rule (`presentation-protocol.md`) triggers the brainstorm skill
inline — approach comparison, recommendation, and user choice are handled by that
existing pipeline. Do not duplicate brainstorm output within this phase.

### After all findings reviewed

Synthesize the decisions made during the discussion:

- Summary table: finding × decision (fix now / defer / accept / investigate)
- Count by decision type
- If any findings are marked "fix now": list them and offer to transition
  to the appropriate workflow (`/fix` for defects, `/start` for enhancements).
  The chosen workflow's Phase 0 records `parent_workflow` pointing at
  this audit, and its terminal Commit phase (Phase 4 for `/fix`,
  Phase 7 for `/start`) updates this audit's
  `findings[i].resolved_commit` with the child's commit SHA.
- If any findings are marked "investigate further": list them and offer
  to invoke `skills/investigate/SKILL.md` auto-activated, or `/fix` if
  a specific fault candidate has emerged.

After all findings are reviewed and the summary table is written,
**gate the terminal write** on child workflow linkage:

- For every finding with `decision: "fix-now"`, either (a)
  `findings[i].child_workflow` is populated (meaning `/fix` or `/start`
  was spawned and wrote back the link at its Phase 0), OR (b) the user
  has explicitly re-decided that finding to `defer` or `accept` after
  declining to spawn a child.
- If any `fix-now` finding still lacks `child_workflow` AND the user
  has not explicitly deferred, leave `current_phase` at
  `remediation-discussion` and wait. Do not advance to terminal while
  the audit has open fix-now intents — advancing would let the Stop
  hook auto-archive (A4 sees no active children yet) before the child
  workflow can write the parent linkage, causing the child to find
  the parent in `archive/` and skip the writeback.

Once the gate passes, set `current_phase: "summary-complete"` and
`next_action: "archive"` in the workflow file per
`continuity-protocol.md`. The Stop hook auto-archives when conditions
A1 + A4 are met (no commit requirement for audit workflows — see
`continuity-protocol.md` Archive and Completion Lifecycle). If hooks
did not fire, the user can run `/omcc-dev:resume archive
<workflow_id>` manually. If this audit has active children (open
fix-now workflows that did succeed in writing back but have not yet
reached terminal state themselves), archive is further gated by A4
until those children reach terminal state or the user explicitly
archives with a child-dangling warning.

# Ensemble Affinity

Ensemble Affinity determines how broadly the dual-model ensemble (Claude + Codex)
is applied during a workflow. Evaluated from the Task Profile produced by
`orchestration.md` Step 1.

---

## Notation

Analysis dimensions (prose) and persisted Task Profile fields
(YAML keys in `task_profile` per `continuity-protocol.md` State File Schema)
correspond as follows:

| Analysis dimension | Persisted field |
|---|---|
| Scope | `scope` |
| Layers | `layers` |
| Risk areas | `risks` (list of sub-category labels) |
| Complexity | `complexity` (low / medium / high rollup) |
| Ensemble Affinity | `ensemble_affinity` (LOW / MEDIUM / HIGH, derived) |

The match rules below reference dimensions by their prose name. The
two are the same conceptual dimension at different granularity:
"Risk areas" is the analyst's vocabulary; `risks` is the YAML key.
`orchestration.md` Step 1 enumerates the same dimensions and their
sub-categories.

### Sub-categories

**Risk areas** (sub-category labels that may appear in `risks`):

- **Security** — auth, crypto, secrets, credential exposure
- **Data** — schema change, migration, data integrity
- **Public interfaces** — API, SDK, plugin contract, CLI
- **Concurrency** — shared resources, async, race conditions
- **Failure** — external dependencies, partial failure, timeout
- **Novelty / Precedent** — first-of-a-kind patterns; new
  plugin-level public contracts; frontier integration with limited
  prior art. *Example:* archive `start-20260430T143149Z` recorded
  `frontier (design-domain multi-model is less precedented than
  research)` as a risk feeding the MEDIUM tier evaluation.
- **Downstream blast radius** — state coupling; schema coupling;
  cross-plugin contract impact; lifecycle/loop fan-out across many
  call sites. *Example:* archive `fix-20260430T140040Z` was a 3-file
  dispatch swap with temp-file lifecycle and per-(variant, zone) loop
  risk; the blast-radius sub-category captures this even when scope
  and layer count are small.

**Complexity** sub-inputs (factors feeding the low / medium / high rollup):

- **Domain complexity** — level of domain knowledge and business-rule
  complexity required (orchestration.md Step 1 analysis dimension).
- Algorithmic or mathematical depth.
- Cross-service or cross-process coordination.

These sub-categories are **tagging vocabulary only**. They expand the
analyst's reasoning record but do NOT introduce new top-down match
conditions. The HIGH/MEDIUM/LOW rules below key on specific keywords
(`security`, `concurrency`, `data migration`, `public API change`); a
`risks` list whose only labels are `Novelty / Precedent` and/or
`Downstream blast radius` does NOT auto-promote the affinity tier
under the rules below.

When such labels appear, the analyst is expected to consider whether
they imply one of the canonical match keywords (e.g., a novelty-flagged
plugin contract may also be a public API change; a high-blast-radius
schema rewrite may also be a data migration). Promotion happens through
the canonical keyword match, not through the sub-category label.

---

## Evaluation Criteria

Evaluate top-down. The first matching level applies.

### HIGH

Any ONE of the following:

- Risks include security or concurrency
- Complexity: high
- Core task involves algorithmic or mathematical implementation
- Bug is intermittent, hard to reproduce, or crosses service boundaries
- Scope: 5+ files across 3+ layers

### MEDIUM

Not HIGH, but any ONE of the following:

- Complexity: medium
- Layers: 2 or more
- Risks include data migration or public API change
- Refactoring that must preserve existing behavior

### LOW

None of the above criteria apply.

---

## Ensemble Scope by Affinity

### HIGH and MEDIUM — Full ensemble across all phases

| Command  | Ensemble Phases                                                                    |
|----------|------------------------------------------------------------------------------------|
| `/start` | Phase 1 (Brainstorm), Phase 2 (Explore), Phase 3 (Plan + Verify), Phase 5 (Review) |
| `/fix`   | Phase 1 (Investigate), Phase 3 (Fix & Verify)                                      |
| `/audit` | Phase 2 (Parallel Scan), Phase 4 (Present Findings)                                 |

When the task warrants any ensemble at all, the cost of running Codex on all phases
is negligible compared to the risk of missing something by skipping a phase.

### LOW — Review phase only

| Command  | Ensemble Phases          |
|----------|--------------------------|
| `/start` | Phase 5 (Review)         |
| `/fix`   | Phase 3 (Fix & Verify)   |
| `/audit` | Phase 4 (Present Findings)|

Even trivial changes benefit from an independent second review.
Exploration and brainstorm ensemble would add latency without
meaningful value for simple tasks.

---

## Future work — pending empirical baseline

Two affinity-rule refinements were proposed in GitHub issue #97 but
deferred from the current iteration because the local archive sample
(`<cwd>/.claude/omcc-dev/archive/`) does not yet contain enough
workflows of the relevant types to validate or refute them. The
`ensemble_results` capture introduced alongside this iteration
(`continuity-protocol.md` § Workflow-type-specific frontmatter and
`ensemble-protocol.md` § Result Bookkeeping) is the data
infrastructure that future revisitation depends on — once
`ensemble_results` rows accumulate, retrospective analysis becomes
possible.

### H1 — LOW `/start` plus 3+ ordered tasks → plan-verify dispatch

Hypothesis: when a LOW-affinity `/start` workflow's plan contains
three or more ordered or dependency-linked tasks, plan-verify
catches ordering or dependency mistakes that the LOW-tier
review-only ensemble misses.

Revisit conditions (any one suffices to re-evaluate):
- At least 3 archived `/start` workflows where
  `task_profile.ensemble_affinity == LOW` AND the recorded plan has
  `>= 3` tasks with ordering or `blocked_by` edges.
- A LOW-affinity `/start` post-mortem reports a Phase 5 review
  finding that an earlier plan-verify pass would have caught.

### H2 — HIGH `/fix` second-pass `fix-verify`

Hypothesis: HIGH-affinity `/fix` workflows benefit from a second
`fix-verify` pass after initial verification, because the first
pass under-catches issues introduced during the fix application.

Revisit conditions (any one suffices):
- At least 3 archived `/fix` workflows where
  `task_profile.ensemble_affinity == HIGH`, with `ensemble_results`
  rows for `fix-verify` showing a verdict of `concerns` or
  `conflict` that required a second iteration.
- A HIGH-affinity `/fix` post-mortem reports a regression caught
  only after additional `fix-verify` passes.

### Method

When either H1 or H2's revisit condition fires, run a fresh `/start`
or `/audit` against `ensemble-affinity.md` § Evaluation Criteria with
`ensemble_results` data as the empirical input. Until then the rules
above remain unchanged — adding affinity-conditional dispatches
without empirical basis is explicitly out of scope (`continuity-protocol.md`
schema-stability principle: rule changes that affect default
behavior require evidence, not just intuition).

---

## Related

- Model and Effort Policy: `ensemble-protocol.md` Prompt Construction Rules.
- Independence Rule: `ensemble-protocol.md` Independence Rule (canonical
  definition and single exception for Plan Verification).

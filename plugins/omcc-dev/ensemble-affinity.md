# Ensemble Affinity

Ensemble Affinity determines how broadly the dual-model ensemble (Claude + Codex)
is applied during a workflow. Evaluated from the Task Profile produced by
`orchestration.md` Step 1.

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

## Model and Effort Policy

See `ensemble-protocol.md` Prompt Construction Rules.

---

## Independence Rule

See `ensemble-protocol.md` Independence Rule for the canonical definition
and its single exception (Plan Verification).

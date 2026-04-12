---
description: Systematic feature development — think, explore, plan, build, review
argument-hint: Feature description or goal
---

# Start

$ARGUMENTS

---

## Phase 1: Brainstorm (no code allowed)

Before writing any code:

1. Clarify the goal: "What problem does this solve? What does success look like?"
2. Quick context scan: check project structure, tech stack, and key config files
   to inform the Practical Fit perspective
3. Build the Task Profile (`orchestration.md` Step 1), including Ensemble Affinity
4. If ensemble active (Affinity MEDIUM or HIGH):
   - Launch Codex **brainstorm** ensemble point (background) per `ensemble-protocol.md`
5. Follow the Evidence-Based Choice Protocol (`choice-protocol.md`):
   - **Research**: Search official docs, standards, and community consensus before proposing options
   - **Compare**: Evaluate 2+ approaches across the five perspectives (Essence, Foundation, Standards, Best Practice, Practical Fit)
   - **Recommend**: Always provide a recommended option with confidence level, decisive factors, and conditions to choose differently
6. If ensemble was launched (Affinity MEDIUM or HIGH):
   - Collect Codex brainstorm result (wait for background notification if not yet complete)
   - Synthesize per `ensemble-protocol.md`
   - Add any Codex-proposed approaches that Claude did not consider
   - Elevate confidence for approaches both models recommended
7. **Wait for user to choose a direction** — do not proceed without explicit approval

If the user says "just do it" or "your call", run the protocol but present only the recommendation
(skip the interactive choice step) and confirm before proceeding.

---

## Phase 2: Explore Codebase

Follow `orchestration.md`, targeting Analysis Agents for this feature's scope and layers.

If ensemble active (Affinity MEDIUM or HIGH):
- Launch Codex **explore** ensemble point (background) simultaneously with agent dispatch

Launch all selected agents in parallel (single message, multiple Agent calls).

After agents return:
1. If ensemble was launched (Affinity MEDIUM or HIGH):
   - Collect Codex explore result
   - Synthesize: merge Claude agent findings + Codex findings, label unique discoveries by source
2. Read the key files identified
3. Summarize: existing patterns, reusable components, integration points
4. Follow the Presentation Mode Protocol (`presentation-protocol.md`) before presenting.
5. Present unified findings to user

---

## Phase 3: Plan and Verify

Create a structured implementation plan:

1. Decompose into tasks — each independently executable with a clear completion criterion
2. Order by dependencies
3. If ensemble active (Affinity MEDIUM or HIGH):
   - Launch Codex **plan-verify** ensemble point (background) with Claude's draft plan as input
   - Collect Codex verification result
   - Synthesize: incorporate valid gaps, adjust ordering, flag disagreements
4. Follow the Presentation Mode Protocol (`presentation-protocol.md`) before presenting.
5. Present the unified final plan to user for approval
6. **Wait for approval** before proceeding to implementation

Use TodoWrite to register approved tasks for progress tracking.

---

## Phase 4: Implement

Execute the plan task by task:

1. For each task, follow the TDD cycle (see TDD Rules in `CLAUDE.md`)
2. If no test framework, implement directly but verify each task manually
3. Mark each task as completed in TodoWrite as you go
4. If a task reveals the plan needs adjustment, pause and discuss with user

---

## Phase 5: Review

Follow `orchestration.md`, targeting Review Agents for this implementation's scope and risk areas.

Launch all selected reviewers in parallel (single message, multiple Agent calls).

If ensemble active (all affinity levels — including LOW):
- Simultaneously launch Codex **review** ensemble point (background)
  with `--scope working-tree`

After agents return:
1. Collect Codex review result
2. Synthesize: deduplicate findings, unify severity, label sources per `ensemble-protocol.md`
3. Follow the Presentation Mode Protocol (`presentation-protocol.md`) before presenting.
4. Present unified review report to user
5. Fix CRITICAL issues; discuss SUGGESTION items with user

---

## Phase 6: Commit

Create a commit with this message format:

```
feat(scope): [one-line description]
```

If the changes warrant a PR, ask the user whether to create one.

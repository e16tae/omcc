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
2. Propose 2-3 approaches with tradeoffs for each
3. **Wait for user to choose a direction** — do not proceed without explicit approval

If the user says "just do it" or "your call", state your recommendation with reasoning and confirm.

---

## Phase 2: Explore Codebase

Launch 2 agents in parallel to understand the relevant codebase:

- **architecture-mapper agent**: Map the structure, layers, and entry points related to this feature
- **flow-tracer agent**: Trace the most relevant existing flow end-to-end

After agents return:
1. Read the key files they identified
2. Summarize: existing patterns, reusable components, integration points
3. Present findings to user

---

## Phase 3: Plan

Create a structured implementation plan:

1. Decompose into tasks — each independently executable with a clear completion criterion
2. Order by dependencies
3. Present the plan to user for approval
4. **Wait for approval** before proceeding to implementation

Use TodoWrite to register approved tasks for progress tracking.

---

## Phase 4: Design Verification (optional — Codex)

After the plan is approved, offer cross-model verification:

"Want Codex to challenge this design? (`/codex:adversarial-review`)"

- If user accepts → they run `/codex:adversarial-review` and share results
- If user declines → proceed to Phase 5
- Do not run it automatically — let the user decide and invoke it

---

## Phase 5: Implement

Execute the plan task by task:

1. For each task, follow the TDD cycle when a test framework is available:
   - RED: Write a failing test first
   - GREEN: Minimal implementation to pass
   - REFACTOR: Clean up while tests stay green
2. If no test framework, implement directly but verify each task manually
3. Mark each task as completed in TodoWrite as you go
4. If a task reveals the plan needs adjustment, pause and discuss with user

---

## Phase 6: Review

Launch 3 reviewer agents in parallel (single message, 3 Agent calls):

- **Reviewer 1 (correctness)**: Bugs, edge cases, logic errors, missing error handling
- **Reviewer 2 (simplicity)**: Unnecessary complexity, duplication, over-abstraction
- **Reviewer 3 (conventions)**: Project pattern consistency, naming, style

After agents return:
1. Merge findings, remove duplicates, sort by severity
2. Present consolidated review to user
3. Fix CRITICAL issues; discuss SUGGESTION items with user

Then offer Codex review:

"Want a second opinion from Codex? (`/codex:review`)"

- If user accepts → they run `/codex:review` and share results
- If user declines → proceed to Phase 7

---

## Phase 7: Commit

Create a commit with this message format:

```
feat(scope): [one-line description]
```

If the changes warrant a PR, ask the user whether to create one.

---
name: plan
description: Decomposes work into structured, dependency-ordered tasks with clear completion criteria. Make sure to use this skill whenever the user asks to plan work, break down a task, figure out implementation steps, or organize a large change — even if they just say "how do I start" or "what should I do first". Trigger phrases include "plan this", "how should I approach this", "break this down", "what are the steps", "where do I start", "implementation plan", "task breakdown".
---

# Structured Planning

Decompose a goal into structured, ordered tasks with clear completion criteria.

## When auto-activated (without /start command)

### Step 1: Understand the goal

1. Clarify what needs to be accomplished
2. If there is codebase context from a prior explore, use it
3. Identify constraints and requirements

### Step 2: Decompose

Break the goal into tasks following these principles:

1. **Each task is independently executable** — one focused unit of work
2. **Each task has a clear completion criterion** — "done" is unambiguous
3. **Dependencies are explicit** — which tasks must finish before others can start
4. **No task is too large** — if a task feels complex, split it further

### Step 3: Order by dependencies

1. Identify which tasks block others
2. Arrange in dependency order
3. Group independent tasks that can run in parallel
4. If all tasks are independent, present as a flat list without Phase groupings
   and note that tasks can be executed in any order

### Step 4: Present for approval

Follow the Presentation Mode Protocol (`presentation-protocol.md`) before presenting.

Output format:

```
## Plan: [goal]

### Phase 1: [name]
- [ ] Task 1.1: [description]
      Done when: [completion criterion]
- [ ] Task 1.2: [description]
      Done when: [completion criterion]
      Depends on: 1.1

### Phase 2: [name]
- [ ] Task 2.1: [description]
      Done when: [completion criterion]
      Depends on: 1.2

Estimated scope: [small / medium / large]
```

Wait for the user to approve, modify, or reject the plan before proceeding.

If the user rejects the plan, ask what needs to change:
- If the issue is task decomposition (plan-level): revise the plan using the same
  explore data.
- If the issue is the overall approach (brainstorm-level): return to Phase 1
  (Brainstorm) with the rejection reason as new context.

Register approved tasks with TaskCreate for progress tracking.

### Native Plan mode compatibility

Claude Code's native Plan mode (`EnterPlanMode` / `ExitPlanMode`) enforces
read-only operation during research/planning. Users who want hard enforcement
in addition to this skill's approval gates can enter Plan mode manually
before invoking the skill; the skill itself does not change session mode
state, since mode is a user-controlled layer.

---

## When invoked by command (/start)

Full planning with ensemble verification.

### Step 1: Create the plan

Follow the auto-activated steps (Understand → Decompose → Order) using context
from the preceding brainstorm and explore phases.

### Step 2: Ensemble verification (if Affinity MEDIUM or HIGH)

1. Launch Codex **plan-verify** ensemble point (background) per `ensemble-protocol.md`
   with Claude's draft plan as input
2. Collect Codex verification result
3. Synthesize: incorporate valid gaps, adjust ordering, flag disagreements

### Step 3: Present for approval

Follow the Presentation Mode Protocol (`presentation-protocol.md`) before presenting.
Present the unified final plan to user for approval.

**Wait for approval** before proceeding to implementation.

If the user rejects the plan, ask what needs to change:
- If the issue is task decomposition (plan-level): revise the plan using the same
  explore data.
- If the issue is the overall approach (brainstorm-level): return to Phase 1
  (Brainstorm) with the rejection reason as new context.

Register approved tasks with TaskCreate for progress tracking.

### State write (when invoked by /start)

After approval and TaskCreate registration, write the plan snapshot to
the invoking command's target workflow file per `continuity-protocol.md`
Phase-boundary Write Rules (fields: `tasks` and, in deliverable mode,
`plan.deliverables`). Under hierarchical workflows the target is the
specific node the command is driving (root or a shard), not
ambiguously "the active workflow".

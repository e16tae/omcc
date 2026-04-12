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
Register approved tasks with TodoWrite for progress tracking.

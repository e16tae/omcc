---
description: Systematic feature development — think, explore, plan, build, review
argument-hint: Feature description or goal
---

# Start

$ARGUMENTS

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

---

## Phase 4: Implement

Execute the plan task by task:

1. For each task, follow the TDD cycle (see TDD Rules in `CLAUDE.md`)
2. If no test framework, implement directly but verify each task manually
3. Mark each task as completed in TodoWrite as you go
4. If a task reveals the plan needs adjustment, pause and discuss with user

---

## Phase 5: Review

Follow the parallel-review skill's command-invoked mode (`skills/parallel-review/SKILL.md`).

---

## Phase 6: Resolve Findings

If Phase 5 produced findings, address them before committing:

1. For each finding, evaluate whether the fix approach involves a meaningful choice
   between 2+ alternatives. If so, follow the brainstorm skill to compare approaches
   and wait for user approval before applying.
2. If the fix is straightforward (single clear approach), present the approach and
   confirm with the user before applying.
3. After each fix, verify (run relevant tests or grep for the fixed pattern).
4. After all findings are resolved or explicitly deferred by the user, proceed to commit.

Do not proceed to commit until the user confirms that findings are resolved.

---

## Phase 7: Commit

Create a commit with this message format:

```
feat(scope): [one-line description]
```

If the changes warrant a PR, ask the user whether to create one.

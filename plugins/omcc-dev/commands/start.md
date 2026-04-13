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

### Design Document

After plan approval, create .claude/design-context.md (not committed to git)
capturing the full context for subsequent phases:

```markdown
# Design Context

## Decision (from Brainstorm)
- Chosen: [selected approach]
- Why: [full rationale]
- Why not alternatives: [reasons for each rejected approach]
- User constraints: [stated priorities and constraints]

## Architecture (from Explore)
- Key patterns: [patterns to follow and why]
- Integration points: [existing code touchpoints]
- Pitfalls: [what to avoid and why]

## Plan
- [full task list with dependencies and completion criteria]

## Deliverable Progress
- [ ] [deliverable or task grouping status]
```

Present the Design Document to the user for review — "Does this accurately
capture the decision context?"

### Deliverable assessment

Evaluate whether the plan should be executed as a single pass or in deliverables:

> "Can the full implementation be completed in one pass while maintaining context
> quality for all tasks?"

- YES → single pass (maximum coherence)
- NO → group tasks into independently completable deliverables, present grouping
  to user for approval

This is a quality judgment, not a cost optimization. Present the assessment
and reasoning to the user for final decision.

---

## Phase 4: Implement

### Single pass mode

Execute the plan task by task:

1. For each task, follow the TDD cycle (see TDD Rules in `CLAUDE.md`)
2. If no test framework, implement directly but verify each task manually
3. Mark each task as completed in TodoWrite as you go
4. If a task reveals the plan needs adjustment — see Plan Adjustment below

### Deliverable mode

For each deliverable:

1. **Re-contextualize**: Read .claude/design-context.md and the code files
   this deliverable depends on. This restores full context regardless of
   conversation compression.
2. **Implement**: Execute tasks in this deliverable following TDD cycle
3. **Review**: Follow Phase 5 (full parallel-review + Codex)
4. **Resolve**: Follow Phase 6 (Resolve & Converge)
5. **Commit**: Commit this deliverable
6. **Update**: Update Design Document (progress status + any new discoveries)

After all deliverables: proceed to Cross-deliverable Final Review (Phase 5b).

### Plan Adjustment

If a task reveals the plan needs adjustment, assess the impact:

1. **Remaining tasks only affected** (e.g., function name differs from expected):
   Report to user, adjust remaining task descriptions inline. Update Design Document.
2. **Completed code also affected** (e.g., planned API doesn't support required feature):
   Report to user with impact assessment. Re-run plan skill for remaining tasks.
   Update Design Document.
3. **Brainstorm decision itself invalidated** (e.g., chosen approach is infeasible):
   Report to user with evidence. Return to Phase 1 (Brainstorm) with the
   discovery as new context. Update Design Document.

In all cases: present the situation and proposed response to the user for approval.

---

## Phase 5: Review

Follow the parallel-review skill's command-invoked mode (`skills/parallel-review/SKILL.md`).

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

Delete .claude/design-context.md after commit/PR is complete.
If a previous Design Document exists at the start of a new `/start` invocation,
ask the user whether to delete it (leftover from a prior session).

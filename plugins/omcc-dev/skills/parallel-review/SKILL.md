---
name: parallel-review
description: Reviews code changes from multiple independent perspectives (correctness, simplicity, conventions). Make sure to use this skill whenever the user asks for code review, quality feedback, or wants their changes checked — even if they just say "how does this look" or "any issues". Trigger phrases include "review this", "check my code", "code review", "quality check", "how does this look", "any issues with this", "review my changes", "check for problems".
---

# Multi-Perspective Parallel Review

Review code changes from multiple independent perspectives to catch what single-perspective review misses.

## When auto-activated (without /start or /audit command)

Provide a structured multi-perspective review. Since this is auto-activated, work within the current context.

### Step 1: Identify what to review

1. Run `git diff --stat` to see the scope of changes
2. If no uncommitted changes, ask the user what to review
3. Determine if this is a small change (1-2 files) or large change (3+ files)

### Step 2: Determine review perspectives

Follow `orchestration.md`, targeting Review Agents based on the scope of changes and risk areas.
Evaluate the changes independently from each selected perspective.

### Step 3: Synthesize

1. Merge findings from all perspectives
2. Remove duplicates
3. Sort by severity (CRITICAL first, SUGGESTION last)
4. Follow the Presentation Mode Protocol (`presentation-protocol.md`) before presenting.
5. Present the consolidated review to the user

### Output format

```
## Review Summary
[1-2 sentence overall assessment]

## Critical Issues
- [file:line] [perspective] — [description]

## Suggestions
- [file:line] [perspective] — [description]

## Looks Good
- [what was done well]
```

---

## When invoked by command (/start)

Full review with agent spawning and ensemble coordination.

### Step 1: Spawn review agents

Follow `orchestration.md`, targeting Review Agents based on the implementation's
scope and risk areas.
Launch all selected reviewers in parallel (single message, multiple Agent calls).

### Step 2: Ensemble coordination (all affinity levels — including LOW)

Simultaneously with agent dispatch:
- Launch Codex **review** ensemble point (background) per `ensemble-protocol.md`
  with `--scope working-tree`

### Step 3: Synthesize

After agents return:
1. Collect Codex review result
2. Deduplicate findings across all sources
3. Unify severity ratings
4. Label sources per `ensemble-protocol.md`

### Step 4: Present

Follow the Presentation Mode Protocol (`presentation-protocol.md`) before presenting.
Present unified review findings to user.

Do not fix issues in this skill. Fixing is handled by the invoking command
(e.g., /start Phase 6: Resolve Findings).

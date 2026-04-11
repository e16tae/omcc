---
name: parallel-review
description: Reviews code changes from multiple independent perspectives (correctness, simplicity, conventions). Make sure to use this skill whenever the user asks for code review, quality feedback, or wants their changes checked — even if they just say "how does this look" or "any issues". Trigger phrases include "리뷰", "코드 검토", "확인해줘", "괜찮아?", "review this", "check my code", "code review", "quality check", "how does this look", "any issues with this".
---

# Multi-Perspective Parallel Review

Review code changes from multiple independent perspectives to catch what single-perspective review misses.

## When auto-activated (without /start or /audit command)

Provide a structured multi-perspective review. Since this is auto-activated, work within the current context.

### Step 1: Identify what to review

1. Run `git diff --stat` to see the scope of changes
2. If no uncommitted changes, ask the user what to review
3. Determine if this is a small change (1-2 files) or large change (3+ files)

### Step 2: Review from three perspectives

For each perspective, evaluate the changes independently:

**Correctness**: Are there bugs, edge cases, logic errors, missing error handling, or null risks? What inputs could produce wrong results?

**Simplicity**: Is anything unnecessarily complex, duplicated, or over-abstracted? Could anything be simpler while achieving the same result?

**Conventions**: Does the code match existing project patterns, naming, file organization, and error handling style? Check CLAUDE.md for project rules.

### Step 3: Synthesize

1. Merge findings from all three perspectives
2. Remove duplicates
3. Sort by severity (CRITICAL first, SUGGESTION last)
4. Present the consolidated review to the user

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

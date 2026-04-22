---
name: parallel-review
description: Reviews code changes from multiple independent perspectives (correctness, simplicity, conventions). Make sure to use this skill whenever the user asks for code review, quality feedback, or wants their changes checked — even if they just say "how does this look" or "any issues". Trigger phrases include "review this", "check my code", "code review", "quality check", "how does this look", "any issues with this", "review my changes", "check for problems".
---

# Multi-Perspective Parallel Review

Review code changes from multiple independent perspectives to catch what single-perspective review misses.

## When auto-activated (without /start or /audit command)

Lightweight in-context review — Claude evaluates each selected perspective
directly in the current conversation (no subagent spawning), so Claude's own
git tools cover the diff.

### Step 1: Identify what to review

Collect the full change set (Claude uses its Bash tool directly):
- `git diff --stat` for scope overview
- `git diff --cached` + `git diff` for staged and unstaged hunks
  (together, these handle partially staged files that `git diff HEAD` can mask)
- `git ls-files --others --exclude-standard` + `Read` each untracked file

If there are no uncommitted changes, ask the user what to review.

### Step 2: Determine review perspectives

Select review perspectives from `agent-taxonomy.md` based on the scope of
changes and risk areas. Evaluate each perspective **directly in context**
without spawning subagents (auto-activated mode is meant to be lightweight;
the full parallel-agent workflow runs under `/start` or `/audit`).

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

### Step 1: Collect change context and spawn review agents

Reviewer subagents have read-only file tools (`Read`, `Glob`, `Grep`) and do
not run `git` themselves. The orchestrator collects the change set first and
embeds it in each reviewer's mission:

1. Collect the full change set for review context. For a single commit-pending
   review:
   - `git diff --cached` — staged hunks (index vs HEAD)
   - `git diff` — unstaged hunks (worktree vs index). Collecting both
     separately captures partially-staged files that `git diff HEAD` can mask
     (staged version is hidden when a later unstaged edit exists in the same file).
   - `git ls-files --others --exclude-standard` — untracked new files
   - Read each untracked file with the `Read` tool so its contents are part
     of the review context.
   For an entire-branch review:
   - `git diff [base]...HEAD` — the full branch diff. Note any untracked
     files separately; they should typically be committed before merge.
2. Follow `orchestration.md`, targeting Review Agents based on the
   implementation's scope and risk areas.
3. Include the relevant diff hunks and file paths in each reviewer's mission
   prompt, so the agent can evaluate before/after behavior rather than only
   current file contents.
4. Launch all selected reviewers in parallel (single message, multiple Agent calls).

### Step 2: Ensemble coordination

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

### State write (when invoked by /start or /audit)

After synthesis, the invoking command writes the review result into the
active workflow file per `continuity-protocol.md` Phase-boundary Write
Rules. This skill does not write state itself — it hands findings to
the command, which owns the write.

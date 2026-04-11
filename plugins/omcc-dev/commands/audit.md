---
description: Systematic codebase audit — parallel scanning across categories with structured report
argument-hint: Audit scope (e.g., "security", "performance", "full")
---

# Audit

$ARGUMENTS

---

## Phase 1: Determine Scope

If $ARGUMENTS specifies the audit type, use it directly. Otherwise, help the user decide:

1. **Audit type**: security / performance / code quality / tech debt / full (all of the above)
2. **Target scope**: entire codebase / specific directory or module

When the user is unsure, gather minimal context first (e.g., recent git log, directory structure,
project config) then explain what each audit type covers and recommend the most appropriate type
and scope. If context is insufficient, default to "full". State the reasoning.

---

## Phase 2: Parallel Scan

Follow the Dynamic Agent Orchestration process (`orchestration.md`):

1. **Task Profiling**: Analyze the audit target — layers present, potential risk areas, codebase size and complexity

2. **Agent Composition**: Select from Review Agents in `agent-taxonomy.md` based on audit type

   ### If "full" audit:
   Always include the baseline set: **security, performance, simplicity, conventions, debt**.
   These cannot be excluded — "full" guarantees complete coverage of these categories.
   Then use orchestration to determine if additional specialist perspectives
   (correctness, concurrency, api-design, error-resilience, migration-safety) are warranted based on the codebase's characteristics.

   ### If specific type:
   Decompose the chosen type into distinct sub-aspects and assign one agent per sub-aspect.
   Example: "security" audit → separate missions for auth/authz, input validation, secrets management.

3. **Mission Briefing**: Give each agent a concrete audit mission specific to this codebase
4. Launch all selected agents in parallel (single message, multiple Agent calls)

---

## Phase 3: Integrate Built-in Results

If the audit includes security:
- Also mention that the user can run `/security-review` (Claude Code built-in command) for git-diff-based security analysis
- This is NOT an omcc-dev command — it is a native Claude Code feature
- Integrate those results if the user provides them

---

## Phase 4: Codex Cross-Audit (optional)

After scan results are collected, offer:

"Want Codex to challenge the codebase design? (`/codex:adversarial-review`)"

- If user accepts → they run `/codex:adversarial-review` and share results
- If user declines → proceed to Phase 5
- Do not run it automatically

---

## Phase 5: Generate Report

Synthesize all findings into a structured report:

```markdown
# Audit Report — [date]

## Summary
- Critical: N issues
- High: N issues
- Medium: N issues
- Low: N issues

## Critical Issues
| Location | Category | Description | Recommended Action |
|----------|----------|-------------|-------------------|
| file:line | security | [description] | [action] |

## High Issues
| Location | Category | Description | Recommended Action |
|----------|----------|-------------|-------------------|

## Medium Issues
...

## Low Issues
...

## Positive Observations
- [things done well]
```

Present the report to the user. Offer to write it to a file if they want a persistent record.

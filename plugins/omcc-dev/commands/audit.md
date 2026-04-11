---
description: Systematic codebase audit — parallel scanning across categories with structured report
argument-hint: Audit scope (e.g., "security", "performance", "full")
---

# Audit

$ARGUMENTS

---

## Phase 1: Determine Scope

If $ARGUMENTS specifies the audit type, use it directly. Otherwise, ask the user:

1. **Audit type**: security / performance / code quality / tech debt / full (all of the above)
2. **Target scope**: entire codebase / specific directory or module

---

## Phase 2: Parallel Scan

Launch reviewer agents in parallel based on audit type:

### If "full" audit (4 agents):

Launch 4 reviewer agents in parallel (single message, 4 Agent calls):

- **Reviewer 1 (security)**: OWASP Top 10 — injection, auth, sensitive data exposure, XXE, access control. Also check for hardcoded secrets, unsafe dependencies.
- **Reviewer 2 (performance)**: N+1 queries, unnecessary recomputation, memory leak patterns, large payloads, missing indexes.
- **Reviewer 3 (code quality)**: Duplication, excessive complexity, unused code, inconsistent patterns.
- **Reviewer 4 (tech debt)**: TODO/FIXME/HACK comments, deprecated API usage, missing test coverage areas.

### If specific type (3 agents):

Launch 3 reviewer agents focused on the chosen type, each examining a different aspect of that category.

---

## Phase 3: Integrate Built-in Results

If the audit includes security:
- Also mention that the user can run `/security-review` for git-diff-based security analysis
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

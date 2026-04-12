---
description: Systematic codebase audit — parallel scanning across categories with structured report
argument-hint: Audit scope (e.g., "security", "performance", "full")
---

# Audit

$ARGUMENTS

---

## Phase 1: Determine Scope

If $ARGUMENTS specifies the audit type, use it directly. Otherwise:

1. Gather minimal context (recent git log, directory structure, project config)
2. Follow the brainstorm skill's command-invoked mode (`skills/brainstorm/SKILL.md`)
   to compare audit types and recommend the most appropriate type and scope
3. If context is insufficient, default to "full". State the reasoning.

**Audit types**: security / performance / code quality / tech debt / full (all of the above)
**Target scope**: entire codebase / specific directory or module

Build the Task Profile (`orchestration.md` Step 1), including Ensemble Affinity.

---

## Phase 2: Parallel Scan

Follow `orchestration.md`, targeting Review Agents based on audit type.

### Agent selection rules for audits

**Full audit**: Always include the baseline set: **security, performance, simplicity, conventions, debt**.
These cannot be excluded — "full" guarantees complete coverage of these categories.
Then use orchestration to determine if additional specialist perspectives
(correctness, concurrency, api-design, error-resilience, migration-safety) are warranted based on the codebase's characteristics.

**Specific type**: Decompose the chosen type into distinct sub-aspects and assign one agent per sub-aspect.
Example: "security" audit → separate missions for auth/authz, input validation, secrets management.

Launch all selected agents in parallel (single message, multiple Agent calls).

If ensemble active (Affinity MEDIUM or HIGH):
- Simultaneously launch Codex **audit-scan** ensemble point (background) per `ensemble-protocol.md`
- Focus text is derived from the audit type per `ensemble-protocol.md` audit-scan definition

---

## Phase 3: Integrate Built-in Results

If the audit includes security:
- Mention that the user can run `/security-review` (Claude Code built-in command)
  for git-diff-based security analysis
- This is NOT an omcc-dev command — it is a native Claude Code feature
- Integrate those results if the user provides them

---

## Phase 4: Generate Report

Collect Codex audit-scan result from Phase 2 background task (if ensemble was launched).

If ensemble active (Affinity MEDIUM or HIGH — launched in Phase 2):
- Synthesize Claude agent findings + Codex adversarial-review findings per `ensemble-protocol.md`
- Deduplicate by location
- Unify severity ratings (elevate confidence when both sides agree)
- Source-label all findings (Claude / Codex / Both)

If ensemble not active (LOW affinity):
- Launch Codex **audit-scan** ensemble point now (review-phase ensemble for LOW affinity)
- Collect and synthesize into the report

Follow the Presentation Mode Protocol (`presentation-protocol.md`) before presenting.

Synthesize all findings into a structured report:

```markdown
# Audit Report — [date]

## Summary
- Critical: N issues
- High: N issues
- Medium: N issues
- Low: N issues

## Critical Issues
| Location | Category | Source | Description | Recommended Action |
|----------|----------|--------|-------------|-------------------|
| file:line | security | [Both] | [description] | [action] |

## High Issues
| Location | Category | Source | Description | Recommended Action |
|----------|----------|--------|-------------|-------------------|

## Medium Issues
...

## Low Issues
...

## Positive Observations
- [things done well]
```

Present the report to the user. Offer to write it to a file if they want a persistent record.

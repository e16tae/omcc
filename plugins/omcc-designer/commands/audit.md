---
description: Design quality audit — evaluation with remediation discussion
argument-hint: Design input + optional scope (e.g., "./poster.png", "accessibility", "full")
---

# Audit

$ARGUMENTS

Use `TaskCreate` and `TaskUpdate` to track audit progress.

---

## Audit Pipeline

Follow the design-evaluation skill's command-invoked mode (`skills/design-evaluation/SKILL.md`).

The skill handles scope selection, input analysis, multi-perspective
evaluation, findings presentation (organized by severity), and structured
per-finding remediation discussion (Issue / Alternatives / Decision).

---

## Completion

After all findings are reviewed, output the summary table
(finding × decision) and, if any findings are marked "fix now", offer to
revise the specification or transition to `/omcc-designer:start` for redesign.

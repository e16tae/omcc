---
description: Research a topic — produce a durable cited research brief
argument-hint: Research topic or question
---

# Research

$ARGUMENTS

Use `TaskCreate` and `TaskUpdate` to track progress.

Follow the research skill's command-invoked mode (`skills/research/SKILL.md`).
The skill handles topic intake, research execution, synthesis, and output
assembly per its referenced specs.

---

## Completion

Output depends on whether the brief was actually written:

- **If saved** (overwrite or distinct-directory branch): "✓ Research brief
  saved." plus the saved file path under `./output/YYYY-MM-DD_<topic-slug>/`.
  Offer to: adjust scope and re-run, deepen specific findings, or export to a
  different location.
- **If aborted** (existing-directory abort branch): "ℹ Brief presented inline
  without saving (existing-directory abort)." No path. Offer to save under a
  distinct directory on user confirmation.

Do NOT print the "✓ saved" message when no file was written.

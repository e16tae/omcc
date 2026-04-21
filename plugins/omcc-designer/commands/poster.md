---
description: Poster design specification — uses existing brief or runs full pipeline
argument-hint: Brief file path or design request description
---

# Poster

$ARGUMENTS

Use `TaskCreate` and `TaskUpdate` to track progress.

---

## Poster Design

Follow the poster skill's command-invoked mode (`skills/poster/SKILL.md`).

The poster skill handles input detection, brief validation, and full-pipeline
fallback internally. This command simply delegates.

---

## Completion

After the poster spec is saved, output: "✓ Poster specification complete."
with the poster_spec.md path. Offer to adjust layout, swap AI-tool prompts,
or regenerate specific zones.

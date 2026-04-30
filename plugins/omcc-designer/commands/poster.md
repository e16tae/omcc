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

## Optional chain — poster-render

After the poster spec is saved, unconditionally dispatch the
`poster-render` skill (`skills/poster-render/SKILL.md`) as a
chain-tail. poster-render owns the full dispatch logic: pre-flight
(codex plugin + runtime checks + output-dir writability), one-time
Tool dispatch decision (user consent prompt that discloses the
planned codex call count regardless of brief field value), and
graceful-skip path when codex is unavailable or the user declines.
This command does not duplicate the trigger conditions — see
poster-render's SKILL.md for the canonical spec.

`/start` Phase 4 dispatches poster-render the same way, so `/start`
and `/poster` produce identical chain behavior for any given brief.

---

## Completion

Output: "✓ Poster pipeline complete." with the saved file paths
(poster_spec.md, and — when the chain ran — the rendered zone images
under the project directory). Offer to adjust layout, swap AI-tool
prompts, or regenerate specific zones. If `poster-render` ran, also
offer to re-render specific zones.

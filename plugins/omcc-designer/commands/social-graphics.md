---
description: Social graphics specification — multi-variant (Instagram post / story / YouTube thumbnail) using existing brief or full pipeline
argument-hint: Brief file path or design request description (e.g., "Instagram post and YouTube thumbnail for next week's launch")
---

# Social Graphics

$ARGUMENTS

Use `TaskCreate` and `TaskUpdate` to track progress.

---

## Social Graphics Design

Follow the social-graphics skill's command-invoked mode
(`skills/social-graphics/SKILL.md`).

The social-graphics skill handles input detection, brief validation
(including Variants block / whitelist / collision rules), and
full-pipeline fallback internally. This command simply delegates.

---

## Optional chain — social-graphics-render

After the social_graphics_spec.md is saved, unconditionally dispatch
the `social-graphics-render` skill
(`skills/social-graphics-render/SKILL.md`) as a chain-tail.
social-graphics-render owns the full dispatch logic: pre-flight
(codex plugin + runtime checks + output-dir writability), one-time
Tool dispatch decision (user consent prompt that discloses the
planned codex call count — Σ zones across all variants — regardless
of brief field value), the variant-outer / zone-inner 2D loop,
dimension validation, and graceful-skip path when codex is
unavailable or the user declines. This command does not duplicate
the trigger conditions — see social-graphics-render's SKILL.md for
the canonical spec.

`/start` Phase 4 dispatches social-graphics-render the same way,
so `/start` and `/social-graphics` produce identical chain
behavior for any given brief.

---

## Completion

Output: "✓ Social graphics pipeline complete." with the saved file
paths (social_graphics_spec.md, and — when the chain ran — the
per-variant rendered zone images under the project directory).
Offer to adjust layout, swap AI-tool prompts, or regenerate specific
(variant, zone) pairs. If `social-graphics-render` ran, also offer
to re-render specific (variant, zone) pairs.

---
description: Full design pipeline — analysis, consultation interview, brief generation, domain-specific output (poster / social-graphics / etc.)
argument-hint: Design request description (e.g., "conference poster for a tech event next month" or "Instagram post and YouTube thumbnail for next week's launch")
---

# Start

$ARGUMENTS

Use `TaskCreate` to register each phase and `TaskUpdate` to mark progress as
the pipeline advances.

---

## Phase 1: Design Analysis

Follow the design-analysis skill's command-invoked mode (`skills/design-analysis/SKILL.md`).

Analysis results are kept internally and not exposed to the user.

---

## Phase 2: Design Consultation Interview

Follow the design-interview skill's command-invoked mode (`skills/design-interview/SKILL.md`).

Proceed through Step A (project context) > Step B (brand identity) > Step C (visual direction & color) > Step D (content & layout) > Step E (technical requirements).
Get user confirmation after interview completion before proceeding to Phase 3.

---

## Phase 3: Design Brief Generation

Follow the brief-generation skill's command-invoked mode (`skills/brief-generation/SKILL.md`).

Save the design brief to ./output/YYYY-MM-DD_project-name/design_brief.md
(directory naming and sanitization per `skills/brief-generation/references/output-file-rules.md`).

---

## Phase 4: Domain-Specific Output

Read the brief's Target medium field (after alias normalization per
`skills/brief-generation/references/design-brief-spec.md` "Target
medium aliases") and dispatch via the registry below.

| Canonical medium | Domain skill | Spec output filename | Optional chain-tail |
|------------------|--------------|----------------------|---------------------|
| `poster` | `skills/poster/SKILL.md` | poster_spec.md | `skills/poster-render/SKILL.md` |
| `social-graphics` | `skills/social-graphics/SKILL.md` | social_graphics_spec.md (H2 variant sub-blocks) | `skills/social-graphics-render/SKILL.md` |

**Chain-tail dispatch rule**: when the row defines an optional
chain-tail, dispatch it unconditionally after the domain skill
returns. The chain-tail owns its own full dispatch logic
(pre-flight, Tool dispatch decision with user consent, per-zone
or per-variant loop, graceful-skip on codex absence / user
decline) — see its SKILL.md for the canonical spec. This command
does NOT duplicate the trigger conditions.

**Output paths**: all paths are relative to
`./output/YYYY-MM-DD_project-name/` per
`skills/brief-generation/references/output-file-rules.md`.

**Unmapped media**: for any canonical medium not in the table
(`brochure`, `infographic`, `frontend`, etc.), the corresponding
domain skill is not yet available. Inform the user: "The
<medium> domain skill is not yet available. The design brief has
been saved and can be used when the skill is added." End the
pipeline.

**Adding a new domain skill**: append a new row to the registry
table. The four columns are sufficient — chain-tail dispatch and
unmapped-medium fallback work uniformly without bullet-prose
duplication.

---

## Completion

Output: "✓ Design pipeline complete." with the saved file paths
(brief, domain output, and — when a chain-tail render ran — the
rendered zone images under the project directory). Offer to revise
the brief, regenerate the domain output, or start another project.

If a chain-tail render ran (`poster-render` or
`social-graphics-render`), also offer to re-render specific zones
(or, for social-graphics, specific (variant, zone) pairs).

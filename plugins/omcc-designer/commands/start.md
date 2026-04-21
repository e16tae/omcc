---
description: Full design pipeline — analysis, consultation interview, brief generation, poster specification
argument-hint: Design request description (e.g., "conference poster for a tech event next month")
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

Read the brief's Target medium field and dispatch to the matching domain
skill. Currently available domain skills:

- **poster** → follow `skills/poster/SKILL.md`; save to
  ./output/YYYY-MM-DD_project-name/poster_spec.md per output-file-rules.

For any other medium (brochure, infographic, frontend, etc.), the
corresponding domain skill is not yet available. Inform the user: "The
<medium> domain skill is not yet available. The design brief has been saved
and can be used when the skill is added." End the pipeline.

When adding a new domain skill, extend the bullet list above with the
medium-to-skill mapping.

---

## Completion

Output: "✓ Design pipeline complete." with the saved file paths (brief and
any domain output). Offer to revise the brief, regenerate the domain output,
or start another project.

---
description: Full design pipeline — analysis, consultation interview, brief generation, poster specification
argument-hint: Design request description (e.g., "conference poster for a tech event next month")
---

# Start

$ARGUMENTS

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

Save the design brief to ./output/YYYY-MM-DD_project-name/design_brief.md.

---

## Phase 4: Domain-Specific Output

### Medium gate

Check the brief's Target medium field:
- **poster**: Follow the poster skill's command-invoked mode (`skills/poster/SKILL.md`).
  Save poster specification to ./output/YYYY-MM-DD_project-name/poster_spec.md.
- **brochure / infographic / frontend**: These domains are not yet implemented.
  Inform the user: "The [medium] domain skill is not available yet. The design brief
  has been saved and can be used when the domain skill is added."
  Save the brief only and end the pipeline.

Output the pipeline completion message and offer modification assistance.

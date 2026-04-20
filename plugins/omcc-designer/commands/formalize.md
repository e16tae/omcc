---
description: Formalize an existing design into a structured design brief
argument-hint: Image path, Figma URL, or PDF path (e.g., "./poster.png" or "figma.com/design/...")
---

# Formalize

$ARGUMENTS

---

## Phase 1: Design Extraction

Follow the design-extraction skill's command-invoked mode (`skills/design-extraction/SKILL.md`).

Extraction results are kept internally and not exposed to the user.

---

## Phase 2: Design Confirmation Interview

Follow the design-interview skill's command-invoked mode (`skills/design-interview/SKILL.md`).

The interview receives extraction data instead of analysis data.
The design-extraction skill's command-invoked mode defines how the interview
adjusts its behavior for confirmation mode (observation-first language for
high-confidence extractions, exploration for gaps).

Proceed through Step A (project context) > Step B (brand identity) > Step C (visual direction & color) > Step D (content & layout) > Step E (technical requirements).
Get user confirmation after interview completion before proceeding to Phase 3.

---

## Phase 3: Design Brief Generation

Follow the brief-generation skill's command-invoked mode (`skills/brief-generation/SKILL.md`).

Save the design brief to ./output/YYYY-MM-DD_project-name/design_brief.md.

---

Output the pipeline completion message and offer modification assistance.

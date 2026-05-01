---
description: Formalize an existing design into a structured design brief
argument-hint: Image path, Figma URL, or PDF path (e.g., "./poster.png" or "figma.com/design/...")
---

# Formalize

$ARGUMENTS

Use `TaskCreate` to register each phase and `TaskUpdate` to mark progress.

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

Save the design brief to ./output/YYYY-MM-DD_project-name/design_brief.md
(directory naming and sanitization per `skills/brief-generation/references/output-file-rules.md`).

---

## Phase 4: DESIGN.md Emission

After the brief is saved, emit a DESIGN.md artifact (Google design.md
spec, Apache 2.0) as a secondary formalization output. This converts
the visually-extracted brand tokens into a machine-consumable form
for downstream AI coding agents.

**Skip Phase 4 if** the brief's canonical `Target medium` is
`frontend`. In that case, the `frontend` Phase 4 domain skill (invoked
via the suggestion at the Completion step, or directly by
`/start medium=frontend`) is the authoritative DESIGN.md author —
emitting a second copy here would produce two competing files. End
the formalize pipeline at design_brief.md only; let the user opt into
`/omcc-designer:frontend` for the DESIGN.md.

For all other media, perform the emission inline:

1. Apply the mapping contract from
   `skills/design-extraction/references/extraction-guide.md`
   "Mapping extraction to DESIGN.md sections" — five extraction areas
   project to DESIGN.md frontmatter (`colors` / `typography` / optional
   `rounded` / `spacing` / `components`) plus the 8 standard h2 body
   sections in canonical order.
2. Apply the **Hex precision warning** from the same file: surface to
   the user that the extracted hex values are visually estimated
   (unless the input was a Figma file with metadata) and offer a
   confirm-each-color (or confirm-all) gate before promoting them
   into DESIGN.md tokens.
3. Author the body sections from the brief's confirmed values
   (Brand Identity, Color Palette, Typography, Visual Direction
   constraints). Sections without an extraction source — Elevation
   & Depth, Shapes (when `rounded` is not extractable from the
   visual input), Components (no UI component data is extractable
   from non-frontend visual inputs by design), `spacing` (only
   qualitatively described in extraction-guide.md) — are **omitted**
   rather than fabricated. They are NOT mandatory per the spec,
   and authoring them from scratch without source data contradicts
   the formalize pipeline's "observe, don't fabricate" principle.
   If the user wants a fuller design system with these sections,
   suggest they invoke /omcc-designer:frontend on the saved brief
   afterward — that skill handles brand-personality-driven
   derivation with confirmation gates.
4. Save to ./output/YYYY-MM-DD_project-name/DESIGN.md (uppercase per
   the external-standard-exception clause in
   `skills/brief-generation/references/output-file-rules.md`).
5. Report both saved file paths in the completion message.

The DESIGN.md the formalize pipeline produces is therefore a **partial
spec** by design — it captures what the visual input directly evidenced.
For a fuller design system (with Layout / Elevation / Shapes / Components
authored from brand personality), the user can subsequently invoke
`/omcc-designer:frontend` with the saved brief.

---

## Completion

Output: "✓ Brief formalized from the provided input." with the saved
file paths (design_brief.md and, when emitted, DESIGN.md). Suggest the
appropriate domain command for the next step based on the brief's
canonical `Target medium`:

- `Target medium: poster` → `/omcc-designer:poster`
- `Target medium: social-graphics` → `/omcc-designer:social-graphics`
- `Target medium: frontend` → `/omcc-designer:frontend` (this command
  is the authoritative DESIGN.md producer for the frontend medium —
  Phase 4 above was skipped to defer to it)
- Other media (`brochure`, `infographic`) — pipeline ends here
  until their domain commands are implemented.

If the brief's `Target medium` did not normalize to a canonical
value, surface the alias table from
`skills/brief-generation/references/design-brief-spec.md`
"Target medium aliases" and ask the user to repair the brief
before invoking a domain command.

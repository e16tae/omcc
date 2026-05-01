---
description: Frontend design system spec (DESIGN.md, Google design.md) — uses existing brief or runs full pipeline
argument-hint: Brief file path or design request description
---

# Frontend

$ARGUMENTS

Use `TaskCreate` and `TaskUpdate` to track progress.

---

## Frontend Domain

Follow the frontend skill's command-invoked mode (`skills/frontend/SKILL.md`).

The frontend skill handles input detection, brief validation, and full-pipeline
fallback internally. This command simply delegates.

The output artifact is `DESIGN.md` (uppercase per the Google design.md
spec, Apache 2.0; see
`skills/frontend/references/frontend-guide.md`). It contains design
tokens (colors / typography / rounded / spacing / components) as YAML
frontmatter plus 8 standard markdown sections (Overview, Colors,
Typography, Layout, Elevation & Depth, Shapes, Components, Do's and
Don'ts).

---

## No chain-tail

The frontend domain has no chain-tail render skill — `DESIGN.md` is
the terminal artifact. AI coding agents read it directly to generate
brand-consistent UI components. There are no zone PNGs to render.

`/start` Phase 4 dispatches this skill the same way, so `/start
medium=frontend` and `/frontend` produce identical output for any
given brief.

---

## Completion

Output: "✓ Frontend pipeline complete." with the saved file path
(`DESIGN.md`). Surface two follow-up notes:

1. **git-root copy** — to make the design system available to Claude
   Code's general markdown-context loading on the consuming project,
   copy or symlink the saved DESIGN.md to that project's git root.
2. **Optional spec lint (soft dependency)** —
   `npx @google/design.md lint <path>` validates the file against the
   upstream spec. Not invoked automatically; users opt in.

### Optional next step (cross-plugin handoff, suggestion only)

If `/omcc-dev:start` is installed and you want to implement this design
system, run `/omcc-dev:start <DESIGN.md path>`. The omcc-dev plugin's
`/start` recognizes `DESIGN.md` as an artifact handoff and ingests the
spec automatically as initial context for its workflow. This is
informational; no automatic invocation occurs from this command.

Offer to adjust tokens (colors / typography / rounded / spacing /
components), expand the typography scale, or regenerate specific
sections of the body.

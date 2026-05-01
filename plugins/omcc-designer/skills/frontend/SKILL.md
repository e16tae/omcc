---
name: frontend
description: "Generates a Google DESIGN.md spec (Apache 2.0) from a design brief, tailored for AI coding agents to produce brand-consistent frontend UI. Outputs colors/typography/rounded/spacing/components tokens as YAML frontmatter plus 8 standard markdown sections (Overview, Colors, Typography, Layout, Elevation & Depth, Shapes, Components, Do's and Don'ts). Use this skill when the user needs frontend design, web design system, UI design tokens, or a DESIGN.md artifact."
---

# Phase 4: Frontend Domain — DESIGN.md Specification

Generate a `DESIGN.md` artifact conforming to the Google design.md spec
(Apache 2.0; upstream at https://github.com/google-labs-code/design.md).
The output combines machine-readable design tokens (YAML frontmatter)
with human-readable design rationale (8 standard markdown sections).
Coding agents read this file to produce brand-consistent UI components.

The spec mapping rules, token derivation policy, per-section authoring
guide, and the upstream-spec source pin live in
`skills/frontend/references/frontend-guide.md`.

## When auto-activated (without /start or /frontend command)

### Input detection

Determine whether the input is a brief file path or a raw design request:
- **File path**: Exists on disk and contains "# Design Brief" header → brief mode
- **Otherwise** → raw request mode

### Brief mode

1. Read the brief file.
2. Validate per `skills/brief-generation/references/design-brief-spec.md` —
   completeness, medium match (canonical Target medium must equal
   "frontend" after alias normalization per the spec's "Target medium
   aliases" table), and staleness. If the brief's Target medium does
   not normalize to "frontend", inform the user and offer to re-run
   the interview for frontend.
3. **Confirmed field check**: Before using any brief field, verify it
   is not tagged `[unconfirmed]` — see
   `skills/design-interview/references/confirmed-decision-principle.md`.
   If a required field is unconfirmed, ask the user to confirm it
   before proceeding.
4. If validation passes: proceed to Step 1 (Token derivation).
5. If validation fails: inform the user of specific issues and offer
   to run the full pipeline.

### Raw request mode

No brief was provided — direct generation from raw input is not permitted
because `skills/design-interview/references/confirmed-decision-principle.md`
requires user-confirmed decisions before encoding. Run the full pipeline
before producing the DESIGN.md:

1. Invoke the design-analysis skill on the raw request to produce the
   Phase 1 analysis.
2. Invoke the design-interview skill to confirm design decisions.
3. Invoke the brief-generation skill to produce the brief at the
   standard output path per
   `skills/brief-generation/references/output-file-rules.md`.
4. Continue with Steps 1-3 below using the generated brief.

If the user declines the interview, save no files and end; DESIGN.md
generation cannot proceed without confirmed decisions.

### Step 1: Token derivation (YAML frontmatter)

Using the brief's Brand Identity, Color Palette, Typography, and Visual
Direction:

1. **`name`** — required. Use the brief's Project name (or Brand
   name if Brand Identity is more central than the project itself).
2. **`description`** — optional. One-sentence summary of the design
   system's intent, drawn from the brief's Brand personality + Visual
   Direction.Mood keywords.
3. **`colors`** — export the brief's 5 fixed slots verbatim as DESIGN.md
   custom tokens:
   - Primary → `colors.primary`
   - Secondary → `colors.secondary`
   - Accent → `colors.accent`
   - Neutral light → `colors.neutral-light`
   - Neutral dark → `colors.neutral-dark`
   Token *values* are the brief's hex codes verbatim. Per the DESIGN.md
   spec, "Recommended Token Names" (primary/secondary/tertiary/neutral)
   is Non-Normative; consumer behavior accepts any color token name
   with a valid hex value. **Do not** rename Accent → tertiary; the
   brief's semantic role is "accent" and the rename loses that
   information.
4. **`typography`** — export the brief's 3 roles verbatim:
   - Heading font → `typography.heading` (`fontFamily`, `fontWeight`)
   - Body font → `typography.body`
   - Accent font → `typography.accent` (omit if brief says "none")
   The brief does not carry `fontSize`, `lineHeight`, or `letterSpacing`.
   Do not fabricate these values. If the user explicitly asks for a
   richer 9-15-level scale, follow the "Typography expansion" interview
   in `skills/frontend/references/frontend-guide.md` and confirm every derived value with the
   user before writing.
5. **`rounded`** — the brief has no corner-radius data. Derive from
   the brief's Brand personality + Visual Direction (angular / rounded
   / soft) per `skills/frontend/references/frontend-guide.md` "Rounded derivation". **Always
   present the derived scale to the user for confirmation before
   writing.** Never fabricate silently.
6. **`spacing`** — the brief has no spacing scale. Derive a base unit
   (4px or 8px) and a small set (`xs`, `sm`, `md`, `lg`, `xl`) from
   brand personality (dense / spacious) per `skills/frontend/references/frontend-guide.md`
   "Spacing derivation". **Confirm before writing.**
7. **`components`** — derive a minimal default set
   (`button-primary`, `button-primary-hover`, `input-field`, `card`)
   from brand personality. **List the proposed set to the user, ask
   which components to include and which to skip, and confirm each
   component's tokens before writing.** See `skills/frontend/references/frontend-guide.md`
   "Components derivation".

Use token references (`{path.to.token}`) inside `components` to point
at primitives in `colors`/`typography`/`rounded`/`spacing` — never
hard-code values that already exist as tokens. Composite references
(e.g., `{typography.heading}`) are valid only inside `components`.

### Step 2: 8 standard markdown sections (body)

Author the 8 required h2 sections in the canonical order. Aliases
("Brand & Style" for Overview, "Layout & Spacing" for Layout, "Elevation"
for Elevation & Depth) are valid. Do not use a top-level h1 — the spec
treats h1 as a non-parsed title; sections are h2 only. Do not duplicate
section headings; the spec rejects files with duplicate sections.

1. **Overview** (alias: "Brand & Style") — synthesize from brief's
   Project Info (Purpose, Audience, Tone) + Visual Direction (Mood
   keywords, Style reference). Write for an AI coding agent: brand
   personality + emotional tone + holistic look-and-feel.
2. **Colors** — prose rationale for each token defined in the
   frontmatter. Pull the brief's Color Palette.Palette rationale +
   per-role usage guidance (Primary for headlines, Accent sparingly,
   neutrals for surfaces).
3. **Typography** — prose rationale for the type strategy from the
   brief's Font pairing rationale + Visual Direction.
4. **Layout** (alias: "Layout & Spacing") — describe the layout
   strategy. The brief carries no grid system for `frontend` (canvas
   dimensions do not apply to viewport UI); derive a sensible default
   (fluid grid, max-width pattern, base spacing unit) from brand
   personality and confirm with the user.
5. **Elevation & Depth** (alias: "Elevation") — author from scratch.
   The brief has no elevation data. Derive an approach (flat / tonal
   layers / shadows) from brand personality and Visual Direction.
   Confirm with the user.
6. **Shapes** — author from scratch. Reflect the `rounded` token scale
   in prose: which corner radii apply where (cards / buttons / inputs).
7. **Components** — prose guidance per component defined in the
   frontmatter (button states, input states, card variants).
8. **Do's and Don'ts** — convert brief's Visual Direction.Constraints
   into structured do/don't bullets. Add WCAG-AA contrast guidance
   (normal text ≥ 4.5:1) as a default Do entry.

### Step 3: Validate and save

**Hex precision check (extraction-provenance briefs only)**: if the
brief was produced via /omcc-designer:formalize or via /start with an
extraction-driven Phase 1 (visual input — image / Figma / PDF / URL,
without authoritative metadata), the brief's Color Palette hex values
are visually estimated. Per
`skills/design-extraction/references/extraction-guide.md` "Hex precision
warning", before promoting them into a normative DESIGN.md `colors:`
token block, surface to the user:

> The colors carried in the brief were visually estimated from the
> input image. If you have an authoritative brand guide or design
> tokens, please verify the hex values before treating the saved
> DESIGN.md as canonical.

Offer a confirm-each-color (or confirm-all) gate before save. If the
brief came from a text-only design-analysis path (no visual input),
the warning does not apply.

1. **Section order check**: confirm the 8 h2 headings appear in the
   canonical order (aliases counted as their canonical name). The spec
   raises a `section-order` warning on order violations.
2. **Token reference resolution**: every `{path.to.token}` reference
   inside `components` must resolve to a defined token. Inline check
   before save.
3. **No duplicate section headings**: this is the only spec ERROR.
   Verify before save.
4. **Save** to ./output/YYYY-MM-DD_project-name/DESIGN.md —
   directory naming and sanitization per
   `skills/brief-generation/references/output-file-rules.md`. The
   filename is uppercase `DESIGN.md` per the
   external-standard-exception clause in that file.
5. Present the saved file path to the user and surface the
   **git-root copy note**: to make the design system available to
   Claude Code's general markdown-context loading (alongside CLAUDE.md
   / AGENTS.md), copy or symlink the DESIGN.md to the consuming
   project's git root. The omcc-designer output directory is the
   archival source; the git-root copy is the consumer-facing handle.

### Soft dependency: linting

The skill does not invoke any linter. Users who want spec validation
can run, separately:

```
npx @google/design.md lint ./output/YYYY-MM-DD_project-name/DESIGN.md
```

The CLI lives at the npm package `@google/design.md` (Apache 2.0;
upstream at https://github.com/google-labs-code/design.md). It is
**not** an omcc-designer dependency — this is a soft, optional
integration.
For full lint-rule semantics (broken-ref / contrast-ratio /
orphaned-tokens / etc.) see the upstream README.

**Output language**: write the markdown body sections in the user's
request language. The frontmatter keys are normative and stay in
English (`colors`, `typography`, etc., per the spec); token names
follow the same convention. Token *values* (hex codes, dimensions)
are language-neutral.

---

## When invoked by command (/start, /frontend)

### When invoked by /start

The brief is already generated in Phase 3. Skip input detection and
brief mode — proceed directly from Step 1 with the Phase 3 brief.

**Medium gate**: Before Step 1, verify the brief's canonical Target
medium equals "frontend" (after alias normalization per
`skills/brief-generation/references/design-brief-spec.md` "Target
medium aliases"). If not: inform the user that the confirmed medium
is different, the brief has been saved, and the corresponding domain
skill is the one that matches.

### When invoked by /frontend

Full procedure as auto-activated mode: input detection, brief
validation or raw request handling, then Steps 1-3. After saving,
output the completion message including the saved file path, the
linter-CLI hint (soft dependency), and the git-root-copy note.

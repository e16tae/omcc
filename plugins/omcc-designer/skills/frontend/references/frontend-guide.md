# Frontend Domain Guide — DESIGN.md authoring

Authoring rules and token derivation heuristics for the `frontend` skill,
which produces a `DESIGN.md` artifact conforming to the Google design.md
spec.

---

## Upstream spec source

- **Project**: Google design.md (Apache License 2.0)
- **Repository**: https://github.com/google-labs-code/design.md
- **Specification path**: docs/spec.md (upstream repository, not a
  local file)
- **Status**: `version: alpha` — actively evolving. This skill follows
  the current spec at the URL above. Two complementary mechanisms keep
  drift in check:
  1. **Dynamic spec sync (Step 0 of the skill)**: when Node + npx are
     available, the skill calls `npx @google/design.md spec` at
     invocation time to inject the current spec into the working
     context. The skill prefers the freshly-fetched spec over the
     static rules below when they disagree.
  2. **Static authoring rules (this guide)**: the durable fallback
     used when the dynamic fetch is unavailable. Contributors revise
     these rules when upstream behavior breaks them — the rules are
     the offline source of truth.

### NOTICE (Apache 2.0 attribution)

```
This skill embeds authoring rules derived from the Google design.md
specification (https://github.com/google-labs-code/design.md), licensed
under the Apache License, Version 2.0. Copyright (c) Google LLC.
The full upstream license is at:
  https://github.com/google-labs-code/design.md/blob/main/LICENSE
The skill does not redistribute the upstream source; it implements
spec-conforming authoring procedures.
```

When a `DESIGN.md` is generated, the skill does NOT inject this NOTICE
into the output file (the upstream spec does not require per-output
attribution). The NOTICE is required only inside this skill's reference
documentation, which is where the spec influence lives.

---

## Spec at-a-glance

A `DESIGN.md` has two parts:

1. **YAML frontmatter** — design tokens (machine-readable). Optional but
   recommended for the frontend domain (the whole point is enabling AI
   coding agents to consume tokens directly).
2. **Markdown body** — 8 standard h2 sections in fixed order, providing
   human-readable rationale for each token.

### Token namespace (frontmatter)

```yaml
version: alpha            # optional — pin to upstream version label
name: <project name>      # required
description: <one line>   # optional
colors:                   # map<token-name, "#" + hex sRGB>
  <token>: "#RRGGBB"
typography:               # map<token-name, Typography>
  <token>:
    fontFamily: <string>          # only required field per upstream spec
    fontSize: <Dimension>         # optional
    fontWeight: <number>          # optional
    lineHeight: <Dimension | number>  # optional
    letterSpacing: <Dimension>    # optional
    fontFeature: <string>         # optional
    fontVariation: <string>       # optional
rounded:                  # map<scale-level, Dimension>
  <level>: <px|em|rem>
spacing:                  # map<scale-level, Dimension | number>
  <level>: <px|em|rem|number>
components:               # map<component-name, map<property, value | {ref}>>
  <component-name>:
    backgroundColor: "{colors.<token>}"
    textColor: <Color | {colors.<token>}>
    typography: "{typography.<token>}"   # composite ref OK only in components
    rounded: "{rounded.<level>}"
    padding: <Dimension>
    size | height | width: <Dimension>
```

### Section order (h2, fixed)

| # | Canonical name | Aliases (also valid) |
|---|---|---|
| 1 | Overview | "Brand & Style" |
| 2 | Colors | — |
| 3 | Typography | — |
| 4 | Layout | "Layout & Spacing" |
| 5 | Elevation & Depth | "Elevation" |
| 6 | Shapes | — |
| 7 | Components | — |
| 8 | Do's and Don'ts | — |

Sections may be omitted if not relevant, but those present must appear in
this order. The frontend skill SHOULD emit all 8 (omitting any of them
weakens the output for AI coding agents). **Duplicate section headings**
are the only spec ERROR — never produce two h2 with the same canonical
name (or two aliases of the same canonical).

### Consumer behavior for unknown content (informative)

| Case | Behavior | Implication for this skill |
|---|---|---|
| Unknown section heading | preserved | We may add custom h2 sections after #8 if needed |
| Unknown color/typography token name | accepted | Custom token names (e.g., `accent`, `neutral-light`) are spec-valid |
| Unknown component property | accepted with warning | Stick to the documented property set when possible |
| Duplicate h2 heading | ERROR (rejected) | Section-uniqueness is mandatory |

---

## Token derivation policy

### Colors — direct mapping (no fabrication)

The brief carries 5 fixed color slots. Export them verbatim with custom
token names that preserve the brief's semantic role:

| Brief slot | DESIGN.md token | Source |
|---|---|---|
| Primary | `colors.primary` | brief.Color Palette |
| Secondary | `colors.secondary` | brief.Color Palette |
| Accent | `colors.accent` | brief.Color Palette (NOT renamed to `tertiary`) |
| Neutral light | `colors.neutral-light` | brief.Color Palette |
| Neutral dark | `colors.neutral-dark` | brief.Color Palette |

Rationale for keeping `accent` rather than the spec's "Recommended"
`tertiary`: the brief's semantic role is *accent* — a color used
sparingly for emphasis and CTAs. Renaming to `tertiary` (a Material
Design 3 convention for a third-tier palette of equal prominence with
primary/secondary) loses that role information. Per the spec, "Recommended
Token Names" is **Non-Normative** and "unknown color token name —
Accept if value is valid", so `accent` is fully spec-conforming.

Hex values are copied verbatim from the brief. **Do not** introduce new
shades, ramps (e.g., `primary-50`/`primary-90`), or color-space
conversions (e.g., HSL/OKLCH) unless the user explicitly asks for them
during the optional expansion interview below.

### Typography — direct mapping (no fabrication)

The brief carries 3 fixed font roles. Export them with `fontFamily` and
`fontWeight`:

| Brief role | DESIGN.md token | Notes |
|---|---|---|
| Heading font | `typography.heading` | `fontFamily` from brief, `fontWeight` from brief's "weight, style" |
| Body font | `typography.body` | same |
| Accent font | `typography.accent` | omit if brief says "none" |

The brief does **not** carry `fontSize`, `lineHeight`, or `letterSpacing`.
**Do not fabricate these values.** The DESIGN.md spec does not require
them; tokens with only `fontFamily` and `fontWeight` are valid.

### Typography expansion (optional, interview-driven)

If the user explicitly asks for a richer scale (DESIGN.md commonly uses
9-15 typography levels: `headline-display`, `headline-lg`, `headline-md`,
`body-lg`, `body-md`, `body-sm`, `label-lg`, `label-md`, `label-sm`),
follow this interview:

1. **Confirm the scale set**: ask the user which levels are needed.
   Default suggestion: `headline-lg`, `headline-md`, `body-lg`,
   `body-md`, `body-sm`, `label-md` (6 levels). Do not exceed user
   request.
2. **Confirm the base size and ratio**: e.g., "16px body-md with a
   1.25 modular scale" or explicit per-level sizes.
3. **Confirm `lineHeight`**: prefer unitless multipliers (1.5 for body,
   1.2 for headlines) per CSS best practice.
4. **Confirm `letterSpacing`**: usually 0 for body, -0.02em for
   headlines, +0.05em for uppercase labels. Confirm explicitly.
5. **Write only the confirmed levels** to `typography:`. Map
   `typography.heading` → `typography.headline-md` (or whichever heading
   level the user prefers); body / accent similarly. Drop the original
   3-role names if the expanded scale fully replaces them, or keep both
   if the user wants the simple roles as aliases.

Never silently expand without the interview. Brief data is the only
trusted source; everything else must be user-confirmed.

### Rounded derivation

The brief has no corner-radius data. Derive from brand personality:

| Brand personality cue | Rounded scale (suggested) |
|---|---|
| angular, geometric, brutalist, technical | `sm: 0px`, `md: 2px`, `lg: 4px`, `full: 9999px` |
| neutral, professional, modern | `sm: 4px`, `md: 8px`, `lg: 12px`, `full: 9999px` |
| soft, friendly, approachable | `sm: 8px`, `md: 16px`, `lg: 24px`, `full: 9999px` |
| playful, organic | `sm: 12px`, `md: 24px`, `lg: 32px`, `full: 9999px` |

These are starting points. **Always present the derived scale to the
user for confirmation** before writing — wording: "Based on a
[personality keyword] brand, I propose the rounded scale below.
Adjust or confirm?"

Pick a unit consistently within the rounded scale (px, em, or rem are
all valid per the spec; mixing them is allowed but reduces readability).

### Spacing derivation

The brief has no spacing scale. Derive from layout density preference
(usually visible from Visual Direction.Mood keywords + Brand
personality):

| Layout density | Base unit | Scale (suggested) |
|---|---|---|
| dense, compact | 4px | `xs: 2px`, `sm: 4px`, `md: 8px`, `lg: 16px`, `xl: 24px` |
| balanced (default) | 8px | `xs: 4px`, `sm: 8px`, `md: 16px`, `lg: 32px`, `xl: 64px` |
| spacious, airy | 8px | `xs: 8px`, `sm: 16px`, `md: 24px`, `lg: 48px`, `xl: 96px` |

The 8px-base balanced scale is the safe default. **Confirm with the
user** before writing.

### Components derivation

The brief carries no UI component data (image zones in Content Map are
AI-prompt targets, not UI components). Derive a minimal default set:

```yaml
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.neutral-light}"     # or neutral-dark, by contrast
    rounded: "{rounded.md}"
    padding: 12px 24px
  button-primary-hover:
    backgroundColor: "{colors.accent}"      # subtle: same family
  input-field:
    backgroundColor: "{colors.neutral-light}"
    textColor: "{colors.neutral-dark}"
    rounded: "{rounded.sm}"
    padding: 8px 12px
    height: 40px
  card:
    backgroundColor: "{colors.neutral-light}"
    rounded: "{rounded.lg}"
    padding: 24px
```

**List the proposed component set to the user**, ask which to keep,
which to skip, and whether to add other components (e.g., `chip`,
`tooltip`, `nav-item`, `link`). Confirm each component's tokens before
writing.

For variants (hover / active / pressed / disabled), follow the spec:
each variant is a separate component entry with a related-key naming
(`button-primary-hover`, `button-primary-active`). Do not invent
"states" sub-objects — the spec does not support them.

---

## Section authoring guide (8 sections)

For each section, this guide notes (a) the brief field that feeds it,
(b) when to author from scratch, (c) audience-translation reminder.

The audience-translation reminder is critical: the brief is for a
designer / client, the DESIGN.md is for an AI coding agent. Same fact,
different framing.

### 1. Overview (alias: "Brand & Style")

**Source**: brief.Project Info (Purpose, Audience, Tone) +
brief.Visual Direction (Mood keywords, Style reference).

**What to write**: 2-4 sentences capturing the brand personality and
the holistic look-and-feel. Frame for an agent generating UI: which
direction is "more correct" when an explicit rule is missing? Examples:

- "Architectural minimalism with journalistic gravitas. The UI evokes
  a premium matte finish — a high-end broadsheet."
- "Vibrant-minimalist glassmorphism. Energy comes from the background;
  interface elements are frosted lenses that focus attention."

**Avoid**: client-facing language ("modern, bold, fresh"). Instead,
make a *committed* aesthetic statement.

### 2. Colors

**Source**: brief.Color Palette.

**What to write**: prose rationale per token defined in the frontmatter.
Pull the brief's Palette rationale + per-role usage guidance.

Format suggestion (markdown bullet per token, mirroring the spec
example):

```markdown
- **Primary (#1A1C1E):** Deep ink for headlines and core text.
- **Accent (#B8422E):** Used exclusively for primary actions and
  critical highlights — never decoratively.
- ...
```

### 3. Typography

**Source**: brief.Typography (Font pairing rationale + Heading/Body/
Accent fonts) + brief.Visual Direction.

**What to write**: prose explaining the type strategy — how the heading
and body work together, when the accent font appears, treatment notes
(e.g., "labels are uppercase with +0.1em letter-spacing").

If the typography expansion interview ran, also document the chosen
scale and the size/lineHeight/letterSpacing decisions per level.

### 4. Layout (alias: "Layout & Spacing")

**Source**: derived (the brief has no grid system for `frontend`; canvas
dimensions do not apply to viewport UI).

**What to author from scratch**: confirm with the user via brief
personality:
- Grid model: fluid grid (mobile-first), max-width grid (1200px desktop
  cap), or full-bleed.
- Base spacing unit: from the spacing-derivation interview.
- Containment / negative-space stance: dense vs airy.

### 5. Elevation & Depth (alias: "Elevation")

**Source**: derived (brief has no elevation data).

**What to author from scratch**: choose an approach with the user:
- Flat (borders + color contrast for hierarchy)
- Tonal layers (background variants on the same hue)
- Soft shadows (offset, blur, spread per level)
- Glassmorphism (backdrop-filter blur, transparency, edge highlights)

Document the chosen approach with concrete values when applicable
(e.g., `box-shadow: 0 8px 32px 0 rgba(0,0,0,0.1)` for level-2 cards).

### 6. Shapes

**Source**: derived from the rounded-derivation interview.

**What to write**: prose linking each `rounded.*` token to its use site
(cards, buttons, inputs, modals). Note any non-radius shape language
(e.g., "icons use 2px stroke caps to match border weights").

### 7. Components

**Source**: the components frontmatter + the components-derivation
interview.

**What to write**: per component defined in the frontmatter, prose
guidance on:
- When to use (vs alternatives)
- States (hover / active / pressed / disabled / focus) — link to the
  variant component entries
- Accessibility notes (contrast, target size)
- Anti-patterns (what NOT to do)

### 8. Do's and Don'ts

**Source**: brief.Visual Direction.Constraints + WCAG defaults.

**What to write**: structured do/don't bullets. Always include:
- Do: maintain WCAG AA contrast (4.5:1 for normal text, 3:1 for large)
- Do: use the primary color only for the single most important action
  per screen (unless the brand personality contradicts)
- Don't: mix rounded and sharp corners in the same view (unless
  intentional — note the deliberate exception in prose)

Add brief-specific items from the Constraints field.

---

## Validation before save

1. **Section order**: 8 h2 in canonical order (aliases counted as their
   canonical name).
2. **Section uniqueness**: no two h2 of the same canonical name (the
   only ERROR-level rule).
3. **Token references**: every `{path.to.token}` inside `components`
   must resolve to a defined token.
4. **No embedded h1 in body**: the body's section starts at h2. A
   top-level title (h1) is allowed but not parsed.
5. **Color values**: every `colors.*` value is `"#"` + sRGB hex
   (the spec example uses 6-digit `#RRGGBB`; that is the recommended
   form). `rgb()` / `hsl()` and other CSS color functions do NOT
   belong at the token primitive level. They MAY appear inside
   `components` property values when alpha is needed (e.g.,
   `rgba(255,255,255,0.1)` for a glass surface), since `components`
   property values are free-form per the spec.

---

## Soft dependencies — upstream tooling (opt-in)

The CLI is published as `@google/design.md` (npm). Two of its
subcommands integrate with this skill on an opt-in basis:

### Spec sync (skill auto-invokes when available)

The frontend SKILL.md "Step 0: Optional spec sync" attempts to fetch
the current upstream spec into the working context before token
derivation:

```bash
npx --yes @google/design.md spec --format markdown
```

This is the only place where the skill itself runs the CLI, and the
invocation is **best-effort** — failures (Node missing, offline, npm
fetch failure) silently fall back to the static authoring rules in
this guide. The point of the dynamic fetch is to catch upstream
drift between releases of this skill.

### Lint (user runs separately)

If the user wants spec validation of the saved DESIGN.md:

```bash
npx @google/design.md lint ./output/YYYY-MM-DD_project-name/DESIGN.md
```

This skill does NOT auto-invoke `lint`. Users who want validation
run it manually after save.

### CLI subcommand reference

- `lint` — 8 rules at the time of writing (broken-ref, missing-primary,
  contrast-ratio, orphaned-tokens, token-summary, missing-sections,
  missing-typography, section-order). Exit code `1` on errors.
- `diff <before> <after>` — token regression detection.
- `export --format tailwind|dtcg` — token export to Tailwind theme
  config or W3C DTCG `tokens.json`.
- `spec` — print the current spec (auto-fetched in Step 0; users can
  also run it directly to read the spec).

The CLI is **not** an omcc-designer dependency; users who want validation install Node and run
the CLI themselves.

---

## Output destination and Claude Code consumption

omcc-designer always writes to `./output/YYYY-MM-DD_project-name/`. The
upstream DESIGN.md convention places the file at the **consuming
project's git root** so Claude Code (or any markdown-context-loading AI
agent) picks it up automatically alongside `CLAUDE.md` / `AGENTS.md`.

The skill always prints a final note after save:

> Saved to ./output/YYYY-MM-DD_project-name/DESIGN.md. To make the
> design system available to Claude Code's context loading on the
> consuming frontend project, copy or symlink this file to that
> project's git root.

This is intentional — omcc-designer does not silently write outside
its output directory.

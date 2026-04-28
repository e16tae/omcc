---
name: social-graphics
description: "Generates multi-variant social graphics design specifications from a design brief — Instagram post (1080×1080), Instagram story (1080×1920), YouTube thumbnail (1280×720), or any combination — including per-variant layout, typography placement, and AI image generation prompts. Handles input detection, brief validation with Variants block, and full pipeline fallback. Use this skill when the user needs Instagram post, Instagram story, YouTube thumbnail, or other social-graphics specs (single or multi-variant)."
---

# Phase 4: Social Graphics Design Specification

Generate a multi-variant social graphics design specification from
the design brief. The output is a single social_graphics_spec.md
with one H2 sub-block per variant (e.g., `## Variant: instagram-post
(1080×1080)`), each variant carrying its own three-layer breakdown:
layout structure, typography specification, and designer's vision
for AI image generation.

The brief's `Variants:` block drives the per-variant set; top-level
Technical Specifications fields act as shared defaults that each
variant entry may override field-by-field. See
`skills/brief-generation/references/design-brief-spec.md`
"Target medium aliases" for the canonical variant whitelist.

## When auto-activated (without /start or /social-graphics command)

### Input detection

Determine whether the input is a brief file path or a raw design request:
- **File path**: Exists on disk and contains "# Design Brief" header → brief mode
- **Otherwise** → raw request mode

### Brief mode

1. Read the brief file.
2. Validate per `skills/brief-generation/references/design-brief-spec.md` —
   completeness, medium match (canonical Target medium must equal
   `social-graphics` after alias normalization), staleness, and the
   Variants validation rules (block present, whitelist conformance,
   no collision, per-variant effective Tech Specs cover Dimensions /
   Orientation / Resolution / Output format / Platform). If the
   brief's Target medium does not normalize to `social-graphics`,
   inform the user and offer to re-run the interview for
   social-graphics.
3. **Confirmed field check**: Before using any brief field, verify
   it is not tagged `[unconfirmed]` — see
   `skills/design-interview/references/confirmed-decision-principle.md`.
   If a required field is unconfirmed, ask the user to confirm it
   before proceeding.
4. If validation passes: proceed to Step 1 (Variant set resolution).
5. If validation fails: inform the user of the specific issue
   (citing the alias / collision / coverage rule that failed) and
   offer to run the full pipeline.

### Raw request mode

No brief was provided — direct generation from raw input is not
permitted because
`skills/design-interview/references/confirmed-decision-principle.md`
requires user-confirmed decisions before encoding. Run the full
pipeline before producing the spec:

1. Invoke the design-analysis skill on the raw request to produce
   the Phase 1 analysis (alias-normalize the implied Target medium
   and Variants per
   `skills/design-analysis/references/analysis-guide.md`).
2. Invoke the design-interview skill to confirm design decisions
   including Step E variant set selection.
3. Invoke the brief-generation skill to produce the brief at the
   standard output path per
   `skills/brief-generation/references/output-file-rules.md`.
4. Continue with Steps 1-5 below using the generated brief.

If the user declines the interview, save no files and end; spec
generation cannot proceed without confirmed decisions.

### Step 1: Variant set resolution

Before any per-variant work, resolve the active Variants list:

1. Read the brief's `Variants:` block (under Technical
   Specifications). Each variant entry may override a subset of
   the top-level fields (Dimensions / Orientation / Resolution /
   Output format / Platform / Safe area).
2. For each variant, compute its **effective Technical Specifications**
   by combining the variant's overrides with the top-level shared
   defaults — overrides win field-by-field; shared defaults fill
   gaps.
3. Validate every variant id against the canonical whitelist defined
   in `skills/brief-generation/references/design-brief-spec.md`
   "Target medium aliases" (currently `instagram-post`,
   `instagram-story`, `youtube-thumbnail`).
4. Detect duplicates — including aliases that normalize to the same
   canonical id — and surface a repair prompt rather than silently
   deduplicating. Brief generation should already prevent this; this
   is defensive.
5. Confirm each variant's effective Dimensions / Orientation /
   Resolution / Output format / Platform are present. If a variant
   omits a field and the shared default does not fill it, surface
   a repair prompt naming the variant + missing field.

The result is a list of per-variant context objects that Steps 2-4
iterate over.

### Step 2: Per-variant layout structure

For each variant in the resolved set:

1. Define the grid system (columns, rows, gutters) appropriate to
   the variant's effective Dimensions and Orientation. The grid
   shape is intentionally per-variant — IG square (1:1), IG story
   (9:16), and YT thumbnail (16:9) demand different compositions.
2. Map content elements (from the brief's Content Map) to grid
   zones, adapted to the variant's aspect ratio. The same semantic
   content (e.g., "hook headline") may live in different zones
   across variants — that is expected.
3. Establish visual hierarchy through size and position, mindful
   of platform-specific safe zones (IG story top/bottom UI bands,
   YT timestamp/logo overlay, IG grid-crop center). See
   `skills/social-graphics/references/social-graphics-guide.md`
   "Per-platform safe zones".
4. Define edge margins. Print bleed is N/A for raster social
   graphics; use the variant's Safe area override (or the platform
   default from the guide) instead.
5. Create a zone map with labeled areas for this variant.

Follow per-variant layout guidelines in
`skills/social-graphics/references/social-graphics-guide.md`.

### Step 3: Per-variant typography specification

For each variant, using the brief's typography and content map:

1. Assign fonts, sizes, weights, and colors to each text element
   for this variant's grid.
2. Define position coordinates (grid zone reference, alignment).
3. Specify line height, letter spacing, and text transforms.
4. Ensure minimum text size compliance per the variant's effective
   Resolution and viewing distance (e.g., a thumbnail viewed at a
   small player-overlay scale demands larger relative text than a
   full-bleed story).
5. Verify contrast ratios for each text-on-background combination
   per variant.

This layer is applied by the human designer — not included in AI
image prompts. Per-variant typography is documented even though the
rendered raw zone PNGs intentionally carry no text composition (see
Step 4's boundary statement).

### Step 4: Per-variant designer's vision and AI image generation

For each variant and each image zone within that variant:

1. Compose a comprehensive **Designer's Vision** description
   covering: position & space, subject & elements, mood &
   atmosphere, lighting, color direction, composition & framing,
   style & texture, constraints. The composition adapts to the
   variant's aspect ratio.
2. Add an **Image Generation Guide** with universal tips for
   translating the vision into any image generation tool.
3. If the brief specifies image generation tools (Technical
   Specifications):
   - **Research each tool** using WebSearch for current best
     practices (per-variant aspect-ratio handling, safe-zone
     awareness, raster output).
   - Generate **tool-specific optimized prompts** based on the
     research.
   - Include the research date for freshness tracking.

**Boundary statement (load-bearing)**: AI image generation prompts
for social graphics MUST request raw, text-free image content only.
The visible headline / CTA / overlay text belongs to Layer 2
(typography) and is composed by the human designer — not by the
image generator. This rule applies stricter than for posters
because social formats (especially YT thumbnail and IG story)
conventionally show heavy text overlays, and the temptation to
bake text into the rendered image is high. Resist that temptation.

See
`skills/social-graphics/references/social-graphics-guide.md`
"No text composition" for the full enforcement guidance.

### Step 5: Output assembly and save

Design outputs that include AI image generation prompts must
separate three layers (per variant): layout, typography, and image
generation prompts. Mixing typography into image prompts degrades
output quality. The three-layer separation lets the human apply
text precisely while AI handles visual elements.

Then:

1. Combine all variants' three-layer outputs into a single
   social_graphics_spec.md document, with one H2 sub-block per
   variant: `## Variant: <id> (<W>×<H>)` followed by Layer 1, Layer
   2, Layer 3 sub-sections. Inside each variant's Layer 3, every
   image zone MUST appear as a real H4 markdown heading
   (`#### Zone A: <Purpose>`, `#### Zone B: <Purpose>`, ...) — NOT
   as fenced code text. The chain-tail render skill scans the spec
   for `^####\s+Zone` lines outside fenced blocks; without real
   H4 headings the render chain cannot discover the zones.
2. Above the variant blocks, include shared sections (Project
   Reference, Brand Context) — these come from the brief and are
   identical across variants.
3. Run the per-variant + cross-variant quality checklist per
   `skills/social-graphics/references/social-graphics-guide.md`.
4. Save to ./output/YYYY-MM-DD_project-name/social_graphics_spec.md
   — directory naming and sanitization per
   `skills/brief-generation/references/output-file-rules.md`.
5. Present the spec to the user with a per-variant summary.

**Output language**: Write the spec file (layout / typography text
labels and prose portions) in the user's request language. AI
image generation prompts follow each tool's expected prompt
language (commonly English) per
`skills/social-graphics/references/social-graphics-guide.md`.

---

## When invoked by command (/start, /social-graphics)

### When invoked by /start

The brief is already generated in Phase 3. Skip input detection
and brief mode — proceed directly from Step 1 with the Phase 3
brief.

**Medium gate**: Before Step 1, verify the brief's canonical
Target medium equals `social-graphics` (after alias normalization
per `skills/brief-generation/references/design-brief-spec.md`
"Target medium aliases"). If not: inform the user that the
confirmed medium is different, the brief has been saved, and the
corresponding domain skill is not yet available.

### When invoked by /social-graphics

Full procedure as auto-activated mode: input detection, brief
validation (with Variants validation rules) or raw request
handling, then Steps 1-5. After saving, output the completion
message and offer modification assistance.

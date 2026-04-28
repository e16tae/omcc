# Social Graphics Design Guide

Detailed guidelines for generating multi-variant social graphics
specifications in Phase 4. Encodes social-platform-specific design
expertise for layout, typography, and AI prompts.

The canonical variant whitelist
(`instagram-post`, `instagram-story`, `youtube-thumbnail`) and the
alias normalization rules live in
`skills/brief-generation/references/design-brief-spec.md`
"Target medium aliases" — this guide reads them, does not redefine.

---

## Per-platform safe zones

Each variant has platform-specific UI overlay zones that block
critical content. These are NOT optional designer-chosen safe
margins; they are hard-blocked by the platform UI.

| Variant id | Canvas | Top overlay | Bottom overlay | Side overlay | Other |
|------------|--------|-------------|----------------|--------------|-------|
| `instagram-post` | 1080×1080 | none | none | none | Grid view crops to a 1080×1080 center; the post is already square so no crop concern. Important content should still avoid the very edge to survive Instagram's visual chrome on detail pages. |
| `instagram-story` | 1080×1920 | top ~250 px (sender header overlay) | bottom ~250 px (reply bar / sticker overlay) | none | Critical content lives in the central ~1080×1420 region. |
| `youtube-thumbnail` | 1280×720 | none | bottom-right ~150×40 px (duration badge overlay shown after the player loads) | none | Avoid placing the focal subject's eyes / text in the bottom-right duration zone. |

When a variant's brief specifies a `Safe area` override, that
override **adds** to the platform default — it does not replace it.
For example, a designer adding `Safe area: 80px` to an
`instagram-story` brief produces an effective safe area of the
top/bottom UI bands plus an additional 80px margin on all sides.

---

## Layer 1: Per-variant layout structure

### Aspect-ratio-driven composition

Each variant has a distinct visual logic:

| Variant | Aspect | Recommended composition |
|---------|--------|-------------------------|
| `instagram-post` | 1:1 (square) | **Balanced central composition.** The square invites symmetric or rule-of-thirds with a strong focal subject. Hook content in the upper-third or center; supporting content surrounding. Logo discreet (corner). |
| `instagram-story` | 9:16 (portrait) | **Vertical narrative.** Hook subject in the upper half (visible above bottom UI band); supporting visual / accent in the central region; CTA text in the central band — never at the bottom. Negative space at the very top (above sender header) and the very bottom (above reply bar). |
| `youtube-thumbnail` | 16:9 (landscape) | **Hero-centric, oversized.** Subject's face / hero object scaled large — thumbnails are seen at small player-overlay sizes. Headline text overlay (Layer 2, applied by designer) typically left-aligned with the hero on the right, or vice versa. Avoid clutter; one focal moment dominates. |

### Grid recommendations

Each variant's grid is independent. Do not force a shared grid
across variants — the aspect ratios differ enough that a unified
grid would compromise composition quality.

| Variant | Grid shape | Notes |
|---------|------------|-------|
| `instagram-post` | 4×4 modular OR rule-of-thirds with central focal point | The square forgives most grids; pick the one that best supports the content |
| `instagram-story` | 9-row vertical (top header / hook / hero / supporting / CTA / footer / bottom UI) | Vertical reading order is dominant |
| `youtube-thumbnail` | 16:9 with visual mass split (hero left, text-overlay right OR mirrored) | Reads as one image, not as zones; the "grid" is more about content placement than columns |

### Zone map format

Present the per-variant layout as a labeled zone diagram (one diagram
per variant). Example for `instagram-story`:

```
+--------------------------------+ 0 px
| [TOP UI BAND ~250 px]          |
+--------------------------------+ 250 px
|                                |
|     ZONE A: Hook Headline      |
|         (Layer 2 text)         |
|                                |
+--------------------------------+ 600 px
|                                |
|         ZONE B: Hero           |
|         (Layer 3 image)        |
|         1080 × 820 px          |
|                                |
+--------------------------------+ 1420 px
|     ZONE C: CTA (Layer 2)      |
+--------------------------------+ 1670 px
| [BOTTOM UI BAND ~250 px]       |
+--------------------------------+ 1920 px
```

Include for each zone:
- Zone label and purpose
- Approximate dimensions in pixels
- Content assignment (Layer 2 text or Layer 3 image)
- Background treatment (color, gradient, image, transparent)

---

## Layer 2: Per-variant typography specification

### Text element specification format

Per variant, per text element:

```
Variant: <id>
Element: [Hook Headline / Sub Hook / Body / CTA / Caption]
Content: "[exact text]"
Font: [font name], [weight]
Size: [px for the variant's resolution]
Color: [hex] on [background hex] — contrast ratio: [N:1]
Position: Zone [X], [alignment]
Line height: [multiplier]
Letter spacing: [value]
Transform: [none / uppercase / capitalize]
```

### Size scaling per variant

Default starting points; adjust based on legibility tests at the
typical viewing scale of each platform.

| Element | instagram-post (1080²) | instagram-story (1080×1920) | youtube-thumbnail (1280×720) |
|---------|------------------------|-----------------------------|-------------------------------|
| Hook headline | 64-90 px | 80-110 px | 80-120 px (will be small at player-overlay scale) |
| Sub hook | 36-48 px | 44-56 px | 40-56 px |
| Body / supporting | 24-32 px | 28-36 px | (rare — thumbnails minimize body copy) |
| CTA | 36-48 px (small chip OK) | 44-60 px (more prominent) | (rare — CTAs are external on YouTube) |

### Per-platform readability rules

- **instagram-post**: Survives small grid-view crops; hook should be readable at a 250×250 px thumbnail.
- **instagram-story**: Read at full screen height (1920+px on phones). Generous sizing OK; respect top/bottom UI bands.
- **youtube-thumbnail**: Often viewed at 168×94 px (mobile feed thumbnail). The hook headline must be legible at that size — this drives oversized type.

---

## Layer 3: Per-variant designer's vision and AI image generation

### Designer's vision composition rules per variant

Before composing the per-variant `Designer's Vision`, internalize the
variant's visual logic from the table above. Then compose:

1. **Subject & elements**: What is the focal subject? What supporting
   elements? Where do they sit on the variant's canvas?
2. **Mood & atmosphere**: Match the brief's confirmed mood keywords;
   per-variant mood does not differ unless the campaign explicitly
   varies emotional registers across platforms.
3. **Lighting**: Direction, quality, color temperature. Same campaign
   context across variants typically.
4. **Color direction**: Primary / accent / neutral roles, hex codes
   from the brief's palette.
5. **Composition & framing**: Adapted to the variant's aspect ratio.
   Square balanced; vertical hero-on-top; landscape hero-large-with-
   negative-space-for-text.
6. **Style & texture**: Photographic / illustrative / abstract /
   mixed — same approach across variants typically.
7. **Constraints**: What to avoid. **Always include "no text, no
   typography, no captions, no overlays" — see "No text composition"
   below.**

### Codex prompt author guidance

When the brief lists `codex` (or any image-gen tool) in `Image
generation tools`, the prompt sent to the chain-tail render
(`social-graphics-render`) must:

- State the exact target dimensions (e.g., `1080×1080 px raster image`).
- Describe the subject + composition + mood + lighting + color +
  style, all per the Designer's Vision.
- **Explicitly forbid text content** in the image: "no text, no
  letters, no typography, no captions, no headlines, no logos in
  text form, no UI mockups."
- **Explicitly forbid platform UI mockups**: "do not render
  Instagram chrome, do not render YouTube player UI, do not render
  the timestamp / sender header / reply bar."
- Match the variant's safe zones — for `instagram-story`, the
  prompt should describe the visual subject filling the central
  ~1080×1420 region, not the full 1080×1920 canvas (which would
  bleed into the platform UI bands).

### No text composition

This rule is load-bearing for social graphics. Repeat it in three
places when authoring the spec:

1. **In `skills/social-graphics/SKILL.md` Step 4** (the boundary
   statement): "AI image generation prompts MUST request raw,
   text-free image content only."
2. **In every per-variant Layer 3 sub-block in the saved
   social_graphics_spec.md**: include `Constraints: no text
   content, no typography, no captions, no overlays` as a
   non-negotiable line.
3. **In `skills/social-graphics-render/SKILL.md` "Scope and
   boundary"**: the chain-tail re-asserts the boundary at the
   render entry.

The temptation to bake text into the rendered image is highest for
YT thumbnails (where conventional production includes oversized
captioned text on the image) and IG stories (where the format
encourages large overlay text). Both are Layer 2 responsibilities
applied by the human designer or external compositing — never by
the AI image generator.

---

## Three-layer separation (carries over from poster)

Layout structure / typography specification / image generation
prompts MUST stay distinct because AI image generators cannot
reliably render text. Mixing typography into image prompts
degrades output quality. The three-layer separation lets the human
apply text precisely while AI handles visual / photographic
elements. See the same principle in
`skills/poster/references/poster-guide.md`.

For social graphics, the three layers replicate per variant —
each variant's Layer 1 / Layer 2 / Layer 3 sub-blocks are
independent.

---

## Spec output format markdown template

Save as social_graphics_spec.md with one H2 sub-block per
variant. Shared sections (Project Reference, Brand Context) sit
above the variant blocks.

```markdown
# Social Graphics Design Specification

## Project Reference

(Project Info + Brand Context summary derived from the brief —
identical across variants. Includes confirmed brand personality,
color palette, typography, visual direction, mood keywords.)

## Variant: instagram-post (1080×1080)

### Layer 1: Layout

(Grid, zone map, safe-zone notes, edge margins.)

### Layer 2: Typography

(Per-element font / size / color / position / line-height for this variant's grid.)

### Layer 3: Designer's Vision and AI Image Generation

For each image zone, open with an H4 heading naming the zone id
and purpose — this heading is **load-bearing**: the chain-tail
render skill (`social-graphics-render`) parses it to identify
distinct zones, compute call counts, and derive output filenames.
Without this heading the render skill cannot find any zones.

The two zone examples shown below as `#### Zone A: Hero` and
`#### Zone B: Supporting visual` MUST appear in the saved spec
as actual H4 markdown headings, NOT as fenced code text. The
render skill scans the spec for `^####\s+Zone` lines outside
any fenced code block.

Authoring example (the following two `####` lines are themselves
real H4 headings — the saved spec should look like this):

#### Zone A: Hero
- **Designer's Vision**: position & space, subject & elements,
  mood & atmosphere, lighting, color direction, composition &
  framing, style & texture, constraints (must include text-free).
- **Image Generation Guide**: universal tips for translating to
  any image gen tool.
- **Tool-specific prompts** (if Image generation tools is set):
  per-tool optimized prompts with research date.

#### Zone B: Supporting visual
- (additional zones in the same variant repeat the same shape)

The zone id (e.g., `Zone A`) maps to the filesystem zone-id rule
in `skills/brief-generation/references/output-file-rules.md`
(`Zone A` → `zone_a`). Zone ids are scoped per variant — two
variants in the same spec MAY each have a `Zone A`.

### Production Notes (variant)

(Per-variant production reminders: manual text overlay (Layer 2),
external compositing if applicable, platform-specific export
settings.)

## Variant: instagram-story (1080×1920)

(same Layer 1/2/3/Production Notes structure)

## Variant: youtube-thumbnail (1280×720)

(same structure)

## Production Notes (shared)

(Cross-variant production reminders: campaign-level brand
consistency, rollout sequencing, asset naming.)
```

---

## Quality checklist

Before saving the spec, verify per-variant:

- [ ] Grid + zone map present and respects platform safe zones
- [ ] All text elements have per-variant size / font / color / position / contrast ratio
- [ ] Image zones have Designer's Vision with subject / mood / lighting / color / composition / style / constraints
- [ ] Constraints line includes "no text, no typography, no captions, no overlays"
- [ ] Tool-specific prompts (if applicable) match the variant's exact dimensions
- [ ] Production Notes flag platform-specific UI overlays as Layer 2 / external concerns

Cross-variant verification:

- [ ] Brand palette and typography are consistent across variants (same hex codes, same font family)
- [ ] Mood and visual direction stay coherent — do not drift between variants unless the campaign explicitly demands varied registers
- [ ] No variant's image prompts smuggle text content (most common drift point)
- [ ] Variant id list matches the brief's `Variants:` block exactly (no variant added or dropped silently)

---

## Output language

The spec file (layout / typography text labels and prose portions)
is written in the user's request language. AI image generation
prompts follow each tool's expected prompt language (commonly
English). The plugin's documentation language (this file) is
English regardless of runtime language.

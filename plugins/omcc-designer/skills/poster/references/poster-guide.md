# Poster Design Guide

Detailed guidelines for generating poster design specifications in Phase 4.
Encodes poster-specific design expertise for layout, typography, and AI prompts.

---

## Layer 1: Layout Structure

### Grid system selection

Choose grid based on content volume and visual style:

| Content Type | Recommended Grid | Rationale |
|-------------|-----------------|-----------|
| Single hero image + minimal text | Full-bleed + overlay | Maximum visual impact |
| Balanced image and text | 2-column or asymmetric split | Clear content zones |
| Text-heavy with supporting image | 3-column or modular grid | Organized information hierarchy |
| Data/infographic poster | Modular grid (3x4 or 4x6) | Structured data presentation |
| Event poster | Rule of thirds + focal point | Dynamic composition |

### Visual hierarchy principles

Poster viewing follows predictable patterns:

1. **Primary focal point** (largest/boldest element): Usually upper-third
   for vertical reading, center for radial composition
2. **Secondary information**: Adjacent to primary, smaller scale
3. **Supporting details**: Bottom third or margins
4. **Call to action**: Bottom area, high contrast

### Zone map format

Present the layout as a labeled zone diagram:

```
+------------------------------------------+
|              [BLEED AREA]                 |
|  +--------------------------------------+|
|  |         ZONE A: Hero Image           ||
|  |         (full-width, 50% height)     ||
|  |                                      ||
|  +--------------------------------------+|
|  |  ZONE B: Headline     | ZONE C: Logo ||
|  |  (70% width)          | (30% width)  ||
|  +--------------------------------------+|
|  |         ZONE D: Body Copy            ||
|  |         (full-width, 20% height)     ||
|  +--------------------------------------+|
|  |  ZONE E: CTA          | ZONE F: Info ||
|  |  (50% width)          | (50% width)  ||
|  +--------------------------------------+|
|              [BLEED AREA]                 |
+------------------------------------------+
```

Include:
- Zone label and purpose
- Approximate dimensions (percentage or mm/px)
- Content assignment
- Background treatment (color, gradient, image, transparent)

### Print-specific layout rules

- **Bleed**: Extend background imagery 3mm beyond trim line on all sides
- **Safe area**: Keep all critical content at least 5mm from trim line
- **Fold awareness**: N/A for posters (single sheet)
- **Viewing distance**: Standard poster viewed at 1-3 meters;
  headline should be readable at 3m, body at 1m

### Digital-specific layout rules

- **Edge-to-edge**: No bleed needed, design to exact pixel dimensions
- **Screen density**: Consider retina/HiDPI — use 2x assets
- **Platform constraints**: Instagram crops to square in grid view;
  ensure key content is visible in center square crop

---

## Layer 2: Typography Specification

### Text element specification format

For each text element, provide:

```
Element: [Headline / Subheadline / Body / CTA / Caption]
Content: "[exact text]"
Font: [font name], [weight] (e.g., Poppins, Bold)
Size: [size in pt for print, px for digital]
Color: [hex] on [background hex] — contrast ratio: [N:1]
Position: Zone [X], [alignment] (e.g., Zone B, left-aligned)
Line height: [multiplier] (e.g., 1.2)
Letter spacing: [value] (e.g., -0.02em or normal)
Transform: [none / uppercase / capitalize]
```

### Size scaling by poster format

| Element | A3 (297x420mm) | A2 (420x594mm) | 24x36in (610x914mm) |
|---------|----------------|----------------|---------------------|
| Headline | 48-72pt | 72-96pt | 96-144pt |
| Subheadline | 24-36pt | 36-48pt | 48-72pt |
| Body copy | 12-16pt | 16-20pt | 20-28pt |
| CTA | 18-24pt | 24-36pt | 36-48pt |
| Fine print | 8-10pt | 10-12pt | 12-16pt |

### Digital size scaling

| Element | 1080x1080px | 1080x1920px | 1920x1080px |
|---------|-------------|-------------|-------------|
| Headline | 48-72px | 64-96px | 72-120px |
| Subheadline | 24-36px | 36-48px | 36-56px |
| Body copy | 16-20px | 18-24px | 20-28px |
| CTA | 20-28px | 24-36px | 28-40px |

---

## Layer 3: Designer's Vision and AI Image Generation

### Designer's Vision — per image zone

For each image zone, compose a comprehensive vision description covering
all of the following aspects. This is the designer's professional art direction
— detailed enough that any image generation tool can produce the intended result.

**Required aspects for each zone:**

1. **Position & Space**: Where the zone sits in the layout, what percentage
   of the design it occupies, how it relates to adjacent zones, whether it
   extends into bleed areas

2. **Subject & Elements**: What is depicted — the main subject, supporting
   elements, their spatial arrangement within the zone

3. **Mood & Atmosphere**: The emotional quality the image must convey,
   the energy level, the feeling it should evoke in the viewer

4. **Lighting**: Light source direction, quality (natural/artificial/mixed),
   color temperature, how highlights and shadows create depth and mood

5. **Color Direction**: How the brief's color palette manifests in this zone —
   which palette colors appear where, how the image harmonizes with the
   overall design's color scheme

6. **Composition & Framing**: Camera angle/perspective, rule of thirds or
   other compositional principles, depth of field, foreground/background
   relationship, visual flow direction

7. **Style & Texture**: Visual treatment (photographic/illustrative/abstract),
   level of realism, texture qualities (clean/textured/grain), post-processing feel

8. **Constraints**: What to avoid in this zone, areas that must remain clear
   for text overlay, elements that would conflict with the design's purpose

9. **Technical Notes**: Aspect ratio (derived from zone dimensions),
   resolution requirements, any medium-specific considerations (print vs digital)

### Image Generation Guide

After the vision description, provide universal guidance for translating
the vision into image generation tools:

- Which aspects of the vision are most critical to preserve in the prompt
- How to express color direction (tools can't match exact hex — use tone
  descriptions like "warm amber tones with cool blue contrast")
- Where to specify aspect ratio and quality in the tool's parameter system
- How to express the "clear area for text overlay" requirement

### Tool-Specific Optimization (runtime research)

If the brief's Technical Specifications include image generation tools:

1. **Research each tool** using WebSearch:
   - Query: "[tool name] best practices prompt guide [current year]"
   - Focus on: prompt syntax, parameter options, style modifiers,
     aspect ratio handling, quality settings
2. **Generate optimized prompts** for each tool based on the research:
   - Adapt the Designer's Vision into the tool's preferred prompt format
   - Apply tool-specific best practices discovered in research
   - Include tool-specific parameters
3. **Include research date** so the user knows how current the optimization is

#### codex (handled by poster-render chain)

When the brief's Image generation tools field includes `codex`, the
poster_spec.md author still produces a Designer's Vision per zone, but
**no separate "codex-specific prompt" is needed in the spec**. The codex
prompts are constructed at render time by the `poster-render` skill
(see `skills/poster-render/SKILL.md`) using the Designer's Vision text
directly.

Author guidance for codex-targeted zones:

- Make the Designer's Vision read like a self-contained image generation
  prompt — paragraphs the renderer can pass through verbatim.
- Match the brief's Imagery approach (`photography`, `illustration`,
  `mixed`) explicitly in the vision text. Codex inspects the request
  and uses imagegen-model dispatch when raster intent is clear; for
  simple shape / vector-friendly subjects (small flat icons, geometric
  marks), the codex CLI may pick a deterministic script path instead.
  The poster-render skill compensates by appending a "use the imagegen
  tool" directive in those borderline cases — but framing the vision
  in raster terms first is the cleanest path.
- Do NOT include tool-specific syntax (`--ar`, parameter flags) or
  Midjourney-style command tokens in the vision. Codex consumes
  natural-language prompts.

If no tools are specified in the brief, provide the Designer's Vision and
Image Generation Guide only. The user can apply these to any tool.

### Text-free zone enforcement

**Critical rule**: AI image generators cannot reliably render text.
Never include text content in image generation prompts.

- Do NOT ask the AI to render headlines, body copy, or CTAs
- DO specify "clean area for text overlay" when a zone needs text space
- Typography is ALWAYS Layer 2 (human-applied), never Layer 3 (AI-generated)
- If the design requires text integrated with an image (e.g., text wrapped
  around a shape), specify the shape/space in the AI prompt and note that
  text will be composited afterward

### Vision quality checklist per zone

- [ ] All 9 required aspects described (position, subject, mood, lighting,
      color, composition, style, constraints, technical)
- [ ] Mood matches brief's mood keywords
- [ ] Style matches brief's visual direction
- [ ] Color direction harmonizes with brief's palette
- [ ] No text content in the vision or prompts
- [ ] Text overlay space specified if zone overlaps with text zones
- [ ] Constraints from brief applied (what to avoid)
- [ ] Tool-specific prompts generated (if tools specified in brief; for `codex`, see Tool-Specific Optimization > codex)
- [ ] Research date included for tool-specific sections

---

## Content Overload Handling (Phase 4 fallback)

Content overload should be caught during Phase 2 interview (Step D).
However, if a brief arrives with overloaded content (e.g., user manually
edited the brief after interview, or cross-session reuse):

### Assessment

Apply the poster thresholds from
`skills/design-interview/references/interview-guide.md` Content overload
thresholds table (Poster row: max 3-4 text elements, max 1-2 image zones,
warning if >5 lines body copy).

### Poster-specific response

1. **Prioritize**: Present the content priority list from the brief and
   ask user to select top 3 elements for the poster
2. **Condense**: Offer to rewrite copy shorter while preserving message
3. **Split**: Suggest poster + supplementary material (handout, QR code)
4. **Redirect**: If content fundamentally exceeds poster capacity, recommend
   a different medium and save the brief for future domain skill use

---

## Poster Spec Output Format

```markdown
# Poster Design Specification

## Project Reference
- Brief: [path to design_brief.md]
- Generated: YYYY-MM-DD
- Dimensions: [width x height]
- Format: [print / digital]

---

## Layer 1: Layout Structure

### Grid System
[Grid description]

### Zone Map
[ASCII zone diagram]

### Zone Details
| Zone | Purpose | Content | Dimensions | Background |
|------|---------|---------|------------|------------|
| A | Hero image | [description] | [size] | Image |
| B | Headline | [text] | [size] | Transparent |
| ... | ... | ... | ... | ... |

---

## Layer 2: Typography Specification

### [Element Name]
- Content: "[text]"
- Font: [font], [weight]
- Size: [size]
- Color: [hex] on [background hex] (contrast: [ratio])
- Position: Zone [X], [alignment]
- Line height: [value]
- Letter spacing: [value]

[Repeat for each text element]

---

## Layer 3: Designer's Vision and AI Image Generation

### Zone [X]: [Zone Name]

**Designer's Vision**
- Position & Space: [layout placement, size, relationship to adjacent zones]
- Subject & Elements: [what is depicted, spatial arrangement]
- Mood & Atmosphere: [emotional quality, energy level]
- Lighting: [source, quality, color temperature, depth]
- Color Direction: [palette manifestation, harmony notes]
- Composition & Framing: [angle, rule of thirds, depth of field, flow]
- Style & Texture: [visual treatment, realism level, texture qualities]
- Constraints: [what to avoid, clear areas for text overlay]
- Technical: [aspect ratio, resolution requirements]

**Image Generation Guide**
[Universal tips for translating this vision into any tool]

**Tool-Specific Prompts** (if tools specified in brief)
[Tool name] (researched: YYYY-MM-DD):
[Optimized prompt based on runtime research of tool best practices]

[Repeat for each image zone]

---

## Production Notes
- [Any additional notes for the designer/implementer]
- [Print-specific or digital-specific reminders]
```

# Design Brief Spec

The design brief is the **handoff artifact** between Phase 3 (brief generation)
and Phase 4 (domain-specific output). This single file must contain all design
decisions needed for Phase 4 to run independently in another session.

---

## Brief Structure

```markdown
# Design Brief

## Project Info
- Project: [project title]
- Created: YYYY-MM-DD
- Client: [client name or "personal"]
- Target medium: [poster / brochure / infographic / frontend / social-graphics]
- Purpose: [what the design must achieve]
- Core challenge: [what someone should DO/FEEL/KNOW after seeing this]
- Audience: [target audience description]
- Tone: [formal / casual / playful / corporate / artistic / ...]
- Deadline: [date or "none"]

## Brand Identity
- Brand name: [name or "none"]
- Logo: [description or file reference, or "none"]
- Existing brand guide: [yes — reference / no]
- Brand personality: [2-3 adjective description]

## Color Palette
- Primary: [hex] — [name/role]
- Secondary: [hex] — [name/role]
- Accent: [hex] — [name/role]
- Neutral light: [hex] — [name/role]
- Neutral dark: [hex] — [name/role]
- Palette rationale: [why these colors — brand alignment, psychology, contrast]
- Color mode: [CMYK for print / RGB for digital / both]
- Confirmation: [confirmed / unconfirmed]

## Typography
- Heading font: [font name] — [weight, style]
- Body font: [font name] — [weight, style]
- Accent font: [font name or "none"] — [usage context]
- Font pairing rationale: [why this combination]
- Minimum text size: [size for target medium]
- Confirmation: [confirmed / unconfirmed]

## Visual Direction
- Mood keywords: [3-5 keywords, e.g., "modern, clean, bold, energetic"]
- Style reference: [description of visual style — flat, illustrative, photographic, etc.]
- Imagery approach: [photography / illustration / abstract / mixed]
- Visual metaphors: [key metaphors or symbols to use]
- Constraints: [what to avoid — specific styles, colors, imagery]
- Confirmation: [confirmed / unconfirmed]

## Content Map
- Headline: [primary headline text]
- Subheadline: [secondary text or "none"]
- Body copy: [main body text or summary of key points]
- Call to action: [CTA text and purpose, or "none"]
- Data/statistics: [key numbers or data points, or "none"]
- Image zones:
  - Zone 1: [purpose — background/hero/supporting/icon] [description — what this zone should depict, size/position hint]
  - Zone 2: [purpose] [description]
  - ...
- Content priority: [ordered list of elements by visual importance]
- Confirmation: [confirmed / unconfirmed]

## Technical Specifications
- Dimensions: [width x height, units] — shared default if Variants is set
- Orientation: [portrait / landscape / square] — shared default if Variants is set
- Resolution: [DPI for print, or PX dimensions for digital] — shared default if Variants is set
- Bleed: [size, or "N/A" for digital]
- Safe area: [margin from edges for critical content] — shared default if Variants is set
- Output format: [PDF / PNG / SVG / web / ...] — shared default if Variants is set
- Platform: [print / social media / web / presentation / ...] — shared default if Variants is set
- Image generation tools: [tool names, e.g., "Midjourney, codex" or "none specified"]
- Variants: [list, or "none"]
  - Variant: [variant id, kebab-case, from whitelist below]
    - Dimensions: [width x height, units] — overrides shared default
    - Orientation: [portrait / landscape / square] — overrides shared default
    - Resolution: [DPI or PX] — overrides shared default
    - Output format: [PNG / JPG / ...] — overrides shared default
    - Platform: [Instagram / YouTube / ...] — overrides shared default
    - Safe area: [platform-specific UI overlays / crop zones] — overrides shared default
  - (repeat per variant; any field omitted falls back to the shared default above)
- Confirmation: [confirmed / unconfirmed]

## Supplementary Notes
- [additional context from interview]
- [designer recommendations not captured above]

## Decision Log
| Section | Status | Source |
|---------|--------|--------|
| Project Info | confirmed | Phase 2 Step A |
| Brand Identity | partial | Phase 2 Step B |
| Color Palette | confirmed | Phase 2 Step C |
| Typography | confirmed | Phase 2 Step C |
| Visual Direction | confirmed | Phase 2 Step C |
| Content Map | confirmed | Phase 2 Step D |
| Technical Specs | confirmed | Phase 2 Step E |

Status values: confirmed / partial / unconfirmed / skipped

---

[end of brief]
```

---

## Field Descriptions

### Project Info

| Field | Source | Required | Purpose |
|-------|--------|----------|---------|
| Project | Phase 2 Step A | Required | Directory naming, identification |
| Created | Auto-generated | Required | Staleness detection |
| Client | Phase 2 Step A | Optional | Context, tone calibration |
| Target medium | Phase 1 estimate > Phase 2 confirm | Required | Routes to correct domain skill |
| Purpose | Phase 2 Step A | Required | Design direction foundation |
| Core challenge | Phase 2 Step A | Required (mark as [unconfirmed] with designer recommendation if user unsure) | Drives visual hierarchy, CTA design, and content priority |
| Audience | Phase 2 Step A | Required | Visual tone, complexity calibration |
| Tone | Phase 1 estimate > Phase 2 confirm | Required | Visual direction, color psychology |
| Deadline | Phase 2 Step A | Optional | Priority, scope management |

### Brand Identity

| Field | Source | Required | Purpose |
|-------|--------|----------|---------|
| Brand name | Phase 2 Step B | Optional | Logo placement, consistency |
| Logo | Phase 2 Step B | Optional | Layout zone reservation |
| Existing brand guide | Phase 2 Step B | Required | Determines color/typography freedom |
| Brand personality | Phase 2 Step B | Required | Drives visual direction |

### Color Palette

| Field | Source | Required | Purpose |
|-------|--------|----------|---------|
| Primary/Secondary/Accent | Phase 2 Step C | Required | All visual elements |
| Neutral light/dark | Phase 2 Step C | Required | Background, text, contrast |
| Palette rationale | Phase 2 Step C | Required | Traceability, future consistency |
| Color mode | Phase 2 Step C (confirmed in Step E) | Required | Print vs digital output |
| Confirmation | Auto-tracked | Required | Confirmed Decision Principle |

### Typography

| Field | Source | Required | Purpose |
|-------|--------|----------|---------|
| Heading/Body/Accent font | Phase 2 Step C | Required | All text elements |
| Font pairing rationale | Phase 2 Step C | Required | Design coherence |
| Minimum text size | Phase 2 Step C (confirmed in Step E) | Required | Readability guarantee |
| Confirmation | Auto-tracked | Required | Confirmed Decision Principle |

### Visual Direction

| Field | Source | Required | Purpose |
|-------|--------|----------|---------|
| Mood keywords | Phase 2 Step C | Required | AI prompt generation, overall feel |
| Style reference | Phase 2 Step C | Required | AI prompt style direction |
| Imagery approach | Phase 2 Step C | Required | AI tool selection guidance |
| Visual metaphors | Phase 2 Step C | Optional | Symbolic element direction |
| Constraints | Phase 2 Step C | Optional | Negative prompt guidance |
| Confirmation | Auto-tracked | Required | Confirmed Decision Principle |

### Content Map

| Field | Source | Required | Purpose |
|-------|--------|----------|---------|
| Headline/Subheadline | Phase 2 Step D | Required | Layout hierarchy |
| Body copy | Phase 2 Step D | Required | Space estimation, layout |
| Call to action | Phase 2 Step D | Optional | Visual emphasis zone |
| Data/statistics | Phase 2 Step D | Optional | Infographic/data viz zones |
| Image zones | Phase 2 Step D | Required | AI prompt generation targets |
| Content priority | Phase 2 Step D | Required | Visual hierarchy ordering |
| Confirmation | Auto-tracked | Required | Confirmed Decision Principle |

### Technical Specifications

| Field | Source | Required | Purpose |
|-------|--------|----------|---------|
| Dimensions | Phase 2 Step E | Required at top level (shared default) OR per-variant when Variants is set | Layout grid foundation |
| Orientation | Phase 2 Step E | Required at top level (shared default) OR per-variant when Variants is set | Layout direction |
| Resolution | Phase 2 Step E | Required at top level (shared default) OR per-variant when Variants is set | Image quality requirements |
| Bleed/Safe area | Phase 2 Step E | Conditional (print); per-variant override allowed for platform UI overlays / crop zones | Print production safety; platform-specific overlay safety |
| Output format | Phase 2 Step E | Required at top level (shared default) OR per-variant when Variants is set | File delivery |
| Platform | Phase 2 Step E | Required at top level (shared default) OR per-variant when Variants is set | Design constraints |
| Image generation tools | Phase 2 Step E | Optional input (also an optional Phase 4 chain trigger — see Phase 4 chain extensions) | Enables tool-specific prompt optimization via runtime research; this field's value (including `codex` or its absence) shapes the optional Phase 4 render-chain consent prompt (`poster-render`, `social-graphics-render`, etc.) but never substitutes for user consent. The "Required" column carries two semantics for this row: the field is *optional as input* (a brief is valid without it), and *optional as a chain trigger* (the chain is always offered with explicit consent regardless of the value). |
| Variants | Phase 2 Step E | Required when Target medium is multi-variant (e.g., `social-graphics`); omit for single-canvas media (e.g., `poster`) | Per-variant overrides for Dimensions/Orientation/Resolution/Output format/Platform/Safe area. Each variant id MUST appear in the whitelist defined in `Target medium aliases`. Any field a variant omits falls back to the top-level shared default. |
| Confirmation | Auto-tracked | Required | Confirmed Decision Principle |

### Decision Log

- Tracks confirmation status of each brief section
- Records which interview step produced each decision
- Sections marked `unconfirmed` are excluded from Phase 4 generation
- The designer may offer professional recommendations for unconfirmed sections,
  clearly labeled as suggestions

---

## Usage in Phase 4

| Domain Skill | Primary Brief Sections |
|-------------|----------------------|
| Poster | All sections; Dimensions critical for layout |
| Social graphics | All sections; Variants + per-variant Technical Specs critical for multi-canvas layout. Each variant produces its own Layer 1/2/3 sub-block within a single social_graphics_spec.md. |

Additional domains (brochure, infographic, frontend) will be mapped
when their skills are implemented.

## Target medium aliases

Domain skills MUST canonicalize the user-facing `Target medium` value
to one of the canonical values below before validation.
`design-analysis`, `design-extraction`, `design-interview`, and
`brief-generation` all apply the same normalization.

| User-facing input (case-insensitive) | Canonical value | Implied Variants (if any) |
|--------------------------------------|-----------------|---------------------------|
| `poster`, `포스터` | `poster` | (none — single canvas) |
| `brochure`, `leaflet`, `pamphlet`, `브로슈어` | `brochure` | (none) |
| `infographic`, `infographics`, `인포그래픽` | `infographic` | (none) |
| `frontend`, `web`, `website`, `ui` | `frontend` | (none) |
| `social-graphics`, `social graphics`, `social graphic`, `social media`, `social`, `sns`, `소셜` | `social-graphics` | (user picks variants in Step E) |
| `instagram post`, `ig post`, `인스타 포스트`, `인스타그램 포스트` | `social-graphics` | `[instagram-post]` |
| `instagram story`, `ig story`, `인스타 스토리`, `인스타그램 스토리` | `social-graphics` | `[instagram-story]` |
| `youtube thumbnail`, `yt thumbnail`, `유튜브 썸네일`, `썸네일` | `social-graphics` | `[youtube-thumbnail]` |

**Variant id whitelist** (canonical kebab-case): `instagram-post`,
`instagram-story`, `youtube-thumbnail`. Filesystem representation
translates kebab to snake (`s/-/_/g`, one-way) per
`skills/brief-generation/references/output-file-rules.md`.

If a Target medium value cannot be mapped to the canonical set, the
brief generator and consumer skills MUST fail with a repair prompt
that lists this alias table — never silently coerce.

If only one variant is implied, the brief MAY still set the full
canonical Variants list (post + story + thumbnail) and ask the user
in Step E whether to widen the set; the implied variant is the
**default selection** for that Step E confirmation.

## Phase 4 Chain Extensions

Some domain skills support optional chain-tail extensions that produce
additional artifacts. Chain triggers consult brief fields to shape the
user-facing consent prompt — but never substitute for explicit consent.

| Extension | Consulted field | Effect |
|-----------|-----------------|--------|
| poster-render | Image generation tools | After the poster spec is saved, optionally render raw zone PNGs via the codex CLI's imagegen tool. Always presents a one-time consent prompt before rendering. |
| social-graphics-render | Image generation tools | After the social graphics spec is saved, optionally render raw zone PNGs per variant via the codex CLI's imagegen tool. Iterates variant-outer / zone-inner with a single session-level consent prompt that discloses the total call count (Σ zones across all variants — variants may have differing zone counts). |

Trigger semantics for `poster-render`:

- The chain is **always offered after the poster spec is saved** (never
  silently dispatched). The brief's `Image generation tools` field
  shapes the consent-prompt wording — codex listed → straightforward
  confirmation; non-codex tools listed → override confirmation noting
  the tool mismatch; empty / `none specified` → confirmation with a
  brief-update suggestion — but the user always answers explicitly.
- The chain is also gated by the codex plugin's installation: if the
  codex plugin is not installed (or its runtime is incomplete), the
  chain skips silently with a one-line notice.

Trigger semantics for `social-graphics-render`:

- Identical structure to `poster-render` — always offered after the
  spec is saved, codex plugin presence pre-flighted, consent prompt
  branched on `Image generation tools` field state.
- The consent prompt additionally discloses the planned call count
  (`across N variants, K total codex calls` where K is the sum of
  per-variant zone counts — variants may have differing zone
  counts, so the formula is Σ not multiplication) so the user can
  weigh cost before committing.
- Reuses the same `Image generation tools` field as the trigger.
  This is **not** an overload of a different signal — the field's
  purpose (which image-gen tool the user plans to use) applies
  identically to social graphics. See "Convention for new chain
  extensions" below.

**Convention for new chain extensions**: introduce a dedicated trigger
field rather than overloading an existing one. The current `Image
generation tools` field is **shared** by `poster-render` and
`social-graphics-render` because the signal is genuinely the same
(declares which image-gen tool the user plans to use), not because
of backward compatibility — both chains consume that same semantic
input. New chains that need a *different* signal (e.g., a layout-
optimization chain that should consult a "Layout style" field) MUST
add a new brief field whose name reflects the chain's purpose, not
its surface similarity to an existing field.

See `skills/poster-render/SKILL.md` and
`skills/social-graphics-render/SKILL.md` for full dispatch logic
(codex pre-flight, Tool dispatch decision text, and the per-zone /
per-variant gate).

---

## Brief Validation Rules

When a domain skill receives a brief file, validate:

1. **Structure**: All required sections present.
2. **Medium match**: `Target medium` (after alias normalization per
   the table above) includes the requested output type.
3. **Confirmation coverage**: Project Info, Color Palette, Typography, Visual Direction,
   Content Map, and Technical Specifications must all be `confirmed` or `partial`.
   Sections with `unconfirmed` or `skipped` status block generation — offer to
   re-run the interview for those sections.
4. **Staleness**: If `Created` date is more than 30 days ago, warn the user
   that design trends and project context may have changed.
5. **Variants** (when `Target medium` is multi-variant such as
   `social-graphics`):
   - The `Variants:` block MUST be present and non-empty.
   - Every variant id MUST be in the whitelist defined in
     `Target medium aliases` (`instagram-post`, `instagram-story`,
     `youtube-thumbnail`).
   - Duplicate variant ids in the same brief (including aliases that
     normalize to the same canonical id) are a validation error.
   - Each variant's effective Technical Specifications (its own
     overrides ∪ top-level shared defaults) MUST contain
     `Dimensions`, `Orientation`, `Resolution`, `Output format`,
     `Platform`. Missing both per-variant and shared is a validation
     error with a repair prompt naming the variant + missing field.

If validation fails, offer to run the full pipeline to create a new brief.

---

## Raw Input Handling

When a domain skill is invoked without a brief (raw design request):

1. The skill must **not** generate output directly from raw input.
2. Instead, trigger the full pipeline: analysis > interview > brief > domain output.
3. Reason: Skipping consultation produces generic results that miss the client's
   actual needs and brand identity.

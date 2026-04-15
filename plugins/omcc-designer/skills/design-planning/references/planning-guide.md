# Design Planning Guide

Detailed criteria for creating design strategies and deliverable roadmaps.
This guide is consulted during planning execution — it is not a runtime artifact.

---

## Deliverable Type Taxonomy

### Print media

| Type | Best for | Content capacity | Typical dimensions |
|------|----------|------------------|--------------------|
| Poster | Single key message, visual impact | Low (headline + few lines) | A3, A2, A1, custom |
| Brochure | Multiple topics, detailed info | Medium-high (multi-panel) | A4 tri-fold, bi-fold |
| Flyer | Quick information, handout | Low-medium (single page) | A5, A4 |
| Banner | Event/trade show presence | Very low (brand + tagline) | Various roll-up sizes |
| Business card | Contact info, brand presence | Very low (name + contact) | 90x50mm standard |

### Digital media

| Type | Best for | Content capacity | Typical dimensions |
|------|----------|------------------|--------------------|
| Social media post | Engagement, announcements | Very low (image + short text) | Platform-specific |
| Social media story | Ephemeral, behind-scenes | Very low (vertical image/video) | 1080x1920 |
| Email header | Campaign, newsletter | Low (banner image) | 600-800px wide |
| Web banner | Advertising, promotion | Very low (CTA + image) | IAB standard sizes |
| Infographic | Data, processes, comparisons | High (scrollable) | Variable height |

### Brand assets

| Type | Best for | Content capacity | Typical dimensions |
|------|----------|------------------|--------------------|
| Logo | Brand identity | N/A (mark) | Vector, multiple sizes |
| Brand guide | Consistency reference | High (comprehensive) | PDF document |
| Presentation template | Internal/external decks | Medium per slide | 16:9, 4:3 |
| Letterhead | Official correspondence | Low (header/footer) | A4, Letter |

### Web/app

| Type | Best for | Content capacity | Typical dimensions |
|------|----------|------------------|--------------------|
| Landing page | Conversion, launch | Medium-high | Responsive |
| Hero section | First impression | Low (headline + CTA) | Full-width |
| App screens | Functional interface | Varies | Device-specific |

---

## Deliverable Identification Signals

### From project type

| Project type | Typical deliverables |
|-------------|---------------------|
| Product launch | Poster, landing page, social media set, email header, press kit |
| Event promotion | Poster, flyer, social media set, banner, program/brochure |
| Brand refresh | Logo, brand guide, business card, letterhead, presentation template |
| Campaign | Social media set, web banners, email headers, landing page |
| Conference | Poster, program brochure, name badges, signage, presentation template |
| Internal communication | Infographic, presentation, email header, intranet banner |

### From content signals

- **Multiple messages for different audiences** → Multiple pieces needed
- **Sequential information** → Infographic or brochure
- **Single strong message** → Poster or social media
- **Interactive elements** → Web/app
- **Brand establishment** → Logo + brand guide first

### From user language

- "materials" (plural) → Multiple deliverables
- "campaign" → Coordinated set across channels
- "launch" → Time-sequenced deliverables
- "rebrand" / "refresh" → Brand identity first, then rollout
- "everything" → Full audit of needs

---

## Dependency Patterns

### Common dependency chains

```
Brand identity (logo, colors, fonts)
    ↓
Brand guide
    ↓
Marketing materials (posters, brochures, social media)
    ↓
Campaign-specific variations
```

```
Content strategy (key messages, audience mapping)
    ↓
Hero piece (poster or landing page — establishes visual language)
    ↓
Supporting pieces (social media, email, banners — follow hero style)
```

### Dependency rules

1. **Brand identity before everything**: If no brand guide exists,
   establishing visual identity is always the first deliverable.
2. **Hero piece before supporting pieces**: The largest/most complex
   piece sets the visual language. Smaller pieces follow it.
3. **Content before layout**: If content is not finalized, design
   cannot proceed. Flag content dependencies explicitly.
4. **Print before digital adaptations**: Print requires higher resolution
   and precise dimensions. Digital can be derived from print assets.
5. **Independent pieces can be parallel**: Pieces with no content or
   style dependencies can be designed simultaneously.

### Identifying the hero piece

The hero piece is the deliverable that:
- Has the most visual real estate
- Will be seen by the largest audience
- Sets the tone for all other pieces
- Is the most complex to design

Typically: poster > landing page > brochure > social media

---

## Shared Design Decisions

### What should be shared

These decisions must be consistent across all deliverables in a project:

| Decision | Why shared | Varies when |
|----------|-----------|-------------|
| Color palette | Brand recognition | Sub-brand or audience-specific variations |
| Primary/secondary fonts | Visual consistency | Technical constraints (web-safe fonts) |
| Brand personality | Unified voice | Never varies within a project |
| Imagery approach | Visual coherence | Medium-specific constraints (icon vs photo) |
| Tone | Consistent experience | Audience-specific pieces |

### What can vary

These decisions typically vary per deliverable:

| Decision | Why varies |
|----------|-----------|
| Dimensions | Medium-specific |
| Layout/grid | Content volume and medium |
| Content priority | Different key messages per piece |
| Typography scale | Viewing distance and medium |
| Image zones | Layout-dependent |
| Technical specs | Print vs digital, platform |

### Shared decision format

For each shared decision confirmed during planning, document:
- **Decision**: What was decided (e.g., "Primary color: #2563EB")
- **Rationale**: Why (e.g., "Aligns with existing brand, conveys trust")
- **Scope**: Which deliverables this applies to (usually "all")
- **Exceptions**: Any deliverables exempt from this decision

---

## Roadmap Document Structure

```markdown
# Design Plan

## Project Overview
- Project: [project title]
- Created: YYYY-MM-DD
- Client: [client name or "personal"]
- Goal: [what the project must achieve]
- Total deliverables: [count]

## Shared Design Decisions
- Brand personality: [adjectives]
- Color palette: [hex values with roles] — [confirmed/to be decided]
- Typography: [font names] — [confirmed/to be decided]
- Visual style: [approach] — [confirmed/to be decided]
- Tone: [description] — [confirmed/to be decided]

## Deliverables

### Phase 1: [phase name — e.g., "Brand Foundation"]
1. **[Deliverable name]** — [type]
   - Purpose: [what this piece achieves]
   - Audience: [target]
   - Key content: [main elements]
   - Complexity: [low/medium/high]
   - Dependencies: none

### Phase 2: [phase name — e.g., "Hero Piece"]
2. **[Deliverable name]** — [type]
   - Purpose: [what this piece achieves]
   - Audience: [target]
   - Key content: [main elements]
   - Complexity: [low/medium/high]
   - Dependencies: Phase 1 deliverables

### Phase 3: [phase name — e.g., "Supporting Materials"]
3. **[Deliverable name]** — [type]
   ...

## Recommended Sequence
1. [First deliverable] — [rationale: "establishes visual language"]
2. [Second deliverable] — [rationale: "builds on hero piece style"]
3. ...

## Next Step
Start with: [deliverable name]
Command: `/omcc-designer:start [brief description]`
Context: Apply shared design decisions from this plan.
```

---

## Complexity Assessment

### Per-deliverable complexity

| Factor | Low | Medium | High |
|--------|-----|--------|------|
| Content volume | < 5 elements | 5-15 elements | > 15 elements |
| Brand constraints | Full guide exists | Partial guide | No guide |
| Technical requirements | Standard format | Some custom needs | Complex specs |
| Imagery needs | Stock/simple | Custom illustration | Multi-zone composition |
| Stakeholder count | 1 decision maker | 2-3 stakeholders | Committee |

### Project-level complexity

- **Small** (1-3 deliverables, existing brand): Single session feasible
- **Medium** (4-7 deliverables, partial brand): Multiple sessions, phase-by-phase
- **Large** (8+ deliverables, new brand): Project management recommended,
  hero piece first, then batch remaining

---

## Multi-Medium Handling

When analysis detects multi-medium needs (from design-analysis Area 4):

1. **Confirm scope**: "Your project would benefit from [list of media].
   Would you like to plan all of these?"
2. **Avoid scope creep**: If the user only needs one piece now,
   plan only that piece but note future opportunities.
3. **Budget awareness**: More deliverables = more design time.
   Prioritize by impact if the user has constraints.
4. **Reuse opportunities**: Identify which elements can be reused
   across pieces (hero image, color palette, key copy).

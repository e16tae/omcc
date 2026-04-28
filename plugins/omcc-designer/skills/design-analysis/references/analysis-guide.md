# Design Analysis Guide

Detailed criteria for analyzing design requests in Phase 1.
This guide is consulted during analysis execution — it is not a runtime artifact.

---

## Analysis Area 1: Project Context

Extract the following from the user's request:

### Purpose identification
- **Direct statement**: User explicitly says "I need a poster for..."
- **Indirect signal**: Context implies purpose (e.g., "our conference next month"
  implies promotional purpose)
- **Purpose categories**: Promotional / Informational / Educational / Branding /
  Event / Product launch / Internal communication / Social media / Portfolio

### Audience identification
- **Direct statement**: "for developers", "targeting young professionals"
- **Industry signals**: Technical terms suggest professional audience;
  casual language suggests general audience
- **Age/demographic hints**: Platform mentions (TikTok → younger, LinkedIn → professional)
- **If absent**: Flag as low confidence, prepare interview exploration

### Key message extraction
- Identify the single most important thing the design must communicate
- List supporting messages in priority order
- Flag if no clear message is identifiable — this is a critical gap

### Deadline signals
- Explicit dates ("by next Friday", "for March 15th event")
- Implicit urgency ("urgent", "ASAP", "for next week's...")
- Convert relative dates to absolute using current date

---

## Analysis Area 2: Brand Context

### Existing brand detection
- **Explicit**: User mentions brand name, company, or provides brand guide
- **Implicit**: Use of specific colors, fonts, or style references that suggest
  existing brand guidelines
- **No brand**: Personal project, event without established identity, or
  the user explicitly states no brand exists

### Industry identification
- Extract industry from context (tech, education, healthcare, food, finance, etc.)
- Industry affects: color psychology, imagery conventions, tone expectations
- If unclear, prepare industry-exploration question for interview

### Brand personality estimation
- Based on language tone, purpose, and audience:
  - Professional language + corporate purpose → serious, trustworthy, established
  - Casual language + event purpose → fun, energetic, approachable
  - Technical content + developer audience → clean, modern, precise
- Express as 2-3 adjectives

### Confidence criteria
- **High**: Brand name mentioned, existing guidelines referenced, clear industry
- **Medium**: Industry identifiable but no brand specifics
- **Low**: No brand context at all — personal/new project

---

## Analysis Area 3: Visual Direction

### Style signal extraction
- **Explicit references**: "like Apple's style", "minimalist", "retro"
- **Content-driven signals**: Data-heavy → infographic style; photo-heavy → editorial;
  text-heavy → typographic
- **Platform signals**: Instagram → bold/visual; LinkedIn → professional/clean;
  Print → detailed/high-resolution

### Mood estimation
- Derive from purpose + audience + tone:
  - Conference poster → professional, energetic, inspiring
  - Product launch → sleek, innovative, premium
  - Community event → warm, inclusive, friendly
  - Technical documentation → clean, structured, trustworthy
- Express as 3-5 mood keywords

### Imagery approach estimation
- **Photography**: When realism matters (products, people, places)
- **Illustration**: When concepts matter (ideas, processes, stories)
- **Abstract**: When mood matters more than specifics (backgrounds, patterns)
- **Mixed**: When multiple content types coexist

### Confidence criteria
- **High**: Explicit style references, clear mood language
- **Medium**: Mood derivable from context but no explicit references
- **Low**: No visual direction signals — will need full interview exploration

---

## Analysis Area 4: Medium Estimation

### Medium selection logic

Evaluate the best-fit medium based on:

| Signal | Poster | Brochure | Infographic | Frontend | Social graphics |
|--------|--------|----------|-------------|----------|-----------------|
| Single key message | Strong | Weak | Weak | Weak | Strong |
| Multiple topics | Weak | Strong | Medium | Strong | Medium (multi-variant) |
| Sequential data/process | Weak | Medium | Strong | Medium | Weak |
| Interactive elements needed | N/A | N/A | N/A | Strong | N/A |
| Physical distribution | Strong | Strong | Weak | N/A | Weak |
| Online sharing | Medium | Weak | Strong | Strong | Strong |
| Rich text content | Weak | Strong | Medium | Strong | Weak (text overlay external) |
| Visual impact priority | Strong | Medium | Medium | Medium | Strong |
| Platform-specific aspect ratio | Weak | Weak | Medium | Weak | **Strong** (1:1, 9:16, 16:9) |
| Multiple deliverables from one campaign | Weak | Weak | Weak | Weak | **Strong** (post + story + thumbnail) |

### Content volume assessment
- **Low** (headline + few lines + 1-2 images): Poster or single social variant
- **Medium** (multiple sections, moderate text): Brochure or infographic
- **High** (extensive text, multiple pages): Brochure or frontend
- **Data-heavy** (statistics, processes, comparisons): Infographic
- **Multi-platform single message** (one campaign across IG/YT): Social graphics

### Multi-medium detection
- If content naturally spans multiple media, flag for interview discussion
- Example: "I need materials for our product launch" → poster + brochure + frontend
- Example: "Promote this event on Instagram and YouTube" → social-graphics with multiple variants

### Target medium alias normalization

When the user names a medium, normalize to a canonical value before
recording the estimate. Refer to `skills/brief-generation/references/design-brief-spec.md`
"Target medium aliases" section for the authoritative mapping.

Highlights for analysis-time signal extraction:

| User phrase (case-insensitive, multilingual) | Canonical Target medium | Implied Variants (if any) |
|----------------------------------------------|-------------------------|---------------------------|
| `Instagram post`, `IG post`, `인스타 포스트`, `인스타그램 포스트` | `social-graphics` | `[instagram-post]` |
| `Instagram story`, `IG story`, `인스타 스토리`, `인스타그램 스토리` | `social-graphics` | `[instagram-story]` |
| `YouTube thumbnail`, `YT thumbnail`, `유튜브 썸네일`, `썸네일` | `social-graphics` | `[youtube-thumbnail]` |
| `social media`, `social`, `SNS`, `소셜` | `social-graphics` | (none implied — Step E asks user to pick) |

If the user names multiple variants in one phrase ("Instagram post +
YouTube thumbnail"), the implied Variants list is the union. The
implied list is the **default selection** the interview's Step E
will confirm — never silently locked in.

### Confidence criteria
- **High**: User explicitly states medium ("I need a poster", "Instagram post 만들어줘")
- **Medium**: Content and purpose clearly fit one medium
- **Low**: Content could work in multiple media — interview needed

---

## Analysis Area 5: Complexity Assessment

### Content volume scoring
- Count distinct text elements (headlines, body sections, captions)
- Count image/visual zones needed
- Count data points or statistics
- **Low**: < 5 elements total
- **Medium**: 5-15 elements
- **High**: > 15 elements

### Technical constraint density
- Print specifications (bleed, CMYK, specific dimensions)
- Platform requirements (responsive, social media sizes)
- Brand compliance requirements
- Accessibility requirements (WCAG contrast, alt text)
- **Low**: 0-1 constraints
- **Medium**: 2-3 constraints
- **High**: 4+ constraints

### Design decision complexity
- How many subjective choices need to be made?
- Existing brand guide reduces decisions (colors, fonts pre-decided)
- No brand guide increases decisions significantly
- **Low**: Brand guide exists, single medium, clear content
- **Medium**: Partial brand context, some decisions needed
- **High**: No brand context, multiple media, content structure undecided

---

## Sparse Input Handling

When the request is minimal (e.g., "make a poster for next week's event"):

1. **Do not fabricate context.** Assign low confidence to all areas.
2. **Extract what exists**: "poster" → medium confirmed. "next week" → deadline.
   "event" → purpose category.
3. **Flag everything else** as requiring interview exploration.
4. **Set interview strategy to exploration mode**: More open questions,
   more designer recommendations, longer interview expected.
5. **Present a brief summary**: "I identified that you need a poster for
   an event next week. The interview will cover the details I need to
   create an effective design."

Do not guess brand colors, audience demographics, or visual style from
insufficient evidence. These become interview topics, not analysis outputs.

---

## Analysis Output

The analysis carries forward these items to Phase 2:

- **Project context**: purpose, audience, key messages, deadline — each with confidence level and evidence
- **Brand context**: brand name, industry, personality adjectives, brand guide existence — each with confidence
- **Visual direction**: style signals with sources, mood keywords, imagery approach — with confidence
- **Medium estimation**: estimated medium, confidence, alternatives considered, multi-medium flag
- **Complexity assessment**: content volume, constraint density, decision complexity, overall level
- **Interview strategy**: per-area question density (derived from confidence levels), estimated duration, areas requiring exploration

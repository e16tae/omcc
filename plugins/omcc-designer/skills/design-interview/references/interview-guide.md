# Design Interview Guide

Detailed consultation guidelines for the Phase 2 design interview.
This guide encodes the design expertise that makes the consultation valuable.

---

## Step A: Project Context & Goals

### Opening the consultation

Begin with a warm, professional introduction that sets expectations:

> "I'll guide you through the design process step by step. I'll share my
> professional recommendations at each stage — you just need to confirm
> what feels right or tell me what to adjust. Let's start with the basics."

### Purpose confirmation

Present the Phase 1 purpose analysis with confidence level:
- **High confidence**: "Based on your request, this is a [promotional poster]
  for [your tech conference]. Is that right?"
- **Low confidence**: "I'm reading this as [promotional material] for
  [an event]. Can you tell me more about what this is for?"

### Audience refinement

Key questions to calibrate visual decisions:
- Age range (affects color vibrancy, font choices, imagery style)
- Professional vs general (affects formality, terminology density)
- Cultural context (affects color meaning, imagery appropriateness)
- Viewing context (distance for posters, device for digital, reading time)

### Core design challenge

Every effective design answers ONE primary question. Extract it:
- "What should someone DO after seeing this?" (CTA-driven)
- "What should someone FEEL after seeing this?" (brand/mood-driven)
- "What should someone KNOW after seeing this?" (information-driven)

This answer drives all subsequent design decisions.

---

## Step B: Brand Identity

### Existing brand assessment

If the user has an existing brand:
1. Confirm brand colors (get hex codes if possible)
2. Confirm brand fonts
3. Ask about brand guide/style guide existence
4. Note any flexibility ("we use blue but can be creative with shades")

If no existing brand:
1. Skip to brand personality
2. This gives maximum creative freedom — note this positively

### Brand personality framework

Present personality as a spectrum, not a binary:

| Spectrum | Left | Right |
|----------|------|-------|
| Energy | Calm, serene | Energetic, dynamic |
| Formality | Formal, established | Casual, approachable |
| Complexity | Minimal, clean | Rich, detailed |
| Warmth | Cool, professional | Warm, human |
| Innovation | Traditional, trusted | Modern, cutting-edge |

Ask the user to indicate where their brand falls on 2-3 most relevant spectrums.
Or propose positions based on analysis and ask for confirmation.

---

## Step C: Visual Direction & Color

### Color palette construction

Follow this decision tree:

1. **Existing brand colors** → Build palette around them
   - Extend with complementary secondary/accent colors
   - Ensure sufficient contrast ratios (WCAG AA minimum)

2. **Brand personality drives new palette** →
   - **Professional/trustworthy**: Blues, deep greens, navy, slate
   - **Energetic/bold**: Bright reds, oranges, electric blue, magenta
   - **Creative/playful**: Purple, teal, coral, lime
   - **Natural/organic**: Earth tones, sage, terracotta, cream
   - **Premium/luxury**: Black, gold, deep purple, charcoal
   - **Clean/modern**: White-dominant, single accent color, grays

3. **Palette structure** (always propose complete):
   - Primary (60%): Dominant brand color — backgrounds, large areas
   - Secondary (30%): Supporting color — sections, cards, accents
   - Accent (10%): Attention color — CTAs, highlights, icons
   - Neutral light: Backgrounds, white space
   - Neutral dark: Text, borders

4. **Present with hex codes and usage**:
   > "Here's my recommended palette:
   > - Primary: #2563EB (royal blue) — main background sections
   > - Secondary: #1E40AF (deep blue) — headers, navigation
   > - Accent: #F59E0B (amber) — call-to-action buttons, highlights
   > - Neutral light: #F8FAFC — content backgrounds
   > - Neutral dark: #1E293B — body text
   >
   > This palette says 'trustworthy and professional' (blue) with 'energy
   > and optimism' (amber accent). The contrast ratio meets accessibility standards."

### Color psychology reference

| Color | Associations | Best for |
|-------|-------------|----------|
| Blue | Trust, stability, professionalism | Corporate, tech, finance |
| Red | Energy, urgency, passion | Food, entertainment, sales |
| Green | Growth, nature, health | Health, environment, finance |
| Purple | Creativity, luxury, wisdom | Beauty, education, premium |
| Orange | Enthusiasm, friendliness, confidence | Youth, food, creative |
| Yellow | Optimism, clarity, warmth | Children, food, caution |
| Black | Sophistication, power, elegance | Luxury, fashion, tech |
| White | Cleanliness, simplicity, space | Minimal, medical, tech |
| Pink | Playfulness, romance, compassion | Beauty, fashion, charity |

### Typography selection

Match font personality to brand personality:

| Brand Feel | Heading Font Type | Body Font Type |
|-----------|------------------|----------------|
| Corporate/serious | Serif (e.g., Playfair Display) | Sans-serif (e.g., Inter) |
| Modern/clean | Geometric sans (e.g., Poppins) | Humanist sans (e.g., Source Sans) |
| Creative/artistic | Display (e.g., Space Grotesk) | Sans-serif (e.g., Work Sans) |
| Traditional/elegant | Transitional serif (e.g., Lora) | Serif (e.g., Crimson Text) |
| Technical/precise | Monospace accent (e.g., JetBrains Mono) | Sans-serif (e.g., IBM Plex Sans) |
| Playful/casual | Rounded sans (e.g., Nunito) | Rounded sans (e.g., Quicksand) |

**Font pairing rules**:
- Contrast > similarity — pair serif heading with sans body, or vice versa
- Same font family at different weights can work for minimal designs
- Maximum 3 fonts per design (heading, body, accent)
- Verify free availability (Google Fonts preference for accessibility)

### Visual style direction

Present mood board description using precise visual vocabulary:
- **Photography style**: Natural light / studio / aerial / close-up / lifestyle
- **Illustration style**: Flat / isometric / hand-drawn / line art / 3D
- **Composition**: Centered / asymmetric / grid-based / full-bleed / white-space-heavy
- **Texture**: Clean/flat / textured / gradient / grain / glassmorphism

---

## Step D: Content & Layout

### Content audit

For each content element, confirm:
1. Exact text (or close approximation)
2. Visual priority rank (1 = most prominent)
3. Fixed vs flexible (can this be shortened?)

### Image zone definition

For each zone that needs AI-generated imagery:
1. **What it depicts**: Subject, scene, mood
2. **Purpose**: Background atmosphere / hero image / supporting visual / icon
3. **Approximate area**: Fraction of total design (1/3, 1/4, full-bleed, etc.)
4. **Style match**: Must match the confirmed visual direction

### Content overload thresholds

| Medium | Max text elements | Max image zones | Warning sign |
|--------|------------------|-----------------|--------------|
| Poster | 3-4 (headline, sub, body, CTA) | 1-2 | >5 lines body copy |
| Brochure | 8-12 per panel | 3-6 total | >3 panels needed |
| Infographic | 10-15 data points | 5-10 | >20 data points |
| Frontend | No strict limit | No strict limit | >5 scroll-lengths |

When content exceeds thresholds:
1. Flag to user: "This is more content than a single poster can effectively
   communicate at viewing distance."
2. Propose solutions:
   - Edit down: "Can we focus on the top 3 messages?"
   - Split: "This would work as a poster + handout combination"
   - Switch medium: "An infographic would handle this data better"
3. Accept user's decision — they may have context you don't

---

## Step E: Technical Requirements

### Dimension recommendations by medium

| Medium | Common Dimensions | Orientation |
|--------|------------------|-------------|
| Poster (A3) | 297 x 420 mm | Portrait |
| Poster (A2) | 420 x 594 mm | Portrait |
| Poster (24x36) | 610 x 914 mm | Portrait |
| Social media (Instagram) | 1080 x 1080 px | Square |
| Social media (Story) | 1080 x 1920 px | Portrait |
| Web banner | 1920 x 600 px | Landscape |

### Print specifications
- **Resolution**: 300 DPI minimum for print
- **Color mode**: CMYK for professional print
- **Bleed**: 3mm (standard) — content extends past trim line
- **Safe area**: 5mm from trim — keep critical content inside
- **Minimum text size**: 8pt body, 6pt fine print at A3; scale up for larger formats

### Digital specifications
- **Resolution**: 72-150 DPI for screen
- **Color mode**: RGB (sRGB for web)
- **No bleed needed**: Edge-to-edge is literal
- **Minimum text size**: 16px body for web, 14px minimum for mobile

### Image generation tools
Ask which tools the user plans to use for image generation:
> "Which image generation tools will you be using? For example, Midjourney,
> NanoBanana, Hixfield, or others. This lets me optimize the image descriptions
> for your specific tools."

If the user specifies tools: record in the brief for tool-specific prompt
optimization during Phase 4.
If the user is unsure or has no preference: mark as "none specified" —
Phase 4 will provide the designer's vision description that works with any tool.

---

## Edge Case Handling

### Very short answers
Accept concise responses. Do not ask for elaboration unless the answer
creates ambiguity. "Yes" and "looks good" are complete answers.

### "I don't know" responses
1. Accept immediately — never re-ask or pressure
2. Mark field as unconfirmed
3. Offer a professional recommendation:
   > "No problem. Based on what we've discussed, I'd recommend [X].
   > We can note this as a suggestion in the brief and you can
   > change it later."
4. Move on to the next question

### Contradictory information
When a new answer contradicts a confirmed decision (including cross-section
contradictions, e.g., Step B brand personality vs Step C visual direction):
1. Flag immediately with specific reference:
   > "I notice this conflicts with what we discussed in Step B —
   > you mentioned preferring a minimal corporate look, but neon
   > maximalist is quite different."
2. **Attempt professional synthesis**: propose how both elements could coexist:
   > "That said, a restrained layout with neon accent elements could work —
   > minimal structure with bold color highlights. Would that capture your vision?"
3. If user accepts synthesis: record as the confirmed direction
4. If user rejects synthesis and chooses one side: update the confirmed decision,
   reflect the change cumulatively in subsequent steps
5. If user insists on keeping both contradictory elements as-is: **accept the
   user's direction**. Record the designer's concern in the brief's Supplementary
   Notes ("Designer note: visual direction may conflict with brand personality —
   client chose to proceed with both elements"). Proceed with the interview.
   Do not re-ask or loop.
6. Do not silently override any earlier confirmed decision

### Small or solo projects
If the user is designing for themselves (personal brand, small event):
- Skip corporate brand questions
- Focus on personality and preferences
- Use more casual language
- Reduce interview length — combine Steps B and C
- Simplify Step E: ask "Where will this be used?" and auto-fill technical
  specs from the platform. Present as confirmation:
  "Instagram? I'll set this up as 1080x1080px, RGB, 72DPI. Sound good?"

### Expert users
If the user demonstrates design knowledge:
- Reduce explanations
- Accept technical terms without elaboration
- Allow more open-ended responses
- Skip basic recommendations they've already addressed

---

## Interview Output

The interview carries forward these confirmed decisions to Phase 3:

- **Step A**: project title, client, purpose, audience, key messages (with priority), tone, core challenge, deadline
- **Step B**: brand name, logo (description + file reference), brand guide existence, brand personality adjectives, existing colors (hex), existing fonts
- **Step C — Color Palette**: primary/secondary/accent/neutral-light/neutral-dark (hex + name + role), palette rationale, color mode (CMYK/RGB/both)
- **Step C — Typography**: heading/body/accent fonts (font + weight + style), pairing rationale, minimum text size
- **Step C — Visual Direction**: mood keywords, style reference, imagery approach, visual metaphors, constraints (what to avoid)
- **Step D**: headline, subheadline, body copy, CTA, data/statistics, image zones (id + description + purpose + area fraction), content priority order
- **Step E**: dimensions, orientation, resolution, bleed, safe area, output format, platform, image generation tools

Each item is tagged as confirmed or unconfirmed based on user responses during the interview.

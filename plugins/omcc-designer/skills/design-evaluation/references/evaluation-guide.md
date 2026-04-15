# Design Evaluation Guide

Detailed criteria for evaluating design quality across multiple perspectives.
This guide is consulted during evaluation execution — it is not a runtime artifact.

---

## Severity Rating System

### Critical

Issues that render the design non-functional or harmful:
- Text illegible at intended viewing distance
- Accessibility violation that excludes users (contrast ratio < 3:1 for large text, < 4.5:1 for body text)
- Brand identity violation that misrepresents the organization
- Content error that communicates incorrect information
- Technical specification that prevents production (wrong color mode, insufficient resolution)

### High

Issues that significantly degrade design effectiveness:
- Visual hierarchy failure (primary message is not the most prominent element)
- Color palette conflict (clashing colors that create visual discomfort)
- Typography readability problem (font too small, poor contrast, overly decorative for body text)
- Brand inconsistency in primary elements (wrong logo color, incorrect brand font)
- Layout imbalance that directs attention away from key content

### Medium

Issues that reduce design quality but don't prevent communication:
- Minor spacing inconsistencies (uneven margins, misaligned elements)
- Typography scale issues (insufficient size differentiation between hierarchy levels)
- Color usage inconsistency (accent color used inconsistently across similar elements)
- Brand inconsistency in secondary elements (tone mismatch, style drift)
- Composition issues (awkward whitespace, crowded zones)

### Low

Minor refinement opportunities:
- Subtle alignment differences (1-2px offsets)
- Typography micro-adjustments (letter spacing, line height fine-tuning)
- Color fine-tuning (slight saturation or brightness adjustments)
- Whitespace optimization
- Element proportion refinements

---

## Perspective 1: Brand Consistency

### What to check

1. **Color adherence**: Are the brand's primary, secondary, and accent colors
   used correctly? Are any off-brand colors present?
2. **Typography adherence**: Are the designated brand fonts used? Are weights
   and styles consistent with the brand guide?
3. **Logo usage**: Is the logo placed correctly? Correct clear space?
   Correct version (color/mono/reversed) for the background?
4. **Tone alignment**: Does the overall visual tone match the brand personality?
   (e.g., a "playful" brand shouldn't look "corporate")
5. **Imagery style**: Does the photography/illustration style match
   the brand's established visual language?

### When no brand guide exists

If no brand guide is available:
- Evaluate internal consistency instead (does the design establish and follow
  its own visual language?)
- Note the absence of a brand guide as an observation
- Recommend establishing brand guidelines

### Severity guidance

- **Critical**: Logo misuse that could cause legal issues
- **High**: Wrong brand colors in primary elements, wrong fonts
- **Medium**: Tone mismatch, imagery style drift
- **Low**: Minor brand element inconsistencies in supporting areas

---

## Perspective 2: Visual Hierarchy

### What to check

1. **Primary focal point**: Is there a clear "first look" element?
   Is it the most important content?
2. **Reading flow**: Does the eye move naturally through the content
   in the intended order? Test with squint test or blur test.
3. **Size contrast**: Is there sufficient size difference between
   hierarchy levels? (Minimum 1.25x scale ratio recommended)
4. **Color contrast for hierarchy**: Do color choices reinforce
   the intended reading order? (Brighter/warmer colors attract attention first)
5. **Grouping**: Are related elements visually grouped?
   Are unrelated elements visually separated?
6. **Focal competition**: Are there multiple elements competing
   for primary attention? (Competing focal points weaken all of them)

### Hierarchy scoring

Rate the visual hierarchy on three dimensions:
- **Clarity**: Can the hierarchy be identified within 3 seconds?
- **Correctness**: Does the hierarchy match the content priority?
- **Flow**: Does the eye move smoothly without dead ends?

### Severity guidance

- **Critical**: No discernible hierarchy (everything is equally prominent)
- **High**: Primary message is not the most prominent element
- **Medium**: Hierarchy exists but flow has interruptions or dead ends
- **Low**: Hierarchy is functional but could be more decisive

---

## Perspective 3: Accessibility

### What to check

1. **Color contrast** (WCAG 2.1 guidelines):
   - Body text (< 18pt): minimum 4.5:1 contrast ratio against background
   - Large text (≥ 18pt or 14pt bold): minimum 3:1 contrast ratio
   - Non-text elements (icons, borders, controls): minimum 3:1 against adjacent colors
2. **Color independence**: Is information conveyed by color alone?
   (Should have secondary indicators: shape, pattern, label, position)
3. **Color blindness**: Are critical distinctions visible under common
   color vision deficiencies? (Deuteranopia, Protanopia, Tritanopia)
   - Red/green combinations are highest risk
   - Blue/yellow combinations are secondary risk
4. **Text readability**: Minimum text sizes for medium:
   - Print poster (1m+ viewing): ≥ 24pt body, ≥ 48pt headline
   - Print brochure (hand-held): ≥ 9pt body, ≥ 14pt headline
   - Digital (screen): ≥ 16px body, ≥ 24px headline
5. **Text over images**: Is text placed on a consistent-tone area
   of the image? Is there sufficient contrast? (Overlay or text shadow?)

### Contrast ratio estimation

Without tooling, estimate contrast ratio visually:
- **Excellent (7:1+)**: Black text on white, or vice versa
- **Good (4.5:1+)**: Dark gray on white, white on medium blue
- **Borderline (3:1-4.5:1)**: Medium gray on white, light text on medium background
- **Poor (< 3:1)**: Light gray on white, pastel on pastel

Flag borderline cases and recommend verification with a contrast checker tool.

### Severity guidance

- **Critical**: Body text fails 4.5:1 contrast, critical info conveyed by color alone
- **High**: Large text fails 3:1 contrast, red/green-only distinction for key info
- **Medium**: Non-text elements fail 3:1, text over images without contrast aid
- **Low**: Near-borderline contrast, minor color-independence improvements

---

## Perspective 4: Typography

### What to check

1. **Font count**: Maximum 2-3 font families in a single design.
   More creates visual noise.
2. **Weight usage**: Are font weights used consistently?
   (e.g., Bold for headings, Regular for body, not random)
3. **Size hierarchy**: Is there a clear typographic scale?
   Recommended minimum scale ratio: 1.25x between levels.
4. **Line length**: Optimal: 45-75 characters per line for body text.
   Too long reduces readability, too short creates choppy reading.
5. **Line height**: Body text: 1.4-1.6x font size. Headlines: 1.1-1.3x.
6. **Letter spacing**: Tight letter spacing for headlines is acceptable;
   body text should use default or slightly increased spacing.
7. **Font pairing quality**: Do the fonts complement each other?
   Common patterns: serif heading + sans body, geometric + humanist.
8. **Readability at size**: Is each text element readable at its
   displayed size for the intended viewing distance?

### Severity guidance

- **Critical**: Body text too small to read at intended distance
- **High**: Poor font pairing (fonts that clash), inconsistent weight usage
- **Medium**: Typographic scale inconsistency, suboptimal line length
- **Low**: Minor spacing refinements, line height adjustments

---

## Perspective 5: Color System

### What to check

1. **Palette coherence**: Do the colors form a harmonious palette?
   (Complementary, analogous, triadic, or monochromatic)
2. **Role clarity**: Is each color's role clear?
   (Primary for brand, secondary for sections, accent for emphasis)
3. **Usage consistency**: Is the same color used for the same purpose
   throughout the design? (e.g., accent always means emphasis)
4. **Saturation balance**: Are saturation levels consistent within
   the palette? (Mixing vivid and muted creates discord)
5. **Temperature consistency**: Is the overall palette warm, cool,
   or neutral? Mixed temperature is intentional or accidental?
6. **Background-foreground relationships**: Do backgrounds and foreground
   elements create clear, comfortable contrast?
7. **Color volume**: How much of each color is used? The 60-30-10 rule
   (dominant-secondary-accent) is a starting guideline.

### Severity guidance

- **Critical**: Colors that create visual vibration (clashing high-saturation complementaries at equal volume)
- **High**: Incoherent palette (colors with no harmonic relationship), role confusion
- **Medium**: Minor saturation imbalance, inconsistent usage, proportion issues
- **Low**: Subtle color fine-tuning opportunities

---

## Perspective 6: Layout & Composition

### What to check

1. **Grid consistency**: Is there an underlying grid structure?
   Are elements aligned to it consistently?
2. **Margin consistency**: Are margins uniform? Do they create
   a comfortable frame for the content?
3. **Spacing rhythm**: Is the spacing between elements consistent
   and proportional? (e.g., same spacing between all section breaks)
4. **Alignment**: Are text blocks and images aligned to common edges
   or a grid? Mixed alignment creates visual chaos.
5. **Whitespace**: Is negative space used intentionally?
   Is it balanced (not all on one side)?
6. **Balance**: Is the visual weight distributed appropriately?
   (Symmetrical or asymmetrical — but intentional)
7. **Proximity**: Are related items grouped closely?
   Are unrelated items separated?
8. **Bleed and safe area**: (Print only) Is critical content within
   the safe area? Do background elements extend to bleed?

### Severity guidance

- **Critical**: Content outside safe area (will be cut in print), severe misalignment
- **High**: No discernible grid, inconsistent margins, poor balance
- **Medium**: Minor alignment issues, uneven spacing, whitespace imbalance
- **Low**: Subtle grid refinements, spacing micro-adjustments

---

## Finding Format

Each finding should follow this structure:

```
### [Severity]: [One-line summary]

**Perspective**: [Which evaluation perspective]
**Location**: [Where in the design — zone, element, section]
**Issue**: [What is wrong and why it matters — concrete, specific]
**Recommendation**: [Professional suggestion for improvement]
```

---

## Positive Observations

After listing all issues, note what the design does well:
- Strong design choices worth preserving in any revision
- Elements that effectively serve the design's purpose
- Techniques or patterns that demonstrate design skill

Present as a bulleted list: "What works well in this design:"

---

## Input Type Considerations

### Evaluating a design brief

When the input is a design_brief.md, evaluate the specification itself:
- Are the decisions internally consistent?
- Is the color palette harmonious on paper?
- Do the typography choices work together?
- Are the technical specs appropriate for the target medium?
- Are there gaps that will cause problems in production?

### Evaluating a poster specification

When the input is a poster_spec.md, evaluate:
- Layout structure: grid choice, zone proportions, spatial logic
- Typography specification: readability at scale, hierarchy clarity
- AI prompt quality: will the prompts produce appropriate imagery?
- Overall composition: balance, hierarchy, flow

### Evaluating a visual (image/Figma/PDF)

Use the design-extraction skill's approach to identify elements,
then evaluate the rendered result across all perspectives.
This is the most comprehensive evaluation type.

### Evaluating brief + visual together

The strongest audit: compare specification against execution.
- Does the rendered design match the brief's intent?
- Are the specified colors actually used?
- Does the layout follow the specified grid?
- Are there deviations and are they improvements or errors?

# Design Extraction Guide

Detailed criteria for extracting design elements from existing visuals.
This guide is consulted during extraction execution — it is not a runtime artifact.

---

## Input Type Handling

### Image files (PNG, JPG, JPEG, GIF, WEBP, SVG)

1. Read the image using the Read tool (multimodal analysis)
2. If the image is low resolution or unclear, note limitations in confidence levels
3. For SVG files, also read the raw XML to extract exact color values and font declarations

### Figma URLs

1. Parse the URL to extract fileKey and nodeId:
   - `figma.com/design/:fileKey/:fileName?node-id=:nodeId` → convert `-` to `:` in nodeId
   - `figma.com/design/:fileKey/branch/:branchKey/:fileName` → use branchKey as fileKey
2. Call `get_design_context` with fileKey and nodeId for structured design data
3. Call `get_screenshot` for visual reference
4. Figma extractions yield the highest confidence because design data includes
   exact values (hex colors, font names, sizes, spacing)

### PDF files

1. Read the PDF using the Read tool with pages parameter
2. If multi-page, extract from each page and note page-specific elements
3. PDFs often contain embedded font and color information — note these when visible

### Multiple inputs

When multiple files/URLs are provided:
1. Extract from each input independently
2. Identify shared elements (same colors, fonts, layout patterns) → likely brand elements
3. Identify differences → likely context-specific choices
4. Flag conflicts for interview resolution

---

## Extraction Area 1: Content & Purpose

### Text content extraction

1. **Headline**: The largest/most prominent text element
2. **Subheadline**: Secondary prominent text
3. **Body copy**: Smaller text blocks — transcribe key points, not every word
4. **Call to action**: Buttons, emphasized action text
5. **Data/statistics**: Numbers, charts, data visualizations
6. **Captions/labels**: Small supporting text

For each text element, note its approximate position and visual weight.

### Purpose inference

Based on visible content and design style:
- **Promotional**: Product images, pricing, CTA buttons, brand-forward layout
- **Informational**: Dense text, data visualizations, structured sections
- **Event**: Date/time/location prominent, speaker photos, schedule
- **Branding**: Logo-centric, minimal text, mood-driven imagery
- **Educational**: Step-by-step layout, diagrams, explanatory text

Mark purpose as LOW confidence — this is inference, not observation.

### Audience inference

Based on visual cues:
- Typography style (playful → younger, serif → traditional/professional)
- Color intensity (vibrant → energetic audience, muted → professional)
- Content complexity (technical jargon → specialists, simple language → general)
- Imagery style (corporate photos → business, illustrations → creative/casual)

Mark audience as LOW confidence — this is inference, not observation.

### Confidence criteria

- **High**: Text is clearly legible, content type is unambiguous
- **Medium**: Text partially legible, purpose derivable but not certain
- **Low**: Text illegible, purpose/audience must be inferred from visual cues alone

---

## Extraction Area 2: Brand Identity

### Color extraction

This is the highest-value extraction — colors can be observed precisely.

1. **Identify all distinct colors** used in the design
2. **Map to roles**:
   - Primary: The dominant brand color (largest area or most prominent usage)
   - Secondary: Supporting color used for contrast or sections
   - Accent: Used sparingly for emphasis (CTAs, highlights, icons)
   - Neutral light: Background or light text areas
   - Neutral dark: Text color or dark backgrounds
3. **Extract hex values**: Estimate from visual observation. For Figma inputs,
   use exact values from design data.
4. **Note color relationships**: Complementary, analogous, monochromatic, triadic

When extracting from images (not Figma), acknowledge that hex values are
approximations. State: "These are visually estimated hex values — please
verify against your brand guide if available."

### Typography extraction

1. **Identify font families**: Name the fonts if recognizable.
   Common fonts (Helvetica, Arial, Roboto, Montserrat, Inter, Playfair Display,
   etc.) can be identified visually with medium confidence.
2. **Note weights and styles**: Bold, regular, light, italic
3. **Map to roles**: Heading font, body font, accent/decorative font
4. **Note size relationships**: Approximate ratio between heading and body sizes
5. **Identify font pairing pattern**: Serif + sans-serif, two sans-serifs, etc.

If font identification is uncertain, describe the characteristics instead:
"A geometric sans-serif, similar to Montserrat or Poppins"

### Logo and brand marks

1. **Logo presence**: Is a logo visible? Where is it positioned?
2. **Logo description**: Shape, colors, text content, style (wordmark, icon, combo)
3. **Brand name**: Extract from logo or prominent text
4. **Brand consistency signals**: Does the design appear to follow brand guidelines?

### Brand personality inference

Based on the overall visual impression:
- Color psychology (warm → friendly, cool → professional, neutral → sophisticated)
- Typography personality (geometric → modern, humanist → approachable, serif → traditional)
- Composition (structured → corporate, asymmetric → creative, minimal → premium)
- Express as 2-3 adjectives

### Confidence criteria

- **High**: Colors extracted from Figma/SVG data, fonts explicitly named in source
- **Medium**: Colors visually estimated from image, fonts visually identified
- **Low**: Colors ambiguous (gradients, overlays), fonts unrecognizable

---

## Extraction Area 3: Visual Style

### Design approach identification

Classify the overall design approach:
- **Flat design**: Clean shapes, no shadows/gradients, minimal texture
- **Material/skeuomorphic**: Shadows, depth, physical metaphors
- **Illustrative**: Hand-drawn or vector illustration-driven
- **Photographic**: Photo-dominant with text overlay
- **Typographic**: Text as the primary visual element
- **Data-driven**: Charts, graphs, infographics
- **Mixed**: Combination of approaches

### Mood extraction

Derive mood from visual elements:
- **Color mood**: Warm/cool, saturated/muted, high-contrast/low-contrast
- **Composition mood**: Structured/organic, dense/spacious, symmetric/dynamic
- **Imagery mood**: Literal/abstract, serious/playful, static/energetic
- Express as 3-5 mood keywords

### Imagery approach

- **Photography**: Stock vs custom, lifestyle vs product, people vs objects
- **Illustration**: Flat vs detailed, character vs abstract, hand-drawn vs vector
- **Abstract**: Geometric patterns, gradients, textures
- **Icons**: Line style, filled, outline weight, consistency

### Constraints observation

Note what the design deliberately avoids:
- Absence of certain colors despite brand opportunity
- Consistent avoidance of certain imagery types
- Deliberate whitespace/negative space choices

### Confidence criteria

- **High**: Design approach is clear and consistent
- **Medium**: Style identifiable but some elements conflict
- **Low**: Design is inconsistent or too complex to classify

---

## Extraction Area 4: Layout Structure

### Grid and composition

1. **Grid type**: Single column, multi-column (2, 3, 4+), asymmetric, free-form
2. **Alignment**: Left-aligned, centered, mixed
3. **Content zones**: Identify distinct regions and their purposes
   - Header zone (logo, navigation, title)
   - Hero zone (primary visual/message)
   - Content zones (body text, supporting elements)
   - Footer zone (CTA, contact, legal)

### Visual hierarchy

Identify the reading order — what the eye sees first, second, third:
1. **Primary focal point**: Largest/most contrasting element
2. **Secondary elements**: Supporting information
3. **Tertiary elements**: Details, fine print
4. **Flow direction**: Z-pattern, F-pattern, linear, circular

### Spatial relationships

- **Margins**: Edge spacing (generous → premium, tight → dense/urgent)
- **Padding**: Internal spacing between elements
- **Proximity grouping**: Which elements are grouped together
- **Separation methods**: Lines, space, color blocks, contrast

### Zone mapping

For each identified zone, document:
- **Purpose**: background / hero / supporting / icon / text-block / data-viz
- **Approximate position**: Top-left, center, bottom-right, full-width, etc.
- **Approximate size**: Fraction of total area (e.g., "~40% of design area")
- **Content**: What is in the zone (photo, illustration, text, empty space)

### Confidence criteria

- **High**: Clear grid structure, obvious hierarchy, well-defined zones
- **Medium**: General structure identifiable but zones overlap or are ambiguous
- **Low**: Free-form or complex layout resistant to zone decomposition

---

## Extraction Area 5: Technical Properties

### Dimensions

- **From metadata**: If available (Figma, PDF properties), extract exact dimensions
- **From visual**: Estimate aspect ratio and approximate size
- **Units**: Note whether pixel-based (digital) or physical (print: mm, inches)

### Orientation

- **Portrait**: Height > width
- **Landscape**: Width > height
- **Square**: Approximately equal

### Color mode

- **Print indicators**: CMYK color space, bleed marks, crop marks
- **Digital indicators**: RGB colors, screen-resolution imagery, UI elements
- **If uncertain**: Default to RGB (most common), note uncertainty

### Resolution estimate

- **From metadata**: Exact DPI/PPI if available
- **From visual**: High quality (sharp edges, detailed) vs low quality (artifacts, blur)
- **Print standard**: 300 DPI minimum
- **Digital standard**: 72-150 DPI / pixel dimensions

### Medium identification

Based on dimensions, content, and format:
- **Poster**: Large format, single surface, visual impact-focused
- **Brochure**: Multi-page/fold, text-heavy sections
- **Infographic**: Vertical scroll, data-heavy, sequential sections
- **Social media**: Platform-specific dimensions (1080x1080, 1200x630, etc.)
- **Web/frontend**: Responsive indicators, navigation elements, interactive zones

### Confidence criteria

- **High**: Metadata available (Figma, PDF with properties)
- **Medium**: Dimensions estimated from aspect ratio, medium identifiable
- **Low**: No metadata, unclear format, ambiguous medium

---

## Extraction Output

The extraction produces data in five areas for seamless interview handoff:

- **Areas 1–3**: identical semantics to design-analysis output (Project context,
  Brand context, Visual direction). The interview consumes them unchanged.
- **Area 4 (Medium identification)**: renamed from analysis's "Medium estimation"
  to reflect observation (not inference) on visual input; same semantic role.
- **Area 5 (Layout & content structure)**: replaces analysis's "Complexity
  assessment" with concrete layout data (grid, zones, hierarchy). Interview
  depth is driven by per-area confidence levels, so the separate complexity
  axis is unnecessary for extraction.

- **Project context**: Extracted text elements, inferred purpose and audience — each with confidence level
- **Brand context**: Hex colors with roles, identified fonts, logo description, personality — each with confidence
- **Visual direction**: Design approach, mood keywords, imagery type — with confidence
- **Medium identification**: Identified medium, dimensions, orientation, color mode — with confidence
- **Layout & content structure**: Grid type, zone map, visual hierarchy — with confidence
- **Confirmation strategy**: Per-area question density (driven by confidence levels)
- **Gaps**: Fields that cannot be extracted visually and must be collected in interview
  (typically: project title, client name, deadline, core challenge, detailed purpose/audience)

### Mapping extraction to brief sections

| Extraction area | Brief section(s) | Expected confidence |
|----------------|-------------------|---------------------|
| Project context | Project Info, Content Map | LOW (inferred) |
| Brand context | Brand Identity, Color Palette, Typography | HIGH (observed) |
| Visual direction | Visual Direction | HIGH (observed) |
| Medium identification | Technical Specifications | MEDIUM (metadata-dependent) |
| Layout & content structure | Content Map (zones, priority) | HIGH (observed) |

### Unextractable fields

These fields cannot be determined from visual inspection alone and must
always be collected during the interview:

- Project title (user naming choice)
- Client name
- Deadline
- Core challenge (what someone should DO/FEEL/KNOW)
- Detailed audience description
- Font pairing rationale (design intent, not observation)
- Palette rationale (design intent, not observation)
- Image generation tool preferences

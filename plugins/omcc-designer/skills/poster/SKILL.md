---
name: poster
description: "Generates poster design specifications from a design brief, including layout structure, typography placement, and AI image generation prompts with tool-specific optimization. Handles input detection, brief validation, and full pipeline fallback. Use this skill when the user needs a poster design spec, poster layout, or AI prompts for poster imagery."
---

# Phase 4: Poster Design Specification

Generate a complete poster design specification from the design brief.
Output is organized into three distinct layers: layout structure,
typography specification, and designer's vision for AI image generation.

## When auto-activated (without /start or /poster command)

### Input detection

Determine whether the input is a brief file path or a raw design request:
- **File path**: Exists on disk and contains "# Design Brief" header → brief mode
- **Otherwise** → raw request mode

### Brief mode

1. Read the brief file
2. Validate per `design-brief-spec.md` validation rules
3. **Medium gate**: Verify the brief's Target medium includes "poster".
   If not: inform the user that the brief targets a different medium,
   the brief has been saved, and offer to re-run the interview for poster.
4. **Confirmed field check**: Before using any brief field, verify it is not
   tagged `[unconfirmed]`. Unconfirmed fields must not be used in poster
   generation. If a required field is unconfirmed, ask the user to confirm
   it before proceeding.
5. If validation passes: proceed to Step 1 (Layout structure)
6. If validation fails: inform the user of specific issues and offer to
   run the full pipeline

### Raw request mode

A design consultation is required before poster generation.
Inform the user and offer to run `/omcc-designer:start` for the full pipeline.
Direct generation from raw input is not permitted per `CLAUDE.md`.

### Step 1: Layout structure

Using the brief's technical specifications and content map:

1. Define the grid system (columns, rows, gutters)
2. Map content elements to grid zones
3. Establish visual hierarchy through size and position
4. Define bleed and safe area boundaries (print) or edge margins (digital)
5. Create zone map with labeled areas

Follow layout guidelines in `skills/poster/references/poster-guide.md`.

### Step 2: Typography specification

Using the brief's typography and content map:

1. Assign fonts, sizes, weights, and colors to each text element
2. Define position coordinates (grid zone reference, alignment)
3. Specify line height, letter spacing, and text transforms
4. Ensure minimum text size compliance per technical specs
5. Verify contrast ratios for each text-on-background combination

This layer is applied by the human designer — not included in AI prompts.

### Step 3: Designer's vision and AI image generation

For each image zone defined in the layout:

1. Compose a comprehensive **Designer's Vision** description covering:
   position & space, subject & elements, mood & atmosphere, lighting,
   color direction, composition & framing, style & texture, constraints
2. Add an **Image Generation Guide** with universal tips for translating
   the vision into any image generation tool
3. If the brief specifies image generation tools (Technical Specifications):
   - **Research each tool** using WebSearch for current best practices
   - Generate **tool-specific optimized prompts** based on the research
   - Include the research date for freshness tracking

Follow vision and prompt construction rules in
`skills/poster/references/poster-guide.md`.

### Step 4: Output assembly and save

1. Combine all three layers into the poster spec document
2. Run the quality checklist
3. Save to ./output/YYYY-MM-DD_project-name/poster_spec.md
4. Present the spec to the user with a summary

---

## When invoked by command (/start, /poster)

### When invoked by /start

The brief is already generated in Phase 3. Skip input detection and
brief mode — proceed directly from Step 1 with the Phase 3 brief.

**Medium gate**: Before Step 1, verify the brief's Target medium includes
"poster". If not: inform the user that the confirmed medium is different,
the brief has been saved, and the corresponding domain skill is not yet
available.

### When invoked by /poster

Full procedure as auto-activated mode: input detection, brief validation
or raw request handling, then Steps 1-4. After saving, output the
completion message and offer modification assistance.

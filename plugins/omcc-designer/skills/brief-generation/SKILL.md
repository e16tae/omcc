---
name: brief-generation
description: "Generates a design brief artifact from Phase 2 interview results. The brief is the sole handoff artifact for Phase 4 domain-specific output. Only user-confirmed decisions are encoded. Use this skill when interview results need to be consolidated into a formal brief."
---

# Phase 3: Design Brief Generation

Convert Phase 2 interview results into a formal design brief following
the `design-brief-spec.md` format. The brief is the sole handoff artifact
for Phase 4 and must be self-contained for cross-session use.

## When auto-activated (without /start or /formalize command)

### Step 1: Assemble confirmed decisions

1. Collect all confirmed decisions from the interview
2. Identify unconfirmed fields — tag with `[unconfirmed]`
3. For unconfirmed fields with designer recommendations, include the
   recommendation clearly labeled as a suggestion

### Step 2: Generate the brief

Follow the structure defined in `design-brief-spec.md`:

1. **Project Info**: From Step A interview data
2. **Brand Identity**: From Step B interview data
3. **Color Palette**: From Step C — include hex codes, roles, rationale
4. **Typography**: From Step C — include fonts, weights, pairing rationale
5. **Visual Direction**: From Step C — mood, style, imagery approach
6. **Content Map**: From Step D — text content, image zones, priority
7. **Technical Specifications**: From Step E — dimensions, resolution, color mode
8. **Supplementary Notes**: Any additional context from the interview
9. **Decision Log**: Status tracking table for each section

### Step 3: Quality verification

Run the quality checklist from
`skills/brief-generation/references/brief-guide.md`:
- All confirmed items present
- No unconfirmed items encoded as confirmed
- Hex codes valid
- Dimensions consistent with medium
- Content map matches content priority
- Decision log accurate

### Step 4: Save and present

1. Save to ./output/YYYY-MM-DD_project-name/design_brief.md
2. Present a summary of the brief to the user
3. Ask: "Brief generated. Ready to proceed to [poster/brochure/etc.] design?"

---

## When invoked by command (/start, /formalize)

Same procedure as auto-activated mode.

The next step depends on the invoking command:
- **/start**: Auto-proceeds to Phase 4 (domain skill) after saving.
- **/formalize**: The brief is the final output. Pipeline ends after saving.

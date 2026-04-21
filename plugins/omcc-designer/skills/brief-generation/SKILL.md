---
name: brief-generation
description: "Generates a design brief artifact from Phase 2 interview results. The brief is the sole handoff artifact for Phase 4 domain-specific output. Only user-confirmed decisions are encoded. Primarily invoked as a chained step after the design-interview skill (via /omcc-designer:start or /omcc-designer:formalize)."
---

# Phase 3: Design Brief Generation

Convert Phase 2 interview results into a formal design brief following
`skills/brief-generation/references/design-brief-spec.md`. The brief is the
sole handoff artifact for Phase 4 and must be self-contained for cross-session use.

Only confirmed decisions are encoded — see
`skills/design-interview/references/confirmed-decision-principle.md` for the
estimation-vs-decision semantics. Unconfirmed items must be tagged
`[unconfirmed]`.

## When auto-activated (without /start or /formalize command)

### Step 1: Assemble confirmed decisions

1. Collect all confirmed decisions from the interview
2. Identify unconfirmed fields — tag with `[unconfirmed]`
3. For unconfirmed fields with designer recommendations, include the
   recommendation clearly labeled as a suggestion

### Step 2: Generate the brief

Follow the structure defined in `skills/brief-generation/references/design-brief-spec.md`:

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

1. Save to ./output/YYYY-MM-DD_project-name/design_brief.md — directory naming
   and sanitization per `skills/brief-generation/references/output-file-rules.md`.
2. Present a summary of the brief to the user.
3. Ask: "Brief generated. Ready to proceed to [poster/brochure/etc.] design?"

**Output language**: Write the brief file in the same language the user
used for the request (the plugin's internal documentation stays English, but
user-facing output matches the user's language).

---

## When invoked by command (/start, /formalize)

Same procedure as auto-activated mode.

The next step depends on the invoking command:
- **/start**: Auto-proceeds to Phase 4 (domain skill) after saving.
- **/formalize**: The brief is the final output. Pipeline ends after saving.

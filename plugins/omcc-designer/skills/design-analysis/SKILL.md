---
name: design-analysis
description: "Automatically analyzes a user's design request to identify purpose, audience, key messages, brand context, and visual direction. Produces structured analysis with confidence levels that feed the design interview. Use this skill when the user submits a design request or describes what they need designed. Trigger phrases include 'I need a poster for', 'design something for', 'help me design', 'analyze my design request'."
---

# Phase 1: Design Analysis

Analyze the user's design request to extract structured context that drives
the interview phase. Analysis results are estimations, not decisions —
they become decisions only after user confirmation in Phase 2.

## When auto-activated (without /start or /plan command)

### Step 1: Parse the request

1. Accept the design request as text input
2. Identify explicit statements (the user said it directly)
3. Identify implicit signals (tone of language, industry terms, context clues)
4. Flag missing information that will need interview clarification

### Step 2: Analyze across five areas

Follow the analysis guide (`skills/design-analysis/references/analysis-guide.md`)
to produce structured analysis:

1. **Project context**: Purpose, audience, key messages, deadline signals
2. **Brand context**: Existing brand signals, industry, personality indicators
3. **Visual direction**: Style hints, mood signals, reference points
4. **Medium estimation**: Best-fit medium based on content and purpose
5. **Complexity assessment**: Content volume, technical requirements, constraint density

Assign confidence levels (high/medium/low) to each area based on
evidence density in the original request.

### Step 3: Generate interview strategy

Based on analysis confidence levels, determine interview question density:
- **High confidence areas**: Quick confirmation questions (yes/no)
- **Medium confidence areas**: Targeted questions with proposed options
- **Low confidence/missing areas**: Open exploration with designer recommendations

### Step 4: Present analysis summary

Present the analysis to the user with:
- Key findings per area
- Confidence levels
- Preliminary recommendations
- What the interview will focus on

---

## When invoked by command (/start, /plan)

Same procedure as auto-activated mode.
Difference: Results are kept internally and not presented to the user.
Instead, convert analysis results into the next phase's input and auto-proceed.

The next phase depends on the invoking command:
- **/start**: Proceed to Phase 2 (design-interview skill)
- **/plan**: Proceed to design-planning skill (scope confirmation)

The receiving skill gets:
- Structured analysis data (all five areas)
- Confidence levels per area
- Recommended question density per area
- Identified gaps requiring exploration

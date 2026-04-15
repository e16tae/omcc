---
name: design-planning
description: "Creates a design strategy and deliverable roadmap for multi-piece projects. Identifies needed design artifacts, their dependencies, and shared design decisions. Use this skill when the user needs a design strategy before starting individual pieces. Trigger phrases include 'design plan', 'design strategy', 'design roadmap', 'plan my design project', 'what materials do I need'."
---

# Design Planning

Create a design strategy and deliverable roadmap for projects that require
multiple design artifacts or strategic sequencing.

This skill operates outside the standard 4-phase pipeline (analysis > interview >
brief > domain output). It produces a roadmap that feeds into subsequent
`/omcc-designer:start` invocations for individual deliverables.

Planning results are estimations, not decisions — they become decisions
only after user confirmation.

## When auto-activated (without /plan command)

### Step 1: Analyze the project scope

Use the design-analysis skill's approach to understand the project:

1. **Project context**: What is the initiative? What is the goal?
   (product launch, brand refresh, event promotion, campaign, etc.)
2. **Deliverable identification**: What design pieces are needed?
   Follow the planning guide (`skills/design-planning/references/planning-guide.md`)
   for deliverable type taxonomy and identification signals.
3. **Audience mapping**: Are different pieces targeting different audiences,
   or the same audience across touchpoints?
4. **Timeline signals**: Are there hard deadlines? Sequencing constraints?
   (e.g., "launch poster before event, then follow up with brochure")

### Step 2: Scope confirmation

Present the identified deliverables with rationale.
Follow the Interview Protocol Rules in `CLAUDE.md`:
Designer presents first, one step at a time, minimize user burden.

1. For each deliverable, explain why it is needed and what it accomplishes
2. Ask: "Does this capture everything you need? Anything to add or remove?"
3. Confirm the final deliverable list

### Step 3: Shared design decisions

Identify design decisions that should be consistent across all deliverables:

1. **Brand identity**: Is there an existing brand guide? If not, should one
   be established first?
2. **Color palette**: Same palette across all pieces, or variations?
3. **Typography**: Consistent font family across pieces?
4. **Visual style**: Unified visual language?
5. **Tone**: Same tone or varying by audience/context?

Present recommendations for each shared decision.
These shared decisions will pre-populate the design briefs for individual pieces.

### Step 4: Sequencing and dependencies

1. Identify dependencies between deliverables:
   - Which pieces must be designed first? (e.g., brand identity before marketing materials)
   - Which can be designed in parallel?
   - Which depend on content from other pieces?
2. Propose a sequencing order with rationale
3. Confirm timeline constraints

### Step 5: Generate the design roadmap

Produce a structured roadmap document:

1. **Project overview**: Title, goal, total deliverable count
2. **Shared design decisions**: Confirmed decisions that apply across all pieces
3. **Deliverable list**: Each deliverable with type, purpose, audience,
   key content, dependencies, and complexity
4. **Recommended sequence**: Ordered phases with rationale
5. **Next step**: Which deliverable to start with and why

### Step 6: Present and save

1. Present the roadmap summary to the user
2. Save to ./output/YYYY-MM-DD_project-name/design_plan.md
3. Offer to transition to `/omcc-designer:start` for the first deliverable

### Plan-to-start handoff

When the user transitions from a plan to `/omcc-designer:start` for an
individual deliverable, the shared design decisions from the plan serve
as pre-confirmed context for the analysis and interview phases:

- **Analysis phase**: Shared decisions provide high-confidence context,
  reducing the need for exploration
- **Interview phase**: Pre-confirmed decisions (colors, fonts, brand personality)
  are presented as confirmations rather than proposals
- The user provides the plan file path or references the plan's shared
  decisions when invoking `/omcc-designer:start`

---

## When invoked by command (/plan)

Same procedure as auto-activated mode.
Difference: Step 1 analysis results are kept internally and not exposed
to the user. Auto-proceed from analysis to planning consultation.

The planning consultation (Steps 2-4) follows the same interactive process
as auto-activated mode — user confirmation is required at each step.

After roadmap generation, present the full roadmap and offer to transition
to `/omcc-designer:start` for the first deliverable.

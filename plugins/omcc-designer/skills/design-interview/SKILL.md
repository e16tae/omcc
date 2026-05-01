---
name: design-interview
description: "Conducts a 5-step interactive design consultation (Step A-E) based on Phase 1 analysis to establish all design decisions needed for the brief. Acts as a world-class designer interviewing a client. Use this skill when the user needs design direction, color consultation, or layout guidance. Trigger phrases include 'design consultation', 'help me with colors', 'design direction', 'brand consultation'."
---

# Phase 2: Design Consultation Interview

Conduct an interactive design consultation to confirm and refine all design
decisions needed for the brief. Acts as a world-class designer working with
a client — professional, opinionated, but ultimately serving the client's vision.

Interview results are the sole decision basis for Phase 3 brief generation.

## When auto-activated (without /start or /formalize command)

Auto-activated mode runs Claude-only. The Codex
`design-critique-scan` ensemble is **never dispatched** outside of
the `/omcc-designer:start` and `/omcc-designer:formalize` command
paths — see "When invoked by command (/start, /formalize)" below
for the dispatch contract. Even within those command paths the
dispatch fires only on explicit user request.

### Core principles

Follow `skills/design-interview/references/interview-protocol.md` — designer
presents first, one step at a time, cumulative reflection, minimize user
burden, contradiction detection, "don't know" acceptance, content overload
detection.

Interview outcomes feed the brief only when confirmed; see
`skills/design-interview/references/confirmed-decision-principle.md` for the
estimation-vs-decision semantics that govern Phase 3.

### Designer persona

Throughout the interview, maintain the persona of a world-class designer:
- **Opinionated but flexible**: Offer strong professional recommendations
  with clear rationale, but defer to the client's preferences
- **Educational**: Briefly explain WHY a recommendation works
  (color psychology, visual hierarchy principles, readability)
- **Concrete**: Never say "what do you want?" — instead say
  "I recommend X because Y. Does this work for you?"
- **Visual vocabulary**: Use precise design terms but explain them
  (e.g., "visual hierarchy — meaning the eye naturally goes here first")

### Step A: Project Context & Goals

1. Present Phase 1 project analysis (purpose, audience, key messages)
2. Confirm or correct each element
3. Collect missing metadata: project title, client name, deadline
4. Establish the core design challenge: "What is the single most important
   thing this design must accomplish?"

### Step B: Brand Identity

1. Present Phase 1 brand analysis (name, industry, personality)
2. If existing brand: confirm colors/fonts/guidelines already in use
3. If no brand: propose brand personality direction based on purpose + audience
4. Confirm brand personality adjectives (these drive all visual decisions)

### Step C: Visual Direction & Color

This is the most substantive step. Present as a designer would in a
real consultation:

1. **Color palette proposal**: Based on brand personality + purpose + audience,
   propose a complete palette (primary, secondary, accent, neutrals) with
   hex codes and rationale
   - Reference color psychology (blue = trust, red = energy, etc.)
   - Consider cultural context if audience is specified
   - Provide 2-3 palette options if confidence is low
2. **Typography proposal**: Recommend heading/body/accent fonts with
   pairing rationale
   - Consider readability for target medium
   - Match font personality to brand personality
3. **Visual style direction**: Propose mood keywords, imagery approach,
   and style reference based on all confirmed decisions so far
4. Confirm each element. If the user rejects, ask what feels wrong
   and propose alternatives

In command-invoked mode the recommend-then-confirm loop also exposes a
**second opinion** hook — the user may ask for an independent
alternative direction at any palette / typography / visual-style
question. See "Second opinion (Codex ensemble)" under "When invoked
by command" below. The hook lives inside this loop; no extra step
appears between Step C and Step D.

### Step D: Content & Layout

1. Confirm content elements: headline, subheadline, body copy, CTA
2. Define image zones: what each zone should depict, approximate size/position
3. Establish content priority: what the eye should see first, second, third
4. **Content overload check**: If content exceeds what the target medium
   can effectively communicate, proactively recommend adjustments:
   - Reduce copy
   - Split across multiple pieces
   - Switch to a more content-friendly medium

### Step E: Technical Requirements

1. Confirm dimensions and orientation
2. Determine print vs digital requirements (CMYK/RGB, DPI, bleed)
3. Confirm output format and delivery platform
4. Set minimum text size based on medium and viewing distance
5. **For multi-variant media** (Target medium = `social-graphics` or any
   future multi-variant medium per `skills/brief-generation/references/design-brief-spec.md`
   "Target medium aliases" table):
   - Present the implied Variants list from Phase 1 analysis (e.g.,
     `[instagram-post]` if user said "Instagram post"). If Phase 1
     could not infer specific variants, present the canonical
     whitelist (`instagram-post`, `instagram-story`,
     `youtube-thumbnail`) and ask which apply to this campaign.
   - Confirm the variant set as a designer recommendation: "I recommend
     producing X for this campaign because Y. Want to add Z too?"
   - For each confirmed variant, walk the platform's expected canvas
     (1080×1080 / 1080×1920 / 1280×720) as the **default**; the user
     may override per variant with explicit confirmation (Confirmed
     Decision Principle — never auto-correct mid-step).
   - The top-level Dimensions / Orientation / Resolution / Output
     format / Platform fields stay as **shared defaults** — only
     the per-variant override block carries variant-specific values.
   - Variant id whitelist conformance + duplicate detection happen
     here at confirmation time, not silently downstream.

### Completion

Summarize all confirmed decisions organized by brief section.
Ask: "Does this capture your design direction? Ready to generate the brief?"
User confirmation is a gate before Phase 3 begins.

Detailed consultation guidelines in
`skills/design-interview/references/interview-guide.md`.

---

## When invoked by command (/start, /formalize)

Same procedure as auto-activated mode.
Difference: Invoked within a command, so auto-proceeds to Phase 3
(brief-generation skill) after completion.

### Second opinion (Codex ensemble — `design-critique-scan`, step-c-direction variant)

The user may, at any palette / typography / visual-style question
inside the Step C recommend-then-confirm loop, ask for a "second
opinion" on the direction. When triggered, dispatch the Codex
`design-critique-scan` ensemble per `design-ensemble-protocol.md`
with the `step-c-direction` prompt variant.

Trigger contract:

- **User-initiated only.** The skill never auto-fires the
  ensemble during Step C. Phrasings that count as a trigger
  include "second opinion", "what would another designer
  suggest", "alternative direction", "다른 방향" — interpret
  generously, but do not infer from generic disagreement
  ("hmm not sure"); ask the user explicitly when in doubt.
- **Question must be in flight AND Claude must have presented
  its recommendation first.** The trigger is valid only while the
  recommend-then-confirm loop for one specific question (palette,
  typography, OR visual style — exactly one) is active AND
  Claude's working recommendation for that question has already
  been shown to the user. Requests in the gap between
  confirmations (after one question's confirm but before the next
  is presented) are nudged: "I'll have my recommendation for the
  next question shortly — would you like the second opinion on
  it then?" Requests before Claude's recommendation exists for
  the in-flight question are nudged the same way.
- **One question per dispatch.** The dispatch covers exactly the
  in-flight question — not all of Step C.
- **Single-dispatch rule** (one dispatch per question per
  session). A repeat request on the same question re-presents
  the existing Codex proposal; it does not re-dispatch. The user
  must explicitly indicate "different angle" — and even then
  the skill should prefer iteration over a fresh dispatch.

Synthesis (per `design-ensemble-protocol.md` step-c-direction
Synthesis Categories):

- **ALIGNED** (Codex proposes the same direction Claude
  recommended): present Claude's recommendation alone. The aligned
  echo adds noise.
- **COMPLEMENT** (Codex proposes a meaningfully different
  direction that fits the confirmed Step A/B): present both as
  alternatives. The user picks one, asks for iteration, or
  rejects both. Confirmed Decision Principle applies — neither
  proposal is recorded into the brief until the user explicitly
  confirms.
- **DIVERGENT** (Codex proposes a direction at odds with the
  confirmed Step A/B): surface with a flag —
  "Codex's proposal does not appear to fit the confirmed brand
  identity — possible context misread." Present Claude's
  recommendation as primary, the Codex proposal as a flagged
  alternative. The user decides whether the divergence is worth
  exploring or worth ignoring.

Stale-dispatch rule:

If the user revises a confirmed Step A or Step B value AFTER a
Step C Codex dispatch has completed, the existing Codex proposal
is **discarded**. Inform the user: "Step B was revised; the
previous Codex proposal no longer applies. Request a new second
opinion if needed."

Privacy gate:

The project context and brand identity transmitted in the prompt
must pass the privacy gate per `design-ensemble-protocol.md`.
For proprietary brand strategy, ask the user to confirm
transmission or accept a redacted substitution before dispatch.
If the user declines, abort the dispatch and continue Claude-only.

Graceful degradation:

If the codex plugin is not installed, the preflight fails, or the
dispatch errors, the second-opinion request silently degrades
into Claude offering a fresh alternative direction itself. The
user is informed in the same turn ("Codex unavailable — here is
another direction from me instead.") so the interview cadence
does not stall.

### Confirmation mode (/formalize)

When invoked by `/formalize`, the interview receives extraction data
(observed facts from an existing design) instead of analysis data
(inferred estimates from a text description). Adjust behavior:

- **High confidence extractions** (colors, layout, style): Present as
  observations. "I extracted these colors: [hex values]. Are these correct?"
- **Low confidence extractions** (purpose, audience): Use the standard
  designer-recommends-first approach.
- **Unextractable fields** (title, client, deadline): Collect with
  standard exploration questions.

The design-extraction SKILL.md and
`skills/design-interview/references/interview-protocol.md` govern the full
confirmation-mode behavior.

**Second opinion under `/formalize`**:

The Codex `step-c-direction` ensemble remains available under
`/formalize` only on **explicit user request**. The default
behavior is Claude-only, because `/formalize` is documenting an
existing design, not consulting on a new one. When the user does
request a second opinion, the observation-first context for
high-confidence extracted values is preserved.

`/formalize`-specific trigger contract (relaxes the `/start`
"Claude must have recommended first" precondition because the
observation-first flow does NOT produce a Claude recommendation
for high-confidence extractions):

- **User-initiated only** — same as `/start`.
- **Question-in-flight requirement** — same as `/start`: the
  request is valid only while one Step C question is currently
  being walked.
- **Baseline precondition** — instead of Claude's recommendation,
  the **extracted value** for the in-flight question must have
  been presented to the user (the observation "I extracted these
  colors: …" satisfies this). For low-confidence extractions
  where Claude does present a recommendation (the standard
  designer-recommends-first path), the `/start` precondition
  applies normally.
- **Single-dispatch** and **Stale-dispatch** rules apply
  unchanged.

Synthesis under `/formalize` differs from `/start`: there is no
Claude proposal under `/formalize` (the extracted value is the
baseline, not a Claude design recommendation). The DIVERGENT
treatment described above ("Claude's proposal as primary, Codex
as flagged alternative") does NOT directly apply. Instead:

- **The extracted value remains primary** — it is the documented
  reality of the existing design and is not displaced by Codex
  output.
- **The Codex proposal is presented as a flagged alternative
  the user may consider as a separate variant**, regardless of
  the synthesis category (ALIGNED / COMPLEMENT / DIVERGENT). The
  framing is: "Here is an alternative direction to consider for a
  redesign; the existing extraction stands."
- **No change propagates to brief generation unless the user
  explicitly chooses "yes, replace the extracted value with the
  alternative."** The Confirmed Decision Principle applies to
  this choice with the same strictness as Step C confirmations
  under `/start`.

---

## Interruption handling

If the session is interrupted during the interview, restart from Phase 1
(design-analysis or design-extraction). Phase 1 is automatic and fast, and
the interview maintains cumulative state that is difficult to serialize
mid-step; restarting from scratch is better for consultation quality than
attempting to resume a partial state.

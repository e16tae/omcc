---
name: interview
description: "Conducts a 4-step interactive interview (Step A–D) based on Phase 1 analysis to confirm and correct transcript errors. Use this skill when the user asks to start the interview, confirm transcript content, or verify speakers. Trigger phrases include 'start interview', 'confirm transcript', 'verify speakers'."
---

# Phase 2: User Interview

Confirm and correct issues identified in Phase 1 through a 4-step interactive interview.
Interview results are the sole correction basis for Phase 3.

## When auto-activated (without /start or /correct command)

### Core principles

1. **LLM presents first**: Present analysis results and best guesses before asking. Never ask the user to fill in blanks.
2. **One step at a time**: Present each Step (A–D) in a separate message. Do not bundle multiple steps.
3. **Cumulative reflection**: Immediately apply confirmed results from each step to subsequent steps.
4. **Minimize user burden**: Prefer yes/no or short-answer question formats.
5. **Line number references**: Always cite original transcript line numbers when mentioning ambiguous segments.

Reason: The user may not be a meeting specialist. The most efficient structure is for the LLM
to perform analysis first and let the user only confirm or correct.

### Step A: Domain & context confirmation + metadata collection

1. Request meeting metadata (date, location, attendees, agenda)
2. Present Phase 1 domain estimation → user confirms/corrects

### Step B: Speaker mapping confirmation

1. Present speaker-to-attendee mapping with evidence from Phase 1
2. Confirm duplicate speaker candidates
3. Follow-up questions for unmapped speakers

### Step C: Term/keyword verification

1. Present Phase 1 suspicious terms in batches of 5–7
2. Each item includes line number, original text, correction candidate, context
3. Also handle related sentence boundary anomalies

### Step D: Core content verification

1. Present per-agenda content summary → user confirms/corrects/supplements
2. Identify unclear segments and collect supplementary information
3. Confirm action items (owners, deadlines)

### Completion

Summarize confirmed content and confirm proceeding to Phase 3.

Detailed guidelines in `skills/interview/references/interview-guide.md`.

---

## Interruption handling

If the session is interrupted during the interview, restart from Phase 1
(transcript-analysis). Phase 1 is automatic and fast, and the interview has
only 4 steps, so restart cost is low. The interview maintains cumulative
state that is difficult to serialize mid-step; restarting from scratch is
better for correction accuracy.

---

## When invoked by command (/start, /correct)

Same procedure as auto-activated mode.
Difference: Invoked within a command, so auto-proceeds to Phase 3 (transcript-correction skill) after completion.

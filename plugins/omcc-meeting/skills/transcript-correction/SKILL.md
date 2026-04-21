---
name: transcript-correction
description: "Applies Phase 2 interview results to the original transcript to generate a corrected transcript. Use this skill when the user asks to correct a transcript, generate a corrected version, or apply corrections. Trigger phrases include 'correct transcript', 'apply corrections', 'generate corrected version'."
---

# Phase 3: Corrected Transcript Generation

Apply confirmed corrections from Phase 2 interview to the original transcript.
The corrected transcript is the sole input for Phase 4 (minutes) and Phase 5 (report),
serving as the handoff artifact.

## When auto-activated (without /start or /correct command)

### Core principles

1. **Never modify the original transcript.** The corrected transcript is always a separate file.
2. **Only apply user-confirmed corrections.** Do not autonomously add corrections beyond what was confirmed in Phase 2.
3. **Preserve utterance order (chronological).** Even during speaker merges and sentence boundary reconstruction, maintain the original timeline.

Reason: If content changes without user awareness, document trustworthiness is compromised.

### Step 1: Apply corrections

Apply in strict order (each step affects the next):

1. **Speaker merge** — Replace speaker labels with real names, consolidate duplicates
2. **Term correction** — Replace confirmed terms, unify notation
3. **Sentence boundary reconstruction** — Merge split sentences, split merged sentences, insert speaker transitions
4. **Context supplementation** — Insert user-provided context with supplement tags

### Step 2: Generate header

Generate the corrected transcript header per `transcript-header-spec.md`.
Include meeting info, agenda, supplementary info, and correction summary.

### Step 3: Insert agenda markers

Insert `--- Agenda N: [name] ---` delimiters in the body at agenda boundaries
so Phase 4–5 can extract per-agenda utterances.

### Step 4: Quality verification

Run the quality checklist in `skills/transcript-correction/references/correction-guide.md`.

### Step 5: Save file

Save per `skills/transcript-correction/references/output-file-rules.md` to:
./output/YYYY-MM-DD_meeting-name/corrected_transcript.md

**Output language**: The corrected transcript **body** (utterances,
supplementary notes, prose) is written in the source transcript's language
(typically Korean). The **header structure and field names** defined in
`transcript-header-spec.md` must stay canonical (English field keys) so
Phase 4/5 can extract metadata reliably. Values inside the header (meeting
title, attendee names, agenda items) follow the source language.

Detailed guidelines in `skills/transcript-correction/references/correction-guide.md`.

---

## When invoked by command (/start, /correct)

Same procedure as auto-activated mode.
Differences:
- From `/omcc-meeting:start`: After saving, auto-proceeds to Phase 4 (minutes skill)
- From `/omcc-meeting:correct`: After saving, pipeline ends with save path notification

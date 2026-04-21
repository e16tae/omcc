---
description: Transcript correction only — analysis, interview, corrected transcript generation
argument-hint: Transcript file path or pasted text
---

# Correct

$ARGUMENTS

Use `TaskCreate` to register each phase and `TaskUpdate` to mark progress as the
pipeline advances.

---

## Phase 1: Initial Transcript Analysis

Follow the transcript-analysis skill's command-invoked mode (`skills/transcript-analysis/SKILL.md`).

Analysis results are kept internally and not exposed to the user.

---

## Phase 2: User Interview

Follow the interview skill's command-invoked mode (`skills/interview/SKILL.md`).

Proceed through Step A (metadata) → Step B (speakers) → Step C (terms) → Step D (content).
Get user confirmation after interview completion before proceeding to Phase 3.

---

## Phase 3: Corrected Transcript Generation

Follow the transcript-correction skill's command-invoked mode (`skills/transcript-correction/SKILL.md`).

Save the corrected transcript to ./output/YYYY-MM-DD_meeting-name/corrected_transcript.md.

Notify the user of the save path and how to generate minutes/report from it.

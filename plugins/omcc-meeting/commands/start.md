---
description: Full meeting documentation pipeline — analysis, interview, correction, minutes, report
argument-hint: Transcript file path or pasted text
---

# Start

$ARGUMENTS

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

---

## Phase 4: Meeting Minutes Generation

Follow the minutes skill's command-invoked mode (`skills/minutes/SKILL.md`).

Use the corrected transcript from Phase 3 as input.
Save meeting minutes to ./output/YYYY-MM-DD_meeting-name/minutes.md.

---

## Phase 5: Meeting Report Generation

Follow the report skill's command-invoked mode (`skills/report/SKILL.md`).

Use the corrected transcript from Phase 3 as input (independent of minutes).
Save meeting report to ./output/YYYY-MM-DD_meeting-name/report.md.

Output the pipeline completion message and offer modification assistance.

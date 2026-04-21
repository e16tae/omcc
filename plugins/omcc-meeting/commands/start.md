---
description: Full meeting documentation pipeline — analysis, interview, correction, minutes, report
argument-hint: Transcript file path or pasted text
---

# Start

$ARGUMENTS

Use `TaskCreate` to register each phase and `TaskUpdate` to mark progress as the
pipeline advances. This gives the user visibility into pipeline position,
especially during chunked long-transcript runs.

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

## Phase 4-5: Minutes + Report Generation (parallel)

minutes and report are independent — both read the corrected transcript from Phase 3
directly, and neither references the other. Invoke both skills in the same tool-call
batch and write both files in parallel:
- ./output/YYYY-MM-DD_meeting-name/minutes.md
- ./output/YYYY-MM-DD_meeting-name/report.md

Follow each skill's command-invoked mode:
- `skills/minutes/SKILL.md`
- `skills/report/SKILL.md`

File locations follow `output-file-rules.md`.

After both files are saved, output the pipeline completion message and offer
modification assistance.

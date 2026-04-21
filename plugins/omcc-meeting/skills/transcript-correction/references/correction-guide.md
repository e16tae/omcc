# Phase 3: Corrected Transcript Generation Guide

## Purpose

Apply corrections confirmed in Phase 2 to the original transcript, producing
a corrected transcript as a separate file. The original is never modified.
This corrected transcript is the sole input for Phase 4 and Phase 5.

## Core Principles

See the Non-Destructive Principle in `skills/transcript-correction/SKILL.md`
for the canonical definition.

---

## Correction Application Order

Apply in strict order (each step affects the next):

```
1. Speaker merge → 2. Term correction → 3. Sentence boundary reconstruction → 4. Context supplementation
```

---

## 1. Speaker Merge

Apply mappings confirmed in Phase 2 Step B.

- Replace all speaker labels with real names.
- Consolidate confirmed duplicate speakers under one name.
- Maintain chronological position (do not regroup utterances).
- Unmapped speakers: keep original label. Non-speaking attendees: header only.

---

## 2. Term Correction

Apply corrections confirmed in Phase 2 Step C.

- Replace confirmed terms in specific line context.
- Apply confirmed notation unification globally.
- Adjust particles/grammar as needed after term replacement.
- Unresolved terms: keep original, add annotation.

---

## 3. Sentence Boundary Reconstruction

Apply boundary corrections confirmed in Phase 2.

- **Merge**: Combine same-speaker split fragments. Do not add/remove meaning.
- **Split**: Divide at confirmed split points. Assign speaker labels per confirmation.
- **Insert transitions**: Add speaker transitions where confirmed.
- Unconfirmed anomalies: do not correct.

---

## 4. Context Supplementation

Insert user-provided context from Phase 2 Step D.

- Mark with supplement tags to distinguish from original content.
- Insert after the related line range.
- Use speaker label if known; otherwise mark as supplementary only.
- Preserve user's original phrasing.

---

## Output Format

### Header

Follow the spec in `transcript-header-spec.md`. Include meeting info, agenda,
supplementary info, and correction summary.

### Body

- Speaker labels use real names.
- Each utterance on one line: `speaker: content`
- Insert `--- Agenda N: [name] ---` delimiters at agenda boundaries.
- Supplement tags, unresolved annotations, and unclear markers may remain.

---

## Quality Checklist

- [ ] All original utterances included (no omissions)
- [ ] Chronological order preserved
- [ ] All Phase 2 speaker mappings applied
- [ ] All Phase 2 term corrections applied
- [ ] All Phase 2 boundary corrections applied
- [ ] All Phase 2 supplements inserted with tags
- [ ] No autonomous corrections beyond Phase 2 confirmations
- [ ] Header correction counts match actual corrections

---

## Save

- Path: ./output/YYYY-MM-DD_meeting-name/corrected_transcript.md
- Directory naming per `skills/transcript-correction/references/output-file-rules.md`.
- Encoding: UTF-8

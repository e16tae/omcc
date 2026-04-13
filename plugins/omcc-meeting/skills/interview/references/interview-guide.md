# Phase 2: User Interview Guide

## Purpose

Confirm and correct items identified in Phase 1 through a 4-step interactive interview
(Step A–D). Interview results are the sole correction basis for Phase 3.

## Core Principles

See Interview Protocol Rules in `CLAUDE.md`:
LLM presents first, line number references, cumulative reflection, one step per message, minimize burden.

---

## Issue Density → Question Strategy

| Density | Criteria | Strategy |
|---------|----------|----------|
| None | No issues | Brief 1-sentence confirmation |
| Few | 1–3 issues | Individual confirmation |
| Many | 4+ issues | Batches of 5–7 |
| Severe | Core mismatch | Prioritize |

---

## Step A: Domain & Context Confirmation + Metadata Collection

### Purpose

Establish domain context and collect metadata for downstream analysis.

### Procedure

1. **Request metadata**: Meeting date, location, attendees, agenda. Accept partial responses.
2. **Present domain analysis**: Show Phase 1 domain estimation. Adjust depth by confidence level.
3. **Handle responses**: Confirm → proceed. Correct → apply and reset. Supplement → add context. Unclear → tentatively adopt Phase 1 estimate.

---

## Step B: Speaker Mapping Confirmation

### Purpose

Map transcript speaker labels to actual attendees and resolve duplicates.

### Procedure

1. **Present mapping**: Cross-reference Phase 1 speakers with Step A attendees. Present with evidence (content, title mentions, speech style, role, elimination, temporal patterns).
2. **Handle corrections**: Check cascading effects when a mapping changes.
3. **Unmapped speakers**: Follow up with speech evidence for identification.
4. **Reduced mode** (no attendee list): Skip name mapping, only confirm duplicate candidates.

---

## Step C: Term/Keyword Verification

### Purpose

Confirm suspicious terms to correct STT misrecognition and unify notation.

### Procedure

1. **Present in batches**: 5–7 items per batch. Each includes line number, original text, correction candidate, context.
2. **Prioritize**: Unclear candidates → context mismatch → notation inconsistency.
3. **Handle responses**: Per-item confirm/correct, bulk confirm, additional reports, uncertain → keep original with annotation.
4. **Boundary integration**: Handle term-related sentence boundary anomalies in this step.

---

## Step D: Core Content Verification

### Purpose

Verify per-agenda content accuracy and collect supplementary information.

### Procedure

1. **Present per-agenda summary**: Combine Phase 1 agenda + Step A–C results. Per-speaker key claims in 1–2 sentences. Flag unclear segments with line numbers.
2. **Present in batches**: 1–2 agendas at a time if 3+ total.
3. **Handle responses**: Confirm, correct, supplement, note missing speech, mark unknown as unclear.
4. **Action items**: After all agendas verified, present identified action items. Confirm owners and deadlines.
5. **Remaining boundary anomalies**: Handle alongside content verification.

---

## Completion

Summarize all confirmed content and ask to proceed to Phase 3.

---

## Edge Cases

- **Very short answers**: Proceed normally. Ask specific follow-ups when needed.
- **"Don't know" responses**: Accept immediately. Apply appropriate annotation and move on. Do not re-ask.
- **Contradictory information**: Flag immediately and confirm. Never ignore contradictions.
- **Few issues (brief mode)**: Combine domain/speaker/term confirmation in one message. Still verify Step D per-agenda.
- **1–2 attendees**: Reduce Step B scope.
- **Single agenda**: Skip agenda structure confirmation, go directly to content.

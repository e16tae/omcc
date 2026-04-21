# Phase 5: Meeting Report Generation Guide

## Purpose

Generate a result-focused meeting report from the corrected (or raw) transcript.
A non-attendee should grasp "what was decided and what's next" within 1–2 minutes.

## Minutes vs Report

See the comparison table in `skills/minutes/references/minutes-guide.md`
("Minutes vs Report" section). The table is maintained there to avoid drift
between the two guides.

---

## Input Detection

- Corrected transcript header present → extract metadata.
- No header → raw transcript. Infer metadata.

---

## Writing Principles

1. **Brevity** — 1–2 pages. Each section ≤ 5–7 lines. Summary 2–3 sentences.
2. **Conclusion-focused** — No discussion process. Only "what was decided."
3. **Actionability** — Every action item has owner + deadline (or marked needing confirmation). Convert relative dates to absolute based on meeting date.
4. **Risk prominence** — Pending (undecided) vs risk (decided but dangerous) in separate sections.
5. **Independent** — Use corrected transcript directly. Do NOT reference minutes.

---

## Template Structure

```
Meeting Report

Overview: date, attendees, purpose (one sentence)
Summary: 2–3 sentences (what discussed, what decided, what's next)

Key Decisions table: decision, notes
Action Items table: item, owner, deadline
Pending Items: item — reason
Risks: risk — impact, mitigation

Next Meeting: date, planned agenda
```

---

## Decision Extraction

- Explicit agreement or decision-maker direction without objection → decision.
- Proposal stage or investigation stage → NOT a decision (may be action item or pending).
- Conditional decisions: record with condition in notes.

## Action Item Identification

- Explicit assignments, voluntary acceptances.
- Convert relative dates to absolute using meeting date as basis.
- Unknown owner/deadline: mark as needing confirmation.

## Pending vs Risk

| | Pending | Risk |
|---|---------|------|
| Definition | Undecided | Potential problem |
| Resolution | Make the decision | Preventive action |

If no risks found, state none. Do not fabricate.

---

## Quality Checklist

- [ ] All sections exist (write "None" if empty)
- [ ] Summary ≤ 2–3 sentences
- [ ] All decisions in table
- [ ] All action items have owner + deadline
- [ ] Relative dates converted to absolute
- [ ] Pending and risk properly separated
- [ ] No discussion process
- [ ] No evaluative language
- [ ] ≤ 1–2 pages

---

## Save

- Path: ./output/YYYY-MM-DD_meeting-name/report.md
- Directory naming per `output-file-rules.md`.
- Encoding: UTF-8

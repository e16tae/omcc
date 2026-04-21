# Phase 4: Meeting Minutes Generation Guide

## Purpose

Generate process-focused meeting minutes from the corrected (or raw) transcript.
Records "what was discussed" organized by agenda item.

## Minutes vs Report

| | Minutes (Phase 4) | Report (Phase 5) |
|---|---|---|
| Focus | Process — what was discussed | Results — what was decided |
| Audience | All attendees (record preservation) | Non-attendees, decision-makers |
| Discussion | Per-speaker summarized speech | Omitted — conclusions only |
| Summary | None | 2–3 sentence compression |
| Decisions | Sub-section within agenda | Separate table |
| Action items | Included in decisions | Separate table with owner + deadline |
| Length | Unlimited | 1–2 pages max |

---

## Input Detection

- Corrected transcript header present → extract metadata from header.
- No header → raw transcript. Infer metadata; use speaker labels as-is.

---

## Writing Principles

### Principle 1: Agenda-based structure

Reorganize by agenda, not chronological order. Use agenda list from corrected
transcript header as skeleton.

### Principle 2: Three-part structure

Each agenda has exactly 3 sections: Discussion → Decisions → Pending/Further Discussion.
If a section has no content, write "None". Never omit the section.

### Principle 3: Summarized speech

Do not copy verbatim. Summarize while preserving intent, evidence, exact numbers,
proper nouns, proposals, and conditions. Remove stutters, fillers, emotion, formulaic
agreement. Use 3rd-person narrative. Present opposing views in independent blocks.

### Principle 4: No omissions

Every speaking attendee's key statements must appear at least once.
Off-agenda discussions go in a separate section.

### Principle 5: Neutrality

Facts only. No evaluative language, no emotion/tone inference.

---

## Template Structure

```
Meeting Minutes

Meeting Info: date, location, attendees, agenda list

Per agenda:
  - Discussion (per-speaker summaries)
  - Decisions (specific: who, what, by when)
  - Pending/Further Discussion (with reasons)

Other Discussion (off-agenda items)
Next Meeting (date, planned agenda)
```

---

## Rules

- Agenda names: ≤ 15 chars, noun form, specific.
- Speech ordering: Introduction → proposals → counterarguments → conclusion.
- Decisions: Only explicitly agreed items. Be specific (who/what/when/conditions).
- Pending: Always include the reason.
- Supplement tags: Remove and treat as regular content.
- Unclear annotations: Add footnote noting original needs verification.

---

## Quality Checklist

- [ ] All agendas included
- [ ] Each agenda has all 3 sections
- [ ] Agenda names specific and ≤ 15 chars
- [ ] Metadata matches corrected transcript header
- [ ] Decisions specific (who/what/when)
- [ ] All speaking attendees reflected ≥ 1 time
- [ ] No evaluative expressions
- [ ] Consistent 3rd-person narrative

---

## Save

- Path: ./output/YYYY-MM-DD_meeting-name/minutes.md
- Directory naming per `output-file-rules.md`.
- Encoding: UTF-8

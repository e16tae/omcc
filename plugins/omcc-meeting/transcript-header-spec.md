# Corrected Transcript Header Spec

The corrected transcript is the **handoff artifact** between Phase 3 (correction)
and Phase 4–5 (document generation). This single file must contain all metadata
needed for Phase 4 and Phase 5 to run independently in another session.

---

## Header Structure

```markdown
# Corrected Transcript

## Meeting Info
- Original: [source file path or "direct input"]
- Corrected: YYYY-MM-DD
- Meeting date: [YYYY-MM-DD HH:MM-HH:MM]
- Location: [location] (omit if unknown)
- Attendees: [name1, name2, ...] (non-speaking attendees marked accordingly)
- Meeting type: [planning/review/brainstorming/decision-making/reporting/training/incident-response/recurring/other]
- Domain: [IT-dev/marketing/HR/finance/sales/legal/strategy/manufacturing/design/R&D/other]

## Agenda
1. [agenda name]
2. [agenda name]
...

## Supplementary Info
- [background context from interview]
- [omit this section if none]

## Correction Summary
| Type | Count | Details |
|------|-------|---------|
| Speaker merge | N | [merged speaker pairs] |
| Term correction | N | [corrected terms summary] |
| Sentence boundary | N | [merge M, split K, speaker transition L] |
| Context supplement | N | [supplementation locations] |

---

[Corrected transcript body]
```

---

## Field Descriptions

### Meeting Info

| Field | Source | Required | Purpose |
|-------|--------|----------|---------|
| Original | User input | Required | Traceability |
| Corrected | Auto-generated | Required | Document history |
| Meeting date | Phase 2 Step A | Required (mark unknown if unavailable) | Minutes/report metadata, relative date conversion. If unknown, relative dates cannot be converted → mark as needing confirmation |
| Location | Phase 2 Step A | Optional | Minutes metadata |
| Attendees | Phase 2 Step B | Required | Speaker list, minutes/report metadata |
| Meeting type | Phase 1 → Phase 2 confirm | Optional | Context aid (monologue detection, etc.) |
| Domain | Phase 1 → Phase 2 confirm | Optional | Context aid (term judgment, etc.) |

### Agenda

- Identified in Phase 1 and confirmed in Phase 2 Step D
- Phase 4–5 take agenda order and names from this header
- Agenda boundaries in the body are marked with `--- Agenda N: [name] ---` delimiters
- Line number ranges are NOT used because Phase 3 body edits change the line layout

### Supplementary Info

- Background context provided by the user during Phase 2 interview
- Separate from `[supplement]` tags in the body; records overall context

### Correction Summary

- Audit log of corrections applied in Phase 3
- Records counts and details for traceability

---

## Usage in Phase 4–5

| Phase 4 (Minutes) Field | Header Source |
|-------------------------|--------------|
| Meeting info > date/time | Meeting date |
| Meeting info > location | Location |
| Meeting info > attendees | Attendees |
| Agenda structure | Agenda |
| Speaker attribution | Body speaker labels |

| Phase 5 (Report) Field | Header Source |
|------------------------|--------------|
| Overview > date/time | Meeting date |
| Overview > attendees | Attendees |
| Overview > purpose | Derived from Agenda + Domain |
| Relative date conversion basis | Meeting date |

---

## Uncorrected Input

When `/omcc-meeting:minutes` or `/omcc-meeting:report` receives a raw (uncorrected) transcript:

1. No header exists, so metadata is inferred from transcript content.
2. Speaker labels are used as-is from the original.
3. Agenda structure is auto-detected from the transcript.
4. STT errors may be present since no correction was applied.

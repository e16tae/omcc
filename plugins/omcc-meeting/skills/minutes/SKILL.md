---
name: minutes
description: "Generates process-focused meeting minutes from a corrected or raw transcript. Use this skill when the user asks to create meeting minutes, generate minutes, or write up the meeting. Trigger phrases include 'create minutes', 'generate minutes', 'write up meeting'."
---

# Phase 4: Meeting Minutes Generation

Generate process-focused meeting minutes from the corrected transcript.
Systematically records "what was discussed" organized by agenda item.

## When auto-activated (without /start command)

### Input detection

Determine whether input is a corrected or raw transcript:
- Corrected transcript header present → extract metadata from header.
- No header → raw transcript. Infer metadata from content.

### Writing principles

1. **Agenda-based structure** — Reorganize by agenda, not chronological order
2. **Three-part structure** — Each agenda: Discussion → Decisions → Pending/Further Discussion
3. **Summarized speech** — 3rd-person narrative summarizing key points, not verbatim
4. **No omissions** — Every speaking attendee's key statements reflected at least once
5. **Neutrality** — Facts only; no evaluative or emotional language

### Output

Save to meeting directory: ./output/YYYY-MM-DD_meeting-name/minutes.md

Detailed guidelines and template in `skills/minutes/references/minutes-guide.md`.

---

## When invoked by command (/start)

Same procedure as auto-activated mode.
Difference: Invoked within a command, so auto-proceeds to Phase 5 (report skill) after saving.

# omcc-meeting Methodology Rules

These rules adjust Claude's default behavior while the omcc-meeting plugin is active.
They apply alongside commands (`/omcc-meeting:start`, `/omcc-meeting:correct`) and during general conversation.

---

## Available Commands and Skills

- `/omcc-meeting:start [transcript path or text]` — Full pipeline (analysis → interview → correction → minutes → report)
- `/omcc-meeting:correct [transcript path or text]` — Transcript correction only (analysis → interview → correction)
- `/omcc-meeting:minutes [corrected transcript path or text]` — Generate meeting minutes only (standalone skill)
- `/omcc-meeting:report [corrected transcript path or text]` — Generate meeting report only (standalone skill)

`/start` and `/correct` are commands that chain multiple skills in order.
`/minutes` and `/report` are standalone skill invocations.

### Skill Mapping

| Skill | Phase | Role |
|-------|-------|------|
| transcript-analysis | Phase 1 | Initial transcript analysis (domain, speakers, terms, boundaries, agenda) |
| interview | Phase 2 | Interactive 4-step user interview (Step A–D) |
| transcript-correction | Phase 3 | Corrected transcript generation (apply interview results) |
| minutes | Phase 4 | Meeting minutes generation (process-focused) |
| report | Phase 5 | Meeting report generation (result-focused) |

---

## Pipeline Ordering Rules

The 5-phase pipeline must execute in strict order. Each phase's output directly
affects the accuracy of subsequent phases.

```
Phase 1: Initial transcript analysis (automatic)
    ↓
Phase 2: User interview (interactive)
    ↓
Phase 3: Corrected transcript generation (automatic → file save)
    ↓
Phase 4: Meeting minutes generation (automatic → file save)
    ↓
Phase 5: Meeting report generation (automatic → file save)
```

Do not skip phases or reorder them.

Reason: Phase 1 analysis determines Phase 2 questions, and Phase 2 interview results
are the sole basis for Phase 3 corrections. Breaking the order degrades correction quality.

---

## Non-Destructive Principle

1. **Never modify the original transcript.** The corrected transcript is always a separate file.
2. **Only apply user-confirmed corrections.** The LLM must not autonomously add corrections beyond what was confirmed in Phase 2.
3. **Preserve utterance order (chronological).** Even during speaker merges and sentence boundary reconstruction, maintain the original timeline.

Reason: If content changes without user awareness, document trustworthiness is compromised.
"Only confirmed corrections" is the principle.

---

## Interview Protocol Rules

During Phase 2 interviews, always follow these principles:

1. **LLM presents first**: Present analysis results and best guesses before asking. Never ask the user to fill in blanks.
2. **One step at a time**: Present each Step (A–D) in a separate message. Do not bundle multiple steps.
3. **Cumulative reflection**: Immediately apply confirmed results from each step to subsequent steps.
4. **Minimize user burden**: Prefer yes/no or short-answer question formats.
5. **Line number references**: Always cite original transcript line numbers when mentioning ambiguous segments.

Reason: The user may not be a meeting specialist. The most efficient structure is for the LLM
to perform analysis first and let the user only confirm or correct.

---

## Handoff Rules

The corrected transcript (`transcript-header-spec.md`) is the **sole handoff artifact**
between Phase 3 and Phase 4–5.

### Within-session handoff

When running `/omcc-meeting:start` (full pipeline), conversation context flows naturally
from Phase 3 to Phase 4–5.

### Cross-command handoff

After generating a corrected transcript with `/omcc-meeting:correct`, pass the file path
to `/omcc-meeting:minutes` or `/omcc-meeting:report` in another session.

### Uncorrected input handling

When `/omcc-meeting:minutes` or `/omcc-meeting:report` receives an uncorrected transcript,
proceed directly without correction. Correction is recommended but not enforced.

---

## Output File Rules

### Directory structure

Each meeting is saved in its own directory:

```
./output/YYYY-MM-DD_meeting-name/
├── corrected_transcript.md
├── minutes.md
└── report.md
```

### Directory naming

- `YYYY-MM-DD` is based on the meeting date. If unknown, use the processing date.
- `meeting-name` is derived from the agenda or topic collected in Phase 2 (max 15 characters).
- If the meeting name is unknown, use time-based fallback: `YYYY-MM-DD_HHMM`
- For standalone `/omcc-meeting:minutes` or `/omcc-meeting:report`: derive from input file metadata,
  or default to `YYYY-MM-DD_meeting`.

### Directory name sanitization

Before using a meeting name as a directory component, apply these rules:
- `/` → `-` (hyphen)
- Spaces → `_` (underscore)
- Remove filesystem-forbidden characters (`\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`)
- If longer than 15 characters, truncate at 15 and remove trailing `_`

### Filenames

- Filenames within the directory are fixed: corrected_transcript.md, minutes.md, report.md
- **Naming convention**: multi-word filenames use `snake_case` (lowercase with
  underscore separator). Single-word filenames stay lowercase. Apply this rule
  when introducing new output file types.
- Do not use `_2`, `_3` suffixes. Separate meetings by directory.

### Overwrite protection

If the target output directory already exists, ask the user before overwriting.

### Other

- Create the `output` directory if it does not exist.
- File encoding: UTF-8

---

## Long Transcript Handling

For very long transcripts (60+ minute meetings):

1. In Phase 1, split into chunks by agenda or time segments.
2. For each chunk, repeat Phase 2–3.
3. Include 5-line overlap at chunk boundaries to prevent context loss.
4. In Phase 4–5, integrate all chunks into unified final documents.

Reason: Processing very long transcripts in one pass risks accuracy degradation
due to context window constraints. Chunking ensures quality per segment.

---

## Interview Interruption Handling

If the session is interrupted during Phase 2 interview, restart from Phase 1.
Phase 1 is automatic and fast, and Phase 2 has only 4 steps, so restart cost is low.

Reason: Phase 2 is interactive and difficult to serialize mid-state. Restarting
from scratch is better for correction accuracy.

---

## Language Convention

All documentation in this plugin uses English. This includes CLAUDE.md, commands,
skills, and reference guides.

The plugin processes Korean meeting transcripts and generates Korean-language output
documents. The documentation language and the output language are separate concerns.

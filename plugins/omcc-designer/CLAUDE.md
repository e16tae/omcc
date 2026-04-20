# omcc-designer Methodology Rules

These rules adjust Claude's default behavior while the omcc-designer plugin is active.
They apply alongside commands and during general conversation.

---

## Available Commands and Skills

- `/omcc-designer:start [design request]` — Full pipeline (analysis > interview > brief > poster)
- `/omcc-designer:poster [brief path or design request]` — Poster-only entry (uses existing brief or runs full pipeline)
- `/omcc-designer:formalize [image/Figma/PDF]` — Formalize existing design into a structured brief
- `/omcc-designer:plan [project description]` — Create design strategy and deliverable roadmap
- `/omcc-designer:audit [design input + optional scope]` — Design quality audit with remediation discussion

### Skill Mapping

| Skill | Directly invoked by | Role |
|-------|---------|------|
| design-analysis | start, plan | Automatic analysis of design request |
| design-extraction | formalize | Extract design elements from existing visuals |
| design-interview | start, formalize | Interactive design consultation (5-step) |
| brief-generation | start, formalize | Design brief artifact generation |
| design-planning | plan | Design strategy and deliverable roadmap |
| design-evaluation | audit | Multi-perspective design quality evaluation |
| poster | start, poster | Poster design specification and AI prompt generation |

---

## Pipeline Ordering Rules

### Standard pipeline (start, poster)

The 4-phase pipeline must execute in strict order. Each phase's output directly
affects the quality of subsequent phases.

```
Phase 1: Design analysis (automatic)
    ↓
Phase 2: Design consultation interview (interactive)
    ↓
Phase 3: Design brief generation (automatic → file save)
    ↓
Phase 4: Domain-specific output (automatic → file save)
```

Do not skip phases or reorder them.

### Formalize pipeline

```
Phase 1: Design extraction (automatic — visual input)
    ↓
Phase 2: Design confirmation interview (interactive — confirmation mode)
    ↓
Phase 3: Design brief generation (automatic → file save)
```

The formalize pipeline produces a design brief from an existing visual.
It ends at Phase 3 — the brief is the final output.

### Plan and audit pipelines

The plan and audit commands operate outside the standard 4-phase pipeline.
Each defines its own phase sequence in its command file.

Reason: Phase 1 analysis determines Phase 2 interview focus and question density.
Phase 2 interview results are the sole basis for Phase 3 brief generation.
Breaking the order degrades design quality and may encode unconfirmed assumptions.

---

## Confirmed Decision Principle

Only user-confirmed decisions may be encoded in the design brief and downstream outputs.

1. Phase 1 (analysis or extraction) produces **estimations** with confidence levels — these are proposals, not decisions.
2. Phase 2 (interview) **confirms or corrects** each estimation through user interaction.
3. Phase 3 (brief) encodes only confirmed items. Unconfirmed items are tagged `[unconfirmed]` and excluded from downstream generation.
4. Phase 4 (domain output) operates only on confirmed brief content.
5. **Brief protection**: Never overwrite existing briefs without user confirmation.
   New consultations produce new briefs.
6. **Decision trail**: The brief's Decision Log and Supplementary Notes preserve
   what was confirmed, what was recommended, and what was rejected.

This principle also applies to evaluation findings (audit) and planning
recommendations (plan) — these are estimations until the user confirms
a remediation direction or plan.

The LLM must not autonomously promote estimations to decisions. If the user
says "I don't know" or skips a question, that field remains unconfirmed.

Reason: Design is subjective. If the LLM's color palette guess silently becomes
the final palette without user awareness, the deliverable loses client trust.
"Only confirmed decisions" is the principle — from estimation through encoding,
storage, and retrieval.

---

## Interview Protocol Rules

During design consultation (Phase 2), always follow these principles:

1. **Designer presents first**: Present analysis/extraction results, best guesses,
   and professional recommendations before asking. Never ask the user to start
   from a blank slate.
2. **One step at a time**: Present each Step (A-E) in a separate message.
   Do not bundle multiple steps.
3. **Cumulative reflection**: Immediately apply confirmed results from each step
   to subsequent steps. If brand colors are confirmed in Step B, Step C visual
   direction already reflects them.
4. **Minimize user burden**: Prefer yes/no, selection from options, or short-answer
   question formats. Present concrete proposals ("I recommend this palette: ...")
   rather than open questions ("What colors do you want?").
5. **Contradiction detection**: If a user's answer contradicts a previously confirmed
   decision (e.g., "minimal corporate" in Step B but "neon maximalist" in Step C),
   flag immediately and resolve before proceeding.
6. **"Don't know" acceptance**: When the user says they don't know or aren't sure,
   accept immediately. Never re-ask or pressure. Mark the field as unconfirmed
   and provide a professional recommendation that the user can accept later.
7. **Content overload detection**: If the content volume exceeds what the target
   medium can communicate effectively, proactively recommend a more suitable format
   (e.g., "This content would work better as an infographic than a single poster").

These rules apply to both analysis-sourced interviews (start) and
extraction-sourced interviews (formalize). In formalize mode, high-confidence
extractions use observation-first language ("I extracted...") rather than
recommendation-first language ("I recommend...").

Reason: The user may not be a design professional. The most efficient structure
is for the designer to analyze and recommend first, letting the user only
confirm or adjust.

---

## Output File Rules

### Directory structure

Each design project is saved in its own directory:

```
./output/YYYY-MM-DD_project-name/
├── design_brief.md
├── poster_spec.md
└── design_plan.md
```

### Directory naming

- `YYYY-MM-DD` is the project creation date.
- `project-name` is derived from the project title collected in Phase 2 (max 15 characters).
- If the project name is unknown, use time-based fallback: `YYYY-MM-DD_HHMM`

### Directory name sanitization

Before using a project name as a directory component, apply these rules:
- `/` → `-` (hyphen)
- Spaces → `_` (underscore)
- Remove filesystem-forbidden characters (`\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`)
- If longer than 15 characters, truncate at 15 and remove trailing `_`

### Filenames

- Filenames within the directory are fixed: design_brief.md, poster_spec.md, design_plan.md
- Do not use `_2`, `_3` suffixes. Separate projects by directory.

### Overwrite protection

If the target output directory already exists, ask the user before overwriting.

### Other

- Create the `output` directory if it does not exist.
- File encoding: UTF-8

---

## Brief Handoff Rules

The design brief (`design-brief-spec.md`) is the **sole handoff artifact**
between Phase 3 and Phase 4.

### Within-session handoff

When running `/omcc-designer:start` (full pipeline), conversation context flows
naturally from Phase 3 to Phase 4.

### Cross-command handoff

After generating a design brief with the full pipeline or `/omcc-designer:formalize`,
pass the brief file path to `/omcc-designer:poster` in another session.

### Plan-to-start handoff

When transitioning from a design plan to individual deliverables, the shared
design decisions from the plan serve as pre-confirmed context for the analysis
and interview phases of `/omcc-designer:start`.

### Brief validation

When `/omcc-designer:poster` receives a brief file, validate before use:
1. **Completeness**: All required sections present per `design-brief-spec.md`
2. **Medium match**: Brief's target medium includes the requested output type
3. **Staleness**: Warn if brief is older than 30 days

### Uncorrected input handling

When a domain skill receives a raw design request (no brief), it must run
the full pipeline (analysis > interview > brief) before generating output.
Direct generation from raw input is not permitted.

Reason: Skipping the consultation produces generic results that miss the
client's actual needs and brand identity.

---

## Interrupted Interview Handling

If the session is interrupted during Phase 2 interview, restart from Phase 1.

Reason: Phase 1 is automatic and fast, and Phase 2 maintains cumulative state
that is difficult to serialize mid-step. Restarting from scratch is better
for consultation quality than attempting to resume a partial state.

---

## AI Prompt Output Rules

Design outputs that include AI image generation prompts must separate three layers:

1. **Layout specification**: Grid structure, visual hierarchy, zones, dimensions,
   bleed/safe area. This is the structural blueprint.
2. **Typography specification**: Font selections, sizes, weights, placement
   coordinates, color assignments. This is applied by the human designer.
3. **Image generation prompts**: Per-zone prompts for AI tools. Each zone includes
   tool-specific variants:
   - Midjourney: Natural language description optimized for V7
   - NanoBanana: Tool-specific prompt format
   - Hixfield: Tool-specific prompt format

Reason: AI image generators cannot reliably render text. Mixing typography
into image prompts degrades output quality. Separating layers lets the human
apply text precisely while AI handles visual/photographic elements.

---

## Language Convention

All documentation in this plugin uses English. This includes CLAUDE.md, commands,
skills, and reference guides.

The plugin processes design requests in any language and generates output documents
in the user's language. The documentation language and the output language are
separate concerns.

---
name: transcript-analysis
description: "Automatically analyzes STT transcripts to identify domain, speakers, suspicious terms, sentence boundary anomalies, and agenda structure. Use this skill when the user asks to analyze a transcript, process STT output, or examine meeting content — even if they don't explicitly mention analysis. Trigger phrases include 'analyze transcript', 'process STT', 'examine meeting'."
---

# Phase 1: Initial Transcript Analysis

Read the transcript and automatically identify items that need user confirmation
in Phase 2 interview. Do not ask the user anything in this phase.

## When auto-activated (without /start command)

### Step 1: Input processing

1. Accept transcript as file path or pasted text.
2. **Input validation**:
   - If a file path is given and the file does not exist, inform the user and abort.
   - If the file is empty or contains fewer than 5 lines, warn the user that the
     input appears too short for meaningful analysis.
   - If the content contains no speaker labels, warn the user that it may not be
     a transcript and ask to confirm before proceeding.
3. Load the full transcript with line numbers.
4. Detect and normalize speaker label format.
5. Collect basic statistics: total lines, speaker count, total utterances.

### Step 2: Five-area analysis

Follow the detailed criteria in `skills/transcript-analysis/references/analysis-guide.md`:

1. **Domain estimation** — field, meeting type, confidence level
2. **Speaker analysis** — speaker list + duplicate candidate grouping
3. **Suspicious term extraction** — context mismatch, phonetic similarity, unregistered terms, notation inconsistency
4. **Sentence boundary anomaly detection** — abnormal long utterances, topic jumps, incomplete sentences, abnormal monologues
5. **Agenda structure identification** — topic transitions, line ranges, keywords, agenda names

### Step 3: Present results

Present a structured summary to the user covering:
- Domain estimation (field, meeting type, confidence)
- Speaker overview (count, duplicate candidates)
- Suspicious terms (count by type)
- Sentence boundary anomalies (count by pattern)
- Agenda structure (agenda names, line ranges)

---

## When invoked by command (/start, /correct)

Same procedure as auto-activated mode, but results are kept internally
and not presented to the user. Instead, convert analysis results into
Phase 2 interview questions based on issue density and auto-proceed
to Phase 2 (interview skill).

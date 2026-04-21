# Phase 1: Initial Transcript Analysis Guide

## Purpose

Read the transcript and automatically identify items requiring user confirmation
in Phase 2 interview. Do not ask the user anything in this phase. All results
are stored internally as source material for Phase 2 questions.

## Prerequisites

- Load the full transcript with line numbers.
- Detect and normalize speaker label format.
- Collect basic statistics: total lines, speaker count, total utterances.

---

## 1. Domain Estimation

### Procedure

1. Extract high-frequency nouns, proper nouns, and domain-specific terms.
2. Estimate the meeting's subject field from a standard category list (IT/dev, marketing, HR, finance, sales, legal, strategy, manufacturing, design, R&D, other).
3. Estimate the meeting type (planning, review, brainstorming, decision-making, reporting, training, incident response, recurring, other).
4. Extract 5–10 key evidence terms.
5. Assign confidence: high / medium / low
   - High: 5+ domain-specific terms
   - Medium: 2–4 domain terms, or spans multiple domains
   - Low: Only general terms; domain unclear

---

## 2. Speaker Analysis

### 2-1. Speaker list extraction

For each speaker, collect: total utterance count, first/last utterance line numbers,
key topics (max 3), utterance proportion (% of total).

### 2-2. Duplicate speaker detection

Detect same-person splits across multiple labels. Apply 4 criteria with evidence:

1. **Speech pattern similarity** — Consecutive utterances on the same topic by two speakers.
2. **Role consistency** — Decision-making or reporting roles split across labels.
3. **Temporal discontinuity** — One speaker in first half only, another in second half only. Threshold: ≤ 10% overlap.
4. **Language style** — Same verbal habits, sentence endings, honorific levels.

Likelihood grades: high (3+ criteria), medium (2 criteria), low (1 criterion, note only).

---

## 3. Suspicious Term Extraction

### Criteria

1. **Context unnaturalness** — Term doesn't fit the estimated domain. Evaluate semantic consistency with surrounding 2 sentences.
2. **Phonetic similarity** — A phonetically similar substitute makes context more natural. Record correction candidates.
3. **Unregistered terms** — Not in standard dictionaries but potentially domain jargon, internal proper nouns, or abbreviations. Classify as confirmation request.
4. **Notation inconsistency** — Same concept with different notations. Record all occurrences and propose unification.

---

## 4. Sentence Boundary Anomaly Detection

### Patterns

1. **Abnormal long utterance** — Single utterance ≥ 200 chars (≥ 300 almost certain split failure). Exception: report/presentation-style utterances.
2. **Topic jump** — Clear topic transition within a single sentence without conjunction.
3. **Incomplete sentence** — Utterance ends with particle, connective ending, adnominal form, or adverb. Check if next speaker's utterance forms a natural continuation.
4. **Abnormal monologue** — 5+ consecutive utterances or cumulative ≥ 500 chars by one speaker. Response-type utterances within suggest missing speaker transition.

---

## 5. Agenda Structure Identification

### Procedure

1. Detect topic transition points (explicit transition expressions, new topic keywords, wrap-up expressions, speaker pattern changes).
2. Map line ranges per agenda. Classify meeting greetings/wrap-up separately.
3. Extract 3–5 keywords per agenda (proper nouns first).
4. Generate agenda names (≤ 15 chars, noun form, specific).
5. Cross-reference with user-provided metadata if available.

---

## Phase 2 Linkage

### Issue density → question strategy

| Density | Criteria | Strategy |
|---------|----------|----------|
| None | No issues | Brief 1-sentence confirmation |
| Few | 1–3 issues | Individual confirmation |
| Many | 4+ issues | Batches of 5–7 |
| Severe | Core mismatch | Prioritize |

### Step mapping

| Analysis Area | Phase 2 Step | Linkage |
|--------------|-------------|---------|
| Domain | Step A | Present estimate, request confirmation |
| Speakers | Step B | Present mapping with evidence |
| Terms | Step C | Group by type |
| Boundaries | Step C/D | Alongside term correction or content verification |
| Agenda | Step D | Skeleton for content summary |

### Priority

1. Low-confidence domain → 2. High-likelihood duplicate speakers → 3. Unclear term candidates → 4. Agenda mismatches → 5. Boundary anomalies

---

## Long Transcript Handling

For very long transcripts (60+ minute meetings) that risk context degradation
when analyzed in one pass:

### Chunking procedure

1. Split the transcript into chunks by agenda boundaries or time segments.
2. Include 5-line overlap at chunk boundaries to prevent context loss.
3. Per chunk, run domain estimation first (term extraction depends on it), then the remaining four analyses in parallel. Chunks themselves are independent, so multiple chunks can proceed simultaneously.
4. Merge per-chunk analyses into a unified Phase 1 result:
   - Domain: take the highest-confidence estimation (or multi-domain if chunks disagree)
   - Speakers: union across chunks, then re-run duplicate detection on the merged list
   - Terms, boundaries, agenda: concatenate with chunk origin preserved

### Interview (Phase 2)

Phase 2 remains sequential — the user cannot interview multiple chunks in parallel.
Walk the user through the merged Phase 1 result chunk by chunk when needed.

### Correction (Phase 3)

Apply confirmed corrections per chunk, then integrate into a single
corrected_transcript.md. Phase 4 and Phase 5 then operate on the unified file.

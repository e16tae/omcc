---
name: research
description: "Conducts topic-bound research and produces a durable cited research brief — distinct from decision-bound option comparison (which belongs to omcc-dev's brainstorm skill). Trigger phrases include 'research X', 'investigate <topic>', 'cited brief on', 'literature review', '리서치', '조사해줘'."
---

# Topic-bound Research

Produce a durable, cited research brief on a topic the user wants to
investigate. Output is a reusable artifact (saved to disk per
`skills/research/references/output-file-rules.md`) that downstream
workflows can cite.

This skill is **topic-bound, not decision-bound**. It does not compare
options or recommend a direction. If the user is choosing between
alternatives, the brainstorm skill (in the omcc-dev plugin) is the
right tool — research gathers evidence; brainstorm makes decisions
on top of evidence.

---

## When auto-activated (without /research command)

### Step 1: Topic intake and scoping

1. **Privacy gate** — before any web search:
   - Use generic technology terms in queries, not internal identifiers.
   - Never include proprietary code, internal paths, customer names,
     unpublished product names, or pasted internal documents.
   - When confidentiality is unclear, ask: "This topic mentions <X>.
     Is <X> safe to search externally?"
   - If the user declines or indicates `<X>` is sensitive, ask whether
     to proceed with `<X>` redacted (e.g., generic substitute) or to
     abort the research session.

2. **Empty / over-broad topic check**:
   - If the user's input is empty or has no clear research subject,
     ask one clarifying question: "What specifically would you like
     researched?"
   - If the topic is extremely broad (e.g., "JavaScript"), ask the user
     to narrow to a specific question.
   - Re-ask at most **once**. If the second response is still
     unclear/empty, abort with a graceful message rather than
     looping or inventing a topic.

3. **Sub-question derivation**:
   - Decompose the topic into 1–7 investigation sub-questions
     (each answerable with evidence).
   - Present sub-questions to the user for confirmation/refinement
     before searching.

4. **Scope statement** — articulate in-scope and out-of-scope in 1-3
   sentences.

### Step 2: Research execution

For each sub-question:

1. **Identify search targets** by source-type tier (taxonomy in
   `skills/research/references/research-brief-spec.md`):
   official-docs / standards / academic / secondary.
   Aim for at least one official-docs/standards source per sub-question
   when the topic admits one.

2. **Search and fetch**:
   - WebSearch for ecosystem consensus, benchmarks, current best practices.
   - WebFetch for specific documentation pages.
   - Capture for each source: URL, title (or fallback), access date in
     ISO `YYYY-MM-DD`, source-type classification.

3. **Citation capture** — assign stable numeric `[N]` in
   research-execution capture order; deduplicate URLs (same canonical
   URL = one Sources entry, even when cited multiple times).

4. **Web tool unavailability — graceful degradation**:
   - If WebSearch/WebFetch fail mid-session, do NOT pretend the brief
     is fully cited.
   - Preserve sources captured so far; mark unfinished sub-questions
     with the `[research interrupted — partial coverage]` sentinel
     (one of three permitted markers per the spec audit checklist).
   - Lower the overall confidence rating.
   - Note in "Open Questions / Gaps" which sub-questions remain
     incompletely investigated.
   - State the limitation explicitly to the user before saving.

### Step 3: Synthesis

1. **Organize by sub-question** — each sub-question gets its own
   Findings H3 section.
2. **Inline citations** — every substantive claim has at least one
   `[N]` citation OR is marked with `[uncited inference]` (model's
   own synthesis) or `[research interrupted — partial coverage]`
   (web tools failed). No marketing claims ("best", "fastest", "most
   popular") without a benchmark/consensus citation.
3. **Conflict handling** — when two sources disagree, present both
   with their citations explicitly. Do not pick a winner unless one
   source is significantly higher tier.
4. **Confidence rating** — tied to source-tier coverage:
   - **HIGH**: official-docs, standards, or academic sources cover all
     sub-questions.
   - **MEDIUM**: a mix; some sub-questions only have secondary-tier
     coverage; or one sub-question is interrupted.
   - **LOW**: predominantly secondary-tier; OR multiple sub-questions
     interrupted.

### Step 4: Output assembly and save

1. **Audit checklist** — run through the checklist in
   `skills/research/references/research-brief-spec.md` (citation /
   sentinel coverage, no orphan sources, URL dedup, citation numbering
   stable, sub-question count 1-7, ISO dates, confidence rating exact).

2. **Save** — write the brief to disk per
   `skills/research/references/output-file-rules.md`:
   - Path: `./output/YYYY-MM-DD_<topic-slug>/research_brief.md`
   - Apply slug sanitization (traversal rejection on raw input,
     15-code-point truncation, empty-fallback to `YYYY-MM-DD_HHMM`)
   - Existing-directory: prompt user (overwrite / distinct directory /
     abort), default to distinct on no response

3. **Output language** — the brief is written in the user's interaction
   language. The "Source language" field records the dominant language
   of cited sources (often differs from the brief's writing language).

4. **Present summary**:
   - If saved: confirm the saved file path, summarize the most decisive
     findings in one paragraph, state confidence rating with main
     caveat, list open questions / gaps.
   - If user chose **abort** (no file saved): present the brief
     content inline; no path to confirm. Synthesis summary still applies.

---

## When invoked by command (/research)

Same procedure as above. The command file provides `$ARGUMENTS` as the
topic (may be empty — apply Step 1.2 empty-topic handling) and emits
the completion message after Step 4 returns.

---

## Anti-patterns (do not produce)

- **5-perspective decision comparison** — that frame belongs to
  brainstorm. Research organizes by sub-questions.
- **Recommendation section** — research provides evidence and
  confidence, not a chosen direction.
- **"Option A vs Option B" framing** — if the topic is "X vs Y", the
  sub-questions are still about properties (e.g., "What does each
  guarantee?"), not about which to choose.
- **Marketing claims without citation** — "best", "fastest", "most
  popular" need a benchmark/consensus citation.
- **Stale evidence without flag** — sources >18 months old on rapidly
  evolving topics need an explicit caveat in the Confidence note.
- **Silent gaps** — incomplete coverage must be surfaced in "Open
  Questions / Gaps", not hidden under HIGH confidence.

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

1. **Privacy gate** — before any web search **or external ensemble dispatch**:
   - Use generic technology terms in queries, not internal identifiers.
   - Never include proprietary code, internal paths, customer names,
     unpublished product names, or pasted internal documents.
   - When confidentiality is unclear, ask: "This topic mentions <X>.
     Is <X> safe to search externally?"
   - If the user declines or indicates `<X>` is sensitive, ask whether
     to proceed with `<X>` redacted (e.g., generic substitute) or to
     abort the research session.
   - Redacted substitutions apply equally to web queries and to any
     prompt sent to an external model (e.g., the Codex research-scan
     ensemble described in `research-ensemble-protocol.md`) — never
     transmit the pre-redaction value.

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

Same procedure as above plus a Codex research-scan ensemble that runs
in parallel with web research per `research-ensemble-protocol.md`.
The command file provides `$ARGUMENTS` as the topic (may be empty —
apply Step 1.2 empty-topic handling) and emits the completion message
after Step 4 returns.

### Step 1 addendum (command mode only) — pre-dispatch gates

After Step 1.4 (scope statement) and BEFORE Step 2 begins, run the
existing-directory check defined in
`skills/research/references/output-file-rules.md` for the resolved
output path.

User choices and their downstream effect:

- **Abort**: terminate the session immediately. Do not run Step 2
  web research, do not dispatch Codex, do not attempt to produce a
  brief. Emit the **"aborted at scoping"** completion message
  defined in `commands/research.md` — there is no inline brief to
  present at this stage (research has not run), and an external
  Codex run would be wasted work. This Step 1 abort path is
  distinct from the Step 4 abort path: Step 4 abort happens AFTER
  research has run (so an inline brief exists), Step 1 abort
  happens BEFORE research (so it does not).
- **Overwrite**: record the decision (`save_path = default`,
  `existing_dir_resolved = true`). Proceed to dispatch.
- **Distinct directory**: compute the sibling path per
  `skills/research/references/output-file-rules.md`
  (e.g., `2026-04-29_my-topic_1430/`), record the decision
  (`save_path = sibling`, `existing_dir_resolved = true`). Proceed
  to dispatch.

The recorded `save_path` and `existing_dir_resolved = true` are
**carried into Step 4 save** so that the existing-directory prompt
is NOT repeated. Step 4's save uses `save_path` directly when
`existing_dir_resolved` is true; the user is never asked
overwrite/distinct/abort twice within the same session.

### Step 1 dispatch (command mode only) — Codex research-scan launch

After the existing-directory gate clears, dispatch the Codex
research-scan ensemble per `research-ensemble-protocol.md` Step 1
Launch. The dispatch is a single background-Bash invocation of
`codex-companion task` (foreground subcommand, backgrounded at the
Bash layer) carrying the research-scan prompt. Then proceed to Step 2
without waiting — Codex runs in parallel with Claude's WebSearch /
WebFetch.

If the codex plugin is not installed or the preflight check fails,
skip the dispatch silently and continue Claude-only. The graceful
degradation path is canonical in `research-ensemble-protocol.md`.

### Step 3 collect (command mode only) — Codex output reconciliation

Before applying Step 3.1 (organize by sub-question), check whether
the Codex ensemble was actually dispatched in Step 1. The dispatch
is skipped (silently) when the codex plugin is unavailable, the
preflight check fails, or any of the guards in
`research-ensemble-protocol.md` Step 1 Launch returns `exit 0`
without launching `codex-companion`.

- If the dispatch was skipped: do NOT wait for any background
  notification — there is no in-flight Codex job. Proceed directly
  to Step 3.1 with Claude-only findings.
- If the dispatch was launched: wait for the Codex background
  notification, read the Codex output, and reconcile the Codex
  findings with Claude's findings via the four-category synthesis
  defined in `research-ensemble-protocol.md`:

- AGREED: same conclusion. If sources differ, apply Source Union
  (verified, URL-deduplicated). New Codex sources go through Citation
  Remapping per the protocol — Codex's own labels never enter the
  brief.
- CLAUDE-ONLY: present normally with Claude's citations. No
  source-of-discovery label appears in the brief.
- CODEX-ONLY: take Path A (Claude verifies via WebFetch and adds a
  numeric `[N]` citation) OR Path B (move into Open Questions / Gaps
  without citing the unverified source). Path C (`[uncited
  inference]`) is forbidden for factual external claims.
- CONFLICT: present both interpretations with their citations per
  Step 3.3 below — the existing rule is unchanged.

If Codex was unavailable, timed out, returned empty, or produced
unsalvageable malformed output, proceed with Claude-only findings and
record the degradation in the user-facing completion summary AFTER
the brief is saved. Never insert ensemble-status labels into the
brief artifact itself.

### Step 4 audit (command mode only) — CODEX-ONLY claim handling

The audit checklist (canonical in
`skills/research/references/research-brief-spec.md`) applies as
written. The synthesis above already routed every CODEX-ONLY claim
into either a verified `[N]` citation or an Open Questions entry —
no claim should reach the audit lacking both.

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

# Research Ensemble Protocol

Defines how Claude and Codex operate as a dual-model ensemble for the
**research-scan** ensemble point — the research-domain analog of the
text ensemble points used by other omcc plugins. Activated inside the
research skill's command-invoked mode to cross-validate sub-question
findings against an independent model.

The user never invokes Codex directly. The command path orchestrates
dispatch, collection, and synthesis transparently. When the codex
plugin is not installed or returns no usable output, the ensemble
degrades silently to Claude-only.

This protocol is plugin-local. The omcc-dev plugin's ensemble-protocol
document inspires the structure but is intentionally NOT referenced by
backtick — cross-plugin backtick references in markdown are rejected
by the marketplace structure tests, and per the repo's
"Independence over uniformity" principle each plugin owns its own
domain-specific contracts.

---

## When This Protocol Applies

Activates inside the research skill's command-invoked mode (Step 1
end through Step 3 entry) when a `/omcc-research:research` invocation
runs.

Does NOT apply to:

- Auto-activated research outside the `/omcc-research:research` command
- Inline cross-references from other plugins or commands
- Binary confirmations or progress updates within the same session

---

## Affinity

For omcc-research v2 the ensemble is **always-on** for command-invoked
research. The research domain's quality dimensions (topic depth,
source-tier requirement, controversy, freshness) do not map cleanly
onto the file/layer/risk-based affinity tiers used by code workflows.
A future v3 may introduce graduated affinity; v2 keeps the surface
simple and relies on graceful degradation when the cost would be
unjustified (e.g., the codex plugin is not installed at all).

---

## Execution Pattern

Three steps per research session: Launch, Collect, Synthesize.

### Step 1: Launch — after sub-question confirmation + scope

Pre-conditions before dispatch:

1. The privacy gate has passed for the topic AND the confirmed
   sub-questions. The gate covers BOTH web search AND external
   ensemble dispatch — see "Privacy" below.
2. The existing-directory check (per `skills/research/references/output-file-rules.md`)
   has completed and the user did NOT choose abort. Aborting before
   dispatch prevents wasted Codex runs on a session the user will
   discard.

Dispatch:

3. Resolve codex-companion at runtime via the cache glob:

   ```
   CODEX_HOME=$(ls -1d ~/.claude/plugins/cache/*/codex/*/ 2>/dev/null | sort -V | tail -1)
   [ -n "$CODEX_HOME" ] && [ -f "${CODEX_HOME}scripts/codex-companion.mjs" ]
   ```

   If either check fails, ensemble degrades to Claude-only — see
   "Failure Handling".

4. Construct the research-scan prompt per "Prompt Construction" below
   and write it to a per-dispatch temporary file via Claude's `Write`
   tool. Do NOT embed the prompt text into the shell command itself
   — the prompt contains user-controlled material (topic,
   sub-questions, scope) and any shell-level construct that mixes
   user input with the command line (string interpolation, heredoc,
   etc.) can be collision-prone or injection-prone for some inputs.
   The `Write` tool writes a literal string and never invokes a shell.

   Use a private temp path that is unique per dispatch — e.g.,
   `${TMPDIR:-/tmp}/omcc-research-prompt-<session-id>-<dispatch-id>.txt`.
   Remove the file after dispatch (success or failure).

5. Execute as a background Bash. The shell passes only the file path
   to `codex-companion`; the prompt content is read directly by the
   companion via `fs.readFileSync` and never crosses shell parsing,
   the process argv, or `ps aux`.

   The `CODEX_HOME` resolution and the subsequent `node` invocation
   MUST be in separate, sequenced shell statements (joined with `&&`
   or `;`) — combining them as same-line `VAR=... CMD args` causes
   `$CODEX_HOME` to be expanded BEFORE the assignment takes effect,
   which produces an empty path and silently misroutes the call.

   Canonical form:

   ```
   Bash({
     command: `set -e; \
       PROMPT_FILE="<absolute path written in step 4>"; \
       [ -f "$PROMPT_FILE" ] || exit 1; \
       trap 'rm -f "$PROMPT_FILE"' EXIT; \
       CODEX_HOME=$(ls -1d ~/.claude/plugins/cache/*/codex/*/ 2>/dev/null | sort -V | tail -1); \
       [ -n "$CODEX_HOME" ] || exit 0; \
       [ -f "$CODEX_HOME/scripts/codex-companion.mjs" ] || exit 0; \
       grep -q 'valueOptions.*"prompt-file"' "$CODEX_HOME/scripts/codex-companion.mjs" || exit 0; \
       command -v node >/dev/null 2>&1 || exit 0; \
       CLAUDE_PLUGIN_ROOT="$CODEX_HOME" node "$CODEX_HOME/scripts/codex-companion.mjs" task --prompt-file "$PROMPT_FILE"`,
     run_in_background: true
   })
   ```

   The order matters: `PROMPT_FILE` assignment and the cleanup `trap`
   come BEFORE the codex preflight guards. If a guard exits 0
   (graceful degradation: codex plugin missing, node missing, etc.)
   the `EXIT` trap still fires and removes the temp file. If the trap
   were registered after the preflight, those exit paths would leave
   the prompt file (containing the sanitized topic and sub-questions)
   on disk indefinitely.

   Passing only the path keeps the prompt out of `argv` entirely,
   removing both `ps aux` exposure and the system `ARG_MAX` ceiling.

   The `grep` preflight guard is load-bearing. Older `codex-companion`
   builds that predate `--prompt-file` would treat the unknown flag as
   positional argv, making `"--prompt-file <path>"` the literal prompt.
   The pattern matches the parser's `valueOptions` declaration that
   exists only when the flag is recognized; a miss exits 0 — graceful
   degradation instead of silent malfunction.

   The codex-companion `task` subcommand defaults to foreground
   (synchronous). The `run_in_background: true` flag is at the Bash
   layer so Claude proceeds with its own research while Codex
   completes its turn. Do NOT pass `--background` to codex-companion
   itself — that puts the task into Codex's internal queue and
   requires polling, which violates the "wait for the Bash
   notification, do not poll" rule below.

   Each guard returns `exit 0` (not non-zero) so that the missing-codex
   path is treated as graceful degradation rather than a workflow
   error — the research SKILL's collect step interprets an empty
   output as "Codex unavailable" and proceeds Claude-only. The
   `[ -f "$PROMPT_FILE" ]` guard is the one exception: if the temp
   file was not written, the dispatch is broken and exits non-zero so
   the failure is visible.

6. Claude proceeds immediately to Step 2 of the research SKILL
   (per-sub-question WebSearch / WebFetch).

### Step 2: Collect — before research SKILL Step 3 synthesis

1. Wait for the background Bash notification — do NOT poll, sleep,
   or proactively check status.
2. Read the codex-companion output. The output is the structured
   answer to the research-scan prompt: claims and sources for each
   sub-question.
3. If Codex failed, returned empty, or produced unusable output,
   record the failure mode internally and proceed to Synthesize with
   Claude-only findings. Mention degradation in the user-facing
   completion summary AFTER the brief is saved — never as a finding
   label inside the brief artifact.

### Step 3: Synthesize — during research SKILL Step 3

1. Normalize each Codex finding into the intermediate Claim Shape
   defined below.
2. Reconcile Claude's findings with Codex's findings via the
   four-category taxonomy below.
3. Apply Citation Remapping: Codex's labels are NEVER copied into
   the final brief. Each Codex source must be Claude-verified before
   becoming a numeric `[N]` entry in the Sources section.
4. Apply Source Union for AGREED-with-different-sources cases.
5. Resolve CODEX-ONLY factual claims via the rules below.
6. Hand the merged content back to research SKILL Step 3 for
   sub-question organization, citation numbering (capture order
   preserved), and confidence rating.

---

## Prompt Construction

The research-scan prompt is composed of XML blocks. Required blocks:

- `<task>` — sanitized topic, sub-questions, scope statement
- `<structured_output_contract>` — output shape (claim → conclusion → sources)
- `<grounding_rules>` — every claim grounded in a verifiable source
- `<research_mode>` — separate observed facts from inferences
- `<citation_contract>` — what Codex must include with each source
- `<privacy_contract>` — what Codex must NOT include in its response

Template:

```xml
<task>
Independently research the following topic. Answer each sub-question
with cited evidence. Do not see Claude's findings — produce a fresh
analysis from primary sources where available.

Topic: {sanitized topic}
Scope: {scope statement}
Sub-questions:
1. {sub-question 1}
2. {sub-question 2}
{...}
</task>

<structured_output_contract>
For each sub-question, return:
1. Sub-question (verbatim)
2. Claim (one-sentence answer)
3. Conclusion (longer synthesis paragraph)
4. Sources (list of {url, title, source-type, access-date})
   - source-type: official-docs | standards | academic | secondary
5. Confidence (HIGH | MEDIUM | LOW)
6. Caveats (limits, freshness concerns, alternative interpretations)
</structured_output_contract>

<citation_contract>
- Each substantive claim is backed by at least one source URL.
- Source URLs must be retrievable (no paywalled-only or invented URLs).
- Source-type classification matches the four-tier taxonomy in
  the research brief spec (official-docs / standards / academic /
  secondary).
- Access date in ISO YYYY-MM-DD.
- Do NOT use Codex-internal numeric citation labels in the response —
  identify each source by URL.
</citation_contract>

<grounding_rules>
Every claim references a specific source URL. Inferences (synthesis
beyond cited material) are explicitly labeled "INFERENCE:".
Marketing claims ("best", "fastest", "most popular") require benchmark
or consensus citations.
</grounding_rules>

<research_mode>
Separate observed facts from inferences.
Prefer breadth across sub-questions before depth on any one.
</research_mode>

<privacy_contract>
The topic and sub-questions have been pre-sanitized for proprietary
content. Do not fabricate identifiers, paths, or names beyond what is
stated. Do not echo back any internal identifier the topic may still
reference.
</privacy_contract>
```

Model and effort are NOT passed via flags — the user's Codex config is
the single source of truth.

---

## Independence Rule

Codex must analyze independently. The Codex prompt does NOT include:

- Claude's in-progress findings, synthesis drafts, or citation list
- Claude's confidence ratings or judgments about sources
- Claude's interpretation of which sub-questions are easy or hard

Both models receive the same raw context: topic, sub-questions, scope.
Each model conducts its own search and citation capture. The
research-scan ensemble is **true parallel research**, not gap analysis.
There is no verify-style exception in this protocol.

---

## Normalized Claim Shape

The intermediate shape applied to BOTH Claude and Codex findings before
synthesis:

```
{
  sub_question: <verbatim text>,
  claim: <one-sentence answer>,
  conclusion: <longer synthesis>,
  sources: [
    { url: <canonical url>,
      title: <or hostname/path fallback>,
      source_type: official-docs | standards | academic | secondary,
      access_date: <ISO YYYY-MM-DD>
    },
    ...
  ],
  confidence: HIGH | MEDIUM | LOW,
  caveats: <freshness, alternatives, limits>
}
```

This shape is internal — it is not written into the brief artifact.
The brief uses the structure defined in
`skills/research/references/research-brief-spec.md`. Synthesis maps
normalized claims into the brief's Findings and Sources sections.

---

## Synthesis Categories

This plugin registers **sub-rule extensions** under the omcc-dev base
synthesis taxonomy per the omcc-dev *Extension Contract* (Shape 1 —
sub-rule extension). The category table below mirrors the four base
names — `AGREED`, `CLAUDE-ONLY`, `CODEX-ONLY`, `CONFLICT` — with
identical core semantics. The handling subsections that follow
register research-local qualifiers under those names:

- *AGREED handling* registers the **Source Union** sub-rule
  (different sources, same conclusion) and a confidence-tier
  resolution rule for same-conclusion / different-confidence cases.
- *CODEX-ONLY handling* registers the **Path A / Path B / forbidden
  Path C** sub-rule — citation-discipline scoping that the research
  brief audit imposes on Codex-discovered claims.
- *CONFLICT handling* registers a delegate to the research SKILL's
  Conflict Handling rule and the brief spec's canonical wording.

Base category names and core conditions are not modified, renamed, or
removed by these extensions. Every claim from either model classifies
into one of four categories during reconciliation:

| Category     | Condition                                        |
|--------------|--------------------------------------------------|
| AGREED       | Both models reached the same conclusion          |
| CLAUDE-ONLY  | Claude found it, Codex did not                   |
| CODEX-ONLY   | Codex found it, Claude did not                   |
| CONFLICT     | Models reached opposing conclusions              |

### AGREED handling

- Same sources: present once with the existing citations.
- Different sources, same conclusion: AGREED + **Source Union**
  (verified, URL-deduplicated). Each Codex source goes through
  Citation Remapping before joining the union.
- Same conclusion, different confidence: take the higher confidence
  level only when its source-tier coverage is at least as strong as
  the lower-confidence side. Otherwise keep the lower confidence and
  record the divergence in Open Questions.

### CLAUDE-ONLY handling

Present normally with Claude's citations. No special label appears in
the brief — the brief never carries source-of-discovery labels.

### CODEX-ONLY handling

The brief's audit checklist requires every substantive claim to have
either a `[N]` citation OR an allowed sentinel (per
`skills/research/references/research-brief-spec.md`). CODEX-ONLY
claims must take ONE of these paths:

- **Path A — Verify and cite**: Claude fetches the Codex-provided
  source via WebFetch, confirms the claim, and adds a numeric `[N]`
  citation in research capture order. The claim becomes a normal
  cited finding, indistinguishable from Claude-discovered findings in
  the final brief.
- **Path B — Open Question**: Move the claim into the brief's
  "Open Questions / Gaps" section as an unresolved evidence pointer.
  The Open Questions entry mentions the topic of the gap but does NOT
  cite the unverified source — bare-URL pointers do not pass the
  audit.

Path C — using `[uncited inference]` — is **forbidden** for factual
external claims. The `[uncited inference]` sentinel is reserved for
the model's own interpretation/synthesis. A factual claim attributed
to an external source cannot be inference; it must be verified or
deferred.

### CONFLICT handling

Apply the Conflict Handling rule from the research SKILL Step 3:
present both interpretations with their citations. Do not pick a
winner unless one source is significantly higher tier. The wording in
`skills/research/references/research-brief-spec.md` is canonical when
the two rules diverge.

---

## Citation Remapping

Codex's response uses Codex-internal labels (none, prose, or its own
numbering scheme). These are NOT copied into the final brief. Mapping
rule:

1. For each Codex source URL, canonicalize: strip tracking parameters
   and trailing-slash variations.
2. Compare against Claude's already-captured Sources by canonical URL.
3. If match: the source is already in the brief; the Codex finding's
   citation is the existing `[N]`.
4. If no match (new source from Codex), apply Path A or Path B from
   "CODEX-ONLY handling" above. Path A appends a new entry to Sources
   in research capture order — the next available `[N]`. Path B does
   not modify Sources.

The brief's Sources section remains single-numbered, capture-order
preserving, and URL-deduplicated per
`skills/research/references/research-brief-spec.md`. Codex contributes
to that ordering only via Path A.

---

## Privacy

The research SKILL Step 1.1 privacy gate covers external ensemble
dispatch in addition to web search. Specifically:

- The topic AND sub-questions transmitted in the Codex prompt are
  treated as external transmission. Apply the same redaction rules as
  WebSearch — no proprietary identifiers, paths, customer names,
  unpublished product names, or pasted internal documents.
- The `<privacy_contract>` block in the prompt instructs Codex to
  refrain from fabricating or echoing proprietary identifiers.
- If the user's redaction substitution is generic (e.g., "service X"),
  pass the substituted form to Codex too — never the original
  pre-redaction value.

When the user declines redaction or aborts the session, do NOT
dispatch to Codex.

---

## Failure Handling

### Codex unavailable, not installed, or unauthenticated

- Detect: `CODEX_HOME` resolves to empty, or the codex-companion
  preflight check (file existence + node availability) fails.
- Action: Skip dispatch silently. Proceed Claude-only.
- Surface: Mention in the user-facing completion summary that the
  ensemble was unavailable. Do NOT label findings inside the brief.

### Codex timeout or runtime error

- Detect: Background Bash exits non-zero, or the task subcommand
  reports failure in stderr.
- Action: Record the failure mode internally; proceed Claude-only.
- Surface: Same as above.

### Codex empty output

- Detect: Output contains no claims, only the structural shell, or
  is missing the per-sub-question response blocks.
- Action: Treat as if Codex was unavailable. Proceed Claude-only.
- Surface: Same as above.

### Codex malformed partial output

- Detect: Output is structurally valid but missing required fields
  for some claims (e.g., source-type omitted, claim without
  conclusion, source-URL field empty).
- Action: Parse only the claims that pass structural validation
  (claim + conclusion + at least one retrievable source URL).
  Discard claims with unverifiable or empty source URLs. Continue
  with the salvageable subset for synthesis.
- Surface: Mention in the completion summary that ensemble coverage
  was partial.

### Codex returns CODEX-ONLY claim with no source URL

- Treat as malformed at the per-claim level (no source URL = nothing
  to verify).
- Discard the claim. Do NOT add it to Open Questions — there is
  nothing to follow up on.

### Graceful degradation principle

The brief is always assembled and saved on the Claude-only path.
Ensemble failure NEVER blocks save. The completion summary states
the degradation; the brief itself shows no ensemble-specific labels
or markers — readers of the brief should not be able to tell whether
ensemble ran at all.

---

## State and Recovery

omcc-research has no workflow file analogous to omcc-dev's
`/start` / `/fix` / `/audit` state. The research-scan ensemble is
therefore **in-session only**:

- The `pending_ensemble` bookkeeping pattern from omcc-dev does not
  apply here.
- If the session compacts or terminates while a Codex job is in
  flight, that job becomes uncollectable. The next
  `/omcc-research:research` invocation does NOT recover it — the user
  re-runs the topic.
- This is an explicit design gap for v2. A v3 with workflow state may
  add recovery; v2 trades recovery for plugin simplicity.

---

## Boundary with omcc-dev:brainstorm

Both `omcc-research:research` and `omcc-dev:brainstorm` invoke a
Codex ensemble. The boundary remains the one defined in
`CLAUDE.md`: research is **topic-bound** and produces a durable cited
brief; brainstorm is **decision-bound** and produces an option
comparison.

The shared ensemble surface does not blur this boundary. Each skill's
ensemble point uses a distinct prompt template and synthesizes into a
distinct artifact contract — research-scan into the brief structure,
brainstorm into a recommendation. Researchers gathering evidence
reach for `/omcc-research:research`; reviewers choosing between
options reach for `/omcc-dev:brainstorm`.

---

## Related

- `skills/research/SKILL.md` — research skill body; calls into this
  protocol from its command-invoked mode.
- `skills/research/references/research-brief-spec.md` — canonical
  brief structure, citation conventions, audit checklist.
- `skills/research/references/output-file-rules.md` — output-file
  conventions; the existing-directory check that gates ensemble
  dispatch lives here.
- `commands/research.md` — command entry point.
- `CLAUDE.md` — contributor notes; boundary with brainstorm.

The omcc-dev plugin's ensemble-protocol document inspires this
protocol's three-step Launch / Collect / Synthesize structure and
its independence-and-graceful-degradation principles. That plugin's
protocol covers seven code-domain ensemble point types
(brainstorm / explore / plan-verify / review / investigate /
fix-verify / audit-scan), none of which applies to topic-bound
research; research-scan is the research-domain analog. The
omcc-dev document is referenced here in prose only because
cross-plugin backtick references in markdown are rejected by the
marketplace structure tests.

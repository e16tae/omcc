# Design Ensemble Protocol

Defines how Claude and Codex operate as a dual-model ensemble for the
**design-critique-scan** ensemble point — the design-domain analog of
the text ensemble points used by other omcc plugins. Activated inside
the design-evaluation skill's command-invoked mode (`/omcc-designer:audit`)
and the design-interview skill's command-invoked mode
(`/omcc-designer:start`, `/omcc-designer:formalize`) to provide an
independent design critique alongside Claude's own evaluation or
consultation proposals.

The user never invokes Codex directly. The command path orchestrates
dispatch, collection, and synthesis transparently. When the codex
plugin is not installed or returns no usable output, the ensemble
degrades silently to Claude-only.

This protocol is plugin-local. The omcc-research and omcc-dev plugins
each own their domain-specific ensemble protocols; their structures
inspire this document but are intentionally NOT referenced by backtick
because cross-plugin backtick references in markdown are rejected by
the marketplace structure tests, and per the repo's "Independence over
uniformity" principle each plugin owns its own domain contract.

---

## When This Protocol Applies

Activates in two command-invoked surfaces:

1. **design-evaluation** command-invoked mode (`/omcc-designer:audit`)
   — automatic dispatch after scope is resolved. The `audit-artifact`
   prompt variant is used.
2. **design-interview** command-invoked mode (`/omcc-designer:start`
   or `/omcc-designer:formalize`) — **user-initiated only**. The
   user asks for a "second opinion" inside Step C (Visual Direction
   & Color) recommend-then-confirm loop. The `step-c-direction`
   prompt variant is used.

Does NOT apply to:

- Auto-activated mode of design-evaluation or design-interview
  outside of a command — auto-activated callers run Claude-only. This
  is consistent with the staged-rollout posture: the multi-model
  surface is opt-in per command, not implicit per skill.
- design-analysis, design-extraction, brief-generation,
  design-planning, poster, poster-render, social-graphics, or
  social-graphics-render. Image-render skills already shell out to
  the codex plugin for raster generation; this protocol covers
  text-level critique only.
- Inline cross-references from other plugins or commands.
- Binary confirmations or progress updates within the same session.

---

## Affinity

For omcc-designer v1 the ensemble is **always-on** in
design-evaluation command-invoked mode (the audit-artifact variant)
and **always-available, never auto-fired** in design-interview
command-invoked mode (the step-c-direction variant).

The audit surface always benefits from a second opinion — a missed
issue is exactly the cost the ensemble exists to reduce. The
consultation surface is different: most Step C decisions are
working-memory-resident with the user, and an unsolicited Codex
fork would interrupt the cumulative reflection rhythm the interview
protocol depends on. Hence the consultation rule: dispatch only on
explicit user request.

A future v2 may introduce graduated affinity (e.g., scope-conditional
auto-firing for `/audit accessibility` while keeping consultation
opt-in). v1 keeps the surface simple and relies on graceful
degradation when the cost would be unjustified (e.g., the codex
plugin is not installed at all).

---

## Execution Pattern

Three steps per dispatch: Launch, Collect, Synthesize.

### Step 1: Launch — after scope resolution / user request

Pre-conditions before dispatch:

1. **Scope resolution**:
   - For `audit-artifact`: the design-evaluation SKILL has resolved
     the audit scope (brand consistency / visual hierarchy /
     accessibility / typography / color system / layout / full)
     either from the invocation argument or from input analysis.
     Codex receives the resolved scope, not "decide it yourself".
   - For `step-c-direction`: the user has explicitly requested a
     "second opinion" inside Step C **while a specific question is
     in flight** (the recommend-then-confirm loop is active for one
     of palette / typography / visual style — exactly one — AND
     Claude has already presented its recommendation for that
     question). Requests during the gap between confirmations
     (after one question's confirm but before the next is
     presented) and requests before Claude's recommendation exists
     are rejected — the SKILL nudges the user to wait for the next
     proposal. The interview SKILL has captured: confirmed Step A
     (project context), confirmed Step B (brand identity), the
     current Step C question, and Claude's working recommendation
     for that question.
2. **Privacy gate**: see "Privacy" below. The artifact / brief
   content slated for transmission has been screened (or redacted)
   and the user has confirmed external transmission when the content
   includes proprietary brand or customer material.
3. **Independence**: Codex MUST receive raw context (artifact,
   confirmed Step A/B for direction variant), NOT Claude's draft
   findings or palette/typography proposals. This is the canonical
   independence rule — no "verify-style exception" applies in this
   protocol.

Dispatch:

4. Resolve codex-companion at runtime via the cache glob:

   ```
   CODEX_HOME=$(ls -1d ~/.claude/plugins/cache/*/codex/*/ 2>/dev/null | sort -V | tail -1)
   [ -n "$CODEX_HOME" ] && [ -f "${CODEX_HOME}scripts/codex-companion.mjs" ]
   ```

   If either check fails, ensemble degrades to Claude-only — see
   "Failure Handling".

5. Construct the design-critique-scan prompt per "Prompt
   Construction" below — pick `audit-artifact` or `step-c-direction`
   variant — and write it to a per-dispatch temporary file via
   Claude's `Write` tool. Do NOT embed the prompt text into the
   shell command itself; the prompt contains user-controlled
   material (artifact text, brand description, confirmed Step A/B)
   and any shell-level construct that mixes user input with the
   command line (string interpolation, heredoc, etc.) can be
   collision-prone or injection-prone for some inputs. The `Write`
   tool writes a literal string and never invokes a shell.

   Use a private temp path that is unique per dispatch — e.g.,
   `${TMPDIR:-/tmp}/omcc-designer-critique-prompt-<session-id>-<dispatch-id>.txt`.
   Remove the file after dispatch (success or failure).

6. Execute as a background Bash. The shell passes only the file
   path to `codex-companion`; the prompt content is read directly
   by the companion via `fs.readFileSync` and never crosses shell
   parsing, the process argv, or `ps aux`.

   The `CODEX_HOME` resolution and the subsequent `node` invocation
   MUST be in separate, sequenced shell statements (joined with
   `&&` or `;`) — combining them as same-line `VAR=... CMD args`
   causes `$CODEX_HOME` to be expanded BEFORE the assignment takes
   effect, producing an empty path and silently misrouting the call.

   Canonical form:

   ```
   Bash({
     command: `set -e; \
       PROMPT_FILE="<absolute path written in step 5>"; \
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

   The order matters: `PROMPT_FILE` assignment and the cleanup
   `trap` come BEFORE the codex preflight guards. If a guard exits
   0 (graceful degradation: codex plugin missing, node missing,
   etc.) the `EXIT` trap still fires and removes the temp file. If
   the trap were registered after the preflight, those exit paths
   would leave the prompt file (containing the artifact text or
   Step A/B context) on disk indefinitely.

   Passing only the path keeps the prompt out of `argv` entirely,
   removing both `ps aux` exposure and the system `ARG_MAX` ceiling
   — relevant because design briefs and audit artifacts can be
   long.

   The `grep` preflight guard is load-bearing. Older
   `codex-companion` builds that predate `--prompt-file` would
   treat the unknown flag as positional argv, making
   `"--prompt-file <path>"` the literal prompt. The pattern matches
   the parser's `valueOptions` declaration that exists only when
   the flag is recognized; a miss exits 0 — graceful degradation
   instead of silent malfunction.

   Each guard returns `exit 0` (not non-zero) so the missing-codex
   path is treated as graceful degradation. The
   `[ -f "$PROMPT_FILE" ]` guard is the one exception: if the temp
   file was not written, the dispatch is broken and exits non-zero
   so the failure is visible.

7. Claude proceeds immediately to its own analysis (the
   audit-perspective evaluation, or the Step C palette/typography
   recommendation it had already prepared). **No polling** of the
   background Bash task — the SKILL waits for the completion
   notification before entering Collect.

### Step 2: Collect — before synthesis presentation

1. Wait for the background Bash notification — do NOT poll, sleep,
   or proactively check status.
2. Read the codex-companion output. The output is the structured
   answer to the variant prompt: severity-rated findings (audit
   variant) or alternative direction proposals (Step C variant).
3. Route the output through "Failure Handling" below. The branches
   diverge:
   - **Codex failed / returned empty**: record internally; proceed
     to Synthesize with Claude-only results.
   - **Malformed-partial output**: parse the salvageable subset per
     the "Codex malformed partial output" rule; proceed to
     Synthesize with the surviving records merged into the normal
     pipeline (NOT degraded to Claude-only).
   - **Wrong-language output**: translate to the user's interaction
     language per the "Codex output in the wrong language" rule;
     proceed to Synthesize normally (NOT degraded). Translation
     unavailability falls back to Claude-only.
   Mention any degradation in the user-facing completion summary
   AFTER findings / suggestions are presented — never as a label
   inside the findings table or proposal text.

### Step 3: Synthesize — during SKILL presentation

1. Normalize Codex output into the **Normalized Design Finding
   Shape** (audit variant) or the **Normalized Direction Proposal
   Shape** (Step C variant) defined below.
2. Reconcile Claude's findings/proposals with Codex's via the
   variant-specific synthesis category set below.
3. Hand the merged content back to the SKILL for presentation:
   - Audit: severity-grouped findings (Critical > High > Medium >
     Low > positive observations).
   - Step C: a single coherent recommendation for the user to
     accept / modify / decline (Confirmed Decision Principle).

---

## Independence Rule

Codex must analyze independently. The Codex prompt does NOT include:

- Claude's in-progress findings, draft severities, or proposed
  remediation (audit variant).
- Claude's recommended palette, typography, or visual style proposal
  (step-c-direction variant).
- Claude's confidence ratings or judgments.

Both models receive the same raw context:

- Audit variant: design artifact (image path, brief text, structured
  spec — see "Artifact Packaging" inside the design-evaluation
  SKILL command-invoked mode), resolved audit scope, and the
  evaluation perspectives applicable to that scope.
- Step C variant: confirmed Step A (project context, audience,
  purpose), confirmed Step B (brand identity, personality), and the
  Step C question currently in flight (one of palette / typography /
  visual style — exactly one per dispatch).

The design-critique-scan ensemble is **true parallel critique**, not
gap analysis. There is no verify-style exception.

---

## Prompt Construction

Both variants use XML block structure. Required blocks for both:

- `<task>` — variant-specific job description with sanitized context
- `<structured_output_contract>` — exact output shape
- `<grounding_rules>` — ground claims in artifact/context, label
  inferences
- `<privacy_contract>` — what Codex must NOT include in its response

Variant-specific additional blocks documented below.

Model and effort are NOT passed via flags — the user's Codex config
is the single source of truth.

### Variant 1: `audit-artifact`

For design-evaluation command-invoked mode.

```xml
<task>
Independently evaluate the following design artifact for quality
issues. Do not see Claude's findings — produce a fresh critique
from the artifact alone.

Artifact (verbatim or summary): {sanitized artifact reference}
Audit scope: {one of: brand-consistency | visual-hierarchy |
              accessibility | typography | color-system |
              layout | full}
Applicable evaluation perspectives: {list, derived from scope}

For each issue: assign severity (Critical / High / Medium / Low),
locate it (zone, section, element), explain what the issue is and
why it matters, and recommend a professional fix.
</task>

<structured_output_contract>
Return findings as a list. For each finding:
1. Perspective (one of the applicable perspectives)
2. Severity (Critical / High / Medium / Low)
3. Location (zone / section / element identifier)
4. Issue (what is wrong, with concrete evidence)
5. Recommendation (professional fix direction)

After findings, return a list of positive observations:
- Perspective
- Location
- What the design does well
</structured_output_contract>

<grounding_rules>
Every finding references a specific location in the artifact.
Inferences beyond observed evidence are explicitly labeled
"INFERENCE:". Severity assignments follow the published
severity definitions used by the design-evaluation skill — when
unsure, prefer the lower severity and label the choice explicitly.
</grounding_rules>

<privacy_contract>
The artifact and context have been pre-sanitized for proprietary
brand or customer content. Do not fabricate identifiers, brand
names, or descriptions beyond what is stated. Do not echo back any
internal identifier the artifact may still reference.
</privacy_contract>
```

### Variant 2: `step-c-direction`

For design-interview command-invoked mode, user-initiated.

```xml
<task>
Propose an alternative design direction for the following Step C
question. Base your proposal only on the confirmed project context
and brand identity below. Do not see Claude's recommendation —
produce an independent direction the client may consider.

Project context (Step A confirmed): {sanitized}
Brand identity (Step B confirmed): {sanitized}
Step C question: {one of: palette | typography | visual-style}
Question detail: {specific aspect the user wants a second opinion on}
</task>

<structured_output_contract>
Return:
1. Proposal name (one phrase)
2. Specifications:
   - For palette: hex codes for primary / secondary / accent /
     neutrals, with role for each
   - For typography: heading / body / accent font names with
     pairing rationale
   - For visual style: mood keywords, imagery approach, style
     reference (no proprietary brand citations)
3. Rationale (why this direction fits the confirmed context and
   brand)
4. Tradeoffs (what this direction trades off versus alternatives)
</structured_output_contract>

<grounding_rules>
Ground rationale in the confirmed project context and brand
identity. Avoid color psychology generalizations untethered from
audience or purpose. Inferences beyond confirmed context are
labeled "INFERENCE:".
</grounding_rules>

<privacy_contract>
The project context and brand identity have been pre-sanitized.
Do not fabricate client names, product names, or proprietary
identifiers. Do not echo back any internal identifier the input
may still reference.
</privacy_contract>
```

---

## Normalized Design Finding Shape (audit variant)

Applied to BOTH Claude and Codex findings before synthesis:

```
{
  perspective: <one of brand-consistency | visual-hierarchy |
                accessibility | typography | color-system |
                layout>,
  severity: <Critical | High | Medium | Low>,
  location: <zone / section / element identifier — required>,
  issue: <one-sentence description with evidence>,
  recommendation: <professional fix direction>,
  source: <Claude | Codex>   # internal label, not part of presentation
}
```

A finding without `location` is **discarded** — the audit's
remediation step requires a location sufficient for independent
verification, and a CODEX-ONLY finding lacking it has nothing to
follow up on.

A "positive observation" uses a parallel shape:

```
{
  perspective: <as above>,
  location: <required>,
  what_works: <one-sentence description>,
  source: <Claude | Codex>
}
```

This shape is internal — it is not written into the audit
presentation as-is. The SKILL maps normalized records into the
severity-grouped finding list and the positive observations
section.

---

## Normalized Direction Proposal Shape (step-c-direction variant)

```
{
  question: <palette | typography | visual-style>,
  proposal_name: <one phrase>,
  specifications: <variant-specific structured object>,
  rationale: <paragraph — grounded in confirmed Step A/B>,
  tradeoffs: <paragraph — what this direction trades off>,
  source: <Claude | Codex>
}
```

Step C synthesis presents one or more proposals to the user; the
user picks one (or asks for further iteration). No proposal is
written into the brief without explicit user confirmation
(Confirmed Decision Principle).

---

## Synthesis Categories (audit variant)

Every audit finding from either model classifies into one of five
categories during reconciliation:

| Category                 | Condition                                                                      |
|--------------------------|--------------------------------------------------------------------------------|
| AGREED                   | Both models flag the same issue at the same location, severity matches         |
| AGREED-with-severity-delta | Both flag the same issue at the same location, severity differs               |
| CLAUDE-ONLY              | Only Claude found it                                                           |
| CODEX-ONLY               | Only Codex found it (and `location` is present — otherwise discarded)         |
| CONFLICT                 | Both report at the same location but the issue or recommendation conflicts     |

**"Same location" predicate**: two findings refer to the same
location iff their `perspective` matches AND their `location`
identifier refers to the same element / zone / section. Identifier
matching uses canonical normalization — case-insensitive, trimmed,
and resolving common synonyms (e.g., `headline` ≡ `title block`,
`primary CTA` ≡ `main CTA button`) to a shared canonical token. The
SKILL maintains the synonym table for the domain it operates in;
genuinely ambiguous overlaps (e.g., "header area" vs "headline")
are NOT collapsed and surface as separate findings (CLAUDE-ONLY +
CODEX-ONLY) rather than risk under-counting.

**"Same issue" predicate**: two findings describe the same issue
iff their `recommendation` directions are compatible (a single fix
addresses both, or one fix is a strict refinement of the other).
When both findings share location and perspective but the
recommendations point at incompatible interventions (e.g.,
"increase font size" vs "tighten letter spacing"), the entry is
CONFLICT, not AGREED.

**Source-symmetric location-required rule**: a finding without
`location` is discarded **regardless of source** — the rule applies
identically to Claude and Codex findings. The Failure Handling
section's "CODEX-ONLY without location" entry is an instance of
this symmetric rule, not a Codex-specific exception.

### AGREED handling

- Same severity: present once, severity unchanged. Internal source
  label dropped (presented as an unattributed audit finding).

### AGREED-with-severity-delta handling

- Take the **higher** severity. Both rationales are captured: the
  presented `issue` text is Claude's; a one-sentence parenthetical
  notes the alternate severity rationale ("Alternate severity
  rationale: …" — never name "Claude" or "Codex" in the
  parenthetical, per the no-source-label presentation contract).
  Avoid inflating severity by default — when both models agree the
  issue exists but disagree on severity, the higher rating becomes
  the working assumption, but the lower rating's argument is
  preserved for the user's remediation decision.

### CLAUDE-ONLY handling

- Present normally. No presentation-level source label appears in
  the audit findings table; the internal `[Claude]` label exists
  for SKILL bookkeeping only.

### CODEX-ONLY handling

- Present normally if `location` is present. As with CLAUDE-ONLY,
  no presentation-level source label appears.
- If `location` is absent: discard the finding. Do not surface as
  an unverifiable hint — the audit's remediation loop iterates
  over **actionable** findings, and a finding without a location
  has nothing to act on.

### CONFLICT handling

- Both models report at the same location but the issue
  description, evidence, or recommendation differs (e.g., Claude
  says heading too small; Codex says heading too tight letter-spacing).
- Present both rationales side by side. The remediation step
  treats the CONFLICT entry as one actionable finding with two
  candidate `Issue` framings; the user picks which (or both, or
  neither) to act on.

### Positive observations (parallel taxonomy)

Positive observations are NOT merged via the AGREED/CONFLICT axes —
they are an additive surface, not a defect surface. Apply this
rule:

- Same perspective + same location: deduplicate (present once).
- Otherwise: present each side's positives as separate entries.

No source labels appear in the presented positive observations —
internal `source` is bookkeeping only.

---

## Synthesis Categories (step-c-direction variant)

Reconciliation between Claude's recommendation and Codex's
proposal. The trigger contract (Step 1 Launch precondition for
`step-c-direction`) guarantees Claude has presented a
recommendation BEFORE the dispatch fires — so the synthesis
always has a Claude-side proposal to compare against. The
"Claude has not yet recommended" path does not reach this
synthesis stage; the SKILL rejects the trigger before dispatch.

| Category    | Condition                                                                                                            |
|-------------|----------------------------------------------------------------------------------------------------------------------|
| ALIGNED     | Both propose the same direction (same color family / type pairing / mood keywords)                                   |
| COMPLEMENT  | Codex proposes a meaningfully different direction that fits the confirmed Step A/B equally well                       |
| DIVERGENT   | Codex proposes a direction at odds with the confirmed Step A/B (rare — usually a context-misread by one of the two)   |

### ALIGNED handling

- Present Claude's recommendation. The Codex echo is bookkept but
  not surfaced as a separate proposal — the user picked a single
  question, an aligned echo adds noise without information.

### COMPLEMENT handling

- Present both proposals as alternatives. The user picks one,
  asks for iteration, or rejects both. Confirmed Decision Principle
  applies: neither proposal is recorded as confirmed until the
  user explicitly says so.

### DIVERGENT handling

- Surface the divergence with a brief note: "Codex's proposal does
  not appear to fit the confirmed brand identity — possible
  context misread." Present Claude's proposal as the primary
  recommendation, the Codex proposal as a flagged alternative.
  The user decides whether the divergence is genuinely
  surprising (worth exploring) or a misread (worth ignoring).

### Single-dispatch rule

Each Step C question receives **at most one** Codex dispatch per
question per session. If the user requests another second opinion
on the same question, the SKILL re-presents the existing Codex
proposal rather than re-dispatching. The user must explicitly
indicate "different angle" — and even then the SKILL should
prefer iteration over re-dispatch.

### Stale-dispatch rule

If the user revises a confirmed Step A or Step B after a Step C
Codex dispatch has completed, the existing Codex proposal is
**discarded** — its grounding is no longer valid. The user is
informed: "Step B was revised; the previous Codex proposal no
longer applies. Request a new second opinion if needed."

---

## Privacy

Design artifacts and project context can carry proprietary brand,
customer, or campaign content. The Step 1 Launch privacy gate
covers external transmission to Codex with these rules:

- The artifact text, brand description, project context, and any
  Step A/B confirmed values transmitted in the Codex prompt are
  treated as external transmission. Apply the same redaction
  posture as the research SKILL's Step 1.1 privacy gate: ask the
  user before transmitting proprietary content, accept generic
  substitutions ("client X" for the actual client name), refuse
  dispatch if redaction is declined for content the user marked
  sensitive.
- The `<privacy_contract>` block in each prompt instructs Codex
  to refrain from fabricating or echoing proprietary identifiers.
- If the user's redaction substitution is generic (e.g., "the
  client" instead of the actual name), pass the substituted form
  to Codex too — never the original pre-redaction value.
- For `/audit` of a third-party artifact (the user is critiquing
  someone else's design), the privacy posture is normal — the
  artifact is being critiqued, not authored.
- For `/start` and `/formalize` Step C, the project context
  often contains the user's own brand strategy. Prefer
  user-confirmed redaction over assumption.

When the user declines redaction or aborts the privacy gate, do
NOT dispatch to Codex. Proceed Claude-only.

---

## Failure Handling

### Codex unavailable, not installed, or unauthenticated

- Detect: `CODEX_HOME` resolves to empty, or the codex-companion
  preflight check (file existence + `--prompt-file` support + node
  availability) fails.
- Action: Skip dispatch silently. Proceed Claude-only.
- Surface: Mention in the user-facing completion summary that the
  ensemble was unavailable. Do NOT label findings or proposals
  inside the presentation.

### Codex timeout or runtime error

- Detect: Background Bash exits non-zero, or the task subcommand
  reports failure in stderr. A reasonable session-level wall-clock
  bound is 120 seconds for design critique tasks; the SKILL may
  surface "Codex slow — proceeding with Claude-only" if the bound
  is exceeded with no notification.
- Action: Record the failure mode internally; proceed Claude-only.
- Surface: Same as above.

### Codex empty output

- Detect: Output contains no findings (audit variant) or no
  proposal (Step C variant) — only the structural shell.
- Action: Treat as if Codex was unavailable. Proceed Claude-only.
- Surface: Same as above.

### Codex malformed partial output

- Detect: Output is structurally valid but missing required fields
  for some findings/proposals (e.g., severity omitted, location
  empty, specifications object lacks the requested variant fields).
- Action: Parse only the records that pass structural validation
  (audit: perspective + severity + location + issue + recommendation
  all present; Step C: question + specifications + rationale all
  present). Discard malformed records. Continue with the
  salvageable subset for synthesis.
- Surface: Mention in the completion summary that ensemble
  coverage was partial.

### Codex CODEX-ONLY audit finding without location

- Treat as malformed at the per-record level (no location =
  nothing to verify or remediate). Discard. Do NOT add to a
  separate "Codex hints" section — that would re-introduce
  unverifiable findings under a different label.

### Codex output in the wrong language

- Detect: User's interaction language does not match the language
  of the parsed findings (e.g., user is consulting in Korean but
  Codex returned English findings). The SKILL will translate
  Codex output to the user's interaction language before
  presentation; this is mechanical, not a failure mode in itself,
  unless the translation cannot be performed (offline, model
  unavailable). In that rare case, fall back to Claude-only.
- Action: Translate, presenting in the user's language.
- Surface: No special note unless translation fails.

### Graceful degradation principle

The audit findings table or Step C recommendation is always
assembled and presented on the Claude-only path. Ensemble failure
NEVER blocks presentation. The completion summary states the
degradation; the presented findings/proposals show no
ensemble-specific labels — readers should not be able to tell
whether the ensemble ran at all.

---

## State and Recovery

omcc-designer has no workflow file analogous to omcc-dev's
`/start` / `/fix` / `/audit` state. The design-critique-scan
ensemble is therefore **in-session only**:

- The `pending_ensemble` bookkeeping pattern from omcc-dev does
  not apply here.
- If the session compacts or terminates while a Codex job is in
  flight, that job becomes uncollectable. The next command
  invocation does NOT recover it.
- design-interview interruption (per the SKILL.md
  "Interruption handling" subsection) restarts from Phase 1
  (design-analysis or design-extraction). An in-flight Codex
  Step C dispatch at interruption time is uncollectable; the
  user re-runs the consultation.
- design-evaluation interruption is similar — the user re-runs
  the audit.

This is an explicit design gap for v1. A v2 with workflow state
may add recovery; v1 trades recovery for plugin simplicity.

---

## Boundary with research-scan and dev brainstorm

The omcc plugin marketplace currently exposes three text-level
ensemble surfaces. Each owns its own protocol; the boundaries
prevent feature overlap with the marketplace addition rule.

| Aspect            | design-critique-scan (this protocol) | research-scan (omcc-research)   | brainstorm (omcc-dev)              |
|-------------------|--------------------------------------|----------------------------------|------------------------------------|
| Activation        | `/omcc-designer:audit` always; `/omcc-designer:start` and `/omcc-designer:formalize` Step C user-initiated | `/omcc-research:research` always | `/omcc-dev:start` and `/omcc-dev:audit` brainstorm phase |
| Output shape      | Severity-rated findings + alternative direction proposals | Cited evidence brief             | Option comparison + recommendation |
| Persistence       | In-session only (no artifact)        | Durable artifact (research_brief.md) | In-workflow-state decision record  |
| Synthesis axis    | severity (Critical / High / Medium / Low) + Step C alignment | citation source-tier (official-docs / standards / academic / secondary) | option viability + tradeoffs       |
| Independence rule | Strict; no verify exception          | Strict; no verify exception      | Strict, with one verify exception (plan-verify) |

When in doubt: if the user is **critiquing a design artifact** or
asking for **alternative design direction**, design-critique-scan.
If the user is **gathering cited evidence about a topic**,
research-scan. If the user is **choosing between viable options**,
brainstorm.

---

## Related

- `skills/design-evaluation/SKILL.md` — design-evaluation skill
  body; calls into this protocol from its command-invoked mode
  with the `audit-artifact` variant.
- `skills/design-evaluation/references/evaluation-guide.md` —
  severity definitions referenced by the audit synthesis.
- `skills/design-interview/SKILL.md` — design-interview skill
  body; calls into this protocol from its command-invoked mode
  with the `step-c-direction` variant on user request.
- `skills/design-interview/references/confirmed-decision-principle.md`
  — Confirmed Decision Principle that governs Step C proposals.
- `skills/design-interview/references/interview-protocol.md` —
  recommend-then-confirm loop into which the Step C second
  opinion hook is placed.
- `commands/audit.md` — command entry point for design audit.
- `commands/start.md` — command entry point for the consultation
  pipeline.
- `commands/formalize.md` — command entry point for the
  formalization pipeline.
- `CLAUDE.md` — contributor notes; sanctioned cross-plugin
  dependencies and boundary statement vs research-scan and
  brainstorm.

The omcc-research and omcc-dev ensemble protocols inspire this
protocol's three-step Launch / Collect / Synthesize structure and
its independence-and-graceful-degradation principles. Those
plugins' protocols cover their own ensemble point types
(research-scan and brainstorm / explore / plan-verify / review /
investigate / fix-verify / audit-scan respectively); design
domain has its own contract here. Cross-plugin references are
prose only because cross-plugin backtick references in markdown
are rejected by the marketplace structure tests.

# Ensemble Protocol

Defines how Claude and Codex operate as a dual-model ensemble.
Claude orchestrates the workflow, launches Codex for independent parallel analysis,
and synthesizes both perspectives into a unified result for the user.

Codex is dispatched automatically at command-defined phase boundaries
when Ensemble Affinity warrants it. The user may also opt into an
ad-hoc consultation mid-workflow via `/omcc-dev:codex-now` (see
Codex-now below).

---

## When This Protocol Applies

Activates on either of two paths:

- **Automatic**: Ensemble Affinity (per `ensemble-affinity.md`) is
  evaluated during a command execution. Each command file specifies
  which phases invoke the ensemble and with which ensemble point type.
- **User-initiated**: the user invokes `/omcc-dev:codex-now <question>`
  while a workflow is active. Affinity is not evaluated for this path
  — the user's invocation is itself the dispatch trigger. The
  `commands/codex-now.md` command owns the launch and routes through
  the Codex-now Ensemble Point Type (defined below).

Does NOT apply to:
- Inline skills (`brainstorm`, `explore`, `plan`, `investigate`, `parallel-review`)
  when invoked outside of a command — these run without ensemble unless the
  invoking command has already activated it
- Binary confirmations or progress updates
- Internal orchestration decisions

---

## Execution Pattern

Every ensemble point follows three steps: Launch, Collect, Synthesize.

### Step 1: Launch

1. Determine the ensemble point type (see Ensemble Point Types below)
2. Select the codex-companion subcommand:
   - `task` for analysis, diagnosis, brainstorm, plan verification
   - `review --wait` for code review
   - `adversarial-review --wait` for challenging review with focus text
3. Construct the Codex prompt (see Prompt Construction Rules)
4. Execute via background Bash. The `codex-companion.mjs` script lives in the
   **codex plugin** (not the omcc-dev plugin). Resolve the codex plugin root at
   runtime and override `CLAUDE_PLUGIN_ROOT` so the script can find its own
   prompts and templates:

   ```
   Bash({
     command: `CODEX_HOME=$(ls -1d ~/.claude/plugins/cache/*/codex/*/ 2>/dev/null | sort -V | tail -1) && \
       [ -n "$CODEX_HOME" ] && \
       [ -f "${CODEX_HOME}scripts/codex-companion.mjs" ] && \
       command -v node >/dev/null 2>&1 && \
       CLAUDE_PLUGIN_ROOT="$CODEX_HOME" \
       node "${CODEX_HOME}scripts/codex-companion.mjs" \
       <subcommand> [args]`,
     run_in_background: true
   })
   ```

   The `[ -f ... ]` check verifies the codex-companion.mjs file exists at the
   discovered path before executing it. This guards against a stale or
   incompletely-installed cache entry whose directory matches the glob but
   doesn't contain the actual script.

5. Claude proceeds immediately to its own parallel analysis

### Step 2: Collect

1. Claude completes its own analysis (agents, tools, etc.)
2. Read the Codex output from the completed background Bash task
3. If Codex has not finished yet, wait for the background notification —
   do not poll or sleep
4. If Codex failed or returned empty output, record the failure and proceed
   to Synthesize with Claude-only results

### Step 3: Synthesize

Classify every finding, recommendation, or conclusion from both sources
into one of four categories:

| Category     | Condition                                  | Presentation                                        |
|--------------|--------------------------------------------|-----------------------------------------------------|
| AGREED       | Both Claude and Codex reached same conclusion | Present with elevated confidence. Label: **[Both]** |
| CLAUDE-ONLY  | Claude found it, Codex did not             | Present normally. Label: **[Claude]**                |
| CODEX-ONLY   | Codex found it, Claude did not             | Present normally. Label: **[Codex]**                 |
| CONFLICT     | Claude and Codex disagree                  | Present both with evidence. Ask user to decide       |

Synthesis output replaces the standard single-model output.
Follow the Presentation Mode Protocol (`presentation-protocol.md`)
for the synthesized result.

### State Bookkeeping (mandatory)

Whenever an ensemble point is launched from inside a workflow file
(`/start`, `/fix`, `/audit`, `/omcc-dev:codex-now`, `/resume`, or any
skill executing inside one of those workflows), the orchestrator MUST
record the in-flight job in the workflow file per
`continuity-protocol.md` `pending_ensemble` schema. This makes the "Absent when no Codex job is in flight" invariant
hold and lets `/omcc-dev:resume` recover correctly across compaction.

- After Step 1 Launch returns the background Bash task id, append an
  entry `{job_id, ensemble_type, dispatched_at}` to `pending_ensemble`.
  `job_id` is the identifier returned by the launching Bash call.
  `ensemble_type` is one of the Ensemble Point Types below. If the
  launch failed (Bash exited non-zero before backgrounding, or the
  preflight guard rejected codex-companion), no entry is written.
- After Step 2 Collect completes (success, failure, or graceful
  degradation), remove the entry by `job_id`.
- **Exception** for the in-scope automatic `/start` and `/fix`
  ensembles covered by Result Bookkeeping below: the pending-remove
  is deferred until after Step 3 Synthesize so the remove and the
  matching `ensemble_results` append happen in a single atomic
  mutation. Out-of-scope ensembles (`audit-scan`, `codex-now`)
  follow the unconditional rule above and remove pending at Step 2.

Consumer commands (`commands/audit.md`, `commands/fix.md`, etc.) and
skill files MUST NOT redefine these rules; they cross-reference this
section as the single source of truth.

Stale entries left over by an interrupted session are cleared by
`commands/resume.md` Step 5b before phase rehydration — Bash background
task ids do not survive across sessions, so the recorded handle becomes
uncollectable and the originating phase re-executes the launch on resume.

### Result Bookkeeping (mandatory)

Applies to **automatic phase ensembles in `/start` and `/fix` only**.
Excluded by design:

- `/omcc-dev:codex-now` — user-initiated ad-hoc consultation; result
  stays in-conversation only.
- `/audit` audit-scan — audit results land in `findings` (the
  audit-specific result store at `continuity-protocol.md`
  Workflow-type-specific frontmatter for `/audit`), not in
  `ensemble_results`. This excludes both the Phase 2 MEDIUM/HIGH
  parallel scan and the Phase 4 LOW-affinity deferred scan.

After Step 3 Synthesize produces the `verdict` and `summary` for an
in-scope ensemble point, the orchestrator MUST persist a summary
entry to the workflow file's `ensemble_results` field per
`continuity-protocol.md` `ensemble_results` schema. This makes the
ensemble's contribution durable across session compaction and
`/omcc-dev:resume` rehydration. (Step 2 Collect alone does not
produce a verdict — only the raw Codex output; the synthesized
verdict comes from Step 3.)

- `ensemble_results` entries follow the list-of-maps shape with the
  composite identity `(phase, ensemble_type, run_id)`. Each entry
  records the synthesis verdict (`pass | concerns | conflict`), a
  sanitized summary (`SANITIZE_FIELD_CAPS.ensemble_summary` cap),
  the completion timestamp, and an optional `codex_session_id`.
- The remove-pending and write-result steps MUST be a single atomic
  mutation (one `atomicModifyFile` invocation that updates
  `pending_ensemble` and `ensemble_results` together). Splitting the
  mutation risks a crash window in which `pending_ensemble` is
  cleared but no `ensemble_results` row exists — the originating
  phase would then have no recoverable trace of the run on resume.
- **Supersede policy**: if a phase is re-executed (Plan Adjustment
  case 2 in `commands/start.md`, fix-and-verify retry, etc.), the
  re-run produces a new entry with the same `(phase, ensemble_type)`
  but a NEW `run_id`. Entries are never overwritten in place; the
  list grows and readers (e.g., `commands/resume.md`) display the
  latest by `completed_at` per `(phase, ensemble_type)` while
  preserving full history.
- **Sanitize / scrub / normalize policy** (writer-side, applied
  in this order before persisting):
  1. `scrubSecrets(summary)` — apply the canonical secrets-hygiene
     scrub patterns (`hooks/_utils.mjs` `scrubSecrets`) to redact
     `Authorization: Bearer …`, `api_key=…`, and similar
     credentials that Codex may have quoted from logs or code.
  2. `sanitizeField("ensemble_summary", scrubbed)` — strip control
     characters and apply the 400-char cap.
  3. **Reject LF/CR**: if the sanitized result contains LF
     (`\x0a`) or CR (`\x0d`), drop the entire entry. `sanitize()`
     intentionally preserves newlines as legitimate text, but
     `ensemble_results.summary` is a single-line field by contract
     — `/resume` Step 5c rejects multiline summaries to prevent
     prompt injection, so writers MUST NOT emit them.
  4. **Reject backticks**: `sanitize()` returns `null` on backticks
     per the canonical rule, matching the `commands/checkpoint.md`
     precedent. The entire entry is dropped with a one-line
     stderr warning.
  Codex degradation / failure cases write `verdict: conflict` with
  the failure reason in `summary` only if it survives the four
  steps above; otherwise no entry is written.
- **Timestamp policy**: a `completed_at` that fails ISO-8601 parsing
  or is in the future is treated as **absent** rather than as an
  error, per the `latest_checkpoint` precedent in
  `continuity-protocol.md`. The entry is dropped in this case.
- `codex-now` and `audit-scan` results are NOT persisted to
  `ensemble_results` — only automatic `/start` and `/fix` phase
  ensembles are. `codex-now` and `audit-scan` are still tracked in
  `pending_ensemble` for in-flight job recovery, but their synthesized
  results land in conversation (`codex-now`) or in `findings`
  (`audit-scan`).

Consumer commands and skill files MUST NOT redefine the Result
Bookkeeping rules; they cross-reference this section as the single
source of truth, in the same way they do for State Bookkeeping.

---

## Prompt Construction Rules

All Codex prompts for `task` subcommands use XML block structure.

### Required blocks for every ensemble prompt

- `<task>`: Concrete job description with repository context
- `<structured_output_contract>`: Exact output shape
- `<grounding_rules>`: Ground claims in code/evidence, label inferences

### Additional blocks by ensemble point type

- Analysis/exploration: add `<research_mode>`
- Diagnosis/investigation: add `<verification_loop>`, `<missing_context_gating>`
- Plan verification: add `<dig_deeper_nudge>`, `<completeness_contract>`
- Review/audit: add `<dig_deeper_nudge>`

### Do not pass --model or --effort

The user's config.toml is the single source of truth for model, effort, and
service tier. Passing `--model` or `--effort` flags would override the user's
global configuration.

### Prefer `--prompt-file` for materialized prompts

When the prompt is materialized in a temp file, prefer
`--prompt-file <path>` over positional argv to keep the prompt out of
`ps aux` and avoid the `ARG_MAX` ceiling. Older `codex-companion`
builds without the flag would treat it as positional argv; gate the
dispatch with `grep -q 'valueOptions.*"prompt-file"' "$companion" || exit 0`
so a miss degrades gracefully (matching the missing-codex preflight
contract).

---

## Independence Rule

Codex must analyze independently. Do not include Claude's in-progress findings,
hypotheses, draft conclusions, or intermediate results in the Codex prompt.

Both models receive the same raw context:

- Source code (via Codex's own file access)
- Git state (via Codex's own git access)
- The user's original request or task description

**Single exception**: Plan Verification ensemble. Codex receives Claude's draft plan
as explicit input, because the task is to find gaps in that specific plan.

---

## Ensemble Point Types

### Brainstorm

- **Purpose**: Independent approach generation
- **Subcommand**: `task`
- **Prompt template**:

  ```xml
  <task>
  Given this feature request, independently analyze the problem and propose
  2-3 implementation approaches with tradeoffs.
  Feature: {user's feature description}
  Repository: {repo context from task profile}
  </task>

  <structured_output_contract>
  For each approach:
  1. Name and one-sentence summary
  2. Key tradeoffs (pros and cons)
  3. Risk areas
  4. Estimated scope (files/layers affected)
  </structured_output_contract>

  <grounding_rules>
  Base approaches on the actual repository structure and patterns.
  Do not propose approaches that require frameworks or dependencies
  not present in the project.
  </grounding_rules>
  ```

- **Synthesis**: Merge option sets. If Codex proposed an approach Claude didn't consider,
  add it. If both proposed the same approach, elevate confidence.

### Explore

- **Purpose**: Independent architecture and integration analysis
- **Subcommand**: `task`
- **Prompt template**:

  ```xml
  <task>
  Analyze the codebase architecture relevant to this feature.
  Identify: integration points, existing patterns to follow,
  potential conflict areas, and reusable components.
  Feature: {feature description}
  </task>

  <structured_output_contract>
  Return:
  1. Key files and modules involved
  2. Integration points with existing code
  3. Patterns to follow (with file references)
  4. Potential conflict or risk areas
  </structured_output_contract>

  <research_mode>
  Separate observed facts from inferences.
  Prefer breadth first, then depth where it changes the recommendation.
  </research_mode>

  <grounding_rules>
  Every claim must reference a specific file or code location.
  </grounding_rules>
  ```

- **Synthesis**: Merge structural findings. Claude agents (architecture-mapper, flow-tracer)
  provide deep per-layer analysis; Codex provides a holistic cross-cutting view.
  Flag files/patterns found by only one side.

### Plan-verify

- **Purpose**: Find gaps in Claude's implementation plan
- **Subcommand**: `task`
- **Independence exception**: Receives Claude's draft plan as input
- **Prompt template**:

  ```xml
  <task>
  Review this implementation plan for gaps, missing dependencies, ordering errors,
  underestimated complexity, and edge cases that the plan does not address.

  Plan:
  {Claude's draft plan text}

  Original feature request:
  {user's feature description}
  </task>

  <structured_output_contract>
  Return:
  1. Gaps: missing tasks or considerations
  2. Ordering issues: tasks that should come earlier/later
  3. Risk areas: tasks with underestimated complexity
  4. Edge cases: scenarios the plan does not handle
  </structured_output_contract>

  <dig_deeper_nudge>
  Check for second-order dependencies, rollback paths,
  and failure scenarios before finalizing.
  </dig_deeper_nudge>

  <completeness_contract>
  Do not stop at surface-level observations. Trace each task's dependencies fully.
  </completeness_contract>

  <grounding_rules>
  Ground every gap or issue in specific plan tasks or codebase evidence.
  </grounding_rules>
  ```

- **Synthesis**: Incorporate valid gaps into the plan. If Codex found real missing tasks,
  add them. If Codex flagged ordering issues, adjust. Note any Codex concerns Claude
  disagrees with under CONFLICT.

### Review

- **Purpose**: Independent code review
- **Subcommand**: `review --wait`
- **Arguments**: `--scope branch` or `--scope working-tree` depending on command context
- **No custom prompt** — uses Codex's native review system
- **Synthesis**: Merge findings by location. Same file + same issue → deduplicate,
  take higher severity. Unique findings → label source. Conflicting severity →
  present both assessments.

### Investigate

- **Purpose**: Independent root cause diagnosis
- **Subcommand**: `task`
- **Prompt template**:

  ```xml
  <task>
  Independently diagnose the root cause of this issue.
  Do not follow any pre-existing hypotheses — start from the symptoms
  and trace through the code.
  Symptom: {bug description}
  </task>

  <structured_output_contract>
  Return:
  1. Most likely root cause with evidence
  2. Confidence level (HIGH/MEDIUM/LOW)
  3. Alternative causes considered and why rejected
  4. Suggested verification step
  </structured_output_contract>

  <verification_loop>
  Before finalizing, verify that the proposed root cause explains
  all observed symptoms.
  </verification_loop>

  <missing_context_gating>
  If critical context is missing, state exactly what remains unknown
  rather than guessing.
  </missing_context_gating>

  <grounding_rules>
  Every claim must reference specific code locations.
  Label inferences explicitly.
  </grounding_rules>
  ```

- **Synthesis**: Cross-validate. If both point to same root cause → high confidence,
  proceed. If Codex found a different cause → treat as additional hypothesis, verify
  with targeted check. If conflicting → present both with evidence, ask user.

### Fix-verify

- **Purpose**: Independent review of applied patch
- **Subcommand**: `review --wait --scope working-tree`
- **No custom prompt** — uses Codex's native review system
- **Synthesis**: Same as review type. Merge into fix verification output.

### Audit-scan

- **Purpose**: Parallel adversarial analysis during audit
- **Subcommand**: `adversarial-review --wait`
- **Arguments**: Focus text derived from audit type:
  - Security: `"authentication bypass, injection vectors, secret exposure, authorization boundary violations"`
  - Performance: `"N+1 queries, unnecessary allocation, missing indexes, blocking operations, memory leaks"`
  - Code quality: `"unnecessary complexity, dead code, inconsistent patterns, poor abstractions"`
  - Tech debt: `"TODO/FIXME accumulation, deprecated API usage, test coverage gaps, maintenance burden"`
  - Full: `"design flaws, architectural weaknesses, hidden assumptions, failure modes"`
- **Synthesis**: Merge with Claude agent findings. Deduplicate by location.
  Unify severity ratings. Source-label all findings.

### Codex-now

- **Purpose**: User-initiated ad-hoc Codex consultation on a free-form
  question while a workflow is active. Unlike the other six entries,
  this point is not bound to a phase or affinity — the trigger is the
  `/omcc-dev:codex-now <question>` invocation. See
  `commands/codex-now.md` for the orchestrating command.
- **Subcommand**: `task`
- **Independence exception**: none — the user's question is the
  prompt; Claude's in-progress findings are NOT included unless a
  future opt-in flag is added.
- **Prompt template**:

  ```xml
  <task>
  Answer the user's question independently. Do not propose code edits;
  return analysis or guidance only.

  Question:
  <![CDATA[
  {sanitized user question, verbatim}
  ]]>
  </task>

  <grounding_rules>
  Ground every claim in specific code, files, or documentation.
  Label inferences explicitly. Quote 2-3 lines from any cited source.
  </grounding_rules>

  <privacy_contract>
  The question may reference proprietary identifiers; do not echo
  back any identifier you do not need to answer.
  </privacy_contract>
  ```

  The CDATA wrapper isolates the user-controlled question from the
  XML structure for `<`, `>`, `&`, and stray closing tags. The
  three-byte sequence `]]>` would close the CDATA section
  prematurely; `commands/codex-now.md` Step 2 rejects any question
  containing that token, so the wrapper plus the rejection together
  form the injection defense.

- **Synthesis**: The four-category taxonomy applies only when Claude
  also has a reading on the question worth presenting alongside;
  otherwise present Codex's answer as a single-item CODEX-ONLY
  result with light Claude framing. Always presented in batch mode
  (presentation mode is not asked).

---

## Failure Handling

### Codex unavailable, not installed, or unauthenticated

- **Detect**: CODEX_HOME resolves to empty (plugin not installed), or
  codex-companion exits with auth error
- **Action**: If CODEX_HOME is empty, do not attempt to run codex-companion.mjs.
  Log warning, proceed with Claude-only results.
- **Present**: "Codex ensemble unavailable — results are Claude-only.
  Run `/codex:setup` to configure."

### Codex timeout or error

- **Detect**: background Bash returns error or empty output
- **Action**: Log the error, proceed with Claude-only results
- **Present**: "Codex analysis did not complete — results are Claude-only for this phase."

### Codex returns malformed or incomplete output

- **Detect**: output does not match expected structure, or is structurally valid
  but missing expected sections (e.g., only 2 of 4 required fields present)
- **Action**: Include available output in synthesis attempt. For missing sections,
  record them as "Codex: not analyzed"
- **Present**: "Codex output was partially parsed — some findings may be missing."
  List which sections were present and which were absent.

### Codex review stall on very large branch diffs

- **Detect**: `git diff <base>...HEAD | wc -l` exceeds ~1500 lines, or
  the Codex review job log
  (`~/.claude/plugins/data/codex-<marketplace>/state/.../jobs/<id>.log`)
  shows no progress for >10 minutes after launch. Empirical threshold:
  ~2400 lines across 22 files (schema-2 Branch 2 PR, observed twice)
- **Action**: do not issue a single `review --scope branch`. Slice by
  checking out each cut-point commit in turn and reviewing with
  `--base <prev> --scope branch` against the previous cut point
  (`--base` alone reviews `<base>...HEAD`, so without a checkout the
  segments overlap). Keep each slice under ~800 lines; restore HEAD
  with `git checkout <branch>` after the last slice. Cancel a stalled
  job via `/codex:cancel <job-id>` before retrying
- **Present**: "Branch diff exceeds slicing threshold — review issued
  in K segments"

### Graceful degradation principle

Ensemble failure must never block the workflow. Claude-only results are always
sufficient to proceed. Codex adds value when available but is not required.

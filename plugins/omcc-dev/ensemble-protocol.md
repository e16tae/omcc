# Ensemble Protocol

Defines how Claude and Codex operate as a dual-model ensemble.
Claude orchestrates the workflow, launches Codex for independent parallel analysis,
and synthesizes both perspectives into a unified result for the user.

The user never invokes Codex commands directly.
All Codex interactions are managed by this protocol.

---

## When This Protocol Applies

Activates when Ensemble Affinity (per `ensemble-affinity.md`) is evaluated during
a command execution. Each command file specifies which phases invoke the ensemble
and with which ensemble point type.

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
   - `task --wait` for analysis, diagnosis, brainstorm, plan verification
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
       command -v node >/dev/null 2>&1 && \
       CLAUDE_PLUGIN_ROOT="$CODEX_HOME" \
       node "${CODEX_HOME}scripts/codex-companion.mjs" \
       <subcommand> --wait [args]`,
     run_in_background: true
   })
   ```

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
- **Subcommand**: `task --wait`
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
- **Subcommand**: `task --wait`
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
- **Subcommand**: `task --wait`
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
- **Subcommand**: `task --wait`
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

### Graceful degradation principle

Ensemble failure must never block the workflow. Claude-only results are always
sufficient to proceed. Codex adds value when available but is not required.

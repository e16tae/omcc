---
description: Systematic codebase audit — parallel scanning across categories with remediation discussion
argument-hint: Audit scope (e.g., "security", "performance", "full")
---

# Audit

$ARGUMENTS

---

## Phase 1: Determine Scope

If $ARGUMENTS specifies the audit type, use it directly. Otherwise:

1. Gather minimal context (recent git log, directory structure, project config)
2. Follow the brainstorm skill's command-invoked mode (`skills/brainstorm/SKILL.md`)
   to compare audit types and recommend the most appropriate type and scope
3. If context is insufficient, default to "full". State the reasoning.

**Audit types**: security / performance / code quality / tech debt / full (all of the above)
**Target scope**: entire codebase / specific directory or module

Build the Task Profile (`orchestration.md` Step 1), including Ensemble Affinity.

---

## Phase 2: Parallel Scan

Follow `orchestration.md`, targeting Review Agents based on audit type.

### Agent selection rules for audits

**Full audit**: Always include the baseline set: **security, performance, simplicity, conventions, debt**.
These cannot be excluded — "full" guarantees complete coverage of these categories.
Then use orchestration to determine if additional specialist perspectives
(correctness, concurrency, api-design, error-resilience, migration-safety) are warranted based on the codebase's characteristics.

**Specific type**: Decompose the chosen type into distinct sub-aspects and assign one agent per sub-aspect.
Example: "security" audit → separate missions for auth/authz, input validation, secrets management.

Launch all selected agents in parallel (single message, multiple Agent calls).

If ensemble active (Affinity MEDIUM or HIGH):
- Simultaneously launch Codex **audit-scan** ensemble point (background) per `ensemble-protocol.md`
- Focus text is derived from the audit type per `ensemble-protocol.md` audit-scan definition

---

## Phase 3: Integrate Built-in Results

If the audit includes security:
- Phrase the suggestion so it degrades gracefully if the command is absent:
  "If `/security-review` is available in your Claude Code setup, it provides
  git-diff-based security analysis as a complement to this audit."
  (`/security-review` is a native Claude Code feature, not an omcc-dev command.)
- Integrate those results if the user provides them

---

## Phase 4: Present Findings

Collect Codex audit-scan result from Phase 2 background task (if ensemble was launched).

If ensemble active (Affinity MEDIUM or HIGH — launched in Phase 2):
- Synthesize Claude agent findings + Codex adversarial-review findings per `ensemble-protocol.md`
- Deduplicate by location
- Unify severity ratings (elevate confidence when both sides agree)
- Source-label all findings (Claude / Codex / Both)

If ensemble not active (LOW affinity):
- Launch Codex **audit-scan** ensemble point now (review-phase ensemble for LOW affinity)
- Collect and synthesize into findings

Follow the Presentation Mode Protocol (`presentation-protocol.md`) before presenting.

Present findings directly in conversation, organized by severity (Critical → High → Medium → Low),
followed by positive observations. Do not generate a separate report file.

---

## Phase 5: Remediation Discussion

Walk through each actionable finding from Phase 4 for detailed analysis and direction decision.

If all findings are positive observations with no actionable items, skip this phase
and conclude the audit.

Use the presentation mode already chosen for this audit invocation
(per `presentation-protocol.md` timing rule — do not re-ask).

### Per-finding analysis

For each finding, provide:

1. **Situation**: Explain the finding with concrete code references (file paths,
   function names, data flows) sufficient for independent verification. Cover what
   it means, why it occurs, and how far the impact reaches.

2. **Scenarios**: Describe what happens under each viable remediation approach,
   including a "do nothing" baseline. Focus on concrete consequences — specific
   failure modes, degradation paths, or maintenance costs — not abstract risk levels.

3. **Decision**: The user chooses one of:
   - **Fix now** — address in a subsequent `/fix` or `/start` workflow
   - **Defer** — direction is known but timing is not; record with a trigger condition
   - **Accept risk** — acknowledge and document the rationale for acceptance
   - **Investigate further** — direction itself is unknown; transition to `/omcc-dev:investigate`

When a finding reveals 2+ meaningfully different remediation paths, the
Protocol Interaction Rule (`presentation-protocol.md`) triggers the brainstorm skill
inline — approach comparison, recommendation, and user choice are handled by that
existing pipeline. Do not duplicate brainstorm output within this phase.

### After all findings reviewed

Synthesize the decisions made during the discussion:

- Summary table: finding × decision (fix now / defer / accept / investigate)
- Count by decision type
- If any findings are marked "fix now": list them and offer to transition
  to the appropriate workflow (`/fix` for defects, `/start` for enhancements)
- If any findings are marked "investigate further": list them and offer to
  transition to `/omcc-dev:investigate`

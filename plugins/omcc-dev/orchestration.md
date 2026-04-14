# Dynamic Agent Orchestration

Follow this framework at every stage that allocates agents.
Pursue the best results through task-analysis-based dynamic composition, not static counts.

---

## Principles

1. **Quality first**: Optimize for result quality, not token efficiency
2. **Opus + Max reasoning**: All agents operate on the opus model
3. **Task decides**: No predefined minimum/maximum agent count. If the task requires 1, use 1; if it requires 7, use 7
4. **Mission-specific**: Assign concrete missions tailored to this task, not generic perspective labels
5. **No overlap**: Clearly delineate mission boundaries so multiple perspectives do not review the same area

---

## Orchestration Process

Before allocating agents, always perform these 3 steps.

### Step 1: Task Profiling

Analyze the task along the following dimensions and record the result in this format:

```
Task Profile:
  Scope: [file count], [estimated LOC]
  Layers: [list applicable layers]
  Risks: [list applicable risk areas, or "none"]
  Complexity: [low / medium / high]
  Ensemble Affinity: [LOW / MEDIUM / HIGH] — per ensemble-affinity.md
```

**Analysis dimensions:**

- **Scope**: Number of files changed/targeted, LOC, related directories and modules
- **Layers**: UI / API / business logic / data / infrastructure / configuration
- **Risk areas**: Security (auth, crypto, secrets) / Data (schema, migration) / Public interfaces (API, SDK) / Concurrency (shared resources, async) / Failure (external dependencies, partial failure)
- **Domain complexity**: Level of domain knowledge and business rule complexity this change requires
- **Ensemble Affinity**: Evaluate per `ensemble-affinity.md` criteria. Records whether Codex runs in parallel with Claude agents during this workflow

### Step 2: Agent Composition

Select roles from `agent-taxonomy.md`.

**Selection criteria — ask yourself for each role:**

> "If this perspective is missing, could this task have a **real defect** that goes undetected?"

- YES → include
- NO → exclude

> "Can this perspective provide meaningful feedback that **does not overlap** with other selected perspectives?"

- YES → include
- NO → exclude (not applicable or absorbed by another perspective)

**Overlap resolution:**
When two roles overlap in scope (e.g., correctness and concurrency both examining shared state access):
- If you can write non-overlapping specific missions for each → include both, separate via mission boundaries
- If separating missions still results in reviewing the same thing → merge into the broader role

**Guidelines:**
- Do not over-allocate for simple changes. A README typo fix does not need a security reviewer
- Do not omit perspectives for complex changes. An auth refactoring must include security
- Judge by **actual risk**, not surface-level characteristics. A config file change can affect security

### Step 3: Mission Briefing

Give each selected agent a **concrete mission specific to this task**.

**Bad mission:**
> "Review from a correctness perspective"

**Good mission:**
> "Verify session state transition correctness in this auth middleware refactoring.
> Focus on behavior during concurrent requests while tokens are being refreshed,
> and check how error paths change now that the extractToken function has been removed."

**Mission writing rules:**
1. Include the specific context of this task
2. Specify particular files/functions/areas to focus on
3. Concretize the key question from `agent-taxonomy.md` for this task
4. Explicitly state boundaries to avoid overlap with other agents' missions

**Ensemble parallel track:**

When Ensemble Affinity is MEDIUM or HIGH, the orchestrating command launches a Codex
ensemble point in parallel with the selected agents. The ensemble point type and synthesis
are defined by the invoking command per `ensemble-protocol.md`.

Codex runs as an independent parallel track — it is not an "agent" in the agent taxonomy.
Do not include Codex in the agent count or mission briefing. It receives its own prompt
via `ensemble-protocol.md`.

### Agent failure handling

If any agent fails to return (timeout, error, or empty result):
1. Notify the user which agent (perspective) failed
2. Ask: retry, or proceed with available results?
3. Follow the user's decision
4. If proceeding without retry, note the missing perspective in the synthesis
   output so the user knows coverage was incomplete

---

## Examples

### Example 1: Exploration — understanding codebase before multi-layer feature (Analysis)

```
Task Profile:
  Scope: New feature spans 3 layers (API + business logic + data)
  Layers: API, business logic, data
  Risks: Need to identify integration points with existing code
  Complexity: medium
  Ensemble Affinity: MEDIUM — multi-layer, medium complexity

Agent Composition:
  architecture-mapper x 1 — "Map the connection structure between API and data layers, existing endpoint patterns"
  flow-tracer x 1         — "Trace the request flow of the most similar existing feature to understand integration patterns"
  dependency-analyzer x 1 — "Analyze the dependency graph and impact radius of modules the new feature will touch"
Ensemble: MEDIUM — Codex explore launched in parallel per ensemble-protocol.md
```

### Example 2: Investigation — intermittent 500 errors after deployment (Investigation)

```
Task Profile:
  Scope: Error logs appearing in 2 services
  Layers: API + data
  Risks: Concurrency (connection pool), failure (external service timeout)
  Complexity: high (intermittent — hard to reproduce)
  Ensemble Affinity: HIGH — concurrency risk, high complexity, intermittent

Agent Composition:
  hypothesis-tracer x 1  — "DB connection pool exhaustion hypothesis: trace leak points in connection acquire/release paths"
  regression-hunter x 1  — "Search recent deployment diffs for connection management or timeout configuration changes"
  state-analyzer x 1     — "Analyze state transitions during request processing, especially resource cleanup in error paths"
Ensemble: HIGH — Codex investigate launched in parallel per ensemble-protocol.md
```

### Example 3: Review — simple config edit (Review, 1 file, non-logic)

```
Task Profile:
  Scope: 1 file, 5 LOC
  Layers: configuration
  Risks: none
  Complexity: low
  Ensemble Affinity: LOW — simple config change

Agent Composition:
  conventions x 1 — "Verify config file format and key naming matches existing patterns"
Ensemble: LOW — Codex review at review phase only per ensemble-protocol.md
```

### Example 4: Review — auth middleware refactoring (3 files, security-related)

```
Task Profile:
  Scope: 3 files, 150 LOC
  Layers: API + business logic
  Risks: Security (auth, sessions), public interface (middleware contract)
  Complexity: medium
  Ensemble Affinity: HIGH — security risk

Agent Composition:
  correctness x 1 — "Session state transition correctness, edge cases in token refresh logic"
  security x 1    — "Token handling, CSRF defense, session fixation attack vectors"
  api-design x 1  — "Middleware interface backward compatibility, consumer code impact"
  conventions x 1 — "Whether middleware patterns are consistent with existing project middleware"
  concurrency x 1 — "Session state race conditions under concurrent requests"
Ensemble: HIGH — Codex review launched in parallel per ensemble-protocol.md
```

### Example 5: Review — DB schema migration + API change (8 files, multi-layer)

```
Task Profile:
  Scope: 8 files, 300 LOC
  Layers: API + data + business logic
  Risks: Data (schema change), public interface (API), failure (migration failure)
  Complexity: high
  Ensemble Affinity: HIGH — high complexity, 3 layers, data migration risk

Agent Composition:
  correctness x 1        — "Migration SQL logic correctness, API handler mapping to new schema"
  migration-safety x 1   — "Rollback feasibility, existing data preservation, migration ordering"
  performance x 1        — "New index efficiency, lock impact during migration, query plan changes"
  api-design x 1         — "Response schema backward compatibility, versioning strategy, client impact"
  error-resilience x 1   — "Recovery path on migration failure, partial-apply state handling"
Ensemble: HIGH — Codex review launched in parallel per ensemble-protocol.md
```

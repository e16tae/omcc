---
name: explore
description: Explores a codebase from multiple perspectives to build a structured understanding. Make sure to use this skill whenever the user mentions codebase understanding, project structure, architecture mapping, code orientation, onboarding, or asks how a project works — even if they don't explicitly request "exploration". Trigger phrases include "explain this codebase", "how is this structured", "map the architecture", "help me understand this code", "project structure", "codebase overview".
---

# Codebase Exploration

Explore the codebase systematically from multiple perspectives to build a comprehensive understanding.

## When auto-activated (without /start command)

Provide a structured exploration following these guidelines. Since this is auto-activated (not a full command), work within the current context without spawning separate agents.

### Step 1: Survey the landscape

1. Use Glob to identify the directory structure and key file patterns
2. Read the project's CLAUDE.md, README, and config files (package.json, pyproject.toml, etc.)
3. Identify the primary language, framework, and architecture style

### Step 2: Map from three perspectives

Explore the codebase addressing these three concerns:

**Architecture**: What are the layers? What are the entry points? What are the key abstractions?

**Flow**: Pick the most representative operation and trace it end-to-end. Where does data enter, how is it transformed, where is it stored?

**Conventions**: What naming patterns are used? How are errors handled? What testing approach is used? What style/formatting conventions are followed?

### Step 3: Synthesize

Follow the Presentation Mode Protocol (`presentation-protocol.md`) before presenting.

Present a structured summary covering:
- Architecture overview (2-3 sentences)
- Key files to read first (5-10 paths with why each matters)
- Main data/request flow
- Project conventions
- Notable observations (tech debt, unusual patterns, strengths)

If the user requests, generate an architecture document with Write or save key insights to Memory.

---

## When invoked by command (/start)

Full exploration with agent spawning and ensemble coordination.

### Step 1: Spawn analysis agents

Follow `orchestration.md`, targeting Analysis Agents for the feature's scope and layers.
Launch all selected agents in parallel (single message, multiple Agent calls).

### Step 2: Ensemble coordination (if Affinity MEDIUM or HIGH)

Simultaneously with agent dispatch:
- Launch Codex **explore** ensemble point (background) per `ensemble-protocol.md`

### Step 3: Synthesize

After agents return:
1. If ensemble was launched:
   - Collect Codex explore result
   - Merge Claude agent findings + Codex findings, label unique discoveries by source
2. Read the key files identified by agents
3. Summarize: existing patterns, reusable components, integration points

### Step 4: Present

Follow the Presentation Mode Protocol (`presentation-protocol.md`) before presenting.
Present unified findings to user.

### State write (when invoked by /start)

After synthesis, write the architecture findings to the active workflow
file per `continuity-protocol.md` Phase-boundary Write Rules (fields:
`architecture.patterns`, `architecture.integration_points`,
`architecture.pitfalls`).

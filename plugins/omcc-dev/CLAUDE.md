# omcc-dev Methodology Rules

These rules adjust Claude's default behavior while the omcc-dev plugin is active.
They apply alongside commands (/fix, /start, /audit) and during general conversation.

---

## Agent Orchestration

All stages that spawn agents must follow the Dynamic Agent Orchestration process in `orchestration.md`.
Available agent roles are defined in `agent-taxonomy.md`.
Pursue the best results through task-analysis-based dynamic composition, not static counts.
Inline skills that do not spawn agents (explore, plan, etc.) may also reference the taxonomy for perspective selection.

---

## Available Commands

- `/omcc-dev:fix [bug description]` — Systematic bug fix (multi-hypothesis parallel investigation)
- `/omcc-dev:start [feature description]` — Feature development (brainstorm > explore > plan > build > review)
- `/omcc-dev:audit [scope]` — Code audit (security/performance/quality/debt parallel scan)
- `/omcc-dev:brainstorm` — Evidence-based design decision evaluation
- `/omcc-dev:explore` — Codebase structure exploration
- `/omcc-dev:investigate` — Root cause investigation
- `/omcc-dev:parallel-review` — Multi-perspective code review
- `/omcc-dev:plan` — Work planning

`/fix`, `/start`, and `/audit` support automatic Codex ensemble (see Ensemble Rules).

---

## Brainstorming Rules

Before any new feature or design decision, always follow the brainstorm skill
(`skills/brainstorm/SKILL.md`). This applies both when auto-activated and when
invoked as part of a command.

Do not start implementation until the user confirms a direction.

Reason: Claude's default behavior is to code immediately without research. The brainstorm
skill forces evidence gathering, structured five-perspective comparison, and an explicit
recommendation so the user can make informed decisions even in unfamiliar domains.

---

## Presentation Mode Rules

Before presenting multiple review items, findings, or decisions to the user, always follow
the Presentation Mode Protocol (`presentation-protocol.md`): offer a choice between batch
(all at once) and interview (one by one) presentation.

Reason: Users process structured information differently depending on context. A quick config
review may warrant batch output, while a complex design comparison benefits from item-by-item
discussion. Offering the choice costs one line of interaction but significantly improves the
user's ability to engage with the content.

---

## TDD Rules

Follow the RED-GREEN-REFACTOR cycle for feature implementation:
1. RED: Write a failing test first and confirm failure with Bash
2. GREEN: Minimal implementation to pass the test
3. REFACTOR: Clean up while keeping tests green

Skip this rule in projects without a test framework, but inform the user.

---

## Completion Verification Rules

When finishing a code transformation or bug fix:
1. Run the full test suite (if available)
2. For transformations: Grep for the old pattern to confirm 0 remaining occurrences
3. For bugs: Grep for the same pattern in other locations to check for similar issues

---

## Ensemble Rules

All commands that spawn agents must evaluate Ensemble Affinity (per `ensemble-affinity.md`)
as part of the Task Profile.

When Ensemble Affinity is MEDIUM or HIGH:
- Launch Codex ensemble points automatically at designated phases
- Follow `ensemble-protocol.md` for execution and synthesis
- Never ask the user whether to invoke Codex — it is automatic
- Never tell the user to run `/codex:*` commands manually

When Ensemble Affinity is LOW:
- Launch Codex ensemble at review phases only
- Same protocol applies

Model and effort are never specified in ensemble calls.
The user's config.toml is authoritative.

Codex failure never blocks the workflow. Degrade gracefully to Claude-only results
with a notification.

Reason: The user's dual-model workflow treats Claude and Codex as an ensemble.
Codex is not a secondary tool to be manually invoked — it is a parallel analysis
track that runs automatically when the workflow benefits from independent verification.

---

## Language Convention

All documentation in this project uses English. This includes `CLAUDE.md`, `orchestration.md`,
`agent-taxonomy.md`, `presentation-protocol.md`, `ensemble-protocol.md`,
`ensemble-affinity.md`, commands, skills, agents, and tests.

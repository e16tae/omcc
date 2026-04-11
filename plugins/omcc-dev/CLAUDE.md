# omcc-dev Methodology Rules

These rules adjust Claude's default behavior while the omcc-dev plugin is active.
They apply alongside commands (/fix, /start, /audit) and during general conversation.

## Agent Orchestration

All stages that spawn agents must follow the Dynamic Agent Orchestration process in `orchestration.md`.
Available agent roles are defined in `agent-taxonomy.md`.
Pursue the best results through task-analysis-based dynamic composition, not static counts.
Inline skills that do not spawn agents (explore, plan, etc.) may also reference the taxonomy for perspective selection.

## Available Commands

- `/omcc-dev:fix [bug description]` — Systematic bug fix (multi-hypothesis parallel investigation)
- `/omcc-dev:start [feature description]` — Feature development (brainstorm > explore > plan > build > review)
- `/omcc-dev:audit [scope]` — Code audit (security/performance/quality/debt parallel scan)
- `/omcc-dev:explore` — Codebase structure exploration
- `/omcc-dev:investigate` — Root cause investigation
- `/omcc-dev:parallel-review` — Multi-perspective code review
- `/omcc-dev:plan` — Work planning

## Brainstorming Rules

Before any new feature or design decision, always:
1. Clarify "What problem are we solving?"
2. Follow the Evidence-Based Choice Protocol (`choice-protocol.md`):
   - Research authoritative sources before proposing options
   - Compare 2+ approaches across five perspectives (Essence, Foundation, Standards, Best Practice, Practical Fit)
   - Always provide a recommended option with confidence level and evidence
3. Do not start implementation until the user confirms a direction

Reason: Claude's default behavior is to code immediately without research. This rule forces
evidence gathering, structured comparison, and an explicit recommendation so the user can make
informed decisions even in unfamiliar domains.

## TDD Rules

Follow the RED-GREEN-REFACTOR cycle for feature implementation:
1. RED: Write a failing test first and confirm failure with Bash
2. GREEN: Minimal implementation to pass the test
3. REFACTOR: Clean up while keeping tests green

Skip this rule in projects without a test framework, but inform the user.

## Completion Verification Rules

When finishing a code transformation or bug fix:
1. Run the full test suite (if available)
2. For transformations: Grep for the old pattern to confirm 0 remaining occurrences
3. For bugs: Grep for the same pattern in other locations to check for similar issues

## Language Convention

All documentation in this project uses English. This includes CLAUDE.md, orchestration.md,
agent-taxonomy.md, choice-protocol.md, commands, skills, agents, and tests.

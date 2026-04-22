# omcc-dev — Contributor Notes

Notes for maintainers editing the omcc-dev plugin inside this repo.
End-user behavior lives in canonical components: `commands/`, `skills/`,
`agents/`, and the plugin-level framework docs at the plugin root.

---

## Plugin layout

- `commands/` — thin orchestrators (`start`, `fix`, `audit`, `resume`)
- `skills/` — reusable skill bodies (`brainstorm`, `explore`, `investigate`, `parallel-review`, `plan`)
- `agents/` — subagent definitions (`architecture-mapper`, `flow-tracer`, `hypothesis-tracer`, `reviewer`)
- `hooks/` — plugin-level hook scripts registered via `hooks/hooks.json`
  (`session-start.mjs` with compact matcher, `pre-compact.mjs`,
  `stop.mjs`, and shared `_utils.mjs`). Event handlers for the
  continuity protocol; see `continuity-protocol.md` §Hook Responsibilities.
- Plugin-level framework docs at the plugin root (infrastructure, not per-skill):
  - `orchestration.md` — dynamic agent orchestration framework
  - `agent-taxonomy.md` — catalog of primary agents + orchestration patterns
  - `ensemble-affinity.md` — scope-evaluation rules for Codex ensemble
  - `ensemble-protocol.md` — Claude+Codex dual-model execution contract
  - `presentation-protocol.md` — batch vs interview presentation pattern
  - `continuity-protocol.md` — cross-session workflow state and hook responsibilities

These framework docs live at plugin root because they are plugin-level
infrastructure applied by every skill, not per-skill supporting files. They
are referenced via backtick paths from commands, skills, and other framework
docs.

---

## Optional Codex integration

The ensemble machinery in `ensemble-protocol.md` shells out to the `codex`
plugin's `codex-companion.mjs`. When the `codex` plugin is not installed,
`ensemble-protocol.md` "Failure Handling" degrades gracefully — Claude-only
results are always sufficient. Users who want the dual-model ensemble can
install `codex` from the same marketplace; the dependency is optional, not
required.

---

## Language convention

All documentation in this plugin uses English: CLAUDE.md, commands, skills,
agents, and framework docs.

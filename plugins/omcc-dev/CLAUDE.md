# omcc-dev — Contributor Notes

Notes for maintainers editing the omcc-dev plugin inside this repo.
End-user behavior lives in canonical components: `commands/`, `skills/`,
`agents/`, and the plugin-level framework docs at the plugin root.

---

## Plugin layout

- `commands/` — thin orchestrators (`start`, `fix`, `audit`, `resume`, `checkpoint`)
- `skills/` — reusable skill bodies (`brainstorm`, `explore`, `investigate`, `parallel-review`, `plan`)
- `agents/` — subagent definitions (`architecture-mapper`, `flow-tracer`,
  `hypothesis-tracer`, `reviewer`). Primary agents pin `model: opus` and
  `effort: max` in frontmatter — see `orchestration.md` Principle 2.
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

---

## Schema version

Current state schema: **2** (bumped from 1 in this release). See
`continuity-protocol.md` §Schema 1 → 2 Migration for the one-way
upgrade path that `/omcc-dev:resume` offers when it encounters a
legacy schema-1 file. Key schema-2 features:

- **Hierarchical workflow shards**: `/start` deliverable mode sharp:s
  the root state into `workflows/<root>/<deliverable-A>.md` etc so
  re-contextualization cost is per-deliverable instead of per-root.
- **Operational `children:`**: the active-registry field is actually
  maintained now (append on child bootstrap, remove on child
  archive); Stop-hook A4 walks the transitive closure.
- **Generalized `parent_workflow`**: any workflow type may be a
  parent, not only `/audit`. Writeback dispatches on parent type —
  audit keeps `findings[]`, non-audit uses a new `child_completions[]`.
- **`/omcc-dev:checkpoint`**: user-initiated intra-session context
  milestone; SessionStart injects the digest on re-entry, PreCompact
  skips its mechanical snapshot for 60s after a fresh checkpoint.

Schema drift is guarded by `tests/test_schema_drift.py` — any
spec-vs-code divergence (SUPPORTED_SCHEMA_VERSION, TERMINAL_PHASES,
WORKFLOW_ID_REGEX, SHARD_ID_REGEX, SANITIZE_FIELD_CAPS, Backtick rule
wording) fails CI.

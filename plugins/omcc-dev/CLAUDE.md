# omcc-dev — Contributor Notes

Notes for maintainers editing the omcc-dev plugin inside this repo.
End-user behavior lives in canonical components: `commands/`, `skills/`,
`agents/`, and the plugin-level framework docs at the plugin root.

---

## Plugin layout

- `commands/` — thin orchestrators (`start`, `fix`, `audit`, `resume`, `checkpoint`, `codex-now`)
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

### When to reach for `/omcc-dev:codex-now` vs the automatic ensemble

The automatic ensemble fires at command-defined phase boundaries based on
`ensemble-affinity.md`'s scope/risk evaluation — it is opinionated about
*when* Codex adds value. `/omcc-dev:codex-now <question>` is the
discretionary user-initiated counterpart: an escape hatch when a workflow
is mid-flight and the user wants Codex's perspective on a specific question
that does not match a phase point ("does this plan handle X?", "is there
a known pitfall in Y?"). The question is the prompt itself; Claude's
in-progress findings are not transmitted. Reach for `/codex-now` when you
have a concrete question the automatic dispatch will not answer; trust the
automatic ensemble for everything inside the seven phase-bound types.

---

## Artifact intake (producer-agnostic; canonical spec in `commands/start.md`)

`/omcc-dev:start` accepts an artifact handoff when `$ARGUMENTS` is the
path to any file matching a recognized whitelist entry. The detection
is producer-agnostic — any tool that emits a file at the recognized
path with the expected structural marker can hand off, not just
sibling omcc plugins. omcc-designer's frontend skill (which produces
`DESIGN.md`) and omcc-research (which produces *research_brief.md*) are
the current example producers within this marketplace. Detection
happens in
`commands/start.md` Phase 0 Step 3a; on detection, Step 4 emits a
`## Source Artifact` subsection in the workflow file's Markdown body
(no frontmatter changes — `original_request` remains the single-line
scrubbed `$ARGUMENTS`, preserving compatibility with the YAML scalar
parser in `hooks/_utils.mjs`).

Whitelist policy (contributor-facing):

- The recognized basenames are listed canonically in
  `commands/start.md` Step 3b. New artifact kinds MUST be added there
  (not here in CLAUDE.md). The structural marker is **per artifact**,
  chosen to keep detection i18n-safe for whatever language the
  artifact body uses:
    - `DESIGN.md` → first non-empty line is exactly `---` (YAML
      frontmatter block, mandated by the Google design.md spec).
    - *research_brief.md* → first non-empty line begins with `# `
      (any markdown h1; the literal text `Research Brief` may appear
      in any user language and is not relied on).
- Cross-plugin reference rule applies: only the four external-standard
  filenames (`DESIGN.md`, `README.md`, `AGENTS.md`, `CLAUDE.md`) may
  be cited inside backticks per the `tests/test_plugin_structure.py`
  reference-existence test. Other artifact basenames such as
  *research_brief.md* must be rendered as italic prose to avoid the
  test rejecting the cross-plugin file path.
- Detection is read-only — no parsing of YAML body or h1 trailing
  text, no validation beyond "expected first-line marker present".
  Malformed artifacts (and unreadable / nonexistent paths under a
  whitelisted basename) are warned about and treated as raw input
  rather than rejected outright.

This intake is the receiving half of the cross-plugin handoff
suggestion convention emitted by omcc-designer and omcc-research
completion footers; see those plugins' contributor notes for the
emitting half.

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
WORKFLOW_ID_REGEX, SHARD_ID_REGEX, SANITIZE_FIELD_CAPS (including
`codex_session_id`), MAX_ENSEMBLE_RESULTS_PER_WORKFLOW, Backtick rule
wording, SessionStart `ensemble=` suffix shape, sharded SessionStart
reader rule) fails CI.

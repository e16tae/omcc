# omcc-research — Contributor Notes

Notes for maintainers editing the omcc-research plugin inside this repo.
End-user behavior lives in canonical components: `commands/`, `skills/`,
and `skills/<name>/references/` for progressive disclosure.

---

## Plugin layout

- `commands/` — thin orchestrators
  - `commands/research.md` — `/omcc-research:research <topic>` entry point
- `skills/` — capability logic
  - `skills/research/SKILL.md` — research skill body (auto-activated + command-invoked dual mode)
  - `skills/research/references/research-brief-spec.md` — canonical structure of the
    research brief artifact, plus citation conventions and audit checklist
  - `skills/research/references/output-file-rules.md` — directory naming, slug
    sanitization, fixed filename, overwrite rules, language policy
- `research-ensemble-protocol.md` (plugin root) — research-domain
  Codex ensemble protocol (research-scan ensemble point). Activated
  by the research skill's command-invoked mode; auto-activated mode
  does not dispatch.

The plugin remains lighter than omcc-dev (no `agents/`, no `hooks/`).
Versus the original v1 single-skill single-command layout, v2 adds
one plugin-root framework doc (`research-ensemble-protocol.md`) to
hold the Codex ensemble contract — owning the contract locally is
required because cross-plugin backtick references in markdown are
rejected by `tests/test_plugin_structure.py`, and per the repo's
"Independence over uniformity" principle.

---

## Optional Codex integration

The Codex research-scan ensemble shells out to the codex plugin's
`codex-companion.mjs`. When the codex plugin is not installed, the
preflight in `research-ensemble-protocol.md` "Failure Handling"
degrades gracefully — Claude-only research is always sufficient.
Users who want the dual-model ensemble can install codex from the
same marketplace; the dependency is optional, not required.

---

## Sanctioned cross-plugin handoffs (informational suggestions only)

This plugin emits passive handoff suggestions in selected completion
messages. The pattern is informational — no automatic invocation
crosses plugin boundaries — and follows three rules:

1. **Forward-only**: the source plugin emits the suggestion; the
   target plugin does not need to know it exists. The recipient's
   own intake (e.g., omcc-dev's `/start` artifact intake at its
   commands/start.md Phase 0 Step 3a — see omcc-dev's CLAUDE.md
   "Artifact intake" section) is what actually consumes the handoff.
2. **Conditional wording**: phrase as "If `/<target>:<command>` is
   installed and …, run …" rather than detecting installation. There
   is no reliable command-availability detection in this marketplace
   (cache glob is probabilistic; same marketplace ≠ both installed
   per the `/plugin install codex@omcc` shape in the repo README).
3. **Prose-only cross-plugin references**: the
   `tests/test_plugin_structure.py` reference-existence test
   matches backticked `*.md` paths against the local plugin directory,
   so cross-plugin file references must be unquoted prose or italic
   — only the four external-standard filenames `DESIGN.md`,
   `README.md`, `AGENTS.md`, `CLAUDE.md` are exempt and may appear
   inside backticks. The artifact this plugin produces, *research_brief.md*,
   is NOT exempt; cite it as italic prose in any cross-plugin context.

This pattern is **opt-in per plugin** — new plugins added to the
marketplace are not required to emit handoff footers. Each plugin
decides independently whether and where to suggest a sibling.

Currently registered handoff edges from this plugin:

- `commands/research.md` "## Completion" saved branch →
  `/omcc-dev:start <path-to-the-saved-brief>`. After
  *research_brief.md* is saved, the completion footer suggests
  `/omcc-dev:start` for implementation. omcc-dev's `/start` recognizes
  the brief filename + YAML frontmatter as an artifact handoff and
  ingests it as initial workflow context. The footer is added ONLY
  to the saved branch — abort branches explicitly have no path and
  must not advertise a handoff that has nothing to hand off.

This is the research-side half of a marketplace-level convention; the
omcc-designer plugin emits an analogous footer for `DESIGN.md`
handoffs, and the omcc-dev plugin documents the receiving intake in
its own CLAUDE.md.

---

## Boundary with omcc-dev:brainstorm

omcc-dev's brainstorm skill (plugins/omcc-dev/skills/brainstorm/SKILL.md)
already does external research as part of its decision-support flow
(Step 2: Research), and both skills now invoke a Codex ensemble in
command-invoked mode. The boundary that prevents feature overlap with
the marketplace addition rule (repo CLAUDE.md "Plugin Addition
Procedure" #4):

| Aspect | omcc-dev:brainstorm Step 2 | omcc-research |
|---|---|---|
| Activation | Inside a decision flow | Explicit `/omcc-research:research <topic>` |
| Required output | Comparison + recommendation | Cited brief, no recommendation |
| Persistence | Ephemeral — only the *decision* is saved to workflow state | Durable artifact (research_brief.md on disk) |
| Ensemble point type | brainstorm (option-generation prompt template) | research-scan (cited-evidence prompt template) |

When in doubt: if the user is **choosing between options**, brainstorm.
If the user is **gathering evidence about a topic**, omcc-research.
The shared ensemble surface does not blur this boundary — each
skill's ensemble point uses a distinct prompt template and
synthesizes into its own artifact contract.

---

## Language convention

All documentation in this plugin uses English. Trigger phrases in
SKILL.md `description` include Korean tokens for Korean-language
auto-activation; this is a "Independence over uniformity" deviation
(repo CLAUDE.md) since runtime discovery requires the user's own language.

The plugin processes research requests in any language and writes the
research brief in the user's interaction language.

---

## Schema and version

`plugin.json:version` is bumped automatically by release-please via
the `extra-files` entry in `release-please-config.json`. Do not bump
manually. tests/test_plugins.py enforces version sync with pyproject.toml.

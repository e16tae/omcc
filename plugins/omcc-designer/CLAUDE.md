# omcc-designer — Contributor Notes

Notes for maintainers editing the omcc-designer plugin inside this repo.
End-user behavior lives in canonical components: `commands/`, `skills/`,
and shared references.

---

## Plugin layout

- `commands/` — thin orchestrators (start, formalize, plan, poster, social-graphics, audit)
- `skills/` — per-phase or per-capability logic with progressive disclosure via `references/`
  - `design-analysis` (Phase 1 standard pipeline)
  - `design-extraction` (Phase 1 formalize pipeline)
  - `design-interview` (Phase 2 — the interview skill, also owns cross-skill protocols)
  - `brief-generation` (Phase 3 — owns the brief spec and output file rules)
  - `design-planning` (plan command, produces roadmap)
  - `design-evaluation` (audit command, produces findings + remediation)
  - `poster` (Phase 4 / poster command, produces poster spec)
  - `poster-render` (Phase 4 chain-tail / poster command, renders raw zone images via codex)
  - `social-graphics` (Phase 4 / social-graphics command, produces multi-variant social graphics spec)
  - `social-graphics-render` (Phase 4 chain-tail / social-graphics command, renders per-variant raw zone images via codex)

## Cross-skill shared references

Owner skills provide references consumed by other skills via explicit path.

- `skills/design-interview/references/interview-protocol.md` — interview rules (used by design-interview and design-planning)
- `skills/design-interview/references/confirmed-decision-principle.md` — estimation-vs-decision semantics (used across the plugin)
- `skills/brief-generation/references/design-brief-spec.md` — brief format spec (produced by brief-generation, validated by poster, social-graphics, and other domain skills)
- `skills/brief-generation/references/output-file-rules.md` — shared output directory/filename conventions
- `skills/poster-render/references/codex-call-template.md` — canonical codex-companion invocation contract for chain-tail render skills (consumed by `poster-render` and `social-graphics-render`; the file lives at `poster-render/references/` for historical reasons but is shared, not poster-render-only)

## Cross-plugin sanctioned dependencies

Built-in plugins follow the "Independence over uniformity" principle
(see repo-root CLAUDE.md). Cross-plugin coupling is generally avoided.
The exceptions below are explicit, documented dependencies.

- **Chain-tail render skills → `codex` plugin** (canonical source:
  `omcc` marketplace; detection is marketplace-agnostic). The
  chain-tail render skills (`poster-render` as a tail to `poster`,
  `social-graphics-render` as a tail to `social-graphics`, and any
  future render chains added under the same convention) invoke the
  codex plugin's `codex-companion.mjs` to render image zones. The
  dependency is optional at runtime — if the codex plugin is not
  installed, each render skill emits a one-line notice and exits
  clean (the upstream spec doc remains the user-facing artifact).
  Detection uses the marketplace-agnostic glob
  `~/.claude/plugins/cache/*/codex/*/scripts/codex-companion.mjs`,
  so any marketplace fork installing the codex plugin is supported —
  the `omcc` prefix in colloquial references like "omcc/codex" is
  documentary (canonical source), not a detection key. The shared
  codex invocation contract lives at
  `skills/poster-render/references/codex-call-template.md` (also
  see "Cross-skill shared references" above). See each chain-tail
  skill's SKILL.md "Optional dependency: codex plugin" section
  for the detection contract — currently
  `skills/poster-render/SKILL.md` and
  `skills/social-graphics-render/SKILL.md`.

---

## Language convention

All documentation in this plugin uses English: CLAUDE.md, commands, skills,
and references.

The plugin processes design requests in any language and generates output
documents in the user's language. The documentation language and the output
language are separate concerns.

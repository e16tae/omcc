# omcc-designer — Contributor Notes

Notes for maintainers editing the omcc-designer plugin inside this repo.
End-user behavior lives in canonical components: `commands/`, `skills/`,
and shared references.

---

## Plugin layout

- `commands/` — thin orchestrators (start, formalize, plan, poster, audit)
- `skills/` — per-phase or per-capability logic with progressive disclosure via `references/`
  - `design-analysis` (Phase 1 standard pipeline)
  - `design-extraction` (Phase 1 formalize pipeline)
  - `design-interview` (Phase 2 — the interview skill, also owns cross-skill protocols)
  - `brief-generation` (Phase 3 — owns the brief spec and output file rules)
  - `design-planning` (plan command, produces roadmap)
  - `design-evaluation` (audit command, produces findings + remediation)
  - `poster` (Phase 4 / poster command, produces poster spec)

## Cross-skill shared references

Owner skills provide references consumed by other skills via explicit path.

- `skills/design-interview/references/interview-protocol.md` — interview rules (used by design-interview and design-planning)
- `skills/design-interview/references/confirmed-decision-principle.md` — estimation-vs-decision semantics (used across the plugin)
- `skills/brief-generation/references/design-brief-spec.md` — brief format spec (produced by brief-generation, validated by poster and other domain skills)
- `skills/brief-generation/references/output-file-rules.md` — shared output directory/filename conventions

---

## Language convention

All documentation in this plugin uses English: CLAUDE.md, commands, skills,
and references.

The plugin processes design requests in any language and generates output
documents in the user's language. The documentation language and the output
language are separate concerns.

# omcc-designer — Contributor Notes

Notes for maintainers editing the omcc-designer plugin inside this repo.
End-user behavior lives in canonical components: `commands/`, `skills/`,
and shared references.

---

## Plugin layout

- `commands/` — thin orchestrators (start, formalize, plan, poster, social-graphics, frontend, audit)
- `skills/` — per-phase or per-capability logic with progressive disclosure via `references/`
  - `design-analysis` (Phase 1 standard pipeline)
  - `design-extraction` (Phase 1 formalize pipeline; also owns the DESIGN.md mapping contract used by /formalize Phase 4 and by /omcc-designer:frontend's brief consumption)
  - `design-interview` (Phase 2 — the interview skill, also owns cross-skill protocols)
  - `brief-generation` (Phase 3 — owns the brief spec and output file rules)
  - `design-planning` (plan command, produces roadmap)
  - `design-evaluation` (audit command, produces findings + remediation)
  - `poster` (Phase 4 / poster command, produces poster spec)
  - `poster-render` (Phase 4 chain-tail / poster command, renders raw zone images via codex)
  - `social-graphics` (Phase 4 / social-graphics command, produces multi-variant social graphics spec)
  - `social-graphics-render` (Phase 4 chain-tail / social-graphics command, renders per-variant raw zone images via codex)
  - `frontend` (Phase 4 / frontend command, produces a Google design.md spec — `DESIGN.md` — for AI coding agents; no chain-tail)
- `design-ensemble-protocol.md` (plugin root) — design-domain
  Codex ensemble protocol (design-critique-scan ensemble point
  with audit-artifact + step-c-direction prompt variants).
  Activated by `design-evaluation` and `design-interview`
  command-invoked modes; auto-activated mode runs Claude-only.
  Owning the contract locally is required because cross-plugin
  backtick references in markdown are rejected by
  `tests/test_plugin_structure.py`, and per the repo's
  "Independence over uniformity" principle.

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

- **Text-level critique skills → `codex` plugin** (same canonical
  source and detection mechanism as the render skills). The
  `design-evaluation` and `design-interview` skills shell out to
  the codex plugin's `codex-companion.mjs` for an independent
  second opinion — severity-rated audit critique and Step C
  alternative direction proposals respectively. The dependency
  is optional at runtime — preflight failure degrades silently
  to Claude-only output (audit findings or palette / typography /
  visual-style recommendations remain presentable on the
  Claude-only path). Detection uses the same marketplace-agnostic
  glob. The text critique invocation contract lives at
  `design-ensemble-protocol.md` (plugin root) — **distinct from**
  the image-render contract at
  `skills/poster-render/references/codex-call-template.md`. The
  two contracts share preflight discovery, `--prompt-file`
  dispatch, and EXIT trap discipline, but the render template's
  `--write` / `--cwd` / `SAVED_PATH` mechanics do not apply to
  text task. See each consuming skill's section for activation
  rules — `skills/design-evaluation/SKILL.md`
  "Codex ensemble" subsection (always-on for `/audit`) and
  `skills/design-interview/SKILL.md`
  "Second opinion (Codex ensemble)" subsection
  (user-initiated for `/start` and `/formalize` Step C).

---

## Boundary with research-scan and dev brainstorm

omcc-designer's text-level Codex ensemble (design-critique-scan,
defined at `design-ensemble-protocol.md`) is one of three
text ensemble surfaces in this marketplace. The boundaries
prevent feature overlap with the marketplace addition rule
(repo CLAUDE.md "Plugin Addition Procedure" #4).

| Aspect | design-critique-scan | research-scan (omcc-research) | brainstorm (omcc-dev) |
|--------|----------------------|-------------------------------|------------------------|
| Activation | `/omcc-designer:audit` always; `/omcc-designer:start` and `/omcc-designer:formalize` Step C user-initiated | `/omcc-research:research` always | `/omcc-dev:start` and `/omcc-dev:audit` brainstorm phase |
| Output | Severity-rated findings + alternative direction proposals | Cited evidence brief | Option comparison + recommendation |
| Persistence | In-session only | Durable artifact (research_brief.md) | In-workflow-state decision record |
| Synthesis axis | severity (Critical / High / Medium / Low) + Step C alignment | citation source-tier (official-docs / standards / academic / secondary) | option viability + tradeoffs |

When in doubt: critiquing a design or asking for an alternative
design direction → design-critique-scan. Gathering cited evidence
about a topic → research-scan. Choosing between viable options →
brainstorm.

The shared codex-companion surface does not blur this boundary —
each plugin owns its own protocol contract, prompt template, and
synthesis rules. References across protocols are prose only
because cross-plugin backtick references are rejected by
`tests/test_plugin_structure.py`.

---

## Language convention

All documentation in this plugin uses English: CLAUDE.md, commands, skills,
and references.

The plugin processes design requests in any language and generates output
documents in the user's language. The documentation language and the output
language are separate concerns.

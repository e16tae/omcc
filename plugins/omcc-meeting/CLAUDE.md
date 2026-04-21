# omcc-meeting — Contributor Notes

Notes for maintainers editing the omcc-meeting plugin inside this repo.
End-user behavior lives in canonical components: `commands/`, `skills/`, and
shared specs at the plugin root.

---

## Plugin layout

- `commands/` — thin orchestrators
  - `commands/start.md` — full 5-phase pipeline (analysis → interview → correction → minutes → report)
  - `commands/correct.md` — 3-phase pipeline ending at correction
- `skills/` — per-phase logic with progressive disclosure via `references/`
  - `transcript-analysis` (Phase 1)
  - `interview` (Phase 2, interactive)
  - `transcript-correction` (Phase 3)
  - `minutes` (Phase 4, standalone-invocable)
  - `report` (Phase 5, standalone-invocable)
- Shared specs at plugin root:
  - `transcript-header-spec.md` — corrected transcript header contract
  - `output-file-rules.md` — shared output file/directory conventions

---

## Language convention

All documentation in this plugin uses English: CLAUDE.md, commands, skills,
references, and shared specs.

The plugin processes Korean meeting transcripts and generates Korean-language
output documents. The documentation language and the output language are
separate concerns.

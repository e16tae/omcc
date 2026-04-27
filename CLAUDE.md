# omcc (oh-my-claude-code)

Personal Claude Code plugin marketplace.
Curates external plugins for one-stop installation,
and hosts built-in plugins.

## Structure
- `.claude-plugin/marketplace.json` — Marketplace manifest (core)
- `plugins/` — Built-in plugins
- `scripts/` — CI source accessibility validation scripts
- `tests/` — pytest-based marketplace validation tests
- `pyproject.toml` — Project config and test dependencies
- `.github/workflows/` — CI (validation + release automation)
- `release-please-config.json` + `.release-please-manifest.json` — Release automation config

## marketplace.json Editing Rules
- Always maintain valid JSON
- plugins array sorted alphabetically by name
- Plugin entry required fields: name, description, source
- Optional fields: category, homepage, version, author, license
- Validate: `uv run --extra test pytest -v`

## Plugin Addition Procedure
1. Verify source repo is public and .claude-plugin/plugin.json exists
2. Verify active maintenance or explicitly stable status
3. Verify OSI-approved license
4. Verify no feature overlap with existing plugins
5. Run local tests
6. Add entry to marketplace.json plugins array (insert at alphabetical position)

## Source Type Selection
- git-subdir: Plugin located in a monorepo subdirectory
- github: Plugin in a GitHub repo (owner/repo shorthand)
- url: Plugin at a git repo root
- npm: Plugin distributed as npm package
- ./plugins/...: Built-in plugin within omcc

## Commit Convention (Conventional Commits)

`<type>(<scope>): <description>`

Types: `feat`, `fix`, `docs`, `ci`, `refactor`, `chore`
Scope: plugin name or area

- Add plugin: `feat(name): add ...`
- Update plugin: `fix(name): update ...`
- Remove plugin: `feat(name)!: remove ...` (BREAKING CHANGE)
- Docs/CI: `docs(...)`, `ci(...)`

## Git Workflow

### Pull strategy
Use **merge** for `git pull` — never rebase. Run `git pull --no-rebase`
explicitly; do not rely on bare `git pull`, since `pull.rebase=true`
in any config layer (global, system, or repo) silently turns it into
a rebase. Resolve divergent branches via merge as well.

### Branching
Never commit directly to `main`. All changes go through:
1. create a feature branch (`git checkout -b <type>/<scope>`)
2. commit on the branch
3. push to origin (`git push -u origin <branch>`)
4. open a PR via `gh pr create`

Apply this even when the user says "커밋해" / "commit" — assume PR
workflow unless explicitly told otherwise (e.g., already on a feature
branch, or amending an in-flight PR).

## Versioning
- SemVer (MAJOR.MINOR.PATCH)
- MAJOR: breaking change (plugin removal/rename)
- MINOR: plugin addition
- PATCH: description edits, etc.
- release-please manages versions automatically based on commit messages

## Audit Filter — Known External Constraints

Some audit/review findings on this marketplace are non-actionable
because they reference external constraints that omcc does not control.
Treat the following as **Known — no action** and exclude from severity
tallies during synthesis:

- `marketplace.json` `$schema` field — references the Anthropic-managed
  URL `https://anthropic.com/claude-code/marketplace.schema.json`;
  hosting a project-local schema is out of scope.
- `source.source` field name (nested `source` key inside the `source`
  object) — dictated by the Anthropic marketplace schema, not an omcc
  naming choice.
- `marketplace.json` field structure being coupled to Claude Code's
  schema — inherent to being a marketplace manifest, not a design flaw.

Agents reporting these findings independently is normal; filtering
happens at synthesis.

## Plugin Design Principles

Built-in plugins (under `plugins/`) follow these principles.

### Canonical mechanisms only
End-user-facing rules — methodology, pipeline ordering, interaction protocols,
behavioral constraints — must be delivered through Claude Code's canonical plugin
components: `skills/`, `commands/`, `agents/`, `hooks/`, `settings.json`.
The plugin cache (`~/.claude/plugins/cache/...`) is not in the user's cwd
hierarchy, so plugin-level `CLAUDE.md` is NOT auto-injected for installed users.

### Plugin CLAUDE.md = contributor-only
Each plugin's own `CLAUDE.md` is loaded only when working inside this repo
(cwd-based discovery). Use it for maintainer/contributor notes — never for
end-user methodology rules.

### Independence over uniformity
Each plugin optimizes for its own domain. Do not force structural or
terminological consistency across plugins. Cross-plugin consistency is not a goal.

### Repo conventions over domain rationale

Established repo-wide conventions (language, structure, layout
patterns) take precedence over domain-specific arguments. If a new
plugin's domain seems to warrant a deviation, treat that deviation
as a design decision requiring brainstorm — not as an assumption.

Documentation language across all built-in plugins is **English**,
independent of the plugin's runtime domain (e.g., `omcc-meeting`
processes Korean meeting transcripts but its commands/skills/agents
are written in English). Runtime output language to the user is
determined by the user's interaction language, separately.

### Quality priority
Fundamentals > Standards > Recommendations > Pragmatics. Favor canonical
and spec-aligned approaches over pragmatic shortcuts when they conflict.

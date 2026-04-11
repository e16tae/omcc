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

## Versioning
- SemVer (MAJOR.MINOR.PATCH)
- MAJOR: breaking change (plugin removal/rename)
- MINOR: plugin addition
- PATCH: description edits, etc.
- release-please manages versions automatically based on commit messages

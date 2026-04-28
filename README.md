# omcc (oh-my-claude-code)

Curated Claude Code plugin marketplace.

## Quick Start

### Register marketplace
```
/plugin marketplace add e16tae/omcc
```

### Install a plugin
```
/plugin install codex@omcc
```

### Update marketplace
```
/plugin marketplace update omcc
```

## Plugins

| Plugin | Description | Source |
|--------|-------------|--------|
| codex | Use Codex from Claude Code to review code or delegate tasks | [openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc) |
| omcc-designer | Design consultation plugin with interview-based creative direction, design briefs, domain-specific specifications, existing design formalization, design planning, and quality auditing | built-in |
| omcc-dev | Development workflow framework with systematic bug fixing, feature development, code auditing, and hierarchical workflow shards + intra-session checkpoints for long-running projects (schema 2) | built-in |

## How Plugins Are Selected

- Source repository is public and accessible
- Valid `.claude-plugin/plugin.json` exists
- Actively maintained or explicitly stable
- OSI-approved license
- No functional overlap with existing curated plugins
- Locally tested

## Differences from Official Marketplace

- Curates third-party plugins not in the official catalog
- Includes experimental/niche plugins
- Hosts personal workflow-specific plugins
- Faster curation cycle

## Maintainer Setup

### `RELEASE_PAT` secret (required for automated lockfile sync)

release-please bumps `pyproject.toml` and every built-in `plugin.json` version
on each release, but it does not regenerate `uv.lock`. The release workflow
auto-regenerates the lockfile on the release PR branch, but pushes using the
default `GITHUB_TOKEN` do not retrigger the validate workflow, which would
leave the PR stuck with a stale failing check.

To enable the auto-sync, create a fine-grained or classic personal access
token with `contents: write` on this repository and store it as a repository
secret named `RELEASE_PAT`:

1. GitHub → Settings → Developer settings → Personal access tokens → create
   a token scoped to this repository with `Contents: Read and write` (or the
   classic `repo` scope for private repos; `public_repo` for public).
2. Repository Settings → Secrets and variables → Actions → New repository
   secret → `RELEASE_PAT`.

If branch protection is active on the release-please branch, the rule must
allow pushes from the PAT's owner (configure via Settings → Branches →
bypass list). Scope alone does not bypass branch protection.

Without `RELEASE_PAT`, the `sync-lockfile` job logs a warning and skips; the
maintainer must run `uv lock` manually on each release PR branch before
merging.

## License

MIT

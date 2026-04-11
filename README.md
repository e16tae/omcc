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
| omcc-dev | Development workflow framework with systematic bug fixing, feature development, and code auditing via multi-agent orchestration | built-in |

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

## License

MIT

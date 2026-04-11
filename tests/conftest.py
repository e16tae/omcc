import json
import re
from functools import lru_cache
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
MARKETPLACE_PATH = ROOT_DIR / ".claude-plugin" / "marketplace.json"


@lru_cache(maxsize=1)
def load_marketplace():
    """Load marketplace data. Cached so the file is read at most once."""
    with open(MARKETPLACE_PATH) as f:
        return json.load(f)


def get_plugins():
    """Get plugin list for parametrize."""
    return load_marketplace().get("plugins", [])


def get_local_plugins():
    """Get local plugins with resolved paths for parametrize."""
    return [
        (p, p["source"])
        for p in get_plugins()
        if isinstance(p.get("source"), str) and p["source"].startswith("./")
    ]


def get_git_subdir_plugins():
    """Get git-subdir source plugins for parametrize."""
    return [
        p for p in get_plugins()
        if isinstance(p.get("source"), dict)
        and p["source"].get("source") == "git-subdir"
    ]


def get_url_plugins():
    """Get url source plugins for parametrize."""
    return [
        p for p in get_plugins()
        if isinstance(p.get("source"), dict)
        and p["source"].get("source") == "url"
    ]


@lru_cache(maxsize=None)
def load_plugin_json(source_path):
    """Load a local plugin's plugin.json given its source path."""
    path = ROOT_DIR / source_path / ".claude-plugin" / "plugin.json"
    with open(path) as f:
        return json.load(f)


def parse_frontmatter(text):
    """Parse flat key: value YAML frontmatter from markdown text. Returns dict or None."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.DOTALL)
    if not m:
        return None
    result = {}
    for line in m.group(1).strip().split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            result[key.strip()] = val.strip()
    return result


def get_local_plugin_dirs():
    """Get local plugins with resolved Path objects for parametrize."""
    return [(p, ROOT_DIR / src) for p, src in get_local_plugins()]


def discover_commands(plugin_dir):
    """Return sorted list of .md files in commands/ subdirectory."""
    cmd_dir = plugin_dir / "commands"
    return sorted(cmd_dir.glob("*.md")) if cmd_dir.is_dir() else []


def discover_skills(plugin_dir):
    """Return sorted list of SKILL.md files in skills/*/ subdirectories."""
    skills_dir = plugin_dir / "skills"
    return sorted(skills_dir.glob("*/SKILL.md")) if skills_dir.is_dir() else []


def discover_agents(plugin_dir):
    """Return sorted list of .md files in agents/ subdirectory."""
    agents_dir = plugin_dir / "agents"
    return sorted(agents_dir.glob("*.md")) if agents_dir.is_dir() else []


def _collect_components(discover_fn):
    """Collect (plugin_name, file_path) pairs across all local plugins."""
    result = []
    for entry, plugin_dir in LOCAL_PLUGIN_DIRS:
        for fp in discover_fn(plugin_dir):
            result.append((entry["name"], fp))
    return result


# Pre-filtered lists for parametrize (evaluated once at collection time)
ALL_PLUGINS = get_plugins()
LOCAL_PLUGINS = get_local_plugins()
GIT_SUBDIR_PLUGINS = get_git_subdir_plugins()
URL_PLUGINS = get_url_plugins()
LOCAL_PLUGIN_DIRS = get_local_plugin_dirs()
ALL_COMMANDS = _collect_components(discover_commands)
ALL_SKILLS = _collect_components(discover_skills)
ALL_AGENTS = _collect_components(discover_agents)


def _plugin_id(p):
    return p.get("name", "<unnamed>")


def _local_ids(pairs):
    return [e.get("name", "<unnamed>") for e, _ in pairs]


@pytest.fixture(scope="session")
def marketplace_data():
    return load_marketplace()

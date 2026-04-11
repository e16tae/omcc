import json
from functools import lru_cache
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
MARKETPLACE_PATH = ROOT_DIR / ".claude-plugin" / "marketplace.json"


@lru_cache(maxsize=1)
def load_marketplace():
    """Load marketplace data. Cached so the file is read at most once."""
    try:
        with open(MARKETPLACE_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"plugins": []}


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


def load_plugin_json(source_path):
    """Load a local plugin's plugin.json given its source path."""
    path = ROOT_DIR / source_path / ".claude-plugin" / "plugin.json"
    with open(path) as f:
        return json.load(f)


# Pre-filtered lists for parametrize (evaluated once at collection time)
ALL_PLUGINS = get_plugins()
LOCAL_PLUGINS = get_local_plugins()
GIT_SUBDIR_PLUGINS = get_git_subdir_plugins()
URL_PLUGINS = get_url_plugins()


def _plugin_id(p):
    return p.get("name", "<unnamed>")


def _local_ids(pairs):
    return [e.get("name", "<unnamed>") for e, _ in pairs]


@pytest.fixture(scope="session")
def marketplace_data():
    return load_marketplace()

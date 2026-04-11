"""Shared source type classification for marketplace plugins.

Used by both tests/conftest.py and scripts/validate_marketplace.py to ensure
consistent source type handling. Any changes to classification logic should
be made here only.

Supported source types (per Claude Code official schema):
- local: string starting with "./" — relative path within marketplace repo
- github: object with source="github" — GitHub owner/repo shorthand
- url: object with source="url" — full git URL
- git-subdir: object with source="git-subdir" — subdirectory within git repo
- npm: object with source="npm" — npm package
"""

from pathlib import Path

# All object-based source types recognized by Claude Code
KNOWN_SOURCE_TYPES = frozenset({"github", "url", "git-subdir", "npm"})


def classify_source(plugin):
    """Classify a plugin's source type.

    Returns one of: "local", "github", "url", "git-subdir", "npm", or None
    for unrecognized formats.
    """
    src = plugin.get("source")
    if isinstance(src, str) and src.startswith("./"):
        return "local"
    if isinstance(src, dict):
        source_type = src.get("source")
        if source_type in KNOWN_SOURCE_TYPES:
            return source_type
    return None


def is_local_source(plugin):
    """Check if plugin uses a local (relative path) source."""
    return classify_source(plugin) == "local"


def validate_local_path(source_path, repo_root):
    """Validate a local source path is within the repo root.

    Returns (resolved_path, error_message). error_message is None if valid.
    """
    resolved = (repo_root / source_path).resolve()
    if not resolved.is_relative_to(Path(repo_root).resolve()):
        return resolved, "PATH_TRAVERSAL"
    if not resolved.is_dir():
        return resolved, "MISSING"
    return resolved, None

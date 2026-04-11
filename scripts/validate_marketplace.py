#!/usr/bin/env python3
"""Check plugin source accessibility in marketplace.json."""

import json
import re
import subprocess
import sys
from pathlib import Path

from source_types import classify_source, validate_local_path

MARKETPLACE_PATH = Path(__file__).resolve().parent.parent / ".claude-plugin" / "marketplace.json"


def load_marketplace():
    """Parse marketplace.json and return the data. Exits on JSON errors."""
    try:
        with open(MARKETPLACE_PATH) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON syntax: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"ERROR: {MARKETPLACE_PATH} not found")
        sys.exit(1)


def check_sources(data):
    """Check plugin source accessibility. Returns (results, warnings) tuple."""
    results = []
    warnings = []

    repo_root = MARKETPLACE_PATH.parent.parent.resolve()

    for plugin in data.get("plugins", []):
        name = plugin.get("name", "<unnamed>")
        src = plugin.get("source")
        source_type = classify_source(plugin)

        if source_type in ("url", "git-subdir", "github"):
            url = src.get("url") or src.get("repo")
            if not url:
                warnings.append(f"{name}: missing 'url' in source")
                continue
            # github type uses owner/repo shorthand, not a full URL
            if source_type == "github":
                if not re.match(r'^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$', url):
                    warnings.append(f"{name}: {url} -> INVALID_GITHUB_SHORTHAND (expected owner/repo)")
                    continue
            elif not url.startswith("https://"):
                warnings.append(f"{name}: {url} -> INVALID_SCHEME (https only)")
                continue
            check_url = f"https://github.com/{url}.git" if source_type == "github" else url
            try:
                result = subprocess.run(
                    ["git", "ls-remote", "--", check_url, "HEAD"],
                    capture_output=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    results.append(f"{name}: {check_url} -> OK")
                else:
                    warnings.append(f"{name}: {check_url} -> UNREACHABLE")
            except subprocess.TimeoutExpired:
                warnings.append(f"{name}: {check_url} -> TIMEOUT")
        elif source_type == "npm":
            results.append(f"{name}: npm:{src.get('package', '?')} -> SKIPPED")
        elif source_type == "local":
            _, error = validate_local_path(src, repo_root)
            if error:
                warnings.append(f"{name}: local:{src} -> {error}")
            else:
                results.append(f"{name}: local:{src} -> OK")
        else:
            warnings.append(f"{name}: unknown source format: {src!r}")

    return results, warnings


def main():
    data = load_marketplace()
    results, warnings = check_sources(data)
    for r in results:
        print(r)
    for w in warnings:
        print(f"WARNING: {w}")
    sys.exit(1 if warnings else 0)


if __name__ == "__main__":
    main()

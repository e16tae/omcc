#!/usr/bin/env python3
"""Check plugin source accessibility in marketplace.json."""

import json
import subprocess
import sys
from pathlib import Path

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

        if isinstance(src, dict) and src.get("source") in ("url", "git-subdir"):
            url = src.get("url")
            if not url:
                warnings.append(f"{name}: missing 'url' in source")
                continue
            if not url.startswith("https://"):
                warnings.append(f"{name}: {url} -> INVALID_SCHEME (https only)")
                continue
            try:
                result = subprocess.run(
                    ["git", "ls-remote", "--", url, "HEAD"],
                    capture_output=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    results.append(f"{name}: {url} -> OK")
                else:
                    warnings.append(f"{name}: {url} -> UNREACHABLE")
            except subprocess.TimeoutExpired:
                warnings.append(f"{name}: {url} -> TIMEOUT")
        elif isinstance(src, str) and src.startswith("./"):
            source_dir = (repo_root / src).resolve()
            if not source_dir.is_relative_to(repo_root):
                warnings.append(f"{name}: local:{src} -> PATH_TRAVERSAL")
                continue
            if source_dir.is_dir():
                results.append(f"{name}: local:{src} -> OK")
            else:
                warnings.append(f"{name}: local:{src} -> MISSING")
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

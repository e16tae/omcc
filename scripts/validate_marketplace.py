#!/usr/bin/env python3
"""Validate marketplace.json structure and plugin source accessibility."""

import argparse
import json
import os
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


def validate_structure(data):
    """Validate required fields and alphabetical sort order. Returns error list."""
    errors = []

    for field in ("name", "owner", "plugins"):
        if field not in data:
            errors.append(f"Missing top-level field: {field}")

    if "plugins" not in data:
        return errors

    names = []
    for i, plugin in enumerate(data["plugins"]):
        for field in ("name", "source", "description"):
            if field not in plugin:
                errors.append(f"Plugin {i}: missing '{field}'")
        if "name" in plugin:
            names.append(plugin["name"])

    if names != sorted(names):
        errors.append(f"Plugins not sorted alphabetically: {names}")

    return errors


def check_sources(data):
    """Check plugin source accessibility. Returns (results, warnings) tuple."""
    results = []
    warnings = []

    for plugin in data.get("plugins", []):
        name = plugin.get("name", "<unnamed>")
        src = plugin.get("source")

        if isinstance(src, dict) and src.get("source") in ("url", "git-subdir"):
            url = src.get("url")
            if not url:
                warnings.append(f"{name}: missing 'url' in source")
                continue
            try:
                result = subprocess.run(
                    ["git", "ls-remote", url, "HEAD"],
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
            source_dir = MARKETPLACE_PATH.parent.parent / src
            if source_dir.is_dir():
                results.append(f"{name}: local:{src} -> OK")
            else:
                warnings.append(f"{name}: local:{src} -> MISSING")

    return results, warnings


def cmd_structure(data):
    """Run structure validation. Exit 1 on errors."""
    errors = validate_structure(data)
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1

    plugin_count = len(data.get("plugins", []))
    print(f"Valid: {plugin_count} plugin(s), sorted correctly")
    return 0


def cmd_sources(data):
    """Run source accessibility checks. Exit 1 on warnings."""
    results, warnings = check_sources(data)
    for r in results:
        print(r)
    for w in warnings:
        print(f"WARNING: {w}")
    return 1 if warnings else 0


def cmd_all(data):
    """Run all validations. Source issues are warnings only (exit 0)."""
    errors = validate_structure(data)
    results, warnings = check_sources(data)

    if errors:
        for e in errors:
            print(f"ERROR: {e}")

    for r in results:
        print(r)
    for w in warnings:
        print(f"WARNING: {w}")

    if errors:
        return 1

    plugin_count = len(data.get("plugins", []))
    print(f"Valid: {plugin_count} plugin(s), all checks passed")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Validate marketplace.json")
    parser.add_argument(
        "command",
        nargs="?",
        default="all",
        choices=["structure", "sources", "all"],
        help="validation to run (default: all)",
    )
    args = parser.parse_args()

    data = load_marketplace()

    dispatch = {
        "structure": cmd_structure,
        "sources": cmd_sources,
        "all": cmd_all,
    }
    sys.exit(dispatch[args.command](data))


if __name__ == "__main__":
    main()

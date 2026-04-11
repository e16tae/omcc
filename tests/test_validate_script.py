"""Tests for scripts/validate_marketplace.py source checking logic."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Allow importing the validation script
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import validate_marketplace  # noqa: E402


# ---------------------------------------------------------------------------
# check_sources unit tests
# ---------------------------------------------------------------------------


@pytest.fixture
def repo_root(tmp_path):
    """Create a minimal repo structure for testing."""
    marketplace_dir = tmp_path / ".claude-plugin"
    marketplace_dir.mkdir()
    return tmp_path


def _make_data(plugins):
    return {"plugins": plugins}


class TestLocalSources:
    def test_valid_local_source(self, repo_root):
        plugin_dir = repo_root / "plugins" / "foo"
        plugin_dir.mkdir(parents=True)
        data = _make_data([{"name": "foo", "source": "./plugins/foo"}])

        with patch.object(validate_marketplace, "MARKETPLACE_PATH",
                          repo_root / ".claude-plugin" / "marketplace.json"):
            results, warnings = validate_marketplace.check_sources(data)

        assert any("OK" in r for r in results)
        assert not warnings

    def test_missing_local_source(self, repo_root):
        data = _make_data([{"name": "foo", "source": "./plugins/missing"}])

        with patch.object(validate_marketplace, "MARKETPLACE_PATH",
                          repo_root / ".claude-plugin" / "marketplace.json"):
            results, warnings = validate_marketplace.check_sources(data)

        assert any("MISSING" in w for w in warnings)

    def test_path_traversal_blocked(self, repo_root):
        # Create dir outside repo
        outside = repo_root.parent / "outside"
        outside.mkdir(exist_ok=True)
        data = _make_data([
            {"name": "evil", "source": "./../outside"}
        ])

        with patch.object(validate_marketplace, "MARKETPLACE_PATH",
                          repo_root / ".claude-plugin" / "marketplace.json"):
            results, warnings = validate_marketplace.check_sources(data)

        assert any("PATH_TRAVERSAL" in w for w in warnings)


class TestRemoteSources:
    def test_non_https_rejected(self, repo_root):
        data = _make_data([{
            "name": "bad",
            "source": {"source": "git-subdir", "url": "http://example.com/repo.git"}
        }])

        with patch.object(validate_marketplace, "MARKETPLACE_PATH",
                          repo_root / ".claude-plugin" / "marketplace.json"):
            results, warnings = validate_marketplace.check_sources(data)

        assert any("INVALID_SCHEME" in w for w in warnings)

    def test_missing_url_field(self, repo_root):
        data = _make_data([{
            "name": "bad",
            "source": {"source": "git-subdir", "path": "plugins/x", "ref": "main"}
        }])

        with patch.object(validate_marketplace, "MARKETPLACE_PATH",
                          repo_root / ".claude-plugin" / "marketplace.json"):
            results, warnings = validate_marketplace.check_sources(data)

        assert any("missing 'url'" in w for w in warnings)


class TestUnrecognizedSources:
    def test_unrecognized_dict_source_silently_skipped(self, repo_root):
        """Unrecognized dict source types are currently skipped (no result, no warning)."""
        data = _make_data([{
            "name": "weird",
            "source": {"source": "npm", "package": "foo"}
        }])

        with patch.object(validate_marketplace, "MARKETPLACE_PATH",
                          repo_root / ".claude-plugin" / "marketplace.json"):
            results, warnings = validate_marketplace.check_sources(data)

        assert not results
        # Note: after PR fix/marketplace-schema merges, this should assert warnings

    def test_bare_string_without_dot_slash_skipped(self, repo_root):
        """String sources not starting with './' are currently skipped."""
        data = _make_data([{
            "name": "weird",
            "source": "plugins/no-dot-slash"
        }])

        with patch.object(validate_marketplace, "MARKETPLACE_PATH",
                          repo_root / ".claude-plugin" / "marketplace.json"):
            results, warnings = validate_marketplace.check_sources(data)

        assert not results

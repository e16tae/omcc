import json

import pytest

from conftest import (
    ALL_PLUGINS,
    GIT_SUBDIR_PLUGINS,
    LOCAL_PLUGINS,
    MARKETPLACE_PATH,
    ROOT_DIR,
    URL_PLUGINS,
    _local_ids,
    _plugin_id,
)

# ---------------------------------------------------------------------------
# Marketplace structure
# ---------------------------------------------------------------------------


def test_marketplace_valid_json():
    with open(MARKETPLACE_PATH) as f:
        json.load(f)


def test_marketplace_has_required_fields(marketplace_data):
    for field in ("name", "owner", "plugins"):
        assert field in marketplace_data, f"Missing top-level field: {field}"


def test_marketplace_field_types(marketplace_data):
    assert isinstance(marketplace_data["name"], str)
    assert isinstance(marketplace_data["owner"], dict)
    assert isinstance(marketplace_data["plugins"], list)


# ---------------------------------------------------------------------------
# Per-plugin required fields
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("plugin", ALL_PLUGINS, ids=_plugin_id)
def test_plugin_has_required_fields(plugin):
    for field in ("name", "description", "source"):
        assert field in plugin, f"Plugin {plugin.get('name', '?')}: missing {field}"


@pytest.mark.parametrize("plugin", ALL_PLUGINS, ids=_plugin_id)
def test_plugin_required_field_types(plugin):
    assert isinstance(plugin["name"], str)
    assert isinstance(plugin["description"], str)
    assert isinstance(plugin["source"], (str, dict))


# ---------------------------------------------------------------------------
# Per-plugin optional fields
# ---------------------------------------------------------------------------

_OPTIONAL_FIELD_TYPES = {
    "category": str,
    "homepage": str,
    "version": str,
    "author": dict,
}


@pytest.mark.parametrize("plugin", ALL_PLUGINS, ids=_plugin_id)
def test_plugin_optional_field_types(plugin):
    for field, expected_type in _OPTIONAL_FIELD_TYPES.items():
        if field in plugin:
            assert isinstance(plugin[field], expected_type), (
                f"Plugin {plugin['name']}: {field} should be {expected_type.__name__}, "
                f"got {type(plugin[field]).__name__}"
            )


# ---------------------------------------------------------------------------
# Sorting and uniqueness
# ---------------------------------------------------------------------------


def test_plugins_sorted_alphabetically(marketplace_data):
    names = [p["name"] for p in marketplace_data["plugins"]]
    assert names == sorted(names), f"Plugins not sorted: {names}"


def test_no_duplicate_plugin_names(marketplace_data):
    names = [p["name"] for p in marketplace_data["plugins"]]
    assert len(names) == len(set(names)), f"Duplicate names found among {names}"


# ---------------------------------------------------------------------------
# Source structure validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "plugin,source_path", LOCAL_PLUGINS, ids=_local_ids(LOCAL_PLUGINS)
)
def test_local_source_directory_exists(plugin, source_path):
    assert (ROOT_DIR / source_path).is_dir(), (
        f"Plugin {plugin['name']}: directory {source_path} does not exist"
    )


@pytest.mark.parametrize(
    "plugin,source_path", LOCAL_PLUGINS, ids=_local_ids(LOCAL_PLUGINS)
)
def test_local_source_has_plugin_json(plugin, source_path):
    plugin_json = ROOT_DIR / source_path / ".claude-plugin" / "plugin.json"
    assert plugin_json.is_file(), (
        f"Plugin {plugin['name']}: missing {plugin_json}"
    )


@pytest.mark.parametrize(
    "plugin", GIT_SUBDIR_PLUGINS, ids=[_plugin_id(p) for p in GIT_SUBDIR_PLUGINS]
)
def test_git_subdir_source_fields(plugin):
    src = plugin["source"]
    for field in ("url", "path", "ref"):
        assert field in src, (
            f"Plugin {plugin['name']}: git-subdir source missing {field}"
        )


@pytest.mark.parametrize(
    "plugin", URL_PLUGINS, ids=[_plugin_id(p) for p in URL_PLUGINS]
)
def test_url_source_fields(plugin):
    src = plugin["source"]
    assert "url" in src, f"Plugin {plugin['name']}: url source missing 'url'"

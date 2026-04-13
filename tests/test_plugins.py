import pytest

from conftest import LOCAL_PLUGINS, _local_ids, load_plugin_json

# ---------------------------------------------------------------------------
# plugin.json validation for local plugins
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "entry,source_path", LOCAL_PLUGINS, ids=_local_ids(LOCAL_PLUGINS)
)
def test_plugin_json_valid_json(entry, source_path):
    load_plugin_json(source_path)


@pytest.mark.parametrize(
    "entry,source_path", LOCAL_PLUGINS, ids=_local_ids(LOCAL_PLUGINS)
)
def test_plugin_json_has_required_fields(entry, source_path):
    data = load_plugin_json(source_path)
    for field in ("name", "version", "description"):
        assert field in data, f"Plugin {entry['name']}: plugin.json missing {field}"


@pytest.mark.parametrize(
    "entry,source_path", LOCAL_PLUGINS, ids=_local_ids(LOCAL_PLUGINS)
)
def test_plugin_json_field_types(entry, source_path):
    data = load_plugin_json(source_path)
    assert isinstance(data.get("name"), str), "name should be str"
    assert isinstance(data.get("version"), str), "version should be str"
    assert isinstance(data.get("description"), str), "description should be str"


# ---------------------------------------------------------------------------
# Cross-reference: marketplace name matches plugin.json name
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "entry,source_path", LOCAL_PLUGINS, ids=_local_ids(LOCAL_PLUGINS)
)
def test_plugin_name_matches_marketplace(entry, source_path):
    data = load_plugin_json(source_path)
    assert data["name"] == entry["name"], (
        f"Name mismatch: marketplace says '{entry['name']}', "
        f"plugin.json says '{data['name']}'"
    )


@pytest.mark.parametrize(
    "entry,source_path", LOCAL_PLUGINS, ids=_local_ids(LOCAL_PLUGINS)
)
def test_plugin_version_matches_marketplace(entry, source_path):
    """Local plugin version must match marketplace entry when both specify it."""
    marketplace_version = entry.get("version")
    if marketplace_version is None:
        pytest.skip("marketplace entry has no version")
    data = load_plugin_json(source_path)
    assert data.get("version") == marketplace_version, (
        f"Version mismatch for {entry['name']}: "
        f"marketplace says '{marketplace_version}', "
        f"plugin.json says '{data.get('version')}'"
    )


@pytest.mark.parametrize(
    "entry,source_path", LOCAL_PLUGINS, ids=_local_ids(LOCAL_PLUGINS)
)
def test_plugin_version_is_valid_semver(entry, source_path):
    """Local plugin version must be a valid semver string."""
    import re

    data = load_plugin_json(source_path)
    version = data.get("version")
    assert version is not None, f"Plugin {entry['name']}: plugin.json missing version"
    assert re.match(r"^\d+\.\d+\.\d+", version), (
        f"Plugin {entry['name']}: version '{version}' is not valid semver"
    )

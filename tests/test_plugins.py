import pytest

from conftest import LOCAL_PLUGINS, ROOT_DIR, _local_ids, load_plugin_json

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
    """Local plugin version must match marketplace entry when both specify it.

    This test currently skips for all built-in plugins because their marketplace
    entries intentionally omit `version` (release-please manages versions via
    pyproject.toml + plugin.json, not marketplace.json). The test remains active
    so external or future plugin entries that do include a version are covered.
    """
    marketplace_version = entry.get("version")
    if marketplace_version is None:
        pytest.skip("marketplace entry has no version")
    data = load_plugin_json(source_path)
    assert data.get("version") == marketplace_version, (
        f"Version mismatch for {entry['name']}: "
        f"marketplace says '{marketplace_version}', "
        f"plugin.json says '{data.get('version')}'"
    )


def test_local_plugin_versions_match_project_version():
    """All built-in plugin.json versions must match pyproject.toml version.

    release-please synchronously bumps pyproject.toml and every built-in
    plugin.json as part of each release. Drift between them signals a partial
    release application or an out-of-band manual edit — neither is a valid
    state. This is the invariant that actually protects built-in plugins
    (the marketplace-based check skips because built-in marketplace entries
    intentionally omit version).
    """
    import re

    pyproject_text = (ROOT_DIR / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(
        r'^version\s*=\s*"([^"]+)"', pyproject_text, re.MULTILINE
    )
    assert match, "pyproject.toml is missing a top-level version field"
    project_version = match.group(1)

    mismatches = []
    for plugin, source_path in LOCAL_PLUGINS:
        plugin_version = load_plugin_json(source_path).get("version")
        if plugin_version != project_version:
            mismatches.append(
                f"{plugin['name']}: plugin.json={plugin_version!r} "
                f"vs pyproject.toml={project_version!r}"
            )
    assert not mismatches, (
        "Built-in plugin versions out of sync with pyproject.toml:\n  "
        + "\n  ".join(mismatches)
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

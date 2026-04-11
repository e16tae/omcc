import pytest

from conftest import (
    ALL_AGENTS,
    ALL_COMMANDS,
    ALL_SKILLS,
    LOCAL_PLUGIN_DIRS,
    load_plugin_json,
    parse_frontmatter,
)

# ---------------------------------------------------------------------------
# Guard: ensure parametrize lists are non-empty (prevent vacuous passes)
# ---------------------------------------------------------------------------


def test_local_plugins_discovered():
    assert LOCAL_PLUGIN_DIRS, "No local plugins found — check marketplace.json"


# ---------------------------------------------------------------------------
# plugin.json optional field validation
# ---------------------------------------------------------------------------

_plugin_dir_ids = [e["name"] for e, _ in LOCAL_PLUGIN_DIRS]


@pytest.mark.parametrize(
    "entry,plugin_dir", LOCAL_PLUGIN_DIRS, ids=_plugin_dir_ids
)
def test_plugin_json_optional_field_types(entry, plugin_dir):
    data = load_plugin_json(entry["source"])
    if "category" in data:
        assert isinstance(data["category"], str), "category should be str"
    if "author" in data:
        assert isinstance(data["author"], dict), "author should be dict"
        assert "name" in data["author"], "author must have 'name'"
    if "homepage" in data:
        assert isinstance(data["homepage"], str), "homepage should be str"


# ---------------------------------------------------------------------------
# Command frontmatter validation
# ---------------------------------------------------------------------------

_cmd_ids = [f"{n}:{p.stem}" for n, p in ALL_COMMANDS]


@pytest.mark.parametrize("plugin_name,cmd_path", ALL_COMMANDS, ids=_cmd_ids)
def test_command_frontmatter_has_description(plugin_name, cmd_path):
    text = cmd_path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    assert fm is not None, f"{cmd_path.name}: missing YAML frontmatter"
    assert "description" in fm, f"{cmd_path.name}: missing 'description'"
    assert fm["description"], f"{cmd_path.name}: description must be non-empty"


# ---------------------------------------------------------------------------
# Skill frontmatter validation
# ---------------------------------------------------------------------------

_skill_ids = [f"{n}:{p.parent.name}" for n, p in ALL_SKILLS]


@pytest.mark.parametrize("plugin_name,skill_path", ALL_SKILLS, ids=_skill_ids)
def test_skill_file_named_correctly(plugin_name, skill_path):
    assert skill_path.name == "SKILL.md", f"Expected SKILL.md, got {skill_path.name}"


@pytest.mark.parametrize("plugin_name,skill_path", ALL_SKILLS, ids=_skill_ids)
def test_skill_frontmatter_required_fields(plugin_name, skill_path):
    text = skill_path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    assert fm is not None, f"{skill_path.parent.name}: missing YAML frontmatter"
    assert "name" in fm, f"{skill_path.parent.name}: missing 'name'"
    assert "description" in fm, f"{skill_path.parent.name}: missing 'description'"


# ---------------------------------------------------------------------------
# Agent frontmatter validation
# ---------------------------------------------------------------------------

_agent_ids = [f"{n}:{p.stem}" for n, p in ALL_AGENTS]


@pytest.mark.parametrize("plugin_name,agent_path", ALL_AGENTS, ids=_agent_ids)
def test_agent_frontmatter_required_fields(plugin_name, agent_path):
    text = agent_path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    assert fm is not None, f"{agent_path.name}: missing YAML frontmatter"
    assert "name" in fm, f"{agent_path.name}: missing 'name'"
    assert "description" in fm, f"{agent_path.name}: missing 'description'"


@pytest.mark.parametrize("plugin_name,agent_path", ALL_AGENTS, ids=_agent_ids)
def test_agent_optional_field_types(plugin_name, agent_path):
    text = agent_path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if fm is None:
        pytest.skip("no frontmatter")
    for field in ("model", "tools", "color"):
        if field in fm:
            assert isinstance(fm[field], str), f"{agent_path.name}: {field} should be str"


# ---------------------------------------------------------------------------
# Plugin directory structure validation
# ---------------------------------------------------------------------------

_ALLOWED_ENTRIES = {".claude-plugin", "commands", "skills", "agents", "CLAUDE.md"}


@pytest.mark.parametrize(
    "entry,plugin_dir", LOCAL_PLUGIN_DIRS, ids=_plugin_dir_ids
)
def test_plugin_no_unexpected_top_level_entries(entry, plugin_dir):
    actual = {
        p.name for p in plugin_dir.iterdir()
        if not p.name.startswith(".") or p.name == ".claude-plugin"
    }
    unexpected = actual - _ALLOWED_ENTRIES
    assert not unexpected, f"Unexpected entries at plugin root: {unexpected}"

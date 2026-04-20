import re
from pathlib import Path

import pytest

from conftest import (
    ALL_AGENTS,
    ALL_COMMANDS,
    ALL_SKILLS,
    LOCAL_PLUGIN_DIRS,
    ROOT_DIR,
    discover_commands,
    discover_skills,
    load_plugin_json,
    parse_frontmatter,
)

# ---------------------------------------------------------------------------
# Guard: ensure parametrize lists are non-empty (prevent vacuous passes)
# ---------------------------------------------------------------------------


def test_local_plugins_discovered():
    assert LOCAL_PLUGIN_DIRS, "No local plugins found — check marketplace.json"


# ---------------------------------------------------------------------------
# parse_frontmatter unit tests
# ---------------------------------------------------------------------------


def test_parse_frontmatter_basic():
    text = "---\nname: foo\ndescription: bar baz\n---\nBody content"
    fm = parse_frontmatter(text)
    assert fm == {"name": "foo", "description": "bar baz"}


def test_parse_frontmatter_no_frontmatter():
    assert parse_frontmatter("No frontmatter here") is None


def test_parse_frontmatter_empty_value():
    text = "---\nname: foo\ndescription:\n---\n"
    fm = parse_frontmatter(text)
    assert fm["name"] == "foo"
    assert fm["description"] == ""


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
    if "license" in data:
        assert isinstance(data["license"], str), "license should be str"


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

_STANDARD_ENTRIES = {".claude-plugin", "CLAUDE.md"}


@pytest.mark.parametrize(
    "entry,plugin_dir", LOCAL_PLUGIN_DIRS, ids=_plugin_dir_ids
)
def test_plugin_no_unexpected_top_level_entries(entry, plugin_dir):
    pjson = load_plugin_json(entry["source"])

    # Build allowed set from plugin.json declared component paths
    allowed = set(_STANDARD_ENTRIES)
    for key in ("skills", "commands", "agents"):
        val = pjson.get(key, key)  # default to standard directory name
        if isinstance(val, str):
            allowed.add(val.removeprefix("./"))
        elif isinstance(val, list):
            allowed.update(val)

    actual = {
        p.name for p in plugin_dir.iterdir()
        if not p.name.startswith(".") or p.name == ".claude-plugin"
    }
    unexpected = actual - allowed
    # .md files are documentation and always allowed at plugin root
    unexpected = {f for f in unexpected if not f.endswith(".md")}
    assert not unexpected, f"Unexpected entries at plugin root: {unexpected}"


# ---------------------------------------------------------------------------
# Cross-reference validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "entry,plugin_dir", LOCAL_PLUGIN_DIRS, ids=_plugin_dir_ids
)
def test_referenced_files_exist(entry, plugin_dir):
    """Shared .md files referenced via backtick notation must exist in the plugin."""
    ref_pattern = re.compile(r'`([a-zA-Z0-9_/.-]+\.md)`')
    all_md = list(plugin_dir.rglob("*.md"))

    for md_file in all_md:
        content = md_file.read_text(encoding="utf-8")
        for match in ref_pattern.finditer(content):
            ref_name = match.group(1)
            ref_path = plugin_dir / ref_name
            if not ref_path.exists():
                rel = md_file.relative_to(plugin_dir)
                pytest.fail(
                    f"{entry['name']}: {rel} references `{ref_name}` "
                    f"but it does not exist"
                )


# ---------------------------------------------------------------------------
# CLAUDE.md command/skill list sync
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "entry,plugin_dir", LOCAL_PLUGIN_DIRS, ids=_plugin_dir_ids
)
def test_claude_md_lists_all_commands_and_skills(entry, plugin_dir):
    """CLAUDE.md must mention every command and skill the plugin provides."""
    claude_md_path = plugin_dir / "CLAUDE.md"
    if not claude_md_path.exists():
        pytest.skip("no CLAUDE.md")
    claude_md = claude_md_path.read_text(encoding="utf-8")
    for cmd in discover_commands(plugin_dir):
        assert cmd.stem in claude_md, (
            f"Command '{cmd.stem}' not mentioned in CLAUDE.md"
        )
    for skill in discover_skills(plugin_dir):
        assert skill.parent.name in claude_md, (
            f"Skill '{skill.parent.name}' not mentioned in CLAUDE.md"
        )


# ---------------------------------------------------------------------------
# Cross-plugin Output File Rules drift prevention
# ---------------------------------------------------------------------------


def _extract_h3_section(text: str, heading: str) -> str | None:
    """Return the text of an H3 section (### heading ... until next H2/H3/EOF)."""
    pattern = re.compile(
        rf"^###\s+{re.escape(heading)}\s*\n(.*?)(?=^#{{2,3}}\s|\Z)",
        re.DOTALL | re.MULTILINE,
    )
    m = pattern.search(text)
    return m.group(1).strip() if m else None


def _extract_bullet_rules(section: str) -> list[str]:
    """Return only bullet-list lines from a section, stripping prose.

    The prose lines around rules (intro sentences, etc.) contain domain-specific
    wording like 'project name' vs 'meeting name' which legitimately differs
    per plugin. The bullet rules themselves define the shared behavior that
    must stay in sync.
    """
    return [
        line.strip()
        for line in section.splitlines()
        if line.strip().startswith("-")
    ]


# Plugins that produce output files and therefore have Output File Rules.
# Filename lists vary per plugin, but the sanitization and policy subsections
# must stay in sync to prevent silent behavioral drift.
_OUTPUT_FILE_PLUGIN_DIRS = [
    ROOT_DIR / "plugins" / "omcc-designer",
    ROOT_DIR / "plugins" / "omcc-meeting",
]

# Subsections that should be byte-identical across plugins that produce output.
# Plugin-specific content (Directory structure, Directory naming with project
# vs meeting terminology, Filenames) is intentionally excluded.
_SYNCED_OUTPUT_SUBSECTIONS = [
    "Directory name sanitization",
    "Overwrite protection",
    "Other",
]


@pytest.mark.parametrize("subsection", _SYNCED_OUTPUT_SUBSECTIONS)
def test_output_file_rules_subsections_match_across_plugins(subsection):
    """Output File Rules subsections that define shared behavior must not drift.

    The sanitization rules, overwrite policy, and encoding/directory-creation
    rules apply identically regardless of plugin domain. Allowing the two
    copies (omcc-designer and omcc-meeting) to drift invites silent behavioral
    divergence — users would get different filesystem sanitization depending
    on which plugin produced their output.
    """
    rules_by_plugin = {}
    for plugin_dir in _OUTPUT_FILE_PLUGIN_DIRS:
        claude_md = (plugin_dir / "CLAUDE.md").read_text(encoding="utf-8")
        section = _extract_h3_section(claude_md, subsection)
        if section is None:
            pytest.fail(
                f"{plugin_dir.name} CLAUDE.md missing subsection: "
                f"'### {subsection}'"
            )
        rules_by_plugin[plugin_dir.name] = _extract_bullet_rules(section)

    distinct = {tuple(rules) for rules in rules_by_plugin.values()}
    if len(distinct) > 1:
        plugins = list(rules_by_plugin.keys())
        pytest.fail(
            f"Bullet rules under '### {subsection}' differ between plugins "
            f"{plugins}. These rules must stay in sync."
        )

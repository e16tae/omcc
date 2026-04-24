"""Schema drift guards: enforce that load-bearing values in
`continuity-protocol.md` stay in sync with their `hooks/_utils.mjs`
implementation counterparts.

Adding a new terminal state, changing `WORKFLOW_ID_REGEX`, or bumping
`SUPPORTED_SCHEMA_VERSION` in one place without the other breaks the
hook contract silently. These tests fail-closed so the drift is caught
at CI time instead of at runtime on an installed user's workflow.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "plugins" / "omcc-dev" / "continuity-protocol.md"
UTILS = ROOT / "plugins" / "omcc-dev" / "hooks" / "_utils.mjs"


def _read(path):
    return path.read_text()


def test_supported_schema_version_matches_spec_example():
    """The always-required frontmatter example in the spec names a schema
    integer that must match SUPPORTED_SCHEMA_VERSION in _utils.mjs."""
    spec = _read(SPEC)
    utils = _read(UTILS)
    m = re.search(
        r"```yaml\s*\n---\s*\nschema:\s*(\d+)\s+#\s*integer",
        spec,
    )
    assert m, "could not find schema literal in always-required frontmatter example"
    spec_schema = int(m.group(1))
    m = re.search(r"export const SUPPORTED_SCHEMA_VERSION\s*=\s*(\d+)", utils)
    assert m, "could not find SUPPORTED_SCHEMA_VERSION in _utils.mjs"
    code_schema = int(m.group(1))
    assert spec_schema == code_schema, (
        f"spec example schema: {spec_schema} != "
        f"_utils.mjs SUPPORTED_SCHEMA_VERSION: {code_schema}"
    )


def test_terminal_phases_match_spec():
    """The spec's Terminal states whitelist must match TERMINAL_PHASES in code."""
    spec = _read(SPEC)
    utils = _read(UTILS)
    # Spec: "**Terminal states** (exact whitelist...): `commit-complete`, `summary-complete`."
    m = re.search(
        r"\*\*Terminal states\*\*[^\n]*\n`([^`]+)`,\s*`([^`]+)`\.",
        spec,
    )
    assert m, "could not find Terminal states whitelist in spec"
    spec_phases = {m.group(1), m.group(2)}
    m = re.search(r"export const TERMINAL_PHASES\s*=\s*\[([^\]]+)\]", utils)
    assert m, "could not find TERMINAL_PHASES in _utils.mjs"
    code_phases = set(re.findall(r'"([^"]+)"', m.group(1)))
    assert spec_phases == code_phases, (
        f"spec terminal phases: {spec_phases} != code TERMINAL_PHASES: {code_phases}"
    )


def test_workflow_id_regex_matches_spec():
    """Spec's Format pin must match WORKFLOW_ID_REGEX (minus the
    optional migrated- extension, which the spec lists as a separate
    migration exception)."""
    spec = _read(SPEC)
    utils = _read(UTILS)
    m = re.search(r"Format pin:\s*`([^`]+)`", spec)
    assert m, "could not find workflow-id regex Format pin in spec"
    spec_regex = m.group(1)
    m = re.search(r"WORKFLOW_ID_REGEX\s*=\s*/([^/]+)/", utils)
    assert m, "could not find WORKFLOW_ID_REGEX in _utils.mjs"
    code_regex = m.group(1)
    # Normalize: drop the optional migrated- group, expand \d to [0-9]
    core = code_regex.replace("(migrated-)?", "").replace(r"\d", "[0-9]")
    assert core == spec_regex, (
        f"spec regex: {spec_regex} != code regex (normalized): {core}"
    )


def test_backtick_rule_spec_says_reject_not_strip():
    """Under the Injection defense posture, spec must describe backtick
    handling in SessionStart as row-rejection (skip), not as character
    stripping. Branch 2 B6 lands the matching code change; this test
    locks the spec wording so it cannot drift back to 'strip'."""
    spec = _read(SPEC)
    # Isolate the SessionStart frontmatter sanitization / backtick block.
    m = re.search(
        r"\*\*Backtick rule\*\*[\s\S]*?(?=\n-\s+\*\*Body)",
        spec,
    )
    assert m, "could not find Backtick rule block in spec"
    block = m.group(0)
    assert re.search(
        r"entry is rejected|skipped from the output|row is rejected",
        block,
        re.IGNORECASE,
    ), "Backtick rule no longer describes row rejection"
    # Must not describe backtick handling as stripping — stripping
    # keeps the injection-surface fragment in the echoed summary.
    assert not re.search(
        r"strip[s]?\s+(?:backtick|backquote|the backtick)",
        block,
        re.IGNORECASE,
    ), "Backtick rule block still describes 'strip' behavior"


def test_shard_id_regex_matches_spec():
    """Spec's SHARD_ID_REGEX Format pin must match the code constant."""
    spec = _read(SPEC)
    utils = _read(UTILS)
    m = re.search(
        r"\*\*Shard id format pin\*\*:\s*`\^([^`]+)\$`",
        spec,
    )
    assert m, "could not find shard-id format pin in spec"
    spec_body = m.group(1)
    m = re.search(r"SHARD_ID_REGEX\s*=\s*/\^([^$]+)\$/", utils)
    assert m, "could not find SHARD_ID_REGEX in _utils.mjs"
    code_body = m.group(1)
    assert spec_body == code_body, (
        f"spec regex body: {spec_body} != code regex body: {code_body}"
    )


def test_sanitize_field_caps_spec_matches_code():
    """The spec's SessionStart sanitization block cites SANITIZE_FIELD_CAPS
    explicitly (phase=64, next_action=120, type=16, checkpoint_summary=200).
    The table in _utils.mjs must match."""
    spec = _read(SPEC)
    utils = _read(UTILS)
    spec_caps = dict(
        (name, int(value))
        for name, value in re.findall(
            r"(phase|next_action|type|checkpoint_summary)=(\d+)", spec
        )
    )
    m = re.search(
        r"SANITIZE_FIELD_CAPS\s*=\s*\{([^}]+)\}", utils, re.DOTALL
    )
    assert m, "could not find SANITIZE_FIELD_CAPS in _utils.mjs"
    code_caps = dict(
        (name, int(value))
        for name, value in re.findall(
            r"(phase|next_action|type|checkpoint_summary)\s*:\s*(\d+)",
            m.group(1),
        )
    )
    for name in ("phase", "next_action", "type", "checkpoint_summary"):
        assert name in spec_caps, f"spec missing cap for {name}"
        assert name in code_caps, f"code missing cap for {name}"
        assert spec_caps[name] == code_caps[name], (
            f"cap drift: {name} spec={spec_caps[name]} code={code_caps[name]}"
        )


def test_supported_schema_version_is_2():
    """B1.1 bumped the protocol to schema 2 — confirm the code side is
    there too, not just the spec example."""
    utils = _read(UTILS)
    m = re.search(r"export const SUPPORTED_SCHEMA_VERSION\s*=\s*(\d+)", utils)
    assert m
    assert int(m.group(1)) == 2

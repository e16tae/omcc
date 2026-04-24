"""Unit tests for omcc-dev hooks/_utils.mjs exports.

Invokes node with --input-type=module to import helpers as ESM and asserts
observable behavior at the boundary (stdout / exit code). Complements
test_hooks.py which exercises the three hook scripts as subprocesses.

Requires `node` on PATH.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
UTILS_PATH = ROOT / "plugins" / "omcc-dev" / "hooks" / "_utils.mjs"
UTILS_URL = UTILS_PATH.as_uri()

_NODE_AVAILABLE = shutil.which("node") is not None
pytestmark = pytest.mark.skipif(
    not _NODE_AVAILABLE,
    reason="node binary not available on PATH",
)


def _call_util(snippet, *, imports):
    """Invoke a node ESM snippet that imports names from _utils.mjs.

    Returns (returncode, stdout, stderr). The snippet is responsible for
    writing any assertion-visible output to stdout via console.log.
    """
    names = ", ".join(imports)
    code = f"import {{ {names} }} from '{UTILS_URL}';\n{snippet}\n"
    proc = subprocess.run(
        ["node", "--input-type=module", "-e", code],
        capture_output=True,
        text=True,
        timeout=15,
    )
    return proc.returncode, proc.stdout, proc.stderr


def test_utils_module_imports():
    """Sanity: _utils.mjs imports and exposes SUPPORTED_SCHEMA_VERSION."""
    rc, stdout, stderr = _call_util(
        "console.log(SUPPORTED_SCHEMA_VERSION);",
        imports=["SUPPORTED_SCHEMA_VERSION"],
    )
    assert rc == 0, f"node exit {rc} stderr={stderr}"
    assert stdout.strip() == "2"


# --- atomicModifyFile (1.3) -------------------------------------------------


def test_atomic_modify_file_applies_mutator(tmp_path):
    """Read→transform→write runs under lock; lock sentinel cleaned up."""
    target = tmp_path / "state.md"
    target.write_text("hello\n")
    target_json = json.dumps(str(target))
    rc, stdout, stderr = _call_util(
        f"""
await atomicModifyFile({target_json}, async (current) => current.toUpperCase());
console.log('ok');
""",
        imports=["atomicModifyFile"],
    )
    assert rc == 0, f"rc={rc} stderr={stderr}"
    assert target.read_text() == "HELLO\n"
    assert not Path(f"{target}.lock").exists()


def test_atomic_modify_file_noop_when_mutator_returns_null(tmp_path):
    """mutator returning null signals no-op: original file untouched, no .bak."""
    target = tmp_path / "state.md"
    target.write_text("unchanged\n")
    target_json = json.dumps(str(target))
    rc, stdout, stderr = _call_util(
        f"await atomicModifyFile({target_json}, async (_) => null);\nconsole.log('ok');\n",
        imports=["atomicModifyFile"],
    )
    assert rc == 0, stderr
    assert target.read_text() == "unchanged\n"
    assert not (tmp_path / "state.md.bak").exists()
    assert not Path(f"{target}.lock").exists()


def test_atomic_modify_file_creates_file_when_absent(tmp_path):
    """mutator receives null when target does not exist and may return new content."""
    target = tmp_path / "new.md"
    target_json = json.dumps(str(target))
    rc, stdout, stderr = _call_util(
        f"""
await atomicModifyFile({target_json}, async (current) => {{
  if (current !== null) throw new Error('expected null got ' + JSON.stringify(current));
  return 'created\\n';
}});
console.log('ok');
""",
        imports=["atomicModifyFile"],
    )
    assert rc == 0, stderr
    assert target.read_text() == "created\n"
    assert not Path(f"{target}.lock").exists()


def test_atomic_modify_file_releases_lock_on_mutator_error(tmp_path):
    """Errors from mutator propagate; lock is released; original preserved."""
    target = tmp_path / "state.md"
    target.write_text("pre\n")
    target_json = json.dumps(str(target))
    rc, stdout, stderr = _call_util(
        f"""
try {{
  await atomicModifyFile({target_json}, async () => {{ throw new Error('boom'); }});
}} catch (e) {{
  console.log('caught:' + e.message);
}}
""",
        imports=["atomicModifyFile"],
    )
    assert rc == 0, stderr
    assert "caught:boom" in stdout
    assert target.read_text() == "pre\n"
    assert not Path(f"{target}.lock").exists()


def test_atomic_update_file_still_works(tmp_path):
    """atomicUpdateFile is a thin wrapper around atomicModifyFile; regression guard."""
    target = tmp_path / "state.md"
    target.write_text("v1\n")
    target_json = json.dumps(str(target))
    rc, stdout, stderr = _call_util(
        f"await atomicUpdateFile({target_json}, 'v2\\n');\nconsole.log('ok');\n",
        imports=["atomicUpdateFile"],
    )
    assert rc == 0, stderr
    assert target.read_text() == "v2\n"
    assert (tmp_path / "state.md.bak").read_text() == "v1\n"


# --- FINDING_ID_REGEX / isValidFindingId (1.4) ------------------------------


def test_finding_id_accepts_valid():
    """isValidFindingId accepts ^finding-[0-9]+$ per continuity-protocol.md:86."""
    rc, stdout, stderr = _call_util(
        """
for (const id of ['finding-0', 'finding-1', 'finding-42', 'finding-999']) {
  console.log(id + ':' + isValidFindingId(id));
}
""",
        imports=["isValidFindingId"],
    )
    assert rc == 0, stderr
    lines = stdout.strip().split("\n")
    assert lines == [
        "finding-0:true",
        "finding-1:true",
        "finding-42:true",
        "finding-999:true",
    ]


def test_finding_id_rejects_invalid():
    """Malformed / path-traversal / wrong-type inputs must be rejected."""
    rc, stdout, stderr = _call_util(
        """
for (const id of [
  'finding-', 'finding', 'find-1', 'FINDING-1', 'finding-1.5',
  'finding-1/../etc', '', 'finding-1 ', 'findingx1', 'finding--1',
]) {
  console.log(id + ':' + isValidFindingId(id));
}
console.log('null:' + isValidFindingId(null));
console.log('undef:' + isValidFindingId(undefined));
console.log('number:' + isValidFindingId(1));
console.log('object:' + isValidFindingId({}));
""",
        imports=["isValidFindingId"],
    )
    assert rc == 0, stderr
    for line in stdout.strip().split("\n"):
        assert line.endswith(":false"), f"expected false, got: {line}"


# --- SECRETS_SCRUB_PATTERNS / scrubSecrets (1.5) ----------------------------


def test_scrub_redacts_token_prefixes():
    """Pattern 1: sk*, ghp*, AKIA*, xoxb* etc. per continuity-protocol.md:764-766."""
    rc, stdout, stderr = _call_util(
        """
for (const s of [
  'ghp_1234567890abcdef',
  'sk-ant-api-abc12345',
  'AKIAIOSFODNN7EXAMPLE',
  'xoxb-test-abcdefgh12',
  'github_pat_abcdef12345',
]) {
  console.log(scrubSecrets(s));
}
""",
        imports=["scrubSecrets"],
    )
    assert rc == 0, stderr
    for line in stdout.strip().split("\n"):
        assert line == "[REDACTED]", f"expected REDACTED, got: {line}"


def test_scrub_redacts_bearer_token():
    """Pattern 2: case-sensitive Bearer header per continuity-protocol.md:767."""
    rc, stdout, stderr = _call_util(
        "console.log(scrubSecrets('Bearer abc.def-123+xyz/='));",
        imports=["scrubSecrets"],
    )
    assert rc == 0, stderr
    assert stdout.strip() == "[REDACTED]"


def test_scrub_keyword_value_case_insensitive():
    """Pattern 3: (password|token|secret|api_key|authorization) + :/= + value."""
    rc, stdout, stderr = _call_util(
        """
for (const s of [
  'password=hunter2',
  'PASSWORD: supersecret',
  'api_key = xyz123',
  'API-KEY: ABCDEF',
  'Secret=shh',
  'token : t0k3n',
  'Authorization=opaque',
]) {
  console.log(scrubSecrets(s));
}
""",
        imports=["scrubSecrets"],
    )
    assert rc == 0, stderr
    for line in stdout.strip().split("\n"):
        assert line == "[REDACTED]", f"expected REDACTED, got: {line}"


def test_scrub_replaces_all_occurrences():
    """Global flag: multiple matches in the same string all redact."""
    rc, stdout, stderr = _call_util(
        "console.log(scrubSecrets('ghp_xxxxxxxx and ghp_yyyyyyyy'));",
        imports=["scrubSecrets"],
    )
    assert rc == 0, stderr
    assert stdout.strip() == "[REDACTED] and [REDACTED]"


def test_scrub_passes_through_innocuous_text():
    rc, stdout, stderr = _call_util(
        "console.log(scrubSecrets('this is a normal string'));",
        imports=["scrubSecrets"],
    )
    assert rc == 0, stderr
    assert stdout.strip() == "this is a normal string"


def test_scrub_returns_non_strings_unchanged():
    rc, stdout, stderr = _call_util(
        """
const cases = [null, undefined, 42, {a: 1}];
for (const c of cases) {
  console.log(JSON.stringify(scrubSecrets(c)));
}
""",
        imports=["scrubSecrets"],
    )
    assert rc == 0, stderr
    lines = stdout.strip().split("\n")
    # JSON.stringify(undefined) returns the value undefined (not a string),
    # which console.log prints as the literal "undefined".
    assert lines == ["null", "undefined", "42", '{"a":1}'], lines


# --- SANITIZE_FIELD_CAPS / sanitizeField (1.6) ------------------------------


def test_sanitize_field_applies_table_caps():
    """Each field name gets its table-defined cap."""
    rc, stdout, stderr = _call_util(
        """
const long = 'x'.repeat(300);
console.log('phase:' + sanitizeField('phase', long).length);
console.log('next_action:' + sanitizeField('next_action', long).length);
console.log('type:' + sanitizeField('type', long).length);
console.log('checkpoint_summary:' + sanitizeField('checkpoint_summary', long).length);
""",
        imports=["sanitizeField"],
    )
    assert rc == 0, stderr
    lines = stdout.strip().split("\n")
    assert lines == [
        "phase:64",
        "next_action:120",
        "type:16",
        "checkpoint_summary:200",
    ]


def test_sanitize_field_unknown_name_uses_default_cap():
    """Unknown field name falls back to SANITIZE_CAP (512)."""
    rc, stdout, stderr = _call_util(
        """
const long = 'x'.repeat(1000);
console.log(sanitizeField('nonexistent_field_name', long).length);
""",
        imports=["sanitizeField"],
    )
    assert rc == 0, stderr
    assert stdout.strip() == "512"


def test_sanitize_field_strips_control_chars():
    """sanitizeField inherits sanitize() control-char stripping.
    Backtick handling is covered by the separate reject test below."""
    rc, stdout, stderr = _call_util(
        """
console.log(sanitizeField('phase', 'hello\\u0001world\\u0007').length);
""",
        imports=["sanitizeField"],
    )
    assert rc == 0, stderr
    # \\u0001 and \\u0007 both stripped -> "helloworld" (10 chars)
    assert stdout.strip() == "10"


def test_sanitize_field_rejects_backticks_with_null():
    """B6: a backtick anywhere in the input causes sanitize() /
    sanitizeField() to return null so callers can reject the entry
    entirely rather than leak a stripped fragment into Claude context."""
    rc, stdout, stderr = _call_util(
        "console.log(JSON.stringify(sanitizeField('phase', 'hello`cmd`')));",
        imports=["sanitizeField"],
    )
    assert rc == 0, stderr
    assert stdout.strip() == "null"


# --- walkWorkflowTree (1.7) -------------------------------------------------


def test_walk_tree_empty_or_invalid_inputs_return_empty():
    rc, stdout, stderr = _call_util(
        """
console.log(JSON.stringify(walkWorkflowTree([], 'root')));
console.log(JSON.stringify(walkWorkflowTree(null, 'root')));
console.log(JSON.stringify(walkWorkflowTree([], 42)));
console.log(JSON.stringify(walkWorkflowTree([{id:'only', parent:null}], 'root')));
""",
        imports=["walkWorkflowTree"],
    )
    assert rc == 0, stderr
    assert stdout.strip().split("\n") == ["[]", "[]", "[]", "[]"]


def test_walk_tree_direct_children():
    rc, stdout, stderr = _call_util(
        """
const entries = [
  { id: 'root', parent: null },
  { id: 'A', parent: 'root' },
  { id: 'B', parent: 'root' },
  { id: 'C', parent: 'other' },
];
console.log(JSON.stringify(walkWorkflowTree(entries, 'root').map(e => e.id)));
""",
        imports=["walkWorkflowTree"],
    )
    assert rc == 0, stderr
    result = json.loads(stdout.strip())
    assert set(result) == {"A", "B"}


def test_walk_tree_multi_level_topological():
    """Descendants appear after their parent; BFS order is stable per level."""
    rc, stdout, stderr = _call_util(
        """
const entries = [
  { id: 'root', parent: null },
  { id: 'A', parent: 'root' },
  { id: 'AA', parent: 'A' },
  { id: 'AAA', parent: 'AA' },
];
console.log(JSON.stringify(walkWorkflowTree(entries, 'root').map(e => e.id)));
""",
        imports=["walkWorkflowTree"],
    )
    assert rc == 0, stderr
    assert stdout.strip() == '["A","AA","AAA"]'


def test_walk_tree_handles_direct_cycle():
    """Cycle A->B->A must terminate without infinite loop."""
    rc, stdout, stderr = _call_util(
        """
const entries = [
  { id: 'A', parent: 'B' },
  { id: 'B', parent: 'A' },
];
console.log(JSON.stringify(walkWorkflowTree(entries, 'A').map(e => e.id)));
""",
        imports=["walkWorkflowTree"],
    )
    assert rc == 0, stderr
    # Starting from A: B is a child of A (visited once). B's only listed
    # child is A, already visited, so the walk terminates.
    assert stdout.strip() == '["B"]'


def test_walk_tree_skips_self_parent():
    rc, stdout, stderr = _call_util(
        """
const entries = [
  { id: 'root', parent: null },
  { id: 'loop', parent: 'loop' },
  { id: 'A', parent: 'root' },
];
console.log(JSON.stringify(walkWorkflowTree(entries, 'root').map(e => e.id)));
""",
        imports=["walkWorkflowTree"],
    )
    assert rc == 0, stderr
    assert stdout.strip() == '["A"]'


def test_walk_tree_excludes_root_itself():
    rc, stdout, stderr = _call_util(
        """
const entries = [{ id: 'root', parent: null }];
console.log(JSON.stringify(walkWorkflowTree(entries, 'root').map(e => e.id)));
""",
        imports=["walkWorkflowTree"],
    )
    assert rc == 0, stderr
    assert stdout.strip() == "[]"


# --- parseNestedList + parseActiveRegistry (1.8) ---------------------------


def test_parse_active_registry_regression():
    """Primary regression: active registry parse via parseNestedList."""
    rc, stdout, stderr = _call_util(
        """
const content = `---
schema: 2
updated_at: 2026-04-22T00:00:00Z
active:
  - id: fix-20260422T120000Z-abcdef
    type: fix
    phase: investigate
    parent: null
    children: []
    originating_finding: null
  - id: start-20260422T130000Z-123456
    type: start
    phase: implement
    parent: null
    children:
      - fix-20260422T120000Z-abcdef
    originating_finding: null
---
`;
console.log(JSON.stringify(parseActiveRegistry(content)));
""",
        imports=["parseActiveRegistry"],
    )
    assert rc == 0, stderr
    result = json.loads(stdout.strip())
    assert len(result) == 2
    assert result[0]["id"] == "fix-20260422T120000Z-abcdef"
    assert result[0]["type"] == "fix"
    assert result[0]["parent"] is None
    assert result[0]["children"] == []
    assert result[1]["children"] == ["fix-20260422T120000Z-abcdef"]


def test_parse_nested_list_with_unrelated_top_key():
    """parseNestedList works for any top-level list-of-maps key, not just `active`."""
    rc, stdout, stderr = _call_util(
        """
const fmBody = `schema: 2
findings:
  - id: finding-1
    severity: high
    decision: undecided
  - id: finding-2
    severity: low
    decision: fix-now`;
console.log(JSON.stringify(parseNestedList(fmBody, 'findings')));
""",
        imports=["parseNestedList"],
    )
    assert rc == 0, stderr
    result = json.loads(stdout.strip())
    assert len(result) == 2
    assert result[0]["id"] == "finding-1"
    assert result[0]["severity"] == "high"
    assert result[1]["decision"] == "fix-now"


def test_parse_nested_list_empty_inline_literal():
    """`topKey: []` parses as empty list."""
    rc, stdout, stderr = _call_util(
        """
const fmBody = 'schema: 2\\nfindings: []\\n';
console.log(JSON.stringify(parseNestedList(fmBody, 'findings')));
""",
        imports=["parseNestedList"],
    )
    assert rc == 0, stderr
    assert stdout.strip() == "[]"


def test_parse_nested_list_ignores_malformed_lines():
    """Lines without `key: value` shape are skipped silently (fail-closed)."""
    rc, stdout, stderr = _call_util(
        """
const fmBody = `schema: 2
active:
  - id: valid-id
    type: fix
    malformed line without colon
    phase: investigate`;
const result = parseNestedList(fmBody, 'active', ['children']);
console.log(JSON.stringify(result[0]));
""",
        imports=["parseNestedList"],
    )
    assert rc == 0, stderr
    entry = json.loads(stdout.strip())
    assert entry["id"] == "valid-id"
    assert entry["type"] == "fix"
    assert entry["phase"] == "investigate"


def test_parse_nested_list_respects_inner_list_keys():
    """children is collected as nested list only when listed in innerListKeys."""
    rc, stdout, stderr = _call_util(
        """
const fmBody = `schema: 2
active:
  - id: a
    children:
      - child-1
      - child-2`;
const withInner = parseNestedList(fmBody, 'active', ['children']);
const withoutInner = parseNestedList(fmBody, 'active');
console.log(JSON.stringify(withInner[0].children));
console.log(JSON.stringify(withoutInner[0].children));
""",
        imports=["parseNestedList"],
    )
    assert rc == 0, stderr
    lines = stdout.strip().split("\n")
    assert lines[0] == '["child-1","child-2"]'
    # Without innerListKeys, `children` is parsed as a scalar kv -> "" -> null
    assert lines[1] in ("null", "undefined")


# --- archiveCleanupPolicy (1.9) --------------------------------------------


def test_archive_cleanup_removes_bak_preserves_lock(tmp_path):
    """`.bak` sibling is removed; `.lock` is preserved (may be owned)."""
    archived_src = tmp_path / "archived.md"
    bak = tmp_path / "archived.md.bak"
    lock = tmp_path / "archived.md.lock"
    bak.write_text("bak content")
    lock.write_text("lock content")
    rc, stdout, stderr = _call_util(
        f"await archiveCleanupPolicy({json.dumps(str(archived_src))});\nconsole.log('ok');\n",
        imports=["archiveCleanupPolicy"],
    )
    assert rc == 0, stderr
    assert not bak.exists(), ".bak should be removed"
    assert lock.exists(), ".lock must be preserved"


def test_archive_cleanup_noop_when_bak_absent(tmp_path):
    archived_src = tmp_path / "archived.md"
    rc, stdout, stderr = _call_util(
        f"await archiveCleanupPolicy({json.dumps(str(archived_src))});\nconsole.log('ok');\n",
        imports=["archiveCleanupPolicy"],
    )
    assert rc == 0, stderr
    assert stdout.strip() == "ok"


# --- append/removeChildToParentRegistry (B2.1) ------------------------------

# Note: workflow-id shortids are 6 hex chars per WORKFLOW_ID_REGEX. These
# tests use descriptive aliases via Python variables so intent reads clearly:
_PARENT = "start-20260423T120000Z-aaaaaa"
_CHILD_A = "fix-20260423T125900Z-bbbbba"  # earlier timestamp, sorts first
_CHILD_B = "fix-20260423T130000Z-bbbbbb"
_CHILD_C = "fix-20260423T130000Z-bbbbbc"
_OTHER_PARENT = "start-20260423T999999Z-ffffff"  # not in registry
_OTHER_CHILD = "fix-20260423T130000Z-cccccc"   # not in any child list


def _write_active_registry(path, entries):
    """Helper: write an active.md with the given entries (for B2.1 tests).

    Each entry is a dict {id, parent, children} — minimal shape that
    exercises the new helpers without dragging in _write_active.
    """
    lines = ["---", "schema: 2", "updated_at: 2026-04-23T00:00:00Z", "active:"]
    for e in entries:
        lines.append(f"  - id: {e['id']}")
        lines.append(f"    type: {e.get('type', 'start')}")
        lines.append(f"    phase: {e.get('phase', 'implement')}")
        lines.append(f"    parent: {e['parent'] if e.get('parent') else 'null'}")
        children = e.get("children", [])
        if children:
            lines.append("    children:")
            for c in children:
                lines.append(f"      - {c}")
        else:
            lines.append("    children: []")
        lines.append(f"    originating_finding: null")
    lines.append("---")
    lines.append("")
    path.write_text("\n".join(lines))


def test_append_child_to_empty_children(tmp_path):
    """Parent with `children: []` gets a multi-line children block with one entry."""
    active = tmp_path / "active.md"
    _write_active_registry(active, [
        {"id": _PARENT, "parent": None, "children": []},
    ])
    rc, _, stderr = _call_util(
        f"await appendChildToParentRegistry({json.dumps(str(active))}, "
        f"{json.dumps(_PARENT)}, {json.dumps(_CHILD_B)});\n",
        imports=["appendChildToParentRegistry"],
    )
    assert rc == 0, stderr
    content = active.read_text()
    assert f"children:\n      - {_CHILD_B}" in content
    assert "children: []" not in content


def test_append_child_extends_existing_children(tmp_path):
    """Parent already with children gets a new entry in sorted order."""
    active = tmp_path / "active.md"
    _write_active_registry(active, [
        {"id": _PARENT, "parent": None, "children": [_CHILD_C]},
    ])
    rc, _, stderr = _call_util(
        f"await appendChildToParentRegistry({json.dumps(str(active))}, "
        f"{json.dumps(_PARENT)}, {json.dumps(_CHILD_A)});\n",
        imports=["appendChildToParentRegistry"],
    )
    assert rc == 0, stderr
    content = active.read_text()
    # Sorted ascending: CHILD_A (timestamp earlier) before CHILD_C
    idx_a = content.find(_CHILD_A)
    idx_c = content.find(_CHILD_C)
    assert 0 < idx_a < idx_c, f"expected sorted order; got idx_a={idx_a}, idx_c={idx_c}"


def test_append_child_dedupes(tmp_path):
    """Appending an existing child is a no-op (no duplicate entry)."""
    active = tmp_path / "active.md"
    _write_active_registry(active, [
        {"id": _PARENT, "parent": None, "children": [_CHILD_B]},
    ])
    rc, _, stderr = _call_util(
        f"await appendChildToParentRegistry({json.dumps(str(active))}, "
        f"{json.dumps(_PARENT)}, {json.dumps(_CHILD_B)});\n",
        imports=["appendChildToParentRegistry"],
    )
    assert rc == 0, stderr
    content = active.read_text()
    assert content.count(_CHILD_B) == 1


def test_append_child_noop_for_missing_parent(tmp_path):
    """Unknown parent id: no-op, no throw, content unchanged."""
    active = tmp_path / "active.md"
    _write_active_registry(active, [
        {"id": _PARENT, "parent": None, "children": []},
    ])
    rc, _, stderr = _call_util(
        f"await appendChildToParentRegistry({json.dumps(str(active))}, "
        f"{json.dumps(_OTHER_PARENT)}, {json.dumps(_CHILD_B)});\n",
        imports=["appendChildToParentRegistry"],
    )
    assert rc == 0, stderr
    content = active.read_text()
    assert _CHILD_B not in content


def test_append_child_rejects_invalid_ids(tmp_path):
    """Malformed ids are rejected (path-safety parity with isValidWorkflowId)."""
    active = tmp_path / "active.md"
    _write_active_registry(active, [
        {"id": _PARENT, "parent": None, "children": []},
    ])
    rc, _, stderr = _call_util(
        f"await appendChildToParentRegistry({json.dumps(str(active))}, "
        f"'../evil', {json.dumps(_CHILD_B)});\n",
        imports=["appendChildToParentRegistry"],
    )
    assert rc == 0, stderr
    content = active.read_text()
    assert _CHILD_B not in content


def test_remove_child_from_multi(tmp_path):
    """Remove one of several children; others remain, order preserved."""
    active = tmp_path / "active.md"
    _write_active_registry(active, [
        {"id": _PARENT, "parent": None, "children": [_CHILD_A, _CHILD_C]},
    ])
    rc, _, stderr = _call_util(
        f"await removeChildFromParentRegistry({json.dumps(str(active))}, "
        f"{json.dumps(_PARENT)}, {json.dumps(_CHILD_A)});\n",
        imports=["removeChildFromParentRegistry"],
    )
    assert rc == 0, stderr
    content = active.read_text()
    assert _CHILD_A not in content
    assert _CHILD_C in content


def test_remove_last_child_collapses_to_empty_literal(tmp_path):
    """Removing the last child leaves `children: []` inline literal."""
    active = tmp_path / "active.md"
    _write_active_registry(active, [
        {"id": _PARENT, "parent": None, "children": [_CHILD_B]},
    ])
    rc, _, stderr = _call_util(
        f"await removeChildFromParentRegistry({json.dumps(str(active))}, "
        f"{json.dumps(_PARENT)}, {json.dumps(_CHILD_B)});\n",
        imports=["removeChildFromParentRegistry"],
    )
    assert rc == 0, stderr
    content = active.read_text()
    assert _CHILD_B not in content
    assert "children: []" in content


def test_remove_child_noop_when_absent(tmp_path):
    """Removing a child that isn't in the list is a no-op."""
    active = tmp_path / "active.md"
    _write_active_registry(active, [
        {"id": _PARENT, "parent": None, "children": [_CHILD_A]},
    ])
    rc, _, stderr = _call_util(
        f"await removeChildFromParentRegistry({json.dumps(str(active))}, "
        f"{json.dumps(_PARENT)}, {json.dumps(_OTHER_CHILD)});\n",
        imports=["removeChildFromParentRegistry"],
    )
    assert rc == 0, stderr
    content = active.read_text()
    assert _CHILD_A in content


# --- SHARD_ID_REGEX / isValidShardId / resolveShardPath (B4.3) --------------


def test_shard_id_regex_accepts_deliverable_tokens():
    rc, stdout, stderr = _call_util(
        """
for (const id of ['deliverable-A', 'deliverable-B', 'deliverable-Z']) {
  console.log(id + ':' + isValidShardId(id));
}
""",
        imports=["isValidShardId"],
    )
    assert rc == 0, stderr
    lines = stdout.strip().split("\n")
    assert all(l.endswith(":true") for l in lines), lines


def test_shard_id_regex_rejects_malformed():
    rc, stdout, stderr = _call_util(
        """
for (const id of [
  'deliverable-a', 'deliverable-AA', 'deliverable-1', 'deliverable',
  'deliverable-', 'Deliverable-A', '../escape', 'deliverable-A/..',
]) {
  console.log(id + ':' + isValidShardId(id));
}
console.log('null:' + isValidShardId(null));
console.log('number:' + isValidShardId(42));
""",
        imports=["isValidShardId"],
    )
    assert rc == 0, stderr
    for line in stdout.strip().split("\n"):
        assert line.endswith(":false"), f"expected false, got: {line}"


def test_resolve_shard_path_returns_under_workflows(tmp_path):
    root_id = "start-20260424T120000Z-aaaaaa"
    rc, stdout, stderr = _call_util(
        f"console.log(resolveShardPath({json.dumps(str(tmp_path))}, "
        f"{json.dumps(root_id)}, 'deliverable-A'));",
        imports=["resolveShardPath"],
    )
    assert rc == 0, stderr
    expected = str(
        tmp_path / ".claude" / "omcc-dev" / "workflows" / root_id / "deliverable-A.md"
    )
    assert stdout.strip() == expected


def test_resolve_shard_path_rejects_invalid_root_id(tmp_path):
    rc, _, stderr = _call_util(
        f"""
try {{
  resolveShardPath({json.dumps(str(tmp_path))}, '../evil', 'deliverable-A');
  console.log('no-throw');
}} catch (e) {{ console.log('threw:' + e.message); }}
""",
        imports=["resolveShardPath"],
    )
    assert rc == 0, stderr


def test_resolve_shard_path_rejects_invalid_shard_id(tmp_path):
    root_id = "start-20260424T120000Z-aaaaaa"
    rc, stdout, stderr = _call_util(
        f"""
try {{
  resolveShardPath({json.dumps(str(tmp_path))}, {json.dumps(root_id)}, '../evil');
  console.log('no-throw');
}} catch (e) {{ console.log('threw:' + e.message); }}
""",
        imports=["resolveShardPath"],
    )
    assert rc == 0, stderr
    assert stdout.strip().startswith("threw:")


def test_move_workflow_to_archive_handles_flat(tmp_path):
    """Non-sharded workflow: moves the .md file; no shard dir to touch."""
    wf_id = "fix-20260424T120000Z-aaaaaa"
    workflows = tmp_path / ".claude" / "omcc-dev" / "workflows"
    archive = tmp_path / ".claude" / "omcc-dev" / "archive"
    workflows.mkdir(parents=True)
    archive.mkdir(parents=True)
    wf_path = workflows / f"{wf_id}.md"
    wf_path.write_text("---\nschema: 2\n---\n")
    rc, stdout, stderr = _call_util(
        f"console.log(await moveWorkflowToArchive({json.dumps(str(tmp_path))}, "
        f"{json.dumps(wf_id)}));",
        imports=["moveWorkflowToArchive"],
    )
    assert rc == 0, stderr
    assert stdout.strip() == "true"
    assert not wf_path.exists()
    assert (archive / f"{wf_id}.md").exists()


def test_move_workflow_to_archive_handles_sharded(tmp_path):
    """Sharded root: both the root .md AND the shard directory move."""
    root_id = "start-20260424T120000Z-aaaaaa"
    workflows = tmp_path / ".claude" / "omcc-dev" / "workflows"
    archive = tmp_path / ".claude" / "omcc-dev" / "archive"
    workflows.mkdir(parents=True)
    archive.mkdir(parents=True)
    root_path = workflows / f"{root_id}.md"
    root_path.write_text("---\nschema: 2\n---\n")
    shard_dir = workflows / root_id
    shard_dir.mkdir()
    (shard_dir / "deliverable-A.md").write_text("---\nshard_type: deliverable\n---\n")
    rc, stdout, stderr = _call_util(
        f"console.log(await moveWorkflowToArchive({json.dumps(str(tmp_path))}, "
        f"{json.dumps(root_id)}));",
        imports=["moveWorkflowToArchive"],
    )
    assert rc == 0, stderr
    assert stdout.strip() == "true"
    assert not root_path.exists()
    assert not shard_dir.exists()
    assert (archive / f"{root_id}.md").exists()
    assert (archive / root_id / "deliverable-A.md").exists()

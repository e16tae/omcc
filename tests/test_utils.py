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
    assert stdout.strip() == "1"


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


def test_sanitize_field_strips_control_chars_and_backticks():
    """sanitizeField inherits sanitize() stripping behavior."""
    rc, stdout, stderr = _call_util(
        r"""
console.log(sanitizeField('phase', 'helloworld`cmd`'));
""",
        imports=["sanitizeField"],
    )
    assert rc == 0, stderr
    assert stdout.strip() == "helloworldcmd"


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

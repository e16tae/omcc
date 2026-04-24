"""Tests for migrateSchema1to2 — the schema-1 → schema-2 content rewrite
used by `/omcc-dev:resume` when a legacy state file is detected.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
UTILS_URL = (ROOT / "plugins" / "omcc-dev" / "hooks" / "_utils.mjs").as_uri()

_NODE_AVAILABLE = shutil.which("node") is not None
pytestmark = pytest.mark.skipif(
    not _NODE_AVAILABLE,
    reason="node binary not available on PATH",
)


def _call_util(snippet, *, imports):
    names = ", ".join(imports)
    code = f"import {{ {names} }} from '{UTILS_URL}';\n{snippet}\n"
    proc = subprocess.run(
        ["node", "--input-type=module", "-e", code],
        capture_output=True, text=True, timeout=15,
    )
    return proc.returncode, proc.stdout, proc.stderr


_SCHEMA_1_WORKFLOW = """---
schema: 1
workflow_id: fix-20260401T100000Z-abcdef
workflow_type: fix
original_request: legacy task
started_at: 2026-04-01T10:00:00Z
updated_at: 2026-04-01T10:00:00Z
repo_root: /tmp/x
git_baseline:
  branch: main
  head: deadbeef
  status_digest: aabbcc
current_phase: investigate
next_action: continue
tasks: []
custom_user_field: preserved-verbatim
---

# Legacy body content
"""


def test_migrate_bumps_schema_literal():
    """Happy path: schema: 1 → schema: 2; body unchanged."""
    rc, stdout, stderr = _call_util(
        f"""
const content = {json.dumps(_SCHEMA_1_WORKFLOW)};
const migrated = migrateSchema1to2(content);
console.log(migrated);
""",
        imports=["migrateSchema1to2"],
    )
    assert rc == 0, stderr
    migrated = stdout.rstrip("\n") + "\n"  # node adds trailing newline
    assert "schema: 2" in migrated
    assert "schema: 1" not in migrated
    # body preserved
    assert "# Legacy body content" in migrated


def test_migrate_preserves_unknown_fields():
    """Unknown frontmatter fields (custom_user_field) survive migration."""
    rc, stdout, stderr = _call_util(
        f"""
const content = {json.dumps(_SCHEMA_1_WORKFLOW)};
const migrated = migrateSchema1to2(content);
console.log(migrated.includes('custom_user_field: preserved-verbatim'));
""",
        imports=["migrateSchema1to2"],
    )
    assert rc == 0, stderr
    assert stdout.strip() == "true"


def test_migrate_refreshes_updated_at():
    """updated_at is refreshed so the migration write is visible as an
    edit, not a silent content swap."""
    rc, stdout, stderr = _call_util(
        f"""
const content = {json.dumps(_SCHEMA_1_WORKFLOW)};
const migrated = migrateSchema1to2(content);
// Extract updated_at line
const m = migrated.match(/^updated_at:\\s*(\\S+)/m);
console.log(m ? m[1] : 'missing');
""",
        imports=["migrateSchema1to2"],
    )
    assert rc == 0, stderr
    ts = stdout.strip()
    assert ts != "2026-04-01T10:00:00Z", "updated_at must be refreshed"
    assert ts.endswith("Z")


def test_migrate_returns_null_on_already_schema2():
    """Schema-2 input is already-migrated; returns null so the caller
    does not double-bump."""
    already = _SCHEMA_1_WORKFLOW.replace("schema: 1", "schema: 2", 1)
    rc, stdout, stderr = _call_util(
        f"""
const content = {json.dumps(already)};
console.log(migrateSchema1to2(content) === null);
""",
        imports=["migrateSchema1to2"],
    )
    assert rc == 0, stderr
    assert stdout.strip() == "true"


def test_migrate_returns_null_on_corrupt_input():
    """Content without valid frontmatter returns null."""
    rc, stdout, stderr = _call_util(
        """
console.log(migrateSchema1to2('not yaml at all') === null);
""",
        imports=["migrateSchema1to2"],
    )
    assert rc == 0, stderr
    assert stdout.strip() == "true"


def test_migrate_works_on_active_registry_shape():
    """active.md shares the frontmatter parser and the migration is
    a label bump, so the same helper applies to the registry file."""
    registry_schema1 = """---
schema: 1
updated_at: 2026-04-01T10:00:00Z
active:
  - id: fix-20260401T100000Z-abcdef
    type: fix
    phase: investigate
    parent: null
    children: []
    originating_finding: null
---
"""
    rc, stdout, stderr = _call_util(
        f"""
const content = {json.dumps(registry_schema1)};
const migrated = migrateSchema1to2(content);
console.log(migrated.includes('schema: 2'));
console.log(migrated.includes('schema: 1'));
""",
        imports=["migrateSchema1to2"],
    )
    assert rc == 0, stderr
    lines = stdout.strip().split("\n")
    assert lines[0] == "true"
    assert lines[1] == "false"

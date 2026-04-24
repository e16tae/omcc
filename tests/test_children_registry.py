"""Integration tests for operational `children:` maintenance in the
active registry. Complements:
- tests/test_utils.py — unit tests for appendChildToParentRegistry /
  removeChildFromParentRegistry / serializeActiveRegistry.
- tests/test_hooks.py — Stop-hook auto-archive paths that exercise the
  same back-ref scrub end-to-end.

This file covers invariants and concurrency that span the helpers plus
the commands prose that calls them:
- the parent ↔ child two-way link (parent.children matches child.parent)
- concurrent child bootstraps under atomicModifyFile (lock discipline)
- contract: the commands files that should call the helpers mention them
"""
import json
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
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
    names = ", ".join(imports)
    code = f"import {{ {names} }} from '{UTILS_URL}';\n{snippet}\n"
    proc = subprocess.run(
        ["node", "--input-type=module", "-e", code],
        capture_output=True,
        text=True,
        timeout=20,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _seed_registry(path, parent_id):
    """Write an active.md with a single parent entry (children: [])."""
    content = (
        "---\n"
        "schema: 2\n"
        "updated_at: 2026-04-23T00:00:00Z\n"
        "active:\n"
        f"  - id: {parent_id}\n"
        "    type: start\n"
        "    phase: implement\n"
        "    parent: null\n"
        "    children: []\n"
        "    originating_finding: null\n"
        "---\n"
    )
    path.write_text(content)


def test_two_way_link_invariant_after_multiple_appends(tmp_path):
    """After appending several children, each child id appears exactly once
    in the parent's children list. Order is sorted-ascending."""
    active = tmp_path / "active.md"
    parent = "start-20260423T120000Z-aaaaaa"
    _seed_registry(active, parent)
    children = [
        "fix-20260423T120100Z-bbbbb1",
        "fix-20260423T120200Z-bbbbb2",
        "fix-20260423T120300Z-bbbbb3",
    ]
    for c in children:
        rc, _, stderr = _call_util(
            f"await appendChildToParentRegistry({json.dumps(str(active))}, "
            f"{json.dumps(parent)}, {json.dumps(c)});\n",
            imports=["appendChildToParentRegistry"],
        )
        assert rc == 0, stderr
    content = active.read_text()
    # each child id appears exactly once
    for c in children:
        assert content.count(c) == 1
    # children appear in sorted order (b1 < b2 < b3)
    positions = [content.index(c) for c in children]
    assert positions == sorted(positions)


def test_concurrent_appends_are_both_preserved(tmp_path):
    """Two node subprocesses appending distinct children concurrently:
    both children survive the race because atomicModifyFile serializes
    RMW inside `<active>.lock`."""
    active = tmp_path / "active.md"
    parent = "start-20260423T120000Z-aaaaaa"
    _seed_registry(active, parent)
    child_a = "fix-20260423T120100Z-aaaaa1"
    child_b = "fix-20260423T120200Z-bbbbb1"

    def _do_append(child_id):
        return _call_util(
            f"await appendChildToParentRegistry({json.dumps(str(active))}, "
            f"{json.dumps(parent)}, {json.dumps(child_id)});\n",
            imports=["appendChildToParentRegistry"],
        )

    with ThreadPoolExecutor(max_workers=2) as ex:
        fa = ex.submit(_do_append, child_a)
        fb = ex.submit(_do_append, child_b)
        rc_a, _, err_a = fa.result(timeout=30)
        rc_b, _, err_b = fb.result(timeout=30)
    assert rc_a == 0, err_a
    assert rc_b == 0, err_b
    content = active.read_text()
    assert child_a in content
    assert child_b in content


def test_append_then_remove_restores_empty_literal(tmp_path):
    """The lifecycle append → remove is reversible: the parent returns
    to `children: []` inline literal, not a dangling multi-line block."""
    active = tmp_path / "active.md"
    parent = "start-20260423T120000Z-aaaaaa"
    child = "fix-20260423T120100Z-bbbbbb"
    _seed_registry(active, parent)
    rc, _, stderr = _call_util(
        f"await appendChildToParentRegistry({json.dumps(str(active))}, "
        f"{json.dumps(parent)}, {json.dumps(child)});\n",
        imports=["appendChildToParentRegistry"],
    )
    assert rc == 0, stderr
    rc, _, stderr = _call_util(
        f"await removeChildFromParentRegistry({json.dumps(str(active))}, "
        f"{json.dumps(parent)}, {json.dumps(child)});\n",
        imports=["removeChildFromParentRegistry"],
    )
    assert rc == 0, stderr
    content = active.read_text()
    assert child not in content
    assert "children: []" in content


# --- contract: commands prose references the helpers ---------------------


def _read(path):
    return path.read_text()


def test_start_command_references_appendChildToParentRegistry():
    start = ROOT / "plugins" / "omcc-dev" / "commands" / "start.md"
    assert "appendChildToParentRegistry" in _read(start), (
        "commands/start.md must invoke appendChildToParentRegistry on "
        "child bootstrap per schema-2 continuity-protocol.md Cross-workflow "
        "Handoff / Active registry maintenance"
    )


def test_fix_command_references_appendChildToParentRegistry():
    fix = ROOT / "plugins" / "omcc-dev" / "commands" / "fix.md"
    assert "appendChildToParentRegistry" in _read(fix), (
        "commands/fix.md must invoke appendChildToParentRegistry on child bootstrap"
    )


def test_resume_command_references_removeChildFromParentRegistry_on_archive_paths():
    """Each archival path in resume.md (corrupt-state archive, drift
    archive, manual archive) must mention removeChildFromParentRegistry
    so the back-pointer scrub lands outside the Stop hook as well."""
    resume = ROOT / "plugins" / "omcc-dev" / "commands" / "resume.md"
    content = _read(resume)
    # Expect at least 3 references (Steps 2, 4, 7)
    assert content.count("removeChildFromParentRegistry") >= 3, (
        "resume.md must call removeChildFromParentRegistry on the three "
        "non-Stop archival paths (corrupt / drift / manual)"
    )

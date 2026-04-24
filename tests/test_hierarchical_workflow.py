"""End-to-end integration tests for hierarchical (sharded) workflows.

Complements:
- tests/test_utils.py — unit tests for resolveShardPath, SHARD_ID_REGEX,
  moveWorkflowToArchive's flat vs sharded branches.
- tests/test_children_registry.py — active-registry children ops.
- tests/test_hooks.py — hook-level integration covering the 2-entry
  parent/child cases.

This file focuses on the root+shard directory atomic archive path via
the Stop hook, plus the path-safety posture exposed by resolveShardPath.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HOOKS_DIR = ROOT / "plugins" / "omcc-dev" / "hooks"
UTILS_URL = (HOOKS_DIR / "_utils.mjs").as_uri()

_NODE_AVAILABLE = shutil.which("node") is not None
pytestmark = pytest.mark.skipif(
    not _NODE_AVAILABLE,
    reason="node binary not available on PATH",
)


def _run_hook(script_name, stdin_obj, cwd):
    script = HOOKS_DIR / script_name
    proc = subprocess.run(
        ["node", str(script)],
        input=json.dumps(stdin_obj) if stdin_obj else "",
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=15,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _init_cwd(tmp_path):
    (tmp_path / ".claude" / "omcc-dev" / "workflows").mkdir(parents=True)
    (tmp_path / ".claude" / "omcc-dev" / "archive").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=str(tmp_path), check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=str(tmp_path), check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "test"], cwd=str(tmp_path), check=True
    )
    (tmp_path / "seed.txt").write_text("seed\n")
    subprocess.run(["git", "add", "-A"], cwd=str(tmp_path), check=True)
    subprocess.run(
        ["git", "commit", "-m", "seed", "-q"], cwd=str(tmp_path), check=True
    )
    return tmp_path


def _current_head(cwd):
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(cwd), capture_output=True, text=True, check=True,
    ).stdout.strip()


def _write_root_and_shards(cwd, root_id, phase, deliverable_ids):
    """Create a sharded root layout: root .md + a directory with one
    shard file per deliverable id."""
    head = _current_head(cwd)
    root_path = cwd / ".claude" / "omcc-dev" / "workflows" / f"{root_id}.md"
    deliverables_block = ""
    if deliverable_ids:
        deliverables_block = "plan:\n  deliverables:\n"
        for did in deliverable_ids:
            deliverables_block += (
                f"    - id: {did}\n"
                f"      shard_path: deliverable-{did}.md\n"
                "      status: completed\n"
            )
    root_path.write_text(
        "---\n"
        "schema: 2\n"
        f"workflow_id: {root_id}\n"
        "workflow_type: start\n"
        "original_request: test\n"
        "started_at: 2026-04-24T00:00:00Z\n"
        "updated_at: 2026-04-24T00:00:00Z\n"
        f"repo_root: {cwd}\n"
        "git_baseline:\n"
        "  branch: main\n"
        f"  head: {head}\n"
        "  status_digest: aabbcc\n"
        f"current_phase: {phase}\n"
        "next_action: archive\n"
        "tasks: []\n"
        "task_profile:\n"
        "  scope: x\n"
        "  complexity: low\n"
        "  ensemble_affinity: LOW\n"
        f"{deliverables_block}"
        "---\n"
    )
    shard_dir = cwd / ".claude" / "omcc-dev" / "workflows" / root_id
    shard_dir.mkdir()
    for did in deliverable_ids:
        (shard_dir / f"deliverable-{did}.md").write_text(
            "---\n"
            "schema: 2\n"
            "shard_type: deliverable\n"
            f"root_workflow: {root_id}\n"
            f"deliverable_id: {did}\n"
            "started_at: 2026-04-24T00:00:00Z\n"
            "updated_at: 2026-04-24T00:00:00Z\n"
            "current_phase: commit-complete\n"
            "next_action: archive\n"
            "tasks: []\n"
            "---\n"
        )
    return root_path, shard_dir


def _write_active_root_only(cwd, root_id):
    """Active registry carries only the root — shards are not separate
    registry entries per the hierarchical layout."""
    active = cwd / ".claude" / "omcc-dev" / "active.md"
    active.write_text(
        "---\n"
        "schema: 2\n"
        "updated_at: 2026-04-24T00:00:00Z\n"
        "active:\n"
        f"  - id: {root_id}\n"
        "    type: start\n"
        "    phase: commit-complete\n"
        "    parent: null\n"
        "    children: []\n"
        "    originating_finding: null\n"
        "---\n"
    )


def test_sharded_root_archive_moves_file_and_directory_atomically(tmp_path):
    """Stop hook auto-archives a sharded root: both the .md file and
    the shard directory move into archive/ in one operation."""
    cwd = _init_cwd(tmp_path)
    root_id = "start-20260424T120000Z-aaaaaa"
    root_path, shard_dir = _write_root_and_shards(
        cwd, root_id, "commit-complete", ["A", "B"]
    )
    _write_active_root_only(cwd, root_id)
    # feat-subject commit so A2 + A3 pass for start parent
    (cwd / "feat.txt").write_text("x")
    subprocess.run(["git", "add", "-A"], cwd=str(cwd), check=True)
    subprocess.run(
        ["git", "commit", "-m", "feat(test): sharded thing", "-q"],
        cwd=str(cwd), check=True,
    )
    rc, _, _ = _run_hook("stop.mjs", {"cwd": str(cwd)}, cwd)
    assert rc == 0
    # pre-archive locations cleared
    assert not root_path.exists()
    assert not shard_dir.exists()
    # post-archive locations populated
    archive_root = cwd / ".claude" / "omcc-dev" / "archive" / f"{root_id}.md"
    archive_dir = cwd / ".claude" / "omcc-dev" / "archive" / root_id
    assert archive_root.exists()
    assert archive_dir.is_dir()
    assert (archive_dir / "deliverable-A.md").exists()
    assert (archive_dir / "deliverable-B.md").exists()
    # no journal-incomplete marker — clean success
    assert not (tmp_path / ".claude" / "omcc-dev" / "workflows"
                / f"{root_id}.journal-incomplete").exists()


def test_non_sharded_root_archive_is_unaffected_by_new_helper(tmp_path):
    """moveWorkflowToArchive must handle flat (non-sharded) workflows
    identically to the pre-B4 behavior — no shard dir to touch."""
    cwd = _init_cwd(tmp_path)
    flat_id = "fix-20260424T120000Z-ccccc0"
    flat_path = cwd / ".claude" / "omcc-dev" / "workflows" / f"{flat_id}.md"
    head = _current_head(cwd)
    flat_path.write_text(
        "---\n"
        "schema: 2\n"
        f"workflow_id: {flat_id}\n"
        "workflow_type: fix\n"
        "original_request: test\n"
        "started_at: 2026-04-24T00:00:00Z\n"
        "updated_at: 2026-04-24T00:00:00Z\n"
        f"repo_root: {cwd}\n"
        "git_baseline:\n"
        "  branch: main\n"
        f"  head: {head}\n"
        "  status_digest: aabbcc\n"
        "current_phase: commit-complete\n"
        "next_action: archive\n"
        "tasks: []\n"
        "---\n"
    )
    active = cwd / ".claude" / "omcc-dev" / "active.md"
    active.write_text(
        "---\n"
        "schema: 2\n"
        "updated_at: 2026-04-24T00:00:00Z\n"
        "active:\n"
        f"  - id: {flat_id}\n"
        "    type: fix\n"
        "    phase: commit-complete\n"
        "    parent: null\n"
        "    children: []\n"
        "    originating_finding: null\n"
        "---\n"
    )
    (cwd / "fix.txt").write_text("x")
    subprocess.run(["git", "add", "-A"], cwd=str(cwd), check=True)
    subprocess.run(
        ["git", "commit", "-m", "fix(test): thing", "-q"],
        cwd=str(cwd), check=True,
    )
    rc, _, _ = _run_hook("stop.mjs", {"cwd": str(cwd)}, cwd)
    assert rc == 0
    assert not flat_path.exists()
    assert (cwd / ".claude" / "omcc-dev" / "archive" / f"{flat_id}.md").exists()
    # No spurious shard directory was created or moved
    assert not (cwd / ".claude" / "omcc-dev" / "archive" / flat_id).exists()


def test_shard_id_regex_blocks_path_escape_via_move():
    """resolveShardPath rejects ids that would escape the root
    directory — verified via node import call."""
    code = (
        f"import {{ resolveShardPath }} from '{UTILS_URL}';\n"
        "try {\n"
        "  resolveShardPath('/tmp', 'start-20260424T120000Z-aaaaaa', "
        "'../deliverable-A');\n"
        "  console.log('no-throw');\n"
        "} catch (e) { console.log('threw'); }\n"
    )
    proc = subprocess.run(
        ["node", "--input-type=module", "-e", code],
        capture_output=True, text=True, timeout=10,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "threw"

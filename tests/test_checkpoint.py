"""Hook-level integration tests for /omcc-dev:checkpoint's consumers.

The checkpoint command itself is agent-prose (commands/checkpoint.md)
and not directly exercised here. These tests verify that once the
agent has written a `latest_checkpoint: {at, summary}` map into a
workflow's frontmatter, the two consumer hooks observe it correctly:

- SessionStart injects `checkpoint="<summary>"` into the summary line.
- PreCompact no-ops its mechanical snapshot for 60s after a fresh
  checkpoint, and resumes normal snapshots after the window.
"""
import json
import shutil
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HOOKS_DIR = ROOT / "plugins" / "omcc-dev" / "hooks"

_NODE_AVAILABLE = shutil.which("node") is not None
pytestmark = pytest.mark.skipif(
    not _NODE_AVAILABLE,
    reason="node binary not available on PATH",
)


def _run_hook(script, stdin_obj, cwd):
    proc = subprocess.run(
        ["node", str(HOOKS_DIR / script)],
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


def _head(cwd):
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(cwd), capture_output=True, text=True, check=True,
    ).stdout.strip()


def _write_workflow_with_checkpoint(cwd, wf_id, checkpoint_at, summary):
    """Write a workflow file with a latest_checkpoint map.

    checkpoint_at: ISO-8601 UTC string, or None (omits the block entirely).
    """
    path = cwd / ".claude" / "omcc-dev" / "workflows" / f"{wf_id}.md"
    head = _head(cwd)
    checkpoint_block = ""
    if checkpoint_at is not None:
        checkpoint_block = (
            "latest_checkpoint:\n"
            f"  at: {checkpoint_at}\n"
            f"  summary: {summary}\n"
        )
    path.write_text(
        "---\n"
        "schema: 2\n"
        f"workflow_id: {wf_id}\n"
        "workflow_type: fix\n"
        "original_request: test\n"
        "started_at: 2026-04-24T00:00:00Z\n"
        "updated_at: 2026-04-24T00:00:00Z\n"
        f"repo_root: {cwd}\n"
        "git_baseline:\n"
        "  branch: main\n"
        f"  head: {head}\n"
        "  status_digest: aabbcc\n"
        "current_phase: investigate\n"
        "next_action: working\n"
        "tasks: []\n"
        "task_profile:\n"
        "  scope: x\n"
        "  complexity: low\n"
        "  ensemble_affinity: LOW\n"
        f"{checkpoint_block}"
        "---\n"
    )
    return path


def _write_active(cwd, wf_id):
    active = cwd / ".claude" / "omcc-dev" / "active.md"
    active.write_text(
        "---\n"
        "schema: 2\n"
        "updated_at: 2026-04-24T00:00:00Z\n"
        "active:\n"
        f"  - id: {wf_id}\n"
        "    type: fix\n"
        "    phase: investigate\n"
        "    parent: null\n"
        "    children: []\n"
        "    originating_finding: null\n"
        "---\n"
    )


def test_session_start_emits_checkpoint_summary(tmp_path):
    """When latest_checkpoint.summary is present it shows up in the
    SessionStart summary line as checkpoint="...". """
    cwd = _init_cwd(tmp_path)
    wf_id = "fix-20260424T120000Z-aaaaaa"
    _write_workflow_with_checkpoint(
        cwd, wf_id, "2026-04-24T12:34:56Z", "finished B4 helpers, tests pending"
    )
    _write_active(cwd, wf_id)
    rc, out, _ = _run_hook(
        "session-start.mjs", {"cwd": str(cwd), "source": "compact"}, cwd
    )
    assert rc == 0
    assert 'checkpoint="finished B4 helpers, tests pending"' in out


def test_session_start_omits_checkpoint_when_absent(tmp_path):
    """Without a latest_checkpoint map the summary line omits the
    checkpoint= token entirely (backward-compatible format)."""
    cwd = _init_cwd(tmp_path)
    wf_id = "fix-20260424T120000Z-bbbbbb"
    _write_workflow_with_checkpoint(cwd, wf_id, None, "")
    _write_active(cwd, wf_id)
    rc, out, _ = _run_hook(
        "session-start.mjs", {"cwd": str(cwd), "source": "compact"}, cwd
    )
    assert rc == 0
    assert wf_id in out
    assert "checkpoint=" not in out


def test_pre_compact_skips_snapshot_on_fresh_checkpoint(tmp_path):
    """A latest_checkpoint.at newer than 60s ago suppresses the
    mechanical snapshot for that cycle."""
    cwd = _init_cwd(tmp_path)
    wf_id = "fix-20260424T120000Z-cccccc"
    # "fresh" — 10 seconds ago
    fresh_at = (datetime.now(timezone.utc) - timedelta(seconds=10)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    wf_path = _write_workflow_with_checkpoint(cwd, wf_id, fresh_at, "sync point")
    _write_active(cwd, wf_id)
    original = wf_path.read_text()
    rc, _, _ = _run_hook("pre-compact.mjs", {"cwd": str(cwd)}, cwd)
    assert rc == 0
    assert wf_path.read_text() == original, (
        "PreCompact must not append a snapshot while the user's "
        "checkpoint is still fresh"
    )


def test_pre_compact_resumes_snapshots_after_window(tmp_path):
    """A stale latest_checkpoint.at (>60s ago) does not suppress the
    mechanical snapshot — behavior falls back to the pre-B5 path."""
    cwd = _init_cwd(tmp_path)
    wf_id = "fix-20260424T120000Z-dddddd"
    # "stale" — 120 seconds ago
    stale_at = (datetime.now(timezone.utc) - timedelta(seconds=120)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    wf_path = _write_workflow_with_checkpoint(cwd, wf_id, stale_at, "old sync")
    _write_active(cwd, wf_id)
    rc, _, _ = _run_hook("pre-compact.mjs", {"cwd": str(cwd)}, cwd)
    assert rc == 0
    assert "<!-- pre-compact snapshot -->" in wf_path.read_text(), (
        "mechanical snapshot should have been appended outside the 60s window"
    )


def test_pre_compact_ignores_invalid_checkpoint_timestamp(tmp_path):
    """An unparseable or missing checkpoint `at` is treated as absent —
    the hook falls through to its normal snapshot logic."""
    cwd = _init_cwd(tmp_path)
    wf_id = "fix-20260424T120000Z-eeeeee"
    wf_path = _write_workflow_with_checkpoint(
        cwd, wf_id, "not-a-timestamp", "garbage"
    )
    _write_active(cwd, wf_id)
    rc, _, _ = _run_hook("pre-compact.mjs", {"cwd": str(cwd)}, cwd)
    assert rc == 0
    assert "<!-- pre-compact snapshot -->" in wf_path.read_text()


def test_checkpoint_command_file_exists_and_has_frontmatter():
    """Contract: commands/checkpoint.md is registered as a slash command."""
    cmd = ROOT / "plugins" / "omcc-dev" / "commands" / "checkpoint.md"
    assert cmd.exists()
    text = cmd.read_text()
    # argument-hint + description frontmatter
    assert "description:" in text
    assert "argument-hint:" in text
    # prose calls the helpers we actually ship
    assert "atomicModifyFile" in text
    assert "sanitizeField" in text

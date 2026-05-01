"""Runtime tests for omcc-dev continuity hooks.

Drives each hook via node + stdin JSON and asserts expected behavior for
missing / corrupt / stale / active workflow states.

Requires `node` on PATH. Tests that need git create a local repo in
a tmp_path; no network access, no dependence on the caller's branch.
"""
import json
import shutil
import subprocess
from pathlib import Path
from textwrap import dedent

import pytest

ROOT = Path(__file__).resolve().parent.parent
HOOKS_DIR = ROOT / "plugins" / "omcc-dev" / "hooks"

_NODE_AVAILABLE = shutil.which("node") is not None
pytestmark = pytest.mark.skipif(
    not _NODE_AVAILABLE,
    reason="node binary not available on PATH",
)


def _run_hook(script_name, stdin_obj, cwd):
    """Invoke a hook via node with stdin JSON. Returns (rc, stdout, stderr)."""
    script = HOOKS_DIR / script_name
    assert script.exists(), f"hook script missing: {script}"
    proc = subprocess.run(
        ["node", str(script)],
        input=json.dumps(stdin_obj) if stdin_obj is not None else "",
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=15,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _init_cwd(tmp_path):
    """Create the cwd filesystem layout + a minimal git repo."""
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


def _write_active(cwd, active_list, schema=2):
    """Write the active registry with the given list of workflow entries."""
    path = cwd / ".claude" / "omcc-dev" / "active.md"
    entry_blocks = []
    for e in active_list:
        lines = [f"  - id: {e['id']}"]
        for k in ("type", "phase", "parent", "originating_finding"):
            if k in e:
                val = e[k] if e[k] is not None else "null"
                lines.append(f"    {k}: {val}")
        if "children" in e:
            if e["children"]:
                lines.append("    children:")
                for c in e["children"]:
                    lines.append(f"      - {c}")
            else:
                lines.append("    children: []")
        entry_blocks.append("\n".join(lines))
    header = dedent(f"""\
        ---
        schema: {schema}
        updated_at: 2026-04-22T00:00:00Z
        active:
        """)
    body = header
    if entry_blocks:
        body += "\n".join(entry_blocks) + "\n"
    body += "---\n"
    path.write_text(body)


def _current_head(cwd):
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(cwd), capture_output=True, text=True, check=True,
    ).stdout.strip()


def _write_workflow(cwd, workflow_id, phase, next_action, workflow_type=None,
                    baseline_head=None, body_extra="", schema=2):
    wtype = workflow_type or workflow_id.split("-")[0]
    bh = baseline_head or _current_head(cwd)
    path = cwd / ".claude" / "omcc-dev" / "workflows" / f"{workflow_id}.md"
    # Build frontmatter and body explicitly to avoid dedent interactions with
    # multi-line body_extra (which can include unindented content that would
    # force dedent to remove zero columns and leave the frontmatter indented).
    frontmatter = (
        "---\n"
        f"schema: {schema}\n"
        f"workflow_id: {workflow_id}\n"
        f"workflow_type: {wtype}\n"
        "original_request: test\n"
        "started_at: 2026-04-22T00:00:00Z\n"
        "updated_at: 2026-04-22T00:00:00Z\n"
        f"repo_root: {cwd}\n"
        "git_baseline:\n"
        "  branch: main\n"
        f"  head: {bh}\n"
        "  status_digest: aabbcc\n"
        f"current_phase: {phase}\n"
        f"next_action: {next_action}\n"
        "tasks: []\n"
        "task_profile:\n"
        "  scope: x\n"
        "  complexity: low\n"
        "  ensemble_affinity: LOW\n"
        "---\n"
    )
    content = frontmatter + f"\n# {workflow_id}\n" + body_extra + "\n"
    path.write_text(content)
    return path


# ---------------------------------------------------------------------------
# SessionStart
# ---------------------------------------------------------------------------


class TestSessionStart:
    def test_missing_registry_silent(self, tmp_path):
        _init_cwd(tmp_path)
        rc, out, err = _run_hook(
            "session-start.mjs", {"cwd": str(tmp_path), "source": "compact"}, tmp_path
        )
        assert rc == 0
        assert out == ""

    def test_empty_active_list_silent(self, tmp_path):
        _init_cwd(tmp_path)
        _write_active(tmp_path, [])
        rc, out, _ = _run_hook(
            "session-start.mjs", {"cwd": str(tmp_path), "source": "compact"}, tmp_path
        )
        assert rc == 0
        assert out == ""

    def test_active_workflow_is_summarized(self, tmp_path):
        cwd = _init_cwd(tmp_path)
        wf_id = "fix-20260422T120000Z-abcdef"
        _write_workflow(cwd, wf_id, "investigate", "collect hypotheses", "fix")
        _write_active(cwd, [{"id": wf_id, "type": "fix", "phase": "investigate",
                             "parent": None, "children": []}])
        rc, out, _ = _run_hook(
            "session-start.mjs", {"cwd": str(cwd), "source": "compact"}, cwd
        )
        assert rc == 0
        assert "Active omcc-dev workflow(s):" in out
        assert wf_id in out
        assert "phase=investigate" in out
        assert "/omcc-dev:resume" in out

    def test_invalid_workflow_id_is_skipped(self, tmp_path):
        cwd = _init_cwd(tmp_path)
        _write_active(cwd, [{"id": "../../etc/passwd", "type": "fix", "phase": "x",
                             "parent": None, "children": []}])
        rc, out, _ = _run_hook(
            "session-start.mjs", {"cwd": str(cwd), "source": "compact"}, cwd
        )
        assert rc == 0
        # No valid entries survive regex check → silent
        assert out == ""

    def test_backticks_cause_row_rejection(self, tmp_path):
        """Schema-2 Backtick rule: a field value containing a backtick
        rejects the entire entry (not the character). One-line stderr
        diagnostic identifies the workflow and the field. No stripped
        fragment is ever echoed to stdout."""
        cwd = _init_cwd(tmp_path)
        wf_id = "start-20260422T120000Z-111111"
        _write_workflow(cwd, wf_id, "brainstorm", "try `whoami`", "start")
        _write_active(cwd, [{"id": wf_id, "type": "start", "phase": "brainstorm",
                             "parent": None, "children": []}])
        rc, out, err = _run_hook(
            "session-start.mjs", {"cwd": str(cwd), "source": "compact"}, cwd
        )
        assert rc == 0
        # No stripped fragment — whole entry dropped
        assert wf_id not in out
        assert "`" not in out
        # stderr identifies the rejected entry; summary counts skipped
        assert wf_id in err
        assert "contains backticks" in err
        assert "next_action" in err or "phase" in err
        # When every entry is rejected, stdout is empty and a one-line
        # skip-count summary lands on stderr
        assert out == ""
        assert "entries skipped (backtick)" in err

    def test_corrupt_workflow_file_skipped(self, tmp_path):
        cwd = _init_cwd(tmp_path)
        wf_id = "fix-20260422T120000Z-abcdef"
        # Write a file with no frontmatter
        (cwd / ".claude" / "omcc-dev" / "workflows" / f"{wf_id}.md").write_text(
            "not yaml\n"
        )
        _write_active(cwd, [{"id": wf_id, "type": "fix", "phase": "investigate",
                             "parent": None, "children": []}])
        rc, out, _ = _run_hook(
            "session-start.mjs", {"cwd": str(cwd), "source": "compact"}, cwd
        )
        assert rc == 0
        # Corrupt file handled gracefully; workflow id still appears but with default phase
        # (or is skipped depending on parser robustness — either is acceptable).

    def test_legacy_schema1_workflow_is_skipped_with_diagnostic(self, tmp_path):
        """Legacy schema-1 files are silently skipped by SessionStart; the
        hook writes a stderr diagnostic suggesting /omcc-dev:resume migration
        rather than echoing a potentially mis-interpreted summary back into
        Claude's context."""
        cwd = _init_cwd(tmp_path)
        wf_id = "fix-20260422T120000Z-abcdef"
        _write_workflow(cwd, wf_id, "investigate", "do thing", "fix", schema=1)
        _write_active(cwd, [{"id": wf_id, "type": "fix", "phase": "investigate",
                             "parent": None, "children": []}])
        rc, out, err = _run_hook(
            "session-start.mjs", {"cwd": str(cwd), "source": "compact"}, cwd
        )
        assert rc == 0
        # entry is skipped — no output line at all when it's the only workflow
        assert wf_id not in out
        assert out == ""
        # diagnostic on stderr points user at the migration path
        assert "legacy schema 1" in err
        assert "/omcc-dev:resume" in err


# ---------------------------------------------------------------------------
# PreCompact
# ---------------------------------------------------------------------------


class TestPreCompact:
    def test_missing_registry_exit0(self, tmp_path):
        _init_cwd(tmp_path)
        rc, _, _ = _run_hook("pre-compact.mjs", {"cwd": str(tmp_path)}, tmp_path)
        assert rc == 0

    def test_snapshot_appended_to_workflow(self, tmp_path):
        cwd = _init_cwd(tmp_path)
        wf_id = "audit-20260422T120000Z-abcdef"
        wf_path = _write_workflow(cwd, wf_id, "scan", "collect", "audit")
        _write_active(cwd, [{"id": wf_id, "type": "audit", "phase": "scan",
                             "parent": None, "children": []}])
        rc, _, _ = _run_hook("pre-compact.mjs", {"cwd": str(cwd)}, cwd)
        assert rc == 0
        body = wf_path.read_text()
        assert "<!-- pre-compact snapshot -->" in body
        assert "branch: " in body
        assert "head: " in body

    def test_idempotent_within_60s(self, tmp_path):
        cwd = _init_cwd(tmp_path)
        wf_id = "start-20260422T120000Z-222222"
        wf_path = _write_workflow(cwd, wf_id, "brainstorm", "next", "start")
        _write_active(cwd, [{"id": wf_id, "type": "start", "phase": "brainstorm",
                             "parent": None, "children": []}])
        _run_hook("pre-compact.mjs", {"cwd": str(cwd)}, cwd)
        _run_hook("pre-compact.mjs", {"cwd": str(cwd)}, cwd)
        body = wf_path.read_text()
        assert body.count("<!-- pre-compact snapshot -->") == 1, (
            "second invocation within 60s must be idempotent"
        )

    def test_sensitive_filenames_filtered(self, tmp_path):
        cwd = _init_cwd(tmp_path)
        # Add an .env.local untracked file — it should not appear in the snapshot
        (cwd / ".env.local").write_text("SECRET=abc\n")
        wf_id = "fix-20260422T120000Z-abcdef"
        wf_path = _write_workflow(cwd, wf_id, "investigate", "next", "fix")
        _write_active(cwd, [{"id": wf_id, "type": "fix", "phase": "investigate",
                             "parent": None, "children": []}])
        _run_hook("pre-compact.mjs", {"cwd": str(cwd)}, cwd)
        body = wf_path.read_text()
        assert ".env.local" not in body


# ---------------------------------------------------------------------------
# Stop
# ---------------------------------------------------------------------------


class TestStop:
    def test_stop_hook_active_exits_immediately(self, tmp_path):
        _init_cwd(tmp_path)
        rc, _, _ = _run_hook(
            "stop.mjs",
            {"cwd": str(tmp_path), "stop_hook_active": True},
            tmp_path,
        )
        assert rc == 0

    def test_missing_fields_non_blocking_reminder(self, tmp_path):
        cwd = _init_cwd(tmp_path)
        wf_id = "fix-20260422T120000Z-abcdef"
        _write_workflow(cwd, wf_id, "", "", "fix")
        _write_active(cwd, [{"id": wf_id, "type": "fix", "phase": "investigate",
                             "parent": None, "children": []}])
        rc, _, err = _run_hook("stop.mjs", {"cwd": str(cwd)}, cwd)
        assert rc == 0
        assert "missing" in err.lower()

    def test_non_terminal_no_archive(self, tmp_path):
        cwd = _init_cwd(tmp_path)
        wf_id = "fix-20260422T120000Z-abcdef"
        wf_path = _write_workflow(cwd, wf_id, "investigate", "collect", "fix")
        _write_active(cwd, [{"id": wf_id, "type": "fix", "phase": "investigate",
                             "parent": None, "children": []}])
        rc, _, _ = _run_hook("stop.mjs", {"cwd": str(cwd)}, cwd)
        assert rc == 0
        assert wf_path.exists()

    def test_audit_summary_complete_archives(self, tmp_path):
        cwd = _init_cwd(tmp_path)
        wf_id = "audit-20260422T120000Z-abcdef"
        wf_path = _write_workflow(cwd, wf_id, "summary-complete", "archive", "audit")
        _write_active(cwd, [{"id": wf_id, "type": "audit", "phase": "summary-complete",
                             "parent": None, "children": []}])
        rc, _, _ = _run_hook("stop.mjs", {"cwd": str(cwd)}, cwd)
        assert rc == 0
        archive_path = cwd / ".claude" / "omcc-dev" / "archive" / f"{wf_id}.md"
        assert archive_path.exists(), "audit summary-complete must auto-archive"
        assert not wf_path.exists()

    def test_fix_requires_commit_subject(self, tmp_path):
        cwd = _init_cwd(tmp_path)
        wf_id = "fix-20260422T120000Z-abcdef"
        baseline = _current_head(cwd)
        wf_path = _write_workflow(
            cwd, wf_id, "commit-complete", "archive", "fix",
            baseline_head=baseline,
        )
        _write_active(cwd, [{"id": wf_id, "type": "fix", "phase": "commit-complete",
                             "parent": None, "children": []}])
        _run_hook("stop.mjs", {"cwd": str(cwd)}, cwd)
        assert wf_path.exists(), "no progress → no archive"
        # Add an unrelated commit (wrong subject) — still no archive
        (cwd / "other.txt").write_text("x")
        subprocess.run(["git", "add", "-A"], cwd=str(cwd), check=True)
        subprocess.run(
            ["git", "commit", "-m", "docs: readme tweak", "-q"],
            cwd=str(cwd), check=True,
        )
        _run_hook("stop.mjs", {"cwd": str(cwd)}, cwd)
        assert wf_path.exists(), "non-matching commit subject → no archive"
        # Add a matching fix(scope): commit — now archives
        (cwd / "fix.txt").write_text("x")
        subprocess.run(["git", "add", "-A"], cwd=str(cwd), check=True)
        subprocess.run(
            ["git", "commit", "-m", "fix(test): resolve issue", "-q"],
            cwd=str(cwd), check=True,
        )
        _run_hook("stop.mjs", {"cwd": str(cwd)}, cwd)
        archive_path = cwd / ".claude" / "omcc-dev" / "archive" / f"{wf_id}.md"
        assert archive_path.exists(), "matching commit → archive"

    def test_active_child_blocks_parent_archive(self, tmp_path):
        cwd = _init_cwd(tmp_path)
        parent_id = "audit-20260422T120000Z-000001"
        child_id = "fix-20260422T130000Z-000002"
        parent_path = _write_workflow(cwd, parent_id, "summary-complete", "archive", "audit")
        _write_workflow(cwd, child_id, "fix-and-verify", "work", "fix")
        _write_active(cwd, [
            {"id": parent_id, "type": "audit", "phase": "summary-complete",
             "parent": None, "children": [child_id]},
            {"id": child_id, "type": "fix", "phase": "fix-and-verify",
             "parent": parent_id, "children": []},
        ])
        _run_hook("stop.mjs", {"cwd": str(cwd)}, cwd)
        assert parent_path.exists(), "A4 must block parent archive while child active"

    def test_non_audit_parent_a4_blocks_archive(self, tmp_path):
        """A4 transitive closure is parent-type-agnostic: a non-audit
        parent (start) is also blocked from archive while a child (fix)
        is still active, matching B3 parent generalization."""
        cwd = _init_cwd(tmp_path)
        parent_id = "start-20260424T120000Z-aaaaaa"
        child_id = "fix-20260424T120100Z-bbbbbb"
        parent_path = _write_workflow(
            cwd, parent_id, "commit-complete", "archive", "start"
        )
        _write_workflow(cwd, child_id, "fix-and-verify", "work", "fix")
        _write_active(cwd, [
            {"id": parent_id, "type": "start", "phase": "commit-complete",
             "parent": None, "children": [child_id]},
            {"id": child_id, "type": "fix", "phase": "fix-and-verify",
             "parent": parent_id, "children": []},
        ])
        # feat-subject commit so the start parent would satisfy A2+A3 on its own
        (cwd / "feat.txt").write_text("x")
        subprocess.run(["git", "add", "-A"], cwd=str(cwd), check=True)
        subprocess.run(
            ["git", "commit", "-m", "feat(test): new thing", "-q"],
            cwd=str(cwd), check=True,
        )
        _run_hook("stop.mjs", {"cwd": str(cwd)}, cwd)
        assert parent_path.exists(), (
            "A4 must block non-audit (start) parent archive while a "
            "fix child is still active"
        )

    def test_non_audit_parent_archive_scrubs_children_backref(self, tmp_path):
        """When a fix child terminates, its id is scrubbed from its
        non-audit (start) parent's children list, same as audit-parent
        case but via the generalized path."""
        cwd = _init_cwd(tmp_path)
        parent_id = "start-20260424T120000Z-aaaaaa"
        child_id = "fix-20260424T120100Z-bbbbbb"
        # parent non-terminal so it doesn't auto-archive
        _write_workflow(cwd, parent_id, "implement", "work", "start")
        _write_workflow(cwd, child_id, "commit-complete", "archive", "fix")
        _write_active(cwd, [
            {"id": parent_id, "type": "start", "phase": "implement",
             "parent": None, "children": [child_id]},
            {"id": child_id, "type": "fix", "phase": "commit-complete",
             "parent": parent_id, "children": []},
        ])
        (cwd / "fix.txt").write_text("x")
        subprocess.run(["git", "add", "-A"], cwd=str(cwd), check=True)
        subprocess.run(
            ["git", "commit", "-m", "fix(test): resolve", "-q"],
            cwd=str(cwd), check=True,
        )
        _run_hook("stop.mjs", {"cwd": str(cwd)}, cwd)
        assert (cwd / ".claude" / "omcc-dev" / "archive"
                / f"{child_id}.md").exists()
        registry = (cwd / ".claude" / "omcc-dev" / "active.md").read_text()
        assert parent_id in registry
        assert child_id not in registry

    def test_auto_archive_cleans_parent_children_backref(self, tmp_path):
        """When a child workflow auto-archives, its id is removed from the
        parent entry's `children` list — not just from the registry's
        entry list."""
        cwd = _init_cwd(tmp_path)
        parent_id = "audit-20260423T120000Z-aaaaaa"
        child_id = "fix-20260423T120100Z-bbbbbb"
        # Parent stays non-terminal so only the child auto-archives
        _write_workflow(cwd, parent_id, "remediation-discussion",
                        "discuss", "audit")
        _write_workflow(cwd, child_id, "commit-complete", "archive", "fix")
        _write_active(cwd, [
            {"id": parent_id, "type": "audit",
             "phase": "remediation-discussion",
             "parent": None, "children": [child_id]},
            {"id": child_id, "type": "fix", "phase": "commit-complete",
             "parent": parent_id, "children": []},
        ])
        # Add a fix-subject commit so A2 + A3 pass for the child
        (cwd / "fix.txt").write_text("x")
        subprocess.run(["git", "add", "-A"], cwd=str(cwd), check=True)
        subprocess.run(
            ["git", "commit", "-m", "fix(test): resolve issue", "-q"],
            cwd=str(cwd), check=True,
        )
        _run_hook("stop.mjs", {"cwd": str(cwd)}, cwd)
        # child is archived
        assert (cwd / ".claude" / "omcc-dev" / "archive"
                / f"{child_id}.md").exists()
        # parent entry remains; its `children` no longer lists the archived id
        registry = (cwd / ".claude" / "omcc-dev" / "active.md").read_text()
        assert parent_id in registry
        assert child_id not in registry, \
            "archived child id must be scrubbed from parent.children"

    def test_active_grandchild_blocks_root_archive(self, tmp_path):
        """Transitive A4: an active grandchild blocks the root's archive even
        though the root's direct child is also non-terminal. Pre-hierarchical
        A4 was 1-level; walkWorkflowTree now walks the full descendant tree."""
        cwd = _init_cwd(tmp_path)
        root_id = "audit-20260423T120000Z-aaaaaa"
        mid_id = "fix-20260423T120100Z-bbbbbb"
        leaf_id = "fix-20260423T120200Z-cccccc"
        root_path = _write_workflow(
            cwd, root_id, "summary-complete", "archive", "audit"
        )
        _write_workflow(cwd, mid_id, "investigate", "working", "fix")
        _write_workflow(cwd, leaf_id, "investigate", "working", "fix")
        _write_active(cwd, [
            {"id": root_id, "type": "audit", "phase": "summary-complete",
             "parent": None, "children": [mid_id]},
            {"id": mid_id, "type": "fix", "phase": "investigate",
             "parent": root_id, "children": [leaf_id]},
            {"id": leaf_id, "type": "fix", "phase": "investigate",
             "parent": mid_id, "children": []},
        ])
        _run_hook("stop.mjs", {"cwd": str(cwd)}, cwd)
        assert root_path.exists(), \
            "transitive A4 must block root archive while any descendant is active"
        assert not (
            cwd / ".claude" / "omcc-dev" / "archive" / f"{root_id}.md"
        ).exists()

    def test_stale_registry_entry_reconciled(self, tmp_path):
        """If a workflow file is already in archive/ but the active registry
        still lists it, Stop hook should reconcile by removing the entry."""
        cwd = _init_cwd(tmp_path)
        wf_id = "audit-20260422T120000Z-abcdef"
        # Place file directly in archive/, not workflows/
        archive_path = cwd / ".claude" / "omcc-dev" / "archive" / f"{wf_id}.md"
        archive_path.write_text("---\nschema: 2\n---\n")
        _write_active(cwd, [{"id": wf_id, "type": "audit", "phase": "summary-complete",
                             "parent": None, "children": []}])
        _run_hook("stop.mjs", {"cwd": str(cwd)}, cwd)
        # Active registry no longer lists this id
        active_body = (cwd / ".claude" / "omcc-dev" / "active.md").read_text()
        assert wf_id not in active_body, (
            "stale registry entry should be removed"
        )

    def test_missing_file_not_in_archive_preserves_entry(self, tmp_path):
        """Workflow file absent from BOTH workflows/ and archive/ must preserve
        the active registry entry (not silently drop it on transient races)."""
        cwd = _init_cwd(tmp_path)
        wf_id = "fix-20260422T120000Z-beef01"
        # No file in workflows/ and no file in archive/
        _write_active(cwd, [{"id": wf_id, "type": "fix", "phase": "investigate",
                             "parent": None, "children": []}])
        _run_hook("stop.mjs", {"cwd": str(cwd)}, cwd)
        active_body = (cwd / ".claude" / "omcc-dev" / "active.md").read_text()
        assert wf_id in active_body, (
            "entry must be preserved when file absent from both locations"
        )

    def test_registry_empty_list_after_last_archive(self, tmp_path):
        """After auto-archiving the sole active workflow, active.md must
        contain 'active: []' — not a dangling 'active:' scalar (which
        YAML parses as null)."""
        cwd = _init_cwd(tmp_path)
        wf_id = "audit-20260422T120000Z-cafe02"
        _write_workflow(cwd, wf_id, "summary-complete", "archive", "audit")
        _write_active(cwd, [{"id": wf_id, "type": "audit", "phase": "summary-complete",
                             "parent": None, "children": []}])
        _run_hook("stop.mjs", {"cwd": str(cwd)}, cwd)
        active_body = (cwd / ".claude" / "omcc-dev" / "active.md").read_text()
        assert "active: []" in active_body, (
            f"empty list literal expected, got: {active_body!r}"
        )


class TestPreCompactCap:
    def test_snapshot_cap_trims_oldest(self, tmp_path):
        """50-snapshot cap: body with 50 existing snapshots should have the
        oldest trimmed when a 51st is appended."""
        cwd = _init_cwd(tmp_path)
        wf_id = "start-20260422T120000Z-333333"
        # Pre-seed with 50 snapshot blocks using distinct head SHAs.
        # Use 2020 timestamps so the 60s idempotency window never matches
        # regardless of the host's system clock (this test is about the
        # 50-snapshot cap, not idempotency).
        snap_blocks = "".join(
            "\n<!-- pre-compact snapshot -->\n"
            f"timestamp: 2020-01-01T00:{i // 10:02d}:{(i % 10) * 6:02d}Z\n"
            f"branch: main\nhead: baseline{i:03d}\nstatus:\n  (clean)\n"
            for i in range(50)
        )
        wf_path = _write_workflow(
            cwd, wf_id, "brainstorm", "next", "start",
            body_extra=snap_blocks,
        )
        _write_active(cwd, [{"id": wf_id, "type": "start", "phase": "brainstorm",
                             "parent": None, "children": []}])
        _run_hook("pre-compact.mjs", {"cwd": str(cwd)}, cwd)
        body = wf_path.read_text()
        count = body.count("<!-- pre-compact snapshot -->")
        assert count == 50, f"expected 50 snapshots after trim, got {count}"
        # Oldest seeded snapshot (baseline000) should be gone
        assert "head: baseline000" not in body


# ---------------------------------------------------------------------------
# C.6 — SessionStart ensemble= suffix injection (Issue #100, criterion #5)
# ---------------------------------------------------------------------------


def _ensemble_results_block(entries):
    """Render a YAML 'ensemble_results: ...' frontmatter block."""
    if not entries:
        return "ensemble_results: []\n"
    lines = ["ensemble_results:"]
    for e in entries:
        lines.append(f"  - phase: {e['phase']}")
        for k in ("ensemble_type", "run_id", "verdict", "summary",
                 "completed_at", "codex_session_id"):
            if k in e:
                lines.append(f"    {k}: {e[k]}")
    return "\n".join(lines) + "\n"


def _write_workflow_with_extra_frontmatter(
    cwd, workflow_id, phase, next_action,
    workflow_type=None, extra_frontmatter="", schema=2,
):
    """Like _write_workflow but allows extra frontmatter (e.g.,
    ensemble_results, plan.deliverables) appended just before the
    closing --- terminator."""
    wtype = workflow_type or workflow_id.split("-")[0]
    bh = _current_head(cwd)
    path = cwd / ".claude" / "omcc-dev" / "workflows" / f"{workflow_id}.md"
    frontmatter = (
        "---\n"
        f"schema: {schema}\n"
        f"workflow_id: {workflow_id}\n"
        f"workflow_type: {wtype}\n"
        "original_request: test\n"
        "started_at: 2026-04-22T00:00:00Z\n"
        "updated_at: 2026-04-22T00:00:00Z\n"
        f"repo_root: {cwd}\n"
        "git_baseline:\n"
        "  branch: main\n"
        f"  head: {bh}\n"
        "  status_digest: aabbcc\n"
        f"current_phase: {phase}\n"
        f"next_action: {next_action}\n"
        "tasks: []\n"
        "task_profile:\n"
        "  scope: x\n"
        "  complexity: low\n"
        "  ensemble_affinity: LOW\n"
        f"{extra_frontmatter}"
        "---\n"
    )
    content = frontmatter + f"\n# {workflow_id}\n"
    path.write_text(content)
    return path


def _write_shard_file(cwd, root_id, shard_id, ensemble_entries):
    """Write a shard file under workflows/<root_id>/<shard_id>.md."""
    shard_dir = cwd / ".claude" / "omcc-dev" / "workflows" / root_id
    shard_dir.mkdir(parents=True, exist_ok=True)
    path = shard_dir / f"{shard_id}.md"
    er = _ensemble_results_block(ensemble_entries)
    deliverable_letter = shard_id.split("-")[1]
    fm = (
        "---\n"
        "schema: 2\n"
        "shard_type: deliverable\n"
        f"root_workflow: {root_id}\n"
        f"deliverable_id: {deliverable_letter}\n"
        "started_at: 2026-04-22T00:00:00Z\n"
        "updated_at: 2026-04-22T00:00:00Z\n"
        "current_phase: review\n"
        "next_action: review\n"
        "tasks: []\n"
        f"{er}"
        "---\n"
    )
    path.write_text(fm + f"\n# shard {shard_id}\n")
    return path


def _valid_ensemble_entry(phase, ensemble_type, run_id_suffix, summary,
                          completed_at, verdict="pass"):
    return {
        "phase": phase,
        "ensemble_type": ensemble_type,
        "run_id": f"20260501T000000Z-{run_id_suffix}",
        "verdict": verdict,
        "summary": summary,
        "completed_at": completed_at,
    }


class TestSessionStartEnsembleSuffix:
    """Issue #100 criterion #5: SessionStart emits an ensemble= 1-line
    suffix per active workflow when a valid ensemble_results entry exists.
    Eight fixtures cover empty / single / malformed / backtick / multiple /
    sharded-with-shard / sharded-no-active-shard / tie-completed_at."""

    def test_empty_ensemble_results_no_suffix(self, tmp_path):
        cwd = _init_cwd(tmp_path)
        wf_id = "fix-20260422T120000Z-aaaaaa"
        _write_workflow_with_extra_frontmatter(
            cwd, wf_id, "investigate", "do thing", "fix",
            extra_frontmatter=_ensemble_results_block([]),
        )
        _write_active(cwd, [{"id": wf_id, "type": "fix", "phase": "investigate",
                             "parent": None, "children": []}])
        rc, out, _ = _run_hook(
            "session-start.mjs", {"cwd": str(cwd), "source": "compact"}, cwd
        )
        assert rc == 0
        assert wf_id in out
        assert "ensemble=" not in out

    def test_single_valid_entry_emits_suffix(self, tmp_path):
        cwd = _init_cwd(tmp_path)
        wf_id = "fix-20260422T120000Z-bbbbbb"
        entries = [_valid_ensemble_entry(
            "fix-and-verify", "fix-verify", "111111",
            "verified clean", "2026-04-30T00:00:00Z",
        )]
        _write_workflow_with_extra_frontmatter(
            cwd, wf_id, "fix-and-verify", "commit", "fix",
            extra_frontmatter=_ensemble_results_block(entries),
        )
        _write_active(cwd, [{"id": wf_id, "type": "fix",
                             "phase": "fix-and-verify",
                             "parent": None, "children": []}])
        rc, out, _ = _run_hook(
            "session-start.mjs", {"cwd": str(cwd), "source": "compact"}, cwd
        )
        assert rc == 0
        assert 'ensemble="verified clean"' in out

    def test_malformed_entry_drops_suffix_keeps_base_row(self, tmp_path):
        cwd = _init_cwd(tmp_path)
        wf_id = "fix-20260422T120000Z-cccccc"
        # run_id fails the format regex → fails the gauntlet
        entries = [{
            "phase": "fix-and-verify",
            "ensemble_type": "fix-verify",
            "run_id": "INVALID-RUN-ID",
            "verdict": "pass",
            "summary": "should-not-appear",
            "completed_at": "2026-04-30T00:00:00Z",
        }]
        _write_workflow_with_extra_frontmatter(
            cwd, wf_id, "fix-and-verify", "commit", "fix",
            extra_frontmatter=_ensemble_results_block(entries),
        )
        _write_active(cwd, [{"id": wf_id, "type": "fix",
                             "phase": "fix-and-verify",
                             "parent": None, "children": []}])
        rc, out, err = _run_hook(
            "session-start.mjs", {"cwd": str(cwd), "source": "compact"}, cwd
        )
        assert rc == 0
        assert wf_id in out
        assert "phase=fix-and-verify" in out
        assert "ensemble=" not in out
        assert "should-not-appear" not in out
        assert "should-not-appear" not in err

    def test_backtick_summary_drops_suffix_silent(self, tmp_path):
        cwd = _init_cwd(tmp_path)
        wf_id = "fix-20260422T120000Z-dddddd"
        # Summary contains a backtick → sanitizeField returns null
        entries = [{
            "phase": "fix-and-verify",
            "ensemble_type": "fix-verify",
            "run_id": "20260501T000000Z-aaaaaa",
            "verdict": "pass",
            "summary": "bad whoami output",  # placeholder; we override below
            "completed_at": "2026-04-30T00:00:00Z",
        }]
        # Replace placeholder with backtick-laden summary at write time —
        # the YAML emitter would otherwise need quoting; inject it as a
        # raw frontmatter block instead.
        raw_block = (
            "ensemble_results:\n"
            "  - phase: fix-and-verify\n"
            "    ensemble_type: fix-verify\n"
            "    run_id: 20260501T000000Z-aaaaaa\n"
            "    verdict: pass\n"
            "    summary: bad `whoami` output\n"
            "    completed_at: 2026-04-30T00:00:00Z\n"
        )
        _write_workflow_with_extra_frontmatter(
            cwd, wf_id, "fix-and-verify", "commit", "fix",
            extra_frontmatter=raw_block,
        )
        _write_active(cwd, [{"id": wf_id, "type": "fix",
                             "phase": "fix-and-verify",
                             "parent": None, "children": []}])
        rc, out, err = _run_hook(
            "session-start.mjs", {"cwd": str(cwd), "source": "compact"}, cwd
        )
        assert rc == 0
        assert wf_id in out
        assert "ensemble=" not in out
        assert "`" not in out

    def test_multiple_entries_latest_by_completed_at(self, tmp_path):
        cwd = _init_cwd(tmp_path)
        wf_id = "fix-20260422T120000Z-eeeeee"
        entries = [
            _valid_ensemble_entry(
                "investigate", "investigate", "aaaaaa",
                "older entry", "2026-04-01T00:00:00Z",
            ),
            _valid_ensemble_entry(
                "fix-and-verify", "fix-verify", "bbbbbb",
                "newest entry", "2026-04-30T00:00:00Z",
            ),
            _valid_ensemble_entry(
                "investigate", "investigate", "cccccc",
                "middle entry", "2026-04-15T00:00:00Z",
            ),
        ]
        _write_workflow_with_extra_frontmatter(
            cwd, wf_id, "fix-and-verify", "commit", "fix",
            extra_frontmatter=_ensemble_results_block(entries),
        )
        _write_active(cwd, [{"id": wf_id, "type": "fix",
                             "phase": "fix-and-verify",
                             "parent": None, "children": []}])
        rc, out, _ = _run_hook(
            "session-start.mjs", {"cwd": str(cwd), "source": "compact"}, cwd
        )
        assert rc == 0
        assert 'ensemble="newest entry"' in out
        assert "older entry" not in out
        assert "middle entry" not in out

    def test_sharded_with_ensemble_in_active_shard_only(self, tmp_path):
        cwd = _init_cwd(tmp_path)
        root_id = "start-20260422T120000Z-ffffff"
        shard_id = "deliverable-A"
        deliverables_block = (
            "plan:\n"
            "  deliverables:\n"
            f"    - id: A\n"
            f"      shard_path: {shard_id}.md\n"
            "      status: in_progress\n"
        )
        _write_workflow_with_extra_frontmatter(
            cwd, root_id, "implement", "build deliverable A", "start",
            extra_frontmatter=deliverables_block,
        )
        shard_entries = [_valid_ensemble_entry(
            "review", "review", "111111",
            "shard review pass", "2026-04-30T00:00:00Z",
        )]
        _write_shard_file(cwd, root_id, shard_id, shard_entries)
        _write_active(cwd, [{"id": root_id, "type": "start",
                             "phase": "implement",
                             "parent": None, "children": []}])
        rc, out, _ = _run_hook(
            "session-start.mjs", {"cwd": str(cwd), "source": "compact"}, cwd
        )
        assert rc == 0
        assert 'ensemble="shard review pass"' in out

    def test_sharded_no_active_shard_root_only(self, tmp_path):
        cwd = _init_cwd(tmp_path)
        root_id = "start-20260422T120000Z-aaaaaa"
        deliverables_block = (
            "plan:\n"
            "  deliverables:\n"
            "    - id: A\n"
            "      shard_path: deliverable-A.md\n"
            "      status: completed\n"
            "    - id: B\n"
            "      shard_path: deliverable-B.md\n"
            "      status: completed\n"
        )
        root_entries = [_valid_ensemble_entry(
            "review", "review", "222222",
            "branch-wide review", "2026-05-01T00:00:00Z",
        )]
        extra = deliverables_block + _ensemble_results_block(root_entries)
        _write_workflow_with_extra_frontmatter(
            cwd, root_id, "review", "5b cross-deliverable", "start",
            extra_frontmatter=extra,
        )
        _write_active(cwd, [{"id": root_id, "type": "start",
                             "phase": "review",
                             "parent": None, "children": []}])
        rc, out, _ = _run_hook(
            "session-start.mjs", {"cwd": str(cwd), "source": "compact"}, cwd
        )
        assert rc == 0
        assert 'ensemble="branch-wide review"' in out

    def test_sharded_tie_completed_at_root_first(self, tmp_path):
        cwd = _init_cwd(tmp_path)
        root_id = "start-20260422T120000Z-bbbbbb"
        shard_id = "deliverable-A"
        same_ts = "2026-04-30T00:00:00Z"
        deliverables_block = (
            "plan:\n"
            "  deliverables:\n"
            f"    - id: A\n"
            f"      shard_path: {shard_id}.md\n"
            "      status: in_progress\n"
        )
        root_entries = [_valid_ensemble_entry(
            "plan", "plan-verify", "111111",
            "root entry wins", same_ts,
        )]
        shard_entries = [_valid_ensemble_entry(
            "review", "review", "222222",
            "shard entry loses", same_ts,
        )]
        extra = deliverables_block + _ensemble_results_block(root_entries)
        _write_workflow_with_extra_frontmatter(
            cwd, root_id, "implement", "build A", "start",
            extra_frontmatter=extra,
        )
        _write_shard_file(cwd, root_id, shard_id, shard_entries)
        _write_active(cwd, [{"id": root_id, "type": "start",
                             "phase": "implement",
                             "parent": None, "children": []}])
        rc, out, _ = _run_hook(
            "session-start.mjs", {"cwd": str(cwd), "source": "compact"}, cwd
        )
        assert rc == 0
        assert 'ensemble="root entry wins"' in out
        assert "shard entry loses" not in out

    # ------------------------------------------------------------------
    # Phase 6 review-resolved findings (Issue #100 review)
    # ------------------------------------------------------------------

    def test_missing_summary_field_drops_suffix(self, tmp_path):
        """F1: an entry whose summary field is absent must reject from
        the latest-overall selector — not pass through as empty string."""
        cwd = _init_cwd(tmp_path)
        wf_id = "fix-20260422T120000Z-aaaa01"
        raw_block = (
            "ensemble_results:\n"
            "  - phase: fix-and-verify\n"
            "    ensemble_type: fix-verify\n"
            "    run_id: 20260501T000000Z-aaaaaa\n"
            "    verdict: pass\n"
            "    completed_at: 2026-04-30T00:00:00Z\n"
        )
        _write_workflow_with_extra_frontmatter(
            cwd, wf_id, "fix-and-verify", "commit", "fix",
            extra_frontmatter=raw_block,
        )
        _write_active(cwd, [{"id": wf_id, "type": "fix",
                             "phase": "fix-and-verify",
                             "parent": None, "children": []}])
        rc, out, _ = _run_hook(
            "session-start.mjs", {"cwd": str(cwd), "source": "compact"}, cwd
        )
        assert rc == 0
        assert wf_id in out
        assert "ensemble=" not in out

    def test_missing_summary_does_not_shadow_older_valid(self, tmp_path):
        """F1: when a newer entry has no summary, the latest-overall
        selector must skip it and surface the older valid entry."""
        cwd = _init_cwd(tmp_path)
        wf_id = "fix-20260422T120000Z-aaaa02"
        raw_block = (
            "ensemble_results:\n"
            "  - phase: investigate\n"
            "    ensemble_type: investigate\n"
            "    run_id: 20260501T000000Z-bbbbbb\n"
            "    verdict: pass\n"
            "    summary: older valid\n"
            "    completed_at: 2026-04-01T00:00:00Z\n"
            "  - phase: fix-and-verify\n"
            "    ensemble_type: fix-verify\n"
            "    run_id: 20260501T000000Z-cccccc\n"
            "    verdict: pass\n"
            "    completed_at: 2026-04-30T00:00:00Z\n"
        )
        _write_workflow_with_extra_frontmatter(
            cwd, wf_id, "fix-and-verify", "commit", "fix",
            extra_frontmatter=raw_block,
        )
        _write_active(cwd, [{"id": wf_id, "type": "fix",
                             "phase": "fix-and-verify",
                             "parent": None, "children": []}])
        rc, out, _ = _run_hook(
            "session-start.mjs", {"cwd": str(cwd), "source": "compact"}, cwd
        )
        assert rc == 0
        assert 'ensemble="older valid"' in out

    def test_double_quote_in_summary_drops_suffix(self, tmp_path):
        """F5: a summary containing `\"` would break the line builder's
        quoted output; reject the entry to prevent format-injection."""
        cwd = _init_cwd(tmp_path)
        wf_id = "fix-20260422T120000Z-aaaa03"
        raw_block = (
            "ensemble_results:\n"
            "  - phase: fix-and-verify\n"
            "    ensemble_type: fix-verify\n"
            "    run_id: 20260501T000000Z-dddddd\n"
            "    verdict: pass\n"
            '    summary: bad "quoted" value\n'
            "    completed_at: 2026-04-30T00:00:00Z\n"
        )
        _write_workflow_with_extra_frontmatter(
            cwd, wf_id, "fix-and-verify", "commit", "fix",
            extra_frontmatter=raw_block,
        )
        _write_active(cwd, [{"id": wf_id, "type": "fix",
                             "phase": "fix-and-verify",
                             "parent": None, "children": []}])
        rc, out, _ = _run_hook(
            "session-start.mjs", {"cwd": str(cwd), "source": "compact"}, cwd
        )
        assert rc == 0
        assert wf_id in out
        assert "ensemble=" not in out
        assert 'bad "quoted" value' not in out

    def test_shard_legacy_schema_falls_back_to_root(self, tmp_path):
        """F2: a shard whose schema is unsupported (legacy=1, future>2)
        must not contribute entries; the selector falls back to root."""
        cwd = _init_cwd(tmp_path)
        root_id = "start-20260422T120000Z-aaaa04"
        shard_id = "deliverable-A"
        deliverables_block = (
            "plan:\n"
            "  deliverables:\n"
            f"    - id: A\n"
            f"      shard_path: {shard_id}.md\n"
            "      status: in_progress\n"
        )
        root_entries = [_valid_ensemble_entry(
            "review", "review", "111111",
            "root entry", "2026-04-15T00:00:00Z",
        )]
        extra = deliverables_block + _ensemble_results_block(root_entries)
        _write_workflow_with_extra_frontmatter(
            cwd, root_id, "implement", "build A", "start",
            extra_frontmatter=extra,
        )
        shard_dir = cwd / ".claude" / "omcc-dev" / "workflows" / root_id
        shard_dir.mkdir(parents=True, exist_ok=True)
        shard_path = shard_dir / f"{shard_id}.md"
        shard_entries = [_valid_ensemble_entry(
            "review", "review", "999999",
            "shard would have won", "2026-04-30T00:00:00Z",
        )]
        er = _ensemble_results_block(shard_entries)
        fm = (
            "---\n"
            "schema: 1\n"  # legacy → reject
            "shard_type: deliverable\n"
            f"root_workflow: {root_id}\n"
            "deliverable_id: A\n"
            "started_at: 2026-04-22T00:00:00Z\n"
            "updated_at: 2026-04-22T00:00:00Z\n"
            "current_phase: review\n"
            "next_action: review\n"
            "tasks: []\n"
            f"{er}"
            "---\n"
        )
        shard_path.write_text(fm + "\n# shard\n")
        _write_active(cwd, [{"id": root_id, "type": "start",
                             "phase": "implement",
                             "parent": None, "children": []}])
        rc, out, _ = _run_hook(
            "session-start.mjs", {"cwd": str(cwd), "source": "compact"}, cwd
        )
        assert rc == 0
        assert 'ensemble="root entry"' in out
        assert "shard would have won" not in out

    def test_corrupt_frontmatter_suppresses_workflow_row(self, tmp_path):
        """F7 (Issue #100 review round 2): a workflow file whose
        frontmatter cannot be parsed must NOT produce a SessionStart
        row. The prior `fields = {}` fallback bypassed the
        schema/version gate and surfaced stale phase/next from the
        active registry."""
        cwd = _init_cwd(tmp_path)
        wf_id = "fix-20260422T120000Z-aaaa06"
        (cwd / ".claude" / "omcc-dev" / "workflows" / f"{wf_id}.md").write_text(
            "no frontmatter at all — not even ---\n"
        )
        _write_active(cwd, [{"id": wf_id, "type": "fix",
                             "phase": "investigate",
                             "parent": None, "children": []}])
        rc, out, _ = _run_hook(
            "session-start.mjs", {"cwd": str(cwd), "source": "compact"}, cwd
        )
        assert rc == 0
        assert wf_id not in out

    def test_shard_root_workflow_mismatch_falls_back_to_root(self, tmp_path):
        """F2: a shard whose root_workflow does not match the owning
        workflow id is orphaned/corrupt; do not merge its entries."""
        cwd = _init_cwd(tmp_path)
        root_id = "start-20260422T120000Z-aaaa05"
        other_id = "start-20260422T120000Z-bbbb05"
        shard_id = "deliverable-A"
        deliverables_block = (
            "plan:\n"
            "  deliverables:\n"
            f"    - id: A\n"
            f"      shard_path: {shard_id}.md\n"
            "      status: in_progress\n"
        )
        root_entries = [_valid_ensemble_entry(
            "review", "review", "111111",
            "root entry", "2026-04-15T00:00:00Z",
        )]
        extra = deliverables_block + _ensemble_results_block(root_entries)
        _write_workflow_with_extra_frontmatter(
            cwd, root_id, "implement", "build A", "start",
            extra_frontmatter=extra,
        )
        shard_dir = cwd / ".claude" / "omcc-dev" / "workflows" / root_id
        shard_dir.mkdir(parents=True, exist_ok=True)
        shard_path = shard_dir / f"{shard_id}.md"
        shard_entries = [_valid_ensemble_entry(
            "review", "review", "999999",
            "orphan shard entry", "2026-04-30T00:00:00Z",
        )]
        er = _ensemble_results_block(shard_entries)
        fm = (
            "---\n"
            "schema: 2\n"
            "shard_type: deliverable\n"
            f"root_workflow: {other_id}\n"  # mismatch
            "deliverable_id: A\n"
            "started_at: 2026-04-22T00:00:00Z\n"
            "updated_at: 2026-04-22T00:00:00Z\n"
            "current_phase: review\n"
            "next_action: review\n"
            "tasks: []\n"
            f"{er}"
            "---\n"
        )
        shard_path.write_text(fm + "\n# shard\n")
        _write_active(cwd, [{"id": root_id, "type": "start",
                             "phase": "implement",
                             "parent": None, "children": []}])
        rc, out, _ = _run_hook(
            "session-start.mjs", {"cwd": str(cwd), "source": "compact"}, cwd
        )
        assert rc == 0
        assert 'ensemble="root entry"' in out
        assert "orphan shard entry" not in out

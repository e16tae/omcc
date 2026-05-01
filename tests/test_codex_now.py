"""Contract tests for the /omcc-dev:codex-now command file.

Pin the load-bearing parts of the command prose so the contract
documented in ensemble-protocol.md "Codex-now" subsection and
continuity-protocol.md Phase-boundary Write Rules cannot drift away
silently.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMAND = ROOT / "plugins" / "omcc-dev" / "commands" / "codex-now.md"


def test_codex_now_command_file_exists_and_has_frontmatter():
    """Slash command discovery requires .md file under commands/ with
    `description` frontmatter. `argument-hint` is also load-bearing
    for /codex-now because the question payload IS the argument."""
    assert COMMAND.exists()
    text = COMMAND.read_text(encoding="utf-8")
    assert "description:" in text
    assert "argument-hint:" in text


def test_codex_now_has_six_step_structure():
    """The command body documents a six-step orchestration. Drift in
    step count would imply silent reordering of the dispatch /
    bookkeeping sequence."""
    text = COMMAND.read_text(encoding="utf-8")
    for step in (
        "## Step 1:",
        "## Step 2:",
        "## Step 3:",
        "## Step 4:",
        "## Step 5:",
        "## Step 6:",
    ):
        assert step in text, f"codex-now.md is missing heading {step!r}"


def test_codex_now_uses_documented_helpers():
    """The mutator pseudocode must compose helpers exported by
    hooks/_utils.mjs."""
    text = COMMAND.read_text(encoding="utf-8")
    for helper in ("atomicModifyFile", "parseFrontmatter", "updateUpdatedAt", "sanitizeField"):
        assert helper in text, f"codex-now.md must mention {helper}"


def test_codex_now_mutator_pseudocode_lives_in_correct_steps():
    """`appendMutator` must appear inside Step 4 and `removeMutator`
    inside Step 5. A future refactor that floats them into footnotes
    or different steps must be caught."""
    text = COMMAND.read_text(encoding="utf-8")
    step4 = text.index("## Step 4:")
    step5 = text.index("## Step 5:")
    step6 = text.index("## Step 6:")
    append_idx = text.index("appendMutator")
    remove_idx = text.index("removeMutator")
    assert step4 < append_idx < step5, (
        "appendMutator must appear inside Step 4 (between the Step 4 and "
        "Step 5 headings)"
    )
    assert step5 < remove_idx < step6, (
        "removeMutator must appear inside Step 5 (between the Step 5 and "
        "Step 6 headings)"
    )


def test_codex_now_uses_cdata_wrapping_for_user_question():
    """The prompt template must wrap the user-controlled question in a
    literal CDATA section so XML in the question cannot break out."""
    text = COMMAND.read_text(encoding="utf-8")
    assert "<![CDATA[" in text
    assert "]]>" in text


def test_codex_now_rejects_cdata_terminator_in_user_question():
    """CDATA breakout regression test. A user question containing
    `]]>` would close the CDATA section prematurely. Step 2 must
    explicitly reject questions with that token (no silent
    transformation)."""
    text = COMMAND.read_text(encoding="utf-8")
    assert re.search(
        r"\]\]>[^\n]*reject|reject[^\n]*\]\]>",
        text,
    ), "Step 2 must explicitly reject questions containing the CDATA terminator `]]>`"


def test_codex_now_emits_codex_now_ensemble_type():
    """The pending_ensemble entry uses the new `codex-now` enum
    value; a mismatch would desync the schema-drift test that ties
    the enum to ensemble-protocol headings."""
    text = COMMAND.read_text(encoding="utf-8")
    assert "ensemble_type: codex-now" in text


def test_codex_now_mutator_pins_field_order():
    """The append-side prose must pin the canonical field-order
    insertion point (after presentation_mode, before
    latest_checkpoint) per continuity-protocol.md."""
    text = COMMAND.read_text(encoding="utf-8")
    assert "presentation_mode" in text
    assert "latest_checkpoint" in text

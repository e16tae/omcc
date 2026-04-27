# Presentation Mode Protocol

When presenting review items, findings, or decisions that require user attention,
offer the user a choice of presentation mode. The goal: the user controls how they
consume structured information, without sacrificing depth or detail.

---

## When This Protocol Applies

Activates when you are about to present **multiple items** that require user review or decision:
- Option comparisons (choice protocol)
- Code review findings
- Implementation plan tasks
- Investigation results (multiple hypotheses)
- Audit report findings
- Codebase exploration synthesis

Does NOT apply to:
- Single-item presentations (one finding, one recommendation)
- Binary confirmations (yes/no)
- Progress updates or status reports
- Internal orchestration output

---

## Offering the Choice

At the first major presentation point in a command or skill workflow, ask:

> How would you like to review this?
> **(1) All at once** — full structured output in one view
> **(2) One by one** — walk through each item together, interview style

### Timing rules

- **Commands** (`/start`, `/fix`, `/audit`): Ask once at the first presentation point. Apply the chosen mode to all subsequent presentation points within the same command invocation.
- **Skills** (auto-activated): Ask once before the first presentation.
- **Skills within commands**: When a skill is invoked as part of a command (not auto-activated), the command-level timing rule applies. Do not re-ask within the same command invocation.
- **Mode switching**: The user may request a switch at any time (e.g., "show me the rest all at once" or "let's go through these one by one"). Honor the request immediately. When switching from interview to batch mid-stream, present only the remaining unseen items. After the batch, deliver the aggregate synthesis covering all items (including those already reviewed in interview mode).
- **Shortcut**: If the user has already expressed a preference earlier in the conversation, apply it without re-asking. Re-ask only when a new command or skill is invoked.

---

## Mode 1: Batch (All at Once)

Present all items in a single structured output. This is the default format already used
throughout omcc-dev commands and skills.

**Behavior:**
- Use the existing output formats (tables, lists, structured markdown) defined in each command/skill
- Complete information in one cohesive output
- No pauses between items

---

## Mode 2: Interview (One by One)

Present items sequentially, one at a time, with a pause for user input between each.

**Behavior:**

1. **Show progress**: Begin each item with its position (e.g., "**[2/5]**")
2. **Present one item** with full detail — same depth as batch mode. When output token limits
   or context window constraints make batch mode less thorough, interview mode may include
   additional detail per item since the content is spread across multiple turns.
3. **Pause**: After presenting the item, wait for the user's response. The user may:
   - Ask follow-up questions about this item
   - Request changes or adjustments
   - Confirm and move to the next item (e.g., "next", "ok", "continue")
   - **Stop reviewing** (e.g., "stop", "that's enough") — no further actions are taken
     on remaining items, but a mandatory condensed summary of every unseen item
     (one line per item: position, headline, severity if applicable) is output
     so nothing is silently hidden
   - **Delegate remaining** (e.g., "proceed with recommendations", "handle the rest") —
     apply the recommended action for each remaining item, then present a summary
     of what was done
   - Switch to batch mode for remaining items
4. **Proceed** only after the user signals readiness
5. **Synthesize** at the end: After all items are reviewed, deliver the aggregate sections
   required by the originating workflow (e.g., comparison table and recommendation for
   choice protocol, summary counts for audit, overall assessment for review).
   Then recap decisions made and actions agreed upon during the interview

### Interview mode applied to specific content types

| Content Type | One Item = |
|-------------|-----------|
| Option comparison | One option with its five-perspective analysis |
| Review finding | One finding with location, description, and recommended action |
| Plan task | One task with description, completion criterion, and dependencies |
| Investigation hypothesis | One hypothesis with verdict, confidence, and evidence |
| Audit issue | One issue with location, category, description, and action |
| Exploration perspective | One perspective (Architecture / Flow / Conventions) |

---

## Protocol Interaction Rule

Presentation mode changes only the delivery format, not the decision-making process.
When an individual item contains or reveals a meaningful choice between 2+ approaches:

1. **Recognize**: A choice exists when the item presents 2+ distinct remediation
   paths, implementation strategies, or design alternatives — not when it merely
   lists variations of the same approach.
2. **Invoke inline**: Pause the current item's presentation and run the full
   brainstorm skill (`skills/brainstorm/SKILL.md`) within that item —
   Research, Compare across five perspectives, and Recommend.
3. **Resume**: After the user decides, continue the interview from where it paused.

This applies regardless of the originating content type (audit finding, review
suggestion, plan task, etc.). The item's original format may be extended to
accommodate the comparison.

---

## Content Parity Rule

Both modes must present the **same items** with the **same depth of analysis**.
The difference is purely in delivery format, not in content quality or completeness.

Exception: When technical constraints (output token limits, context window pressure) force
batch mode to compress content, interview mode may provide greater per-item detail since
it spreads the output across multiple turns. This is the only permitted asymmetry.

---

## Use of `AskUserQuestion`

The `AskUserQuestion` tool surfaces options as a multiple-choice UI.
Reserve it for genuinely complex design decisions where all three hold:

- 2+ substantive alternatives exist
- The brainstorm skill has already produced a comparison
- The body of the message has presented the **5-perspective comparison
  + recommendation** in full detail before the tool call

For trivial confirmations, yes/no follow-ups, or self-evident next
steps, do **not** use `AskUserQuestion`. Use a plain text question
instead, framed as: *"Recommended: X. Proceed?"*

If the user replies with "what's the difference?" / "compare them
specifically" after a multiple-choice prompt, drop the tool, present
the detailed comparison + clear recommendation in the body, and ask
for plain-text confirmation.

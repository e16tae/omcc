---
description: Systematic bug fix — investigate root cause first, fix second
argument-hint: Bug description or issue number
---

# Fix

$ARGUMENTS

---

## Phase 1: Investigate

**Do NOT modify code until root cause is confirmed.** Jumping to a fix without understanding the cause leads to symptom-patching, not real fixes.

Follow the investigate skill workflow (`skills/investigate/SKILL.md`) with these additions for the full `/fix` command:

- **Agent spawning**: Unlike the lightweight investigate skill (which works inline), `/fix` spawns investigation agents in parallel via the Dynamic Agent Orchestration process (`orchestration.md`).
  - Minimum 2 hypotheses from distinct failure categories (e.g., code logic vs state/data vs environment/config)
  - More hypotheses when the cause is ambiguous
  - Each agent traces its assigned hypothesis and returns: verdict, confidence, evidence, verification method
- **Evaluate results**: Rank by confidence (HIGH > MEDIUM > LOW). Verify the top hypothesis with a targeted check. If verified → proceed to presenting results. If refuted → try next.
- **Present results**: Follow the Presentation Mode Protocol (`presentation-protocol.md`) before presenting confirmed investigation findings to the user.
- **Strike rule**: If all hypotheses are refuted, stop and suggest Codex escalation: "Would you like to escalate to Codex? (`/codex:rescue [description]`)"

---

## Phase 2: Codex Escalation (only on full strike)

Only if Phase 1 exhausted all hypotheses:
- Ask the user: "All hypotheses were refuted. Want to delegate to Codex for a different perspective?"
- If yes → tell the user to run `/codex:rescue` with the bug description and findings so far
- If no → continue manual investigation with user guidance

---

## Phase 3: Write Failing Test

1. Write a test that reproduces the bug
2. Run with Bash to confirm the test FAILS
3. If no test framework exists, skip this phase and inform the user

---

## Phase 4: Fix and Verify

1. Apply the minimal fix targeting the confirmed root cause
2. Run the failing test — confirm it now PASSES
3. Run the full test suite — confirm no regressions
4. Search for similar patterns: `Grep` for the same code pattern in other locations
5. If similar vulnerable code exists elsewhere, report to user

---

## Phase 5: Commit

Create a commit with this message format:

```
fix(scope): [one-line description]

Symptom: [what was observed]
Root cause: [confirmed cause]
Fix: [what was changed]
```

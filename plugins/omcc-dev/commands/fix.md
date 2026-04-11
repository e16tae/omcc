---
description: Systematic bug fix — investigate root cause first, fix second
argument-hint: Bug description or issue number
---

# Fix

$ARGUMENTS

## Core Principle

**Do NOT modify code until root cause is confirmed.** Jumping to a fix without understanding the cause leads to symptom-patching, not real fixes.

---

## Phase 1: Investigate

Collect symptoms and trace the root cause before any code changes.

1. **Collect symptoms**
   - Identify the error message, stack trace, or unexpected behavior
   - Try to reproduce with Bash (if possible)
   - Check recent changes: `git log --oneline -10`
   - Read the relevant code area

2. **Form hypotheses**
   State 3 distinct hypotheses about the root cause:
   - Hypothesis A (code logic): condition error, boundary issue, type mismatch
   - Hypothesis B (state/data): race condition, null reference, stale cache
   - Hypothesis C (environment): config issue, dependency change, API contract

3. **Parallel investigation**
   Launch 3 hypothesis-tracer agents in parallel (single message, 3 Agent calls):
   - Agent 1: Investigate hypothesis A
   - Agent 2: Investigate hypothesis B
   - Agent 3: Investigate hypothesis C

   Each agent traces its assigned hypothesis and returns: verdict, confidence, evidence, verification method.

4. **Evaluate results**
   - Rank by confidence (HIGH > MEDIUM > LOW)
   - Verify the top hypothesis with a targeted check (temporary log, assertion, or test)
   - If verified → proceed to Phase 3
   - If refuted → try next hypothesis

5. **3-strike rule**
   If 3 hypotheses are all refuted:
   - Stop investigating
   - Report findings to user
   - Suggest: "Would you like to escalate to Codex? (`/codex:rescue [description]`)"

---

## Phase 2: Codex Escalation (only on 3-strike)

Only if Phase 1 exhausted all hypotheses:
- Ask the user: "3 hypotheses were refuted. Want to delegate to Codex for a different perspective?"
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

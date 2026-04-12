---
description: Systematic bug fix — investigate root cause first, fix second
argument-hint: Bug description or issue number
---

# Fix

$ARGUMENTS

---

## Phase 1: Investigate

Follow the investigate skill's command-invoked mode (`skills/investigate/SKILL.md`).

Do not proceed to Phase 2 until root cause is confirmed.

---

## Phase 2: Write Failing Test

1. Write a test that reproduces the bug
2. Run with Bash to confirm the test FAILS
3. If no test framework exists, skip this phase and inform the user

---

## Phase 3: Fix and Verify

1. Apply the minimal fix targeting the confirmed root cause
2. Run the failing test — confirm it now PASSES
3. Run the full test suite — confirm no regressions
4. Ensemble fix verification (all affinity levels — including LOW):
   - Launch Codex **fix-verify** ensemble point (background) with `--scope working-tree`
   - Collect Codex review of the patch
   - Synthesize: merge Codex findings into fix verification
   - Report any additional concerns Codex found in the patch
5. Search for similar patterns: `Grep` for the same code pattern in other locations
6. If similar vulnerable code exists elsewhere, report to user

---

## Phase 4: Commit

Create a commit with this message format:

```
fix(scope): [one-line description]

Symptom: [what was observed]
Root cause: [confirmed cause]
Fix: [what was changed]
```

---
description: Systematic bug fix — investigate root cause first, fix second
argument-hint: Bug description or issue number
---

# Fix

$ARGUMENTS

Use `TaskCreate` and `TaskUpdate` to track progress across phases. Codex
ensemble runs automatically per `ensemble-protocol.md` when Ensemble Affinity
warrants it — never ask the user whether to invoke Codex, and never direct
them to run `/codex:*` commands manually.

---

## Phase 1: Investigate

Follow the investigate skill's command-invoked mode (`skills/investigate/SKILL.md`).

Do not proceed to Phase 2 until root cause is confirmed.

### Post-investigation assessment

After root cause is confirmed, evaluate the fix scope:

1. If the investigation identifies **2+ viable fix approaches**, invoke the brainstorm
   skill to compare approaches and wait for user approval before proceeding.
2. If the confirmed root cause requires **changes to 5+ files or architectural restructuring**,
   report this to the user and recommend transitioning to `/start`. Provide the root cause
   analysis (cause, evidence, impact scope) as context for `/start`'s brainstorm phase.
3. Otherwise, proceed to Phase 2 with the identified fix approach.

---

## Phase 2: Write Failing Test

1. Write a test that reproduces the bug
2. Run with Bash to confirm the test FAILS
3. If no test framework exists, skip this phase and inform the user

---

## Phase 3: Fix and Verify

1. Apply the minimal fix targeting the confirmed root cause
2. If Phase 2 was skipped (no test framework): verify the fix manually —
   Grep for the old buggy pattern to confirm 0 remaining occurrences,
   and run the affected code path to confirm correct behavior.
   Otherwise: Run the failing test — confirm it now PASSES.
3. If test suite available: Run the full test suite — confirm no regressions.
   Without a test framework, manual verification (Steps 2 otherwise + 5) is
   sufficient; inform the user the full suite was skipped.
4. Ensemble fix verification (all affinity levels):
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

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

- **Task Profile**: Build the Task Profile (`orchestration.md` Step 1), including Ensemble Affinity
- **Agent spawning**: Unlike the lightweight investigate skill (which works inline), `/fix` spawns investigation agents in parallel via the Dynamic Agent Orchestration process (`orchestration.md`).
  - Minimum 2 hypotheses from distinct failure categories (e.g., code logic vs state/data vs environment/config)
  - More hypotheses when the cause is ambiguous
  - Each agent traces its assigned hypothesis and returns: verdict, confidence, evidence, verification method
- **Ensemble parallel diagnosis**: If ensemble active (Affinity MEDIUM or HIGH):
  - Simultaneously launch Codex **investigate** ensemble point (background) per `ensemble-protocol.md`
  - Codex receives only the symptom description — not Claude's hypotheses (independence rule)
- **Evaluate and synthesize**:
  - Rank Claude agent results by confidence (HIGH > MEDIUM > LOW)
  - If ensemble was launched (Affinity MEDIUM or HIGH):
    - Collect Codex diagnosis result
    - Synthesize per `ensemble-protocol.md`:
      - Claude hypothesis and Codex diagnosis agree → high confidence, proceed
      - Codex found a different root cause → treat as additional hypothesis, verify with targeted check
      - Both have low confidence → CONFLICT, present both with evidence
  - If ensemble was not launched (Affinity LOW):
    - Evaluate Claude agent results only
  - Verify the top result with a targeted check. If verified → proceed. If refuted → try next.
- **Present results**: Follow the Presentation Mode Protocol (`presentation-protocol.md`) before presenting confirmed investigation findings to the user.
- **Full strike rule**:
  - If ensemble was launched: all Claude hypotheses AND Codex diagnosis are refuted → stop and ask the user for additional context. Both models have been deployed — the issue requires information not available in the codebase.
  - If ensemble was not launched: all Claude hypotheses are refuted → stop and ask the user for additional context or suggest escalation to Codex via `/codex:rescue`.

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
4. If ensemble active (all affinity levels — including LOW):
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

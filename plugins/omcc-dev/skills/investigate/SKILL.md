---
name: investigate
description: Systematically diagnoses bugs and problems through multi-hypothesis investigation. Make sure to use this skill whenever the user reports a bug, encounters an error, or describes unexpected behavior — even if they just say "it's broken" or paste an error message. Trigger phrases include "왜 안 되지", "에러", "버그", "원인", "디버깅", "안 돼", "why isn't this working", "what's causing this", "debug this", "find the root cause", "it's broken", "error". Do NOT jump to fixing — investigate first.
---

# Systematic Investigation

Diagnose the root cause of a bug or unexpected behavior through structured investigation.

**Core principle: Do NOT modify code until the root cause is confirmed.**

## When auto-activated (without /fix command)

Follow this lightweight investigation process:

### Step 1: Collect symptoms

1. Identify the error message, stack trace, or unexpected behavior
2. If possible, try to reproduce with Bash
3. Check recent changes with `git log --oneline -10`
4. Read the relevant code area

### Step 2: Form hypotheses

Before investigating, explicitly state 2-3 possible root causes:

- **Hypothesis A** (code logic): Could this be a logic error, wrong condition, boundary issue, or type mismatch?
- **Hypothesis B** (state/data): Could this be a race condition, stale cache, null reference, or data corruption?
- **Hypothesis C** (environment): Could this be a config issue, dependency change, API contract violation, or environment mismatch?

### Step 3: Investigate and verify

1. Start with the most likely hypothesis
2. Trace the relevant code path
3. Look for concrete evidence (not assumptions)
4. If the hypothesis is refuted, move to the next one

**3-strike rule**: If 3 hypotheses fail, stop and report to the user rather than guessing further.

### Step 4: Report

Present findings in this format:

```
Symptom:      [what was observed]
Root cause:   [confirmed cause]
Evidence:     [what proves this]
Impact scope: [how many files/features are affected]
Recommended fix: [approach, not implementation]
```

Do NOT implement the fix in this skill. If the user wants to proceed with fixing, suggest using `/fix` for the full workflow.

---
name: investigate
description: Systematically diagnoses bugs and problems through multi-hypothesis investigation. Make sure to use this skill whenever the user reports a bug, encounters an error, or describes unexpected behavior — even if they just say "it's broken" or paste an error message. Trigger phrases include "why isn't this working", "what's causing this", "debug this", "find the root cause", "it's broken", "error", "unexpected behavior", "not working". Do NOT jump to fixing — investigate first.
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

Follow `orchestration.md`, targeting Investigation Agents based on the symptom characteristics.
Formulate hypotheses matching the bug's symptoms — fewer when the cause seems clear, more when ambiguous.

State each hypothesis explicitly.

### Step 3: Investigate and verify

1. Start with the most likely hypothesis
2. Trace the relevant code path
3. Look for concrete evidence (not assumptions)
4. If the hypothesis is refuted, move to the next one

**Strike rule**: If all hypotheses fail, stop guessing and report to the user.

### Step 4: Report

Follow the Presentation Mode Protocol (`presentation-protocol.md`) before presenting.

Present findings in this format:

```
Symptom:      [what was observed]
Root cause:   [confirmed cause]
Evidence:     [what proves this]
Impact scope: [how many files/features are affected]
Recommended fix: [approach, not implementation]
```

Do NOT implement the fix in this skill. If the user wants to proceed with fixing, suggest using `/fix` for the full workflow.

Note: `/fix` Phase 1 builds on this investigation workflow by spawning parallel agents and adding the strike-rule escalation path. This skill is the standalone, lightweight version.

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

Note: When auto-activated, this is a lightweight standalone version. The command-invoked
mode below adds parallel agents, ensemble coordination, and the full strike rule.

---

## When invoked by command (/fix)

Full investigation with agent spawning, ensemble parallel diagnosis, and escalation paths.

**Do NOT modify code until root cause is confirmed.**

### Step 1: Task Profile

Build the Task Profile (`orchestration.md` Step 1), including Ensemble Affinity.

### Step 2: Spawn investigation agents

Follow `orchestration.md`, targeting Investigation Agents based on symptom characteristics.

- Minimum 2 hypotheses from distinct failure categories
  (e.g., code logic vs state/data vs environment/config)
- More hypotheses when the cause is ambiguous
- Each agent traces its assigned hypothesis and returns:
  verdict, confidence, evidence, verification method

Launch all agents in parallel (single message, multiple Agent calls).

### Step 3: Ensemble parallel diagnosis (if Affinity MEDIUM or HIGH)

Simultaneously with agent dispatch:
- Launch Codex **investigate** ensemble point (background) per `ensemble-protocol.md`
- Codex receives only the symptom description — not Claude's hypotheses (independence rule)

### Step 4: Evaluate and synthesize

1. Rank Claude agent results by confidence (HIGH > MEDIUM > LOW)
2. If ensemble was launched:
   - Collect Codex diagnosis result
   - Synthesize per `ensemble-protocol.md`:
     - Claude hypothesis and Codex diagnosis agree → high confidence, proceed
     - Codex found a different root cause → treat as additional hypothesis, verify
     - Both have low confidence → CONFLICT, present both with evidence
3. Verify the top result with a targeted check. If verified → proceed. If refuted → try next.

### Step 5: Present

Follow the Presentation Mode Protocol (`presentation-protocol.md`) before presenting.

### Full strike rule

- If ensemble was launched: all Claude hypotheses AND Codex diagnosis are refuted →
  stop and ask the user for additional context. Both models have been deployed —
  the issue requires information not available in the codebase.
- If ensemble was not launched: all Claude hypotheses are refuted →
  stop and ask the user for additional context or suggest escalation to
  Codex via `/codex:rescue`.

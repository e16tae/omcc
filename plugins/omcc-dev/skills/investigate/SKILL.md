---
name: investigate
description: Systematically diagnoses bugs and problems through multi-hypothesis investigation. Make sure to use this skill whenever the user reports a bug, encounters an error, or describes unexpected behavior — even if they just say "it's broken" or paste an error message. Trigger phrases include "why isn't this working", "what's causing this", "debug this", "find the root cause", "it's broken", "error", "unexpected behavior", "not working". Do NOT jump to fixing — investigate first.
---

# Systematic Investigation

Diagnose the root cause of a bug or unexpected behavior through structured investigation.

**Core principle: Do NOT modify code until the root cause is confirmed.**

## When auto-activated (without /fix command)

### Step 1: Symptom assessment

1. Identify the error message, stack trace, or unexpected behavior
2. If possible, try to reproduce with Bash
3. Check recent changes with `git log --oneline -10`
4. Read the relevant code area
5. **Determine**: Is this a genuine bug investigation or a simple question/misactivation?
   - Simple question/misactivation → answer directly, skip remaining steps
   - Genuine bug → proceed to Step 2

### Step 2: Full investigation

Same quality as command-invoked mode — the bug deserves the same investigation
regardless of how the user phrased their request.

1. Build the Task Profile (`orchestration.md` Step 1), including Ensemble Affinity
2. Follow `orchestration.md`, targeting Investigation Agents based on symptom characteristics
3. Investigation subagents have read-only file tools and no `git` access.
   When a hypothesis depends on change history (regression, "worked before",
   post-deployment), collect `git log --oneline -20` and the relevant diffs
   (`git show <commit>`, `git diff <range>`) before spawning and embed them
   in the agent's mission — required for the `regression-hunter` pattern
   (see `agent-taxonomy.md`).
4. Launch agents in parallel for multi-hypothesis investigation
5. If Ensemble Affinity is MEDIUM or HIGH: launch Codex **investigate** ensemble point
   in parallel per `ensemble-protocol.md`

### Step 3: Evaluate and synthesize

Same as command-invoked Step 4 below (rank results, synthesize ensemble, verify top result).

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

Do NOT implement the fix in this skill. If the user wants to proceed with fixing,
suggest using `/fix` for the full workflow.

### Strike rule

Same as command-invoked full strike rule below.

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

Investigation subagents have read-only file tools and do not run `git`
themselves. When a hypothesis depends on change history (regression, "worked
before", post-deployment issue), the orchestrator collects `git log --oneline`
and the relevant diffs first and embeds them in the agent's mission —
especially for the `regression-hunter` pattern (see `agent-taxonomy.md`).

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
  automatically launch Codex investigate ensemble point as a last-resort
  independent diagnosis. If Codex also finds no root cause, stop and ask
  the user for additional context.

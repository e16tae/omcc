---
name: brainstorm
description: "Evaluates design decisions through structured research and multi-perspective comparison. Use this skill whenever the user faces a meaningful choice between approaches, asks 'which should I use?', or needs to evaluate options before implementing — even if they don't explicitly request a comparison. Trigger phrases include 'which approach', 'compare options', 'what's the best way', 'evaluate alternatives', 'design decision', 'should I use X or Y', 'how should I do this'."
---

# Structured Brainstorm

Evaluate choices through evidence-based research and multi-perspective comparison.
The goal: the user can make an informed decision even in domains where they lack
specialized knowledge.

## When auto-activated (without /start or /audit command)

### Step 1: Clarify the choice

1. Identify the decision to be made
2. If only one option is apparent, search for alternatives before proceeding
3. Quick context scan: check project structure, tech stack, and constraints

### Step 2: Research

Before proposing options, gather evidence from authoritative sources.
Do not rely solely on internal knowledge — search first, then synthesize.

**Search targets:**
- **Official documentation**: Language/framework docs, API references, release notes
- **Standards and specifications**: RFCs, W3C, ECMA, POSIX, OpenAPI, etc.
- **Community consensus**: Framework team recommendations, ecosystem-wide patterns
- **Benchmarks and empirical data**: Performance comparisons, adoption metrics
- **Known pitfalls**: Migration guides, deprecation notices, post-mortems

Use WebSearch for current best practices, benchmarks, and community consensus.
Use WebFetch for specific documentation pages when a URL is known.
Name or link every source so the user can verify independently.

If web search tools are unavailable, state this limitation and base research on
internal knowledge, clearly distinguishing verified facts from best-effort recall.

**Privacy guardrails:**
- Use generic technology terms in search queries, not internal identifiers
- Never include proprietary code snippets, internal paths, or customer data in searches
- When confidentiality is unclear, ask the user before searching

If no external source applies (purely project-internal choice), state explicitly:
"No external standards apply — comparison based on project context."

### Step 3: Compare — Five Perspectives

Evaluate each option from five perspectives. Not all perspectives carry equal weight
in every decision — state which are most decisive for this particular choice and why.

| # | Perspective | Core Question |
|---|-------------|---------------|
| 1 | **Essence** | Does this solve the fundamental problem, or just a symptom? |
| 2 | **Foundation** | Is this architecturally sound as a long-term base? |
| 3 | **Standards** | Does it align with industry standards and specifications? |
| 4 | **Best Practice** | Is it the canonical approach recommended by authoritative sources? |
| 5 | **Practical Fit** | Is it the best choice for this project's specific constraints? |

Follow the Presentation Mode Protocol (`presentation-protocol.md`) before presenting
the comparison. In interview mode, one item = one option with its five-perspective analysis.

#### REQUIRED output format — for each option:

```
### Option [letter]: [name]
[1-sentence summary of the approach]

- **Essence**: [substantive assessment — not one-liners but specific reasoning
  explaining WHY this does or doesn't address the fundamental problem] — [source]
- **Foundation**: [substantive assessment — evaluate long-term architectural health,
  maintenance cost, extensibility, coupling implications] — [source]
- **Standards**: [substantive assessment — cite specific standards, RFCs, or specs.
  If none apply, explain why and what adjacent standards exist] — [source]
- **Best Practice**: [substantive assessment — name specific authoritative sources,
  framework recommendations, or community consensus] — [source]
- **Practical Fit**: [substantive assessment — evaluate against THIS project's
  specific tech stack, team constraints, timeline, and existing patterns]
```

#### REQUIRED output format — after all options:

```
### Key Differences
| Perspective | Option A | Option B | ... |
|-------------|----------|----------|-----|
| Essence     | ...      | ...      |     |
| Foundation  | ...      | ...      |     |
| Standards   | ...      | ...      |     |
| Best Practice | ...    | ...      |     |
| Practical Fit | ...    | ...      |     |
```

### Step 4: Recommend

Always provide a recommendation. Never leave the user with only a comparison.

When Essence and Foundation clearly favor one option, recommend it. Do not downgrade
to a different option due to Practical Fit alone — address practical concerns in
the execution plan instead.

#### REQUIRED output format:

```
**Recommendation: Option [letter] ([name])** — Confidence: [HIGH/MEDIUM/LOW]

[2-3 sentence rationale explaining WHY, not just WHAT]

Decisive factors: [which 1-2 perspectives most influenced this recommendation]
Sources: [key references that support the recommendation]

Choose [other option] instead if: [specific conditions under which a different
option becomes the better choice]
```

**Confidence levels:**
- **HIGH** — Strong evidence, clear standards alignment, community consensus
- **MEDIUM** — Good evidence, but reasonable alternatives exist
- **LOW** — Limited evidence, subjective tradeoffs, heavily context-dependent

**Wait for user to choose a direction** before proceeding to implementation.

If the user says "just do it" or "your call", present only the recommendation
(skip the interactive comparison) and confirm before proceeding.

### Edge cases

- **Only one viable option**: Still follow the protocol. Present the single option
  with its perspective analysis and note why alternatives were excluded.
- **All options are roughly equal**: Set confidence to LOW, state that the choice is
  preference-dependent, and recommend based on Practical Fit as the tiebreaker.
- **Rapidly evolving domain**: Flag that the landscape is shifting, cite the date
  of sources, and note what to watch for that might change the recommendation.
- **User rejects all options**: Ask what aspect was missing or unsatisfactory, then
  return to Step 2 (Research) with the refined constraints. If rejected a second
  time, offer to abort the workflow.
- **Search returns no relevant results**: State "No search results found" for the
  affected perspective. Base that perspective's assessment on internal knowledge and
  label it explicitly as "internal knowledge — no external sources found."

---

## When invoked by command (/start, /audit)

Full brainstorm with Task Profile and ensemble coordination.
Follow all auto-activated steps (1-4) above, with these additions:

### Pre-brainstorm: Task Profile

Before Step 1, build the Task Profile:

1. Clarify the goal: "What problem does this solve? What does success look like?"
2. Quick context scan: check project structure, tech stack, and key config files
   to inform the Practical Fit perspective
3. Build the Task Profile (`orchestration.md` Step 1), including Ensemble Affinity

### Ensemble coordination (if Affinity MEDIUM or HIGH)

1. **Before Step 2 (Research)**: Launch Codex **brainstorm** ensemble point
   (background) per `ensemble-protocol.md`
2. **After Step 4 (Recommend)**: Collect Codex brainstorm result
   (wait for background notification if not yet complete)
3. **Synthesize** per `ensemble-protocol.md`:
   - Add any Codex-proposed approaches that Claude did not consider
   - Elevate confidence for approaches both models recommended
   - Label unique approaches by source

### Approval gate

**Wait for user to choose a direction** — do not proceed to the next phase
without explicit approval.

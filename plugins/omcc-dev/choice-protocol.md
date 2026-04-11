# Evidence-Based Choice Protocol

When presenting the user with a choice between approaches, technologies, patterns, or tools,
follow this protocol. The goal: the user can make an informed decision
even in domains where they lack specialized knowledge.

---

## When This Protocol Applies

Activates when:
- The user faces a meaningful choice between 2+ approaches
- A design decision requires selecting between competing patterns or technologies
- Phase 1 (Brainstorm) of `/start` presents approach options
- The user explicitly asks "which should I use?" or the context implies such a question

Does NOT apply to:
- Binary confirmations (plan approval, yes/no questions)
- Scope selection where the user has already specified their choice
- Internal orchestration decisions (see `orchestration.md`)
- Bug hypothesis ranking (handled by `/fix` investigation workflow)

---

## Phase 1: Research

Before presenting options, gather evidence from authoritative sources.
Do not rely solely on internal knowledge — search first, then synthesize.

### Search targets

- **Official documentation**: Language/framework docs, API references, release notes
- **Standards and specifications**: RFCs, W3C, ECMA, POSIX, OpenAPI, etc.
- **Community consensus**: Framework team recommendations, ecosystem-wide patterns
- **Benchmarks and empirical data**: Performance comparisons, adoption metrics
- **Known pitfalls**: Migration guides, deprecation notices, post-mortems

### How to search

- Use WebSearch for current best practices, benchmarks, and community consensus
- Use WebFetch for specific documentation pages when a URL is known
- Name or link every source so the user can verify independently
- If web search tools are unavailable, state this limitation and base research on
  internal knowledge, clearly distinguishing verified facts from best-effort recall

### Privacy guardrails

- Use generic technology terms in search queries, not internal identifiers
  (e.g., "Python async task queue" instead of "our CeleryWorker service")
- Never include proprietary code snippets, internal paths, error logs,
  or customer/tenant data in search queries
- When confidentiality is unclear, ask the user before searching

### Research is mandatory

If no external source applies (purely project-internal choice), state this explicitly:
"No external standards apply — comparison based on project context."

---

## Phase 2: Compare — Five Perspectives

Evaluate each option from five perspectives. Not all perspectives carry equal weight
in every decision — state which are most decisive for this particular choice and why.

### The Five Perspectives

| # | Perspective | Core Question |
|---|-------------|---------------|
| 1 | **Essence** | Does this solve the fundamental problem, or just a symptom? |
| 2 | **Foundation** | Is this architecturally sound as a long-term base? |
| 3 | **Standards** | Does it align with industry standards and specifications? |
| 4 | **Best Practice** | Is it the canonical approach recommended by authoritative sources? |
| 5 | **Practical Fit** | Is it the best choice for this project's specific constraints? |

### Comparison output

For each option, present a structured breakdown:

```
### Option A: [name]
[1-sentence summary of the approach]

- **Essence**: [assessment] — [source if applicable]
- **Foundation**: [assessment] — [source if applicable]
- **Standards**: [assessment] — [source if applicable]
- **Best Practice**: [assessment] — [source if applicable]
- **Practical Fit**: [assessment]
```

After all options, add a side-by-side summary highlighting where they diverge:

```
### Key Differences
| Perspective | Option A | Option B | ... |
|-------------|----------|----------|-----|
| Essence | ... | ... | |
| Foundation | ... | ... | |
| Standards | ... | ... | |
| Best Practice | ... | ... | |
| Practical Fit | ... | ... | |
```

---

## Phase 3: Recommend

Always provide a recommendation. Never leave the user with only a comparison and no guidance.

### Recommendation structure

1. **Recommended option**: Which option, and a 2-3 sentence rationale
2. **Confidence level**:
   - **HIGH** — Strong evidence, clear standards alignment, community consensus
   - **MEDIUM** — Good evidence, but reasonable alternatives exist
   - **LOW** — Limited evidence, subjective tradeoffs, heavily context-dependent
3. **Decisive factors**: Which 1-2 perspectives most influenced this recommendation
4. **Sources**: Key references that support the recommendation
5. **When to choose differently**: Explicitly state conditions under which a non-recommended option becomes the better choice

### Example

> **Recommendation: Option A (Zod)** — Confidence: HIGH
>
> Zod is the TypeScript-native validation library recommended by the tRPC, Next.js, and
> React Hook Form ecosystems. It addresses the fundamental need (type-safe runtime validation
> with zero schema/type duplication) and aligns with current community standards.
>
> Decisive factors: Standards, Best Practice
> Sources: Zod documentation, tRPC official guide, npm trends (Zod vs Joi vs Yup)
>
> Choose Option B (Joi) instead if: the project is pure Node.js without TypeScript,
> or the team has deep Joi expertise and migration cost outweighs the benefit.

---

## Edge Cases

- **Only one viable option**: Still follow the protocol. Present the single option
  with its perspective analysis and note why alternatives were excluded.
- **All options are roughly equal**: Set confidence to LOW, state that the choice is
  preference-dependent, and recommend based on Practical Fit as the tiebreaker.
- **User says "just pick one"**: Provide the recommendation immediately, but still include
  the decisive factors and confidence level so the user understands the basis.
- **Rapidly evolving domain**: Flag that the landscape is shifting, cite the date of sources,
  and note what to watch for that might change the recommendation.

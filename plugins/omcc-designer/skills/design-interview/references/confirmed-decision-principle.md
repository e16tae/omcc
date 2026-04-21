# Confirmed Decision Principle

Only user-confirmed decisions may be encoded in the design brief and
downstream outputs.

1. Phase 1 (analysis or extraction) produces **estimations** with confidence
   levels — these are proposals, not decisions.
2. Phase 2 (interview) **confirms or corrects** each estimation through user
   interaction.
3. Phase 3 (brief) encodes only confirmed items. Unconfirmed items are tagged
   `[unconfirmed]` and excluded from downstream generation.
4. Phase 4 (domain output) operates only on confirmed brief content.
5. **Brief protection**: Never overwrite existing briefs without user
   confirmation. New consultations produce new briefs.
6. **Decision trail**: The brief's Decision Log and Supplementary Notes
   preserve what was confirmed, what was recommended, and what was rejected.

This principle also applies to evaluation findings (audit) and planning
recommendations (plan) — these are estimations until the user confirms a
remediation direction or plan.

The LLM must not autonomously promote estimations to decisions. If the user
says "I don't know" or skips a question, that field remains unconfirmed.

**Why**: Design is subjective. If the LLM's color palette guess silently
becomes the final palette without user awareness, the deliverable loses
client trust. "Only confirmed decisions" is the principle — from estimation
through encoding, storage, and retrieval.

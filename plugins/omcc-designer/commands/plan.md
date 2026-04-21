---
description: Create a design strategy and deliverable roadmap for multi-piece projects
argument-hint: Project description (e.g., "product launch for our new SaaS platform")
---

# Plan

$ARGUMENTS

Use `TaskCreate` and `TaskUpdate` to track progress.

---

## Planning Pipeline

Follow the design-planning skill's command-invoked mode (`skills/design-planning/SKILL.md`).

The skill handles analysis (internal), scope confirmation, shared design
decisions, sequencing, and roadmap generation — all as a single, self-contained
pipeline. Save path per `skills/brief-generation/references/output-file-rules.md`.

---

## Completion

After design_plan.md is saved, output: "✓ Design strategy complete." with
the plan file path and a summary of the deliverable list. Offer to transition
to `/omcc-designer:start` for the first deliverable (using the plan's shared
design decisions as pre-confirmed context).

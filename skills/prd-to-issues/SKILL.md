---
name: prd-to-issues
description: "PRD to issues/tasks decomposition skill. Trigger whenever the user invokes /prd-to-issues, asks to \"break this into tasks\", \"turn this into issues\", \"create a backlog from this\", \"make these into tickets\", \"build a Kanban from this\", or has a completed PRD or spec and needs it decomposed into independently actionable work items. Also trigger when a user wants to plan a sprint, populate a GitHub project, Jira, or Linear backlog, or set up work for parallel AI agent execution. If a /write-a-prd session just completed, offer this skill immediately."
---

# PRD to Issues

## Purpose

Decompose a PRD into independently actionable work items (issues / tasks / tickets)
that can be assigned, tracked, and executed in parallel.

## Decomposition rules

- Each issue must be completable in isolation (no hidden dependencies unless stated)
- Each issue must have a clear, verifiable done state
- Prefer small issues over large ones — split anything > 1 day of work
- Group issues by phase: PLAN → BUILD → TEST → SHIP

## Issue format

```markdown
## [PHASE-N] Issue title

**Type:** feature | fix | chore | spike
**Depends on:** [issue numbers, or none]
**Estimate:** [S / M / L]

### Context
[Why this issue exists — one sentence]

### Acceptance criteria
- [ ] [criterion 1]
- [ ] [criterion 2]

### Notes
[Implementation hints, constraints, or open questions]
```

## Output

Produce a numbered list of issues in phase order.
After the list, provide a dependency graph (text-based is fine).

## Platform variants

- **GitHub Issues / Linear / Jira:** use the format above
- **TASKS.md:** output as a checklist with status column
- **Kanban:** group by phase as swimlanes

## Handoff

When issues are ready, the next step is `tdd` — start with failing tests
before writing any implementation code.

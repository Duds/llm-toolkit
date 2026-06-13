---
name: orient
description: >-
  Session entry point for Cowork work sessions. Reads the project's TASKS.md,
  triages open tasks by dependency order and tangible impact, assesses
  ambiguity, and routes to the right next action or skill. Use this skill at
  the start of every new Cowork session — even if the user seems to know what
  they want, run the triage first. Triggers on: what should I work on, orient
  me, start my session, what's next, check my tasks, triage my tasks,
  prioritise my work, what should I tackle first, or any session-opening
  message without a specific task named. If the user starts a session by
  asking about tasks or priorities, this skill runs first before any other
  action.
---

# Orient — Session Start

## Purpose

Read TASKS.md, triage open work, and identify the single best next action.

## Steps

1. Read `TASKS.md` in the project root. If it doesn't exist, say so and offer to create it.
2. List open tasks grouped by status (blocked / ready / in-progress).
3. Score each ready task by:
   - **Dependency order** — tasks that unblock others score higher
   - **Tangible impact** — tasks with visible, verifiable output score higher
   - **Ambiguity** — tasks that are unclear score lower (flag them)
4. Recommend the single highest-priority task.
5. If the top task is ambiguous, ask one clarifying question before proceeding.

## Output format

```
## Session start — [project name]

**Open tasks:** N
**Recommended next:** [task name]
**Why:** [one sentence]

Ready to start? I'll [brief description of first action].
```

## Notes

- Never present all tasks as equally valid — make a recommendation.
- If TASKS.md has no open tasks, say so and ask what to work on.
- If the user overrides the recommendation, proceed with their choice.

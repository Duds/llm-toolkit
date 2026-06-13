---
name: close-and-learn
description: >-
  Close a session, capture lessons, update memory, and generate a copy-ready
  handoff prompt for a fresh session. Trigger whenever the user says "close
  this session", "wrap up", "lessons learned", "what did we learn", "write a
  handoff prompt", "close and learn", or at the natural end of a significant
  task or engagement. Also trigger when the user invokes /close-and-learn.
  Always run this before starting a new session if work is continuing — it
  preserves context without bloating the next session's inference window.
---

# Close and Learn

## Purpose

End a session cleanly: capture what was decided, what was learned, and what comes next.
Output a handoff prompt the user can paste into a fresh session.

## Steps

1. **Summarise decisions made** — what was built, chosen, or resolved.
2. **Capture lessons learned** — what worked, what didn't, what to do differently.
3. **Standardisation check** — ask: *Did this engagement change how we work?*
   - **Method changed** (a skill, playbook, or instruction should work differently): update the component now, before closing. Learning that sits in memory without changing a component is archived, not standardised.
   - **Principle changed** (a design principle or the framework itself shifted): flag it for a framework document update.
   - **Nothing changed**: note the null result and move on — it's still data.
   The flywheel only closes if something is different after this step.
4. **List outstanding items** — anything unfinished, deferred, or blocked.
5. **Update TASKS.md** — mark completed tasks done, add any new ones surfaced.
6. **Generate handoff prompt** — a self-contained paragraph the user can paste to resume.

## Handoff prompt format

```
## Handoff — [project] — [date]

**Last session:** [1–2 sentences on what was done]
**Decisions:** [bullet list]
**Outstanding:** [bullet list]
**Start here:** [the single next action]
```

## Notes

- Keep the handoff prompt under 200 words — it must fit in a new session's opening without dominating context.
- Don't summarise the whole project history — only what's needed to resume.
- If TASKS.md was not updated during the session, do it now before closing.

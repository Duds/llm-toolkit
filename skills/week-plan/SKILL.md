---
name: week-plan
description: >-
  Set weekly priorities and plan the week ahead. Use this skill whenever Dale
  says "plan my week", "week plan", "what should I focus on this week",
  "set my priorities", "/week-plan", or starts a Monday/Friday session asking
  about the week ahead. Reads TASKS.md files across all project streams, asks
  about calendar shape (or checks if a calendar MCP is available), and outputs
  a date-stamped YYYY-MM-DD-week-priorities.md file in _plans/ (date = Monday
  of the target week). Run this before daily planning to set the frame for
  the week.
---

# Week Plan

## Purpose

Set clear weekly priorities across Dale's contractor streams at DCCEEW, balancing delivery across **environment-digital-gateway** and **national-epa-remediation** under the **environment-digital-reform** program.

---

## Step 1: Determine Target Week

- Default: current week (Mon–Fri)
- If today is Friday or weekend: offer next week instead
- If user passes `next`: plan next week
- Calculate the Monday date for the target week (`YYYY-MM-DD`)

---

## Step 2: Check for Calendar Access

Try to detect if a calendar MCP tool is available in this session. Check the available tool list for anything calendar-related (e.g. Google Calendar, Outlook, or similar).

- **If calendar is available:** pull the week's events and summarise by day (meeting count, largest free block, best deep-work day)
- **If not available (expected at DCCEEW due to security constraints):** ask the user one question:

  > "What does your week look like? Any days packed with meetings, or open blocks for focused work?"

  Accept a casual answer — even "mostly free" or "Tuesday is back-to-back" is enough to shape the plan.

---

## Step 3: Gather Task Context

### 3.1 Root tasks

Read `Projects/TASKS.md`. Extract:
- Open items (unchecked `- [ ]`)
- Note anything blocked or dependency-gated

### 3.2 Stream tasks

Check for `TASKS.md` in each stream directory:
- `environment-digital-reform/environment-digital-gateway/TASKS.md`
- `environment-digital-reform/national-epa-remediation/TASKS.md`

If a stream TASKS.md is **missing**, note it — offer to create one at the end of this session (don't interrupt the planning flow).

### 3.3 Last week's plan

Check for `_plans/[last-monday]-week-priorities.md` (e.g. `_plans/2026-04-14-week-priorities.md`). If it exists, scan for:
- Items marked incomplete → candidate carry-overs
- "Next week" or "Focus" notes at the bottom

---

## Step 4: Suggest Priorities

Don't just ask "what are your top 3?" — synthesise a suggestion from the context gathered.

Think about:
- **Stream balance:** are both gateway and remediation getting attention, or is one being neglected?
- **Urgency:** any tasks that are blocking others or have external dependencies?
- **Carry-overs:** what didn't get done last week that still matters?
- **Calendar fit:** if a day is meeting-heavy, avoid scheduling deep work there

Present 3–4 suggested priorities like this:

> "Based on your tasks and week shape, here's what I'd suggest:
>
> 1. **[Task]** — environment-digital-gateway — [why it matters now]
> 2. **[Task]** — national-epa-remediation — [why: stream has had no recent activity / blocked item / due soon]
> 3. **[Task]** — program-level — [e.g. a root TASKS item or cross-stream coordination]
>
> **Week fit:** [Day] looks best for deep work. [Day] is stacked — good for async/reviews only.
>
> Does this feel right? Add, swap, or drop anything."

Wait for the user to confirm or adjust before proceeding.

---

## Step 5: Generate [monday]-week-priorities.md

Write `_plans/[monday-date]-week-priorities.md` (e.g. `_plans/2026-04-21-week-priorities.md`). Create `_plans/` if it doesn't exist. Each week gets its own file — no archiving needed.

```markdown
# Week Priorities

**Week of:** [Monday YYYY-MM-DD]
**Generated:** [timestamp]

---

## Week Shape

[Either from calendar data or user's description]

| Day | Notes |
|-----|-------|
| Mon | [e.g. 3 meetings, light afternoon] |
| Tue | [e.g. back-to-back] |
| Wed | [e.g. open — deep work] |
| Thu | [e.g. 2 meetings] |
| Fri | [e.g. light, good for wrap-up] |

**Best focus day:** [Day]

---

## Top Priorities

### 1. [Priority title] — [stream: gateway / remediation / program]
- **Why this week:** [one sentence]
- **Done when:** [concrete success criteria]
- **Best slot:** [Day or "any open block"]

### 2. [Priority title] — [stream]
- **Why this week:** [one sentence]
- **Done when:** [concrete success criteria]
- **Best slot:** [Day]

### 3. [Priority title] — [stream]
- **Why this week:** [one sentence]
- **Done when:** [concrete success criteria]
- **Best slot:** [Day]

---

## Carry-overs

[Items from last week that weren't completed — or "None" if clean slate]

- [ ] [Task] — [why it's still relevant]

---

## Stream Balance

| Stream | This week's focus | Status |
|--------|------------------|--------|
| environment-digital-gateway | [brief] | 🟩 Active / 🟨 Light / 🟥 Neglected |
| national-epa-remediation | [brief] | 🟩 Active / 🟨 Light / 🟥 Neglected |
| program-level | [brief] | — |

---

## End of Week Review

*Fill in on Friday*

**Completed:**
-

**Didn't finish:**
-

**Carry to next week:**
-

**One thing to do differently:**
-
```

---

## Step 6: Wrap Up

After saving the file, summarise:

> "Week planned. Saved to `_plans/[monday-date]-week-priorities.md`
>
> **Your top 3:**
> 1. [P1] — [stream] — [day]
> 2. [P2] — [stream] — [day]
> 3. [P3] — [stream] — [day]
>
> **Stream balance:** [gateway: active / remediation: light — worth a task this week]"

If any stream TASKS.md files were missing, offer now:
> "Also — neither gateway nor remediation has a TASKS.md yet. Want me to create them with your open items scaffolded in?"

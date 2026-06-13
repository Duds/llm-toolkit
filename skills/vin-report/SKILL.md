---
name: vin-report
description: Drafts Dale's fortnightly CTO Consulting dashboard update for Vin Gray (Director of Delivery, CTO Consulting). Use this skill whenever Dale says "vin report", "write my CTO report", "fortnightly report for Vin", "/vin-report", or asks to draft his dashboard update for Vin. Also trigger proactively on fortnightly Wednesday afternoons when Dale starts a session — this report is due COB every second Wednesday. The report is saved to reports/ctoc-reports/ for record.
---

# Vin Report — Fortnightly CTO Dashboard Update

## Purpose

Draft Dale's fortnightly dashboard bullet-point update for Vin Gray (Director of Delivery, CTO Consulting), to support Vin and Dan's meeting with Rhiannon. The report covers Dale's work on the AI Program at DCCEEW.

**Recipient:** Vin Gray — vin.gray@ctoconsulting.com.au  
**Cadence:** Every second Wednesday, due COB  
**Format:** Email-ready, copy-paste straight into Outlook  
**Saved to:** `Projects/reports/ctoc-reports/` for record

---

## Step 1: Gather context

Read these sources in parallel:

1. **Week plan** — find the most recent file in `~/Projects/_plans/` (named `YYYY-MM-DD-week-priorities.md`). Extract: top priorities, achievements noted in the end-of-week review, carry-overs, and active blockers for the ICTDS-AI-Capability stream.

2. **TASKS.md** — read `~/Projects/TASKS.md`. Focus on the ICTDS-AI-Capability section: what's in progress, what's recently completed, what's blocked.

3. **Project TASKS.md** — if `~/Projects/ictds-ai-capability/TASKS.md` exists, read it for more granular delivery detail.

4. **Previous report** — check `~/Projects/reports/ctoc-reports/` for the most recent report to maintain continuity.

The goal is to reconstruct what Dale has been doing for the past fortnight — what he progressed, what he finished, and what's slowing him down.

---

## Step 2: Draft the report

Write the report in this exact structure and tone. Keep bullets concise — one idea per bullet, plain business English, no jargon. Do not pad. Do not use bold or markdown inside the body — this will be pasted into Outlook.

```
Hi Vin, see below report.

AI Program: ICT AI Product Factory (Enduring AI Capability Uplift)
Working on:
•	[what Dale is currently progressing — 2–3 bullets covering active workstreams]
Key achievements this fortnight:
•	[concrete, verifiable things completed since the last report — 1–3 bullets]
Risks / roadblocks:
•	[active blockers, dependencies, or risks to delivery — 2–4 bullets]

Dale Rogers
Service Design Contractor | ICT Strategy and Investment
Department of Climate Change, Energy, the Environment and Water
E: dale.rogers@dcceew.gov.au
P: 0400 944492
```

**Tone guidance:**
- Professional but direct — this is a project status update, not a narrative
- "Working on" = current activity, present tense
- "Key achievements" = what finished or reached a milestone, past tense
- "Risks / roadblocks" = genuine blockers, not aspirational caveats
- Avoid naming internal meetings or people who Vin wouldn't know — keep references generic unless Dale confirms otherwise (e.g., "internal stakeholder catch-up" rather than a specific name)

---

## Step 3: Confirm with Dale

Before presenting the final copy, ask Dale three things:

1. **Anything new this fortnight not captured in the plan or tasks?** (e.g., a decision made, a new scope item, a meeting that changed things)
2. **Any internal names or meetings to make generic?** (Vin doesn't have full context on internal DCCEEW stakeholders)
3. **Anything to cut?** (risks or achievements that aren't relevant at the CTO Consulting level)

Make the adjustments based on Dale's answers, then present the final version.

---

## Step 4: Save and Output

1. **Save the report** to:
   ```
   ~/Projects/reports/ctoc-reports/YYYY-MM-DD-vin-report.md
   ```

2. **Present the final report** as a clean code block — ready to copy-paste into an Outlook email to vin.gray@ctoconsulting.com.au with no further editing needed.

3. **Remind Dale:** The next report is due in two weeks (on the following second Wednesday).

---

## Report File Naming Convention

All Vin reports follow the naming pattern:
```
YYYY-MM-DD-vin-report.md
```

This ensures:
- Chronological sorting in file listings
- Easy identification of report period
- Consistency with other dated files in the workspace

---

## Notes

- The Vin report is a concise email-style update for CTOC Consulting
- Saved to `reports/ctoc-reports/` for record
- For the internal DCCEEW ICTSD report, use the ict-report skill (saved to `reports/ict-reports/`)

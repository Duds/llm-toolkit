---
name: ict-report
description: Drafts Dale's weekly ICT Business & Governance Branch status report for internal DCCEEW ICTSD distribution. Use this skill whenever Dale says "ict report", "write my ICT report", "weekly ICT report", "/ict-report", or asks to draft his status update for the ICT Business & Governance Branch. This is the internal DCCEEW report (distinct from the CTOC report for Vin). The report is saved to reports/ict-reports/ for record.
---

# ICT Report — Weekly DCCEEW ICTSD Status Update

## Purpose

Draft Dale's weekly status report for the ICT Business & Governance Branch at DCCEEW. This is an internal report for ICTSD distribution, distinct from the CTOC consulting report for Vin Gray.

**Audience:** ICT Business & Governance Branch leadership  
**Cadence:** Weekly, typically Friday  
**Format:** Markdown report with YAML frontmatter  
**Saved to:** `Projects/reports/ict-reports/` for record

---

## Step 1: Gather Context

Read these sources in parallel:

1. **Week plan** — find the most recent file in `~/Projects/_plans/` (named `YYYY-MM-DD-week-priorities.md`). Extract: top priorities, achievements, carry-overs, and active blockers.

2. **TASKS.md** — read `~/Projects/TASKS.md` and relevant project TASKS.md files for:
   - `ictds-ai-capability/TASKS.md` — AI Product Factory work
   - `environment-digital-reform/TASKS.md` — EDG program work
   - Any other active project TASKS files

3. **Previous ICT report** — check `~/Projects/reports/ict-reports/` for the most recent report to maintain continuity.

---

## Step 2: Draft the Report

Write the report in this structure. Use professional, direct language appropriate for internal ICTSD distribution.

### Report Template

```markdown
---
title: "ICT Business & Governance — Weekly Status Report"
date: YYYY-MM-DD
period: "Week ending Friday, DD MMMM YYYY"
type: report
division: ICT Business & Governance
---

# ICT Business & Governance — Weekly Status Report

**Section:** ICT Strategy and Investment  
**Week Ending:** Friday, [DATE]  
**Report Date:** [DATE]

---

## Acronyms Glossary

- **ConOps** – Concept of Operations for how a capability will run day-to-day
- **EDR** – Environment Digital Reform program
- **EDG** – Environment Digital Gateway (formerly Wayfinder)
- **EPBC** – Environment Protection and Biodiversity Conservation
- **FinOps** – Cloud cost optimisation and financial governance practice
- **GCU** – Geospatial Capability Uplift
- **ICTSD** – ICT Digital Strategy & Design function
- **RDI** – Request for Digital Investment (internal investment intake)

---

## Executive Summary

[Brief 2-3 sentence summary of the week's progress]

---

## Modern AI Enduring Capability

| Item | Status | Notes |
|------|--------|-------|
| [Work item] | [Status] | [Brief notes] |
| [Work item] | [Status] | [Brief notes] |

---

## AI in Environment (Environment Digital Reform)

| Item | Status | Notes |
|------|--------|-------|
| [Work item] | [Status] | [Brief notes] |
| [Work item] | [Status] | [Brief notes] |

---

## EPBC Reform Legacy Remediation

| Item | Status | Notes |
|------|--------|-------|
| [Work item] | [Status] | [Brief notes] |

---

## Key Upcoming

- [Upcoming item with date]
- [Upcoming item with date]

---

*Report generated: [DATE]*
```

**Tone guidance:**
- Professional and direct — this is an internal status update
- Use DCCEEW/ICTSD terminology and acronyms appropriately
- Include specific details relevant to internal stakeholders
- Flag blockers or risks that need ICTSD leadership attention

---

## Step 3: Confirm with Dale

Before finalizing, ask Dale:

1. **Anything new this week not captured in the plan or tasks?**
2. **Any items to emphasize for ICTSD leadership?**
3. **Any blockers or risks to escalate internally?**

Make adjustments based on Dale's answers, then finalize.

---

## Step 4: Save and Output

1. **Save the report** to:
   ```
   ~/Projects/reports/ict-reports/YYYY-MM-DD-ict-weekly-report.md
   ```

2. **Present the final report** for review.

3. **Remind Dale:** The next report is due next week (typically Friday).

---

## Report File Naming Convention

All ICT reports follow the naming pattern:
```
YYYY-MM-DD-ict-weekly-report.md
```

This ensures:
- Chronological sorting in file listings
- Easy identification of report period
- Consistency with other dated files in the workspace

---

## Notes

- The ICT report is for internal DCCEEW ICTSD distribution
- It can include more detail and internal terminology than the CTOC report
- Saved to `reports/ict-reports/` for record
- For the CTOC consulting report (for Vin Gray), use the vin-report skill (saved to `reports/ctoc-reports/`)

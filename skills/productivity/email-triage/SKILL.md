---
name: email-triage
description: "Automated email triage for Gmail. Labels, archives, and generates morning briefs."
version: 1.0.0
author: Dale Rogers
platforms: [macos]
metadata:
  hermes:
    tags: [gmail, email, triage, automation, morning-brief]
---

# Email Triage Protocol

## Overview

Automated Gmail triage using the numbered label system (1-Work through 9-For-Deletion). Runs as a cron job or on-demand.

## Label System

| Label | Purpose | Auto-apply Rules |
|-------|---------|------------------|
| 1-Work & Career | Job-related | Sender domain: linkedin.com, seek.com.au, indeed.com, glassdoor.com |
| 1-Work & Career/Job Opportunities | Job postings | Subject contains: "job", "opportunity", "hiring", "role" |
| 1-Work & Career/Interviews & Offers | Interview stuff | Subject contains: "interview", "offer", "screening" |
| 2-Projects & Code | Dev projects | Sender: github.com, gitlab.com, vercel.com, supabase.io |
| 2-Projects & Code/GitHub Notifications | GitHub alerts | Sender: noreply@github.com |
| 3-Finance & Admin | Money stuff | Sender domain: ato.gov.au, mygov.gov.au, bank domains |
| 4-Personal & Family | Personal | Sender: known contacts, family domains |
| 5-Hobbies & Interests | Fun stuff | Sender: clcboats.com, model-building, sailing |
| 6-Health & Wellness | Medical | Sender: health domains, insurance |
| 7-Community & Events | Events | Sender: meetup.com, eventbrite.com, ticketing |
| 7-Community & Events/Newsletters | Newsletters | Bulk sender, unsubscribe link, weekly digest |
| 8-Subscriptions & Services | SaaS | Sender: aws.amazon.com, tailscale.com, firecrawl.dev |
| 9-For-Deletion | Trash | Dating apps, expired offers, spam patterns |
| 9-For-Deletion/Expired Offers | Old promos | Subject: "expires", "last chance", "final hours" |
| 9-For-Deletion/Newsletter Cleanup | Old newsletters | Older than 30 days, already read |

## Keep in Inbox (Never Auto-archive)

- Chesapeake Light Craft (info@clcboats.com)
- Paint on Plastic (context needed — add sender)
- Personal contacts (family, Jane, close friends)
- Urgent: interview confirmations, deadline reminders

## Auto-archive Rules

- Newsletters older than 7 days (unless unread)
- GitHub notifications older than 3 days (unless unread)
- Promotional emails with "expires" in subject
- Dating app notifications (Hinge, Tinder, Bumble)
- Automated system emails (codespace warnings, etc.)

## Morning Brief Format

```
📧 Morning Email Brief — [Date]

Unread: [N] total
- Work: [N] (job alerts, interviews)
- Projects: [N] (GitHub, deployments)
- Finance: [N] (bills, statements)
- Personal: [N] (family, friends)
- Hobbies: [N] (Chesapeake Light Craft, etc.)
- Events: [N] (meetups, tickets)
- Subscriptions: [N] (SaaS, newsletters)
- Trash: [N] (auto-archived)

🔥 Urgent:
- [Sender] — [Subject] (if flagged)

📌 Keep in Inbox:
- [Sender] — [Subject]

✅ Auto-archived:
- [N] newsletters
- [N] expired offers
- [N] system notifications
```

## Implementation

### Script Location
`~/.agents/scripts/email-triage.py`

### Cron Schedule
```cron
0 8 * * * /Users/dalerogers/.agents/scripts/email-triage.py --brief
0 22 * * * /Users/dalerogers/.agents/scripts/email-triage.py --cleanup
```

### Manual Run
```bash
~/.agents/scripts/email-triage.py --dry-run  # Preview only
~/.agents/scripts/email-triage.py --apply     # Actually apply labels/archive
~/.agents/scripts/email-triage.py --brief     # Generate morning brief
```

## Safety Rules

1. **Never delete** — only archive (Gmail "All Mail" still has it)
2. **Never mark read** — only label and archive
3. **Keep-list override** — Chesapeake Light Craft always stays in inbox
4. **Approval for bulk** — >10 auto-archives requires confirmation
5. **Log everything** — all actions written to ~/.agents/logs/email-triage.log

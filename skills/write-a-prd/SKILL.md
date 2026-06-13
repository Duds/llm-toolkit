---
name: write-a-prd
description: "Product Requirements Document skill. Trigger whenever the user invokes /write-a-prd, asks to \"write a PRD\", \"document this idea\", \"turn this into a spec\", \"formalise this\", \"write a spec\", or has finished brainstorming a feature, product, or project and needs a structured requirements document. Also trigger when a user wants to take conversational or rough notes and produce something ready to share with a team or stakeholder. If a /grill-me session just completed, offer this skill immediately — the two are designed to chain. For AI-agent development contexts, produce sequential phase structure rather than a flat requirement list."
---

# Write a PRD

## Purpose

Turn a brief, conversation, or grill-me output into a structured
Product Requirements Document ready to share or hand to an agent.

## PRD structure

```markdown
# [Feature / Project Name]

## Overview
One paragraph. What is this, why does it exist, who is it for.

## Goals
- [Goal 1 — measurable]
- [Goal 2]

## Non-goals
- [Explicitly out of scope]

## Requirements

### Functional
- [FR-1] [requirement]
- [FR-2] [requirement]

### Non-functional
- [NFR-1] Performance / reliability / security constraints

## Design notes
Key decisions, constraints, or approach notes.

## Open questions
- [ ] [Question that needs resolving before build]

## Definition of done
- [ ] [Acceptance criterion 1]
- [ ] [Acceptance criterion 2]
```

## Rules

- Requirements must be testable — avoid "should be fast", use "< 200ms"
- Separate WHAT from HOW — requirements describe behaviour, not implementation
- Flag open questions rather than making assumptions
- For AI-agent contexts: group requirements into sequential phases (PLAN / BUILD / TEST / SHIP)

## Notes

- For non-code engagements (strategy, documents, personal projects), the `reference/dod-template.md` in ir5-os is the lightweight alternative — use it when a full PRD is more overhead than the engagement warrants.
- The DoD section of the PRD is the artefact for TDD First. If it can't be written, the engagement isn't ready to scope.

## Handoff

When the PRD is complete, offer to run `prd-to-issues` to decompose it into tickets.

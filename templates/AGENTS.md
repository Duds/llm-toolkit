---
# AGENT.md — Cross-Model Project Configuration
# Place this file at the root of every project. Any harness can read it.

name: project-name
description: One-line description of what this project does
type: code           # code | dcceew | personal | program | llm-wiki
status: active       # active | paused | complete | archive
last-updated: YYYY-MM-DD

# Model preferences for this project
models:
  default: claude
  fallback: kimi

# Skills available in this project context
skills:
  - skill-name

# Agents available in this project context
agents:
  - agent-name

# Squads that can be invoked on-demand
squads:
  on-demand:
    - squad-name

# Lifecycle hooks for this project
hooks:
  on-start: []
  on-mode-switch: []

# Project-specific conventions (overrides global STANDARDS.md)
conventions:
  naming: kebab-case
  version_pattern: "-v0_0"  # e.g. document-v0_1.pptx
  mirror_policy: required   # required | recommended | none
---

# Agent Context

## Project Purpose
[1-2 paragraph mission statement]

## Key Files
| File | Purpose |
|------|---------|
| `README.md` | Project overview |
| `TASKS.md` | Active task tracker |

## Conventions
- [Naming rules]
- [File organization]
- [Versioning scheme]
- [Mirror requirements]

## Decision Log
| Date | Decision | Rationale |
|------|----------|-----------|
| YYYY-MM-DD | [Decision] | [Why] |

## Dependencies
- [Other projects this depends on]
- [External systems / APIs]

## Contacts
- Owner: [Name]
- Reviewer: [Name]

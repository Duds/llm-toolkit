---
name: agent-config-schema
description: "Schema standard for AGENT.md project configuration files."
version: 1.0.0
---

# AGENT.md Schema Standard

## Purpose

Project-level configuration that declares context, conventions, and preferred models. Read by harnesses at session start.

## Required Frontmatter

```yaml
---
name: project-name
type: code | design | research | ops
status: active | paused | archived
---
```

## Optional Sections

### Models
```yaml
models:
  default: claude-sonnet-4
  fallback: kimi-k2.6
```

### Skills
```yaml
skills:
  - orient
  - close-and-learn
  - sync-tasks
```

### Squads
```yaml
squads:
  - workspace-cleanup
```

### Conventions
```markdown
## Conventions

- Use TypeScript strict mode
- Test coverage >80%
- No console.log in production
```

### Context
```markdown
## Context

- Previous session: [link to handoff]
- Blocked on: [dependency]
- Next milestone: [date]
```

## Example

```markdown
---
name: rock-oracle
type: code
status: active
---

# Rock Oracle

## Purpose

Pool tracking and analytics platform.

## Models
- default: claude-sonnet-4

## Skills
- orient
- close-and-learn

## Conventions
- Next.js 14 App Router
- Tailwind CSS
- Supabase for data
- Vercel for hosting

## Context
- Previous: [handoff-2026-06-10.md]
- Blocked: Waiting for Azure deployment approval
- Next milestone: 2026-06-20 (soft launch)
```

## Location

`AGENT.md` must be at project root. Harnesses search parent directories until found.

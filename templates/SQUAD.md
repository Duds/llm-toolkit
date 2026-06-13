---
# SQUAD.md — Multi-Agent Team Manifest
# Place this file at the root of a squad directory: ~/.agent/squads/<squad-name>/

name: squad-name
description: What this squad does and when to invoke it
status: active        # active | paused | deprecated
version: 1.0.0

# The lead agent coordinates the squad
lead:
  name: lead-agent-name
  description: Role of the lead agent

# Member agents and their responsibilities
members:
  - name: member-1
    role: Specific responsibility within the squad
    agent_ref: ~/.agent/agents/member-1/AGENT.md
  - name: member-2
    role: Specific responsibility within the squad
    agent_ref: ~/.agent/agents/member-2/AGENT.md

# Workflow: how the squad operates
workflow:
  trigger: "When to invoke this squad"
  steps:
    - step: 1
      agent: lead-agent-name
      action: "What the lead does first"
    - step: 2
      agent: member-1
      action: "What member-1 does"
    - step: 3
      agent: member-2
      action: "What member-2 does"
    - step: 4
      agent: lead-agent-name
      action: "Lead validates and reports"

# Handoff rules between members
handoffs:
  - from: lead-agent-name
    to: member-1
    condition: "When to pass control"
  - from: member-1
    to: member-2
    condition: "When to pass control"

# Output expectations
output:
  format: "What the squad produces"
  delivery: "Where results go"
---

# Squad Context

## Purpose
[Why this squad exists and what problems it solves]

## Agent Definitions

### Lead: [lead-agent-name]
[Detailed role description, perspective, expertise]

### Member: [member-1]
[Detailed role description, perspective, expertise]

### Member: [member-2]
[Detailed role description, perspective, expertise]

## Invocation Examples

### Example 1: [Use case]
```
invoke-squad squad-name --param value
```

### Example 2: [Use case]
```
invoke-squad squad-name --param value
```

## History
| Date | Change | Version |
|------|--------|---------|
| YYYY-MM-DD | Created | 1.0.0 |

---
name: workspace-cleanup
description: >-
  Multi-agent squad that fixes issues identified by the 5S workspace audit.
  Triggered after a /5s run when the user confirms they want fixes applied.
  Handles structure fixes (CLAUDE.md, frontmatter, renames), hygiene fixes
  (temp files, mirrors, cleanup), and validation (re-audit and score).
status: active
version: 1.0.0

lead:
  name: workspace-auditor
  description: Validates all findings, plans fix sequence, re-runs audit after fixes

members:
  - name: structure-fixer
    role: Applies structure fixes — renames, missing CLAUDE.md/AGENT.md, frontmatter, moves to _archive/
    agent_ref: ~/.agent/squads/workspace-cleanup/agents/structure-fixer/AGENT.md
  - name: hygiene-cleaner
    role: Applies hygiene fixes — temp files, stale mirrors, version chains, duplicates
    agent_ref: ~/.agent/squads/workspace-cleanup/agents/hygiene-cleaner/AGENT.md

workflow:
  trigger: "User confirms 'fix these issues' after /5s audit, or says 'invoke workspace-cleanup'"
  steps:
    - step: 1
      agent: workspace-auditor
      action: "Receive 5S audit findings, validate dependencies, plan fix sequence, confirm with user"
    - step: 2
      agent: structure-fixer
      action: "Apply all structure fixes in dependency order (renames before moves)"
    - step: 3
      agent: hygiene-cleaner
      action: "Apply all hygiene fixes (temp files, mirrors, version chains)"
    - step: 4
      agent: workspace-auditor
      action: "Re-run 5S audit subset, compute new health score, report improvement"

handoffs:
  - from: workspace-auditor
    to: structure-fixer
    condition: "User confirmed fix plan and no blocking dependencies"
  - from: structure-fixer
    to: hygiene-cleaner
    condition: "All structure fixes applied and logged"
  - from: hygiene-cleaner
    to: workspace-auditor
    condition: "All hygiene fixes applied and logged"

output:
  format: "Updated workspace + new health score report"
  delivery: "Report back to user with before/after score and any remaining issues"
---

# Workspace Cleanup Squad

## Purpose

The 5S skill is read-only — it detects and reports but never fixes. This squad
bridges the gap: it takes 5S findings and applies the remediation actions.

## Agent Definitions

### Lead: Workspace Auditor

- **Perspective**: Quality assurance and validation
- **Expertise**: Workspace standards, 5S methodology, dependency analysis
- **Responsibility**:
  - Parse 5S findings into actionable fix batches
  - Determine fix order (e.g. rename before move)
  - Validate no destructive conflicts
  - Re-run audit after fixes
  - Report new health score

### Member: Structure Fixer

- **Perspective**: Organization and compliance
- **Expertise**: File naming, YAML frontmatter, project structure
- **Responsibility**:
  - Create missing CLAUDE.md / AGENT.md files
  - Fix frontmatter (status, type, dates)
  - Rename files to kebab-case
  - Move completed/archived projects to `_archive/`
  - Fix date-stamped filenames

### Member: Hygiene Cleaner

- **Perspective**: Cleanliness and freshness
- **Expertise**: File hygiene, mirror management, version control
- **Responsibility**:
  - Delete temp files (`~$*`, `*.tmp`, `Thumbs.db`)
  - Update stale markdown mirrors
  - Archive old versions in version chains
  - Remove empty directories
  - Flag large binaries for asset folders

## Invocation

```
invoke-squad workspace-cleanup
```

Or after /5s:
```
> Would you like me to fix these issues? I can invoke the workspace-cleanup squad.
User: Yes
```

## Safety Rules

1. **Always confirm** before destructive actions (delete, move to archive)
2. **Never** modify `.claude/`, `.claude-resources/`, or `_templates/`
3. **Always** backup before batch renames or moves
4. **Log every change** for the final report

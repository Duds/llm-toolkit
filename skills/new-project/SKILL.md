---
name: new-project
description: >-
  Scaffold a new Claude Code project interactively. Use this skill whenever
  Dale wants to create, initialise, or set up a new project directory with
  the right skills, CLAUDE.md, and .claude/ structure. Trigger on phrases
  like: "create a new project", "scaffold a project", "set up a new repo",
  "new project called X", "initialise a project", "bootstrap a project",
  "start a new code project", "make a new dcceew project", "new personal project".
  Also trigger when Dale says "new-project" or asks how to create a project.
---

# New Project

## Purpose

Scaffold a new project directory with the correct `.claude/skills/` symlinks,
a rich type-specific `CLAUDE.md`, and registration in `setup-skills.sh` — all
in one guided step.

## Steps / Process

1. **Gather inputs** — if the user hasn't provided both a project name and type,
   ask for them before proceeding:
   - **Name:** a short slug (lowercase, hyphens OK, no spaces) — e.g. `wayfinder`
   - **Type:** one of `code`, `dcceew`, or `personal`
   - If type is ambiguous, offer the three options with a one-line description each:
     - `code` — software projects (TDD, PRD, dev-chain skills)
     - `dcceew` — government engagement/deliverable work
     - `personal` — personal site, blog, portfolio, or writing

2. **Validate** — before running anything, confirm:
   - Name matches `^[a-z0-9][a-z0-9-]*$` (no spaces, no uppercase, no leading hyphens)
   - Type is exactly `code`, `dcceew`, or `personal`
   - If validation fails, explain the constraint and ask again

3. **Run the scaffold** — execute the Bash script:
   ```bash
   cd ~/Documents/projects/claude-resources && ./new-project.sh <name> <type>
   ```
   Show the full output to the user.

4. **Report what was created** — after the script succeeds, summarise:
   - Project directory path
   - Skills that were linked (list them)
   - Location of the generated CLAUDE.md
   - Note that global skills (orient, close-and-learn, etc.) are always
     available from `~/.claude/skills/` without being linked per-project

5. **Offer next steps** — ask if they want to:
   - Open the CLAUDE.md to fill in project-specific details (purpose, stack, commands)
   - Run `git init` in the new project directory
   - Start an orient session now

## Output format

After the script runs, output a short summary:

```
Project scaffolded: ~/Documents/projects/<name>

Skills linked:
  • <skill-1>
  • <skill-2>
  ...

CLAUDE.md created at:
  ~/Documents/projects/<name>/CLAUDE.md
  → Open it to fill in project purpose, stack, and common commands.

Global skills (orient, close-and-learn, etc.) are always available — no
action needed.
```

## Notes

- The script is idempotent: safe to re-run on an existing project. It will
  skip already-linked skills and won't overwrite an existing CLAUDE.md.
- The templates in `user/new-project/templates/` drive the CLAUDE.md content.
  Edit those files (not the script) to change what new projects get.
- After adding a new project type, both `new-project.sh` and `setup-skills.sh`
  need updating — remind the user if they ask about custom types.

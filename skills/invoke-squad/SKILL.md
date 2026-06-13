---
name: invoke-squad
description: >-
  Activate a named squad of agents and skills for a domain. Use when the user
  says "activate the [name] squad", "bring in the [name] team", "invoke squad
  [name]", "load the full-stack squad", "set up my DCCEEW team", or uses
  /invoke-squad. Also trigger when starting a project that maps to a squad type
  and the user wants all roles loaded. If no squad name is given, list available
  squads from CATALOG.md and ask the user to choose. Never activate a squad
  that does not exist — show the catalog instead.
---

# Invoke Squad

## Purpose

Load a named squad into the current session: read all agent personas into
context, confirm required skills are available, adopt the lead agent persona,
and print a squad summary — all in one step.

## Steps

1. **Resolve the squad name**
   - If the user provided a name, look for the SQUAD.md at:
     `~/.agent/squads/<name>/SQUAD.md`          (unified — preferred)
     Then fall back to:
     `~/.claude/squads/<name>/SQUAD.md`          (legacy)
     Then fall back to:
     `~/Documents/projects/claude-resources/squads/<name>/SQUAD.md`
   - If no name was given, or if no path has the file, read
     `~/.agent/squads/CATALOG.md` (squads section) and present
     available squads with one-line descriptions. Ask the user to choose one.

2. **Parse the SQUAD.md**
   - Extract the `agents:` list (ordered — first is squad lead)
   - Extract the `skills:` list
   - Extract `display-name:` for the confirmation message

3. **Load each agent**
   - For each agent name in the `agents:` list, read the AGENT.md from:
     `~/.agent/agents/<name>/AGENT.md`          (unified — preferred)
     Then fall back to:
     `~/.claude/agents/<name>/AGENT.md`          (legacy)
     Then fall back to:
     `~/Documents/projects/claude-resources/agents/<name>/AGENT.md`
   - Announce each agent as it loads: "Loading agent: [display-name]..."
   - If an agent file is missing, warn and continue — do not abort the whole
     squad activation

4. **Check required skills**
   - For each skill in the `skills:` list, check whether the skill directory
     exists in `~/.agent/skills/` (unified — preferred), `.claude/skills/`
     (current project), or `~/.claude/skills/` (legacy global).
   - For any missing skills, print the symlink command needed to add them:
     ```
     ln -s ~/Documents/projects/claude-resources/user/<skill> .claude/skills/<skill>
     ```

5. **Adopt the lead persona**
   - The first agent in the `agents:` list is the squad lead.
   - Read that agent's `## Expertise`, `## Approach`, `## Guidelines`, and
     `## Response Style` sections into active context.
   - Announce: "Squad loaded. Active persona: [lead display-name]."

6. **Print squad summary**
   ```
   Squad: [display-name]
   Active persona: [lead agent display-name]
   Available agents: [comma-separated list of display names]
   Skills confirmed: ✓ grill-me  ✓ write-a-prd  ✗ tdd (not linked)
   Say "switch to [role]" to change perspective.
   ```

## Persona Switching

When the user says "switch to [role name]" or "you are now [role]":
1. Find the matching agent in the squad's `agents:` list (fuzzy match on
   `name` or `display-name` fields)
2. Re-read that agent's AGENT.md into context
3. Acknowledge: "Switching to [display-name] perspective."

When the user says "back to lead" or "back to [lead name]":
1. Re-read the first agent's AGENT.md
2. Acknowledge: "Back to [lead display-name]."

## Deactivation

When the user says "deactivate squad", "drop agent personas", or "back to
default":
- Acknowledge and return to default Claude behaviour
- "Squad deactivated. Back to default mode."

## Notes

- Squad activation is **session-scoped** — it does not modify CLAUDE.md
  or any files unless the user explicitly asks.
- If the user says "make this permanent" or "save this to the project", offer
  to append `@`-import lines for each agent's AGENT.md to the project's
  CLAUDE.md. Show the lines first and ask for confirmation before writing.
- When reading multiple AGENT.md files, read them all before adopting the
  lead persona — don't switch personas partway through loading.

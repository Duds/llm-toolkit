---
name: troubleshoot
description: >
  Diagnose and fix broken skills, plugins, MCP servers, and AI tooling
  workflows. Use this skill whenever something in Claude's tooling stack
  isn't working — a skill that won't trigger, a plugin that fails silently
  or won't load, an MCP server with connection errors, a workflow that breaks
  mid-execution, or two plugin versions that have diverged. Trigger on:
  "this skill isn't working", "my plugin is broken", "troubleshoot why X
  didn't fire", "fix my plugin", "skill X never triggers", "plugin won't
  load", "something's wrong with my setup", or any description of unexpected
  behaviour in skills, plugins, or connected tools. When in doubt, trigger —
  this skill handles the full diagnostic and fix loop.
---

# Troubleshoot

## Diagnostic sequence

Work through these in order — stop when you find the issue.

### 1. Skill not triggering

- Read the `description:` field in `SKILL.md` — is it specific enough?
  Vague descriptions cause undertriggering.
- Check the skill is in the right directory (`.claude/skills/` or `~/.claude/skills/`).
- Verify the symlink isn't broken: `ls -la .claude/skills/`
- Try invoking explicitly: `/skill-name` in Claude Code chat.

### 2. Plugin won't load

- Check `~/.claude/plugins/` for the plugin directory.
- Verify `plugin.json` / `marketplace.json` is valid JSON: `jq . plugin.json`
- Check for permission issues: `ls -la ~/.claude/plugins/`
- Restart Claude Code and try again.

### 3. MCP server connection error

- Check the server is running: `ps aux | grep mcp`
- Verify the URL/port in Claude Code MCP settings.
- Test the endpoint directly: `curl http://localhost:PORT/health`
- Check MCP server logs for startup errors.
- Re-authenticate via `/mcp` in Claude Code if OAuth is involved.

### 4. Skill fires but produces wrong output

- Read the full `SKILL.md` — is the instruction body complete?
- Check for truncated content (large SKILL.md files can get cut).
- Verify any referenced resource files exist relative to the skill dir.

### 5. Two versions diverged

- Diff the two `SKILL.md` files: `diff skill-a/SKILL.md skill-b/SKILL.md`
- The canonical version lives in `~/Documents/projects/claude-resources/`.
- Recreate the symlink from canonical: `ln -sf [source] [dest]`

## Fixes

| Symptom | Fix |
|---|---|
| Skill never triggers | Strengthen `description:` — be more specific about trigger phrases |
| Broken symlink | `ln -sf ~/Documents/projects/claude-resources/user/[name] .claude/skills/[name]` |
| MCP auth expired | `/mcp` → reconnect → re-authenticate |
| Plugin JSON invalid | `jq . plugin.json` to find syntax error |
| Skill fires on wrong tasks | Add negative examples to `description:` |

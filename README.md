# ~/.agents — Unified Agent Configuration

Cross-model, cross-harness configuration for AI agents, skills, squads, hooks, protocols, and memory.

> **Status:** Evolved from `llm-toolkit`. `~/.agents/` is the live runtime directory. `~/30-PROJECTS/llm-toolkit/` is the Git-sync repo for cross-machine deployment.

---

## Philosophy

- **One source of truth**: All skills, agents, squads, protocols, and memory live here regardless of harness.
- **Harness-agnostic core**: `AGENT.md`, `SKILL.md`, `SQUAD.md`, `PROTOCOL.md` use shared schemas.
- **Harness-specific bridges**: Thin integration layers in `integrations/` map native config to shared structure.
- **Enforceable protocols**: Rules like Signal authorization are code, not convention.
- **Canonical memory**: One `user.md`, one `env.md`, injected everywhere.

---

## Folder Layout

```
~/.agents/
├── README.md                          # This file
├── config.yaml                        # Global defaults (preferred models, paths, auto-flags)
│
├── core/                              # Cross-cutting concerns
│   ├── protocols/                     # Enforced rules (signal-jane, email-triage)
│   ├── memory/                        # Canonical memory files
│   │   ├── user.md                    # User profile (replaces USER.md)
│   │   ├── env.md                     # Environment facts (replaces MEMORY.md)
│   │   └── projects/                  # Per-project state tracking
│   └── standards/                     # Shared schemas and standards
│
├── skills/                            # All skills (harness-agnostic)
│   ├── productivity/
│   │   ├── orient/
│   │   ├── close-and-learn/
│   │   └── sync-tasks/
│   └── ...
│
├── squads/                            # Multi-agent teams
│   └── workspace-cleanup/
│
├── agents/                            # Single-agent definitions
│
├── hooks/                             # Session lifecycle scripts
│   ├── on-start.sh
│   ├── on-end.sh
│   └── on-project-open.sh
│
├── integrations/                      # Per-harness bridge configs
│   ├── hermes/                        # Hermes-specific (MCP, cron, toolsets)
│   ├── claude/                        # Claude Code (settings.json)
│   ├── kimi/                          # Kimi (agent-config.yaml)
│   └── openclaw/                      # OpenClaw (mission-control.yaml)
│
├── templates/                         # Scaffolds
│   ├── AGENT.md
│   ├── SQUAD.md
│   ├── SKILL.md
│   └── PROTOCOL.md
│
└── scripts/                           # Maintenance utilities
    ├── setup.sh                       # One-time setup (symlinks, config)
    ├── sync.sh                        # Pull latest, check drift
    ├── drift-check.py                 # Compare against live instances
    └── promote.sh                     # Move item from dotfiles to ~/.agents/
```

---

## Quick Start

### 1. Setup (one-time)

```bash
~/.agents/scripts/setup.sh
```

This wires `~/.agents/` to all installed harnesses (Hermes, Claude Code, Kimi).

### 2. Sync (regularly)

```bash
~/.agents/scripts/sync.sh
```

Pulls latest from `~/30-PROJECTS/llm-toolkit/` and updates `~/.agents/`.

### 3. Check drift

```bash
~/.agents/scripts/drift-check.py
```

Reports missing or drifted items compared to live harness instances.

---

## Relationship Map

```
┌─────────────────────────────────────────────────────────────┐
│  ir5-os                                                     │
│  (strategy, roadmap, decisions, health checks)              │
└──────────────────────┬──────────────────────────────────────┘
                       │ owns the "what" and "when"
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  ~/30-PROJECTS/llm-toolkit/  ←  GitHub source of truth      │
│  (portable agent tooling — skills, agents, squads, hooks)   │
└──────────────────────┬──────────────────────────────────────┘
                       │ deploys to
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  ~/.agents/  ←  live runtime directory (this folder)        │
│  (unified config for Hermes, Claude, Kimi, OpenClaw)       │
└──────────────────────┬──────────────────────────────────────┘
                       │ used by
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  project-level AGENT.md files                               │
│  (canopy, fillet, ir5-os, rock-oracle, etc.)                │
└─────────────────────────────────────────────────────────────┘
```

---

## Migration from llm-toolkit

If you previously used `~/.agent/` (singular):

```bash
# Remove old symlink if exists
rm -f ~/.agent

# Create new symlink
ln -s ~/.agents ~/.agent
```

---

## Contributing

- Add new skills to `skills/` with a `SKILL.md` and optional `scripts/` subfolder.
- Add new agents to `agents/` with an `AGENT.md`.
- Add new squads to `squads/` with a `SQUAD.md` and agent subdirectories.
- Add new protocols to `core/protocols/` with a `PROTOCOL.md`.
- Update harness integrations when adding new harness-specific features.
- Run `drift-check.py` before committing to catch missing items.

---

## Notes

- `~/.agents/` is the **runtime** directory. Edit here for immediate effect.
- `~/30-PROJECTS/llm-toolkit/` is the **repo**. Commit there for cross-machine sync.
- Use `promote.sh` to move items from `~/.claude/` (live experiments) to `~/.agents/` (canonical).
- Keep DCCEEW-specific or client-specific content in project-level configs, not in `~/.agents/`.

- Use `promote.sh` to move items from `~/.claude/` (live experiments) to `~/.agents/` (canonical).
- Keep DCCEEW-specific or client-specific content in project-level configs, not in `~/.agents/`.

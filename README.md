# llm-toolkit

Personal unified agent configuration for Claude Code, Kimi, and other LLM harnesses.

This repo is the portable, Mac-first home for Dale Rogers' reusable AI skills, squads, agents, hooks, templates, and harness integration configs. It is intended to be cloned as `~/.agent/` on the home Mac (and can also be used on Windows with minor path adjustments).

---

## What's included

- **~50 reusable skills** in `skills/` — general-purpose tools for writing, documentation, diagrams, frontend design, code review, learning loops, LLM wikis, MCP building, PDF/Office handling, etc.
- **1 squad** in `squads/workspace-cleanup/` — multi-agent workspace hygiene team.
- **Global config** in `config.yaml` — harness-agnostic defaults and search paths.
- **Harness integrations** in `harness-integrations/` — Claude Code, Kimi, and OpenAI bridge configs.
- **Templates** in `templates/` — scaffolds for `AGENT.md` and `SQUAD.md`.
- **Hooks** in `hooks/` — session lifecycle scripts.
- **Migration scripts** in `scripts/` — Windows PowerShell originals plus a Mac setup helper.

---

## Mac setup

1. Clone into `~/.agent`:
   ```bash
   git clone https://github.com/duds/llm-toolkit.git ~/.agent
   ```

2. Run the setup helper:
   ```bash
   ~/.agent/scripts/mac-setup.sh
   ```

3. Restart Claude Code and test a skill:
   ```
   /llm-wiki
   /5s
   ```

### Manual Claude Code bridge

If Claude Code does not automatically resolve `~/.agent/`, create `~/.claude/settings.json`:

```json
{
  "skills": {
    "searchPaths": ["~/.agent/skills"]
  },
  "agents": {
    "searchPaths": ["~/.agent/agents", "~/.agent/squads"]
  }
}
```

---

## Windows notes

This repo was built on Windows, but the canonical runtime target is the home Mac. The PowerShell scripts in `scripts/` are kept as historical references; they may need path tweaks to run on a fresh Windows machine. For new Windows setups, the recommended approach is the same unified `~/.agent/` layout with Git Bash or WSL.

---

# ~/.agent — Unified Agent Configuration

Cross-model, cross-harness configuration for AI agents, skills, squads, and hooks.

## Philosophy

- **One source of truth**: All skills, agents, and squads live here regardless of which model or harness invokes them.
- **Harness-agnostic core**: `AGENT.md`, `SKILL.md`, and `SQUAD.md` use a shared schema that any harness can read.
- **Harness-specific bridges**: Each harness (Claude Code, Kimi, OpenAI, etc.) gets a thin integration layer in `harness-integrations/` that maps its native config format to the shared structure.
- **Project-level `AGENT.md`**: Every project declares its own context, conventions, and preferred models via an `AGENT.md` at its root.

## Folder Layout

```
~/.agent/
├── README.md                          # This file
├── config.yaml                        # Global defaults (preferred models, paths)
│
├── skills/                            # All skills (harness-agnostic)
│   ├── 5s/
│   ├── llm-wiki/
│   ├── llm-wiki-bootstrap/
│   └── ...
│
├── squads/                            # Multi-agent team definitions
│   └── workspace-cleanup/
│       ├── SQUAD.md
│       └── agents/
│           ├── workspace-auditor/
│           ├── structure-fixer/
│           └── hygiene-cleaner/
│
├── agents/                            # Reusable single-agent definitions
│
├── hooks/                             # Session lifecycle scripts
│   ├── on-start.sh
│   └── on-project-open.sh
│
├── harness-integrations/              # Per-harness bridge configs
│   ├── claude/
│   │   └── settings.json
│   ├── kimi/
│   │   └── agent-config.yaml
│   └── openai/
│       └── agents.yaml
│
├── templates/                         # Scaffolds for new projects / squads
│   ├── AGENT.md
│   ├── SQUAD.md
│   └── STANDARDS.md
│
└── scripts/                           # Migration and maintenance utilities
    ├── mac-setup.sh
    ├── migrate-skills.ps1
    └── migrate-projects.ps1
```

## Quick Start

### 1. Register ~/.agent with your harness

**Claude Code:**
```bash
# ~/.claude/settings.json
{
  "skills": {
    "searchPaths": ["~/.agent/skills"]
  },
  "agents": {
    "searchPaths": ["~/.agent/agents"]
  }
}
```

**Kimi:**
```bash
# ~/.kimi/config.yaml
skills:
  searchPaths:
    - ~/.agent/skills
agents:
  searchPaths:
    - ~/.agent/agents
```

### 2. Add AGENT.md to a project

```bash
cp ~/.agent/templates/AGENT.md ./AGENT.md
# Edit to match your project
```

## Schema Standards

### AGENT.md (Project Config)

See [`templates/AGENT.md`](templates/AGENT.md).

### SKILL.md (Skill Definition)

See any skill in `skills/`. Must include YAML frontmatter:

```yaml
---
name: skill-name
description: >-
  What this skill does and when to use it.
---
```

### SQUAD.md (Squad Manifest)

See [`templates/SQUAD.md`](templates/SQUAD.md).

## Contributing

- Add new skills to `skills/` with a `SKILL.md` and optional `scripts/` subfolder.
- Add new agents to `agents/` with an `AGENT.md`.
- Add new squads to `squads/` with a `SQUAD.md` and agent subdirectories.
- Update harness integrations when adding new harness-specific features.

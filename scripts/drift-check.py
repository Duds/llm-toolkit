#!/usr/bin/env python3
"""
drift-check.py: Compare ~/.agents/ against live harness instances.
Reports missing, drifted, and extra files.
"""

import json
import os
import subprocess
from pathlib import Path
from collections import defaultdict

AGENTS_DIR = Path.home() / ".agents"
DOTFILES_CLAUDE = Path.home() / ".claude"
HERMES_SKILLS = Path.home() / ".hermes/skills"

def get_skills(path: Path) -> set:
    """Return set of skill names from a directory."""
    if not path.exists():
        return set()
    return {d.name for d in path.iterdir() if d.is_dir() and (d / "SKILL.md").exists()}

def get_agents(path: Path) -> set:
    """Return set of agent names from a directory."""
    if not path.exists():
        return set()
    return {d.name for d in path.iterdir() if d.is_dir() and (d / "AGENT.md").exists()}

def get_squads(path: Path) -> set:
    """Return set of squad names from a directory."""
    if not path.exists():
        return set()
    return {d.name for d in path.iterdir() if d.is_dir() and (d / "SQUAD.md").exists()}

def check_drift():
    print("=== Drift Check: ~/.agents/ vs Live Instances ===\n")
    
    # Skills
    agents_skills = get_skills(AGENTS_DIR / "skills")
    dotfiles_skills = get_skills(DOTFILES_CLAUDE / "skills")
    hermes_skills = get_skills(HERMES_SKILLS)
    
    print(f"Skills:")
    print(f"  ~/.agents/skills:     {len(agents_skills)} skills")
    print(f"  ~/.claude/skills:     {len(dotfiles_skills)} skills")
    print(f"  ~/.hermes/skills:     {len(hermes_skills)} skills")
    
    only_in_dotfiles = dotfiles_skills - agents_skills
    only_in_agents = agents_skills - dotfiles_skills
    in_both = agents_skills & dotfiles_skills
    
    if only_in_dotfiles:
        print(f"\n  ⚠  Missing in ~/.agents/ (present in ~/.claude/):")
        for s in sorted(only_in_dotfiles):
            print(f"     - {s}")
    
    if only_in_agents:
        print(f"\n  ✓  Only in ~/.agents/ (portable):")
        for s in sorted(only_in_agents):
            print(f"     - {s}")
    
    if in_both:
        print(f"\n  ○  In both (check for drift):")
        for s in sorted(in_both)[:10]:
            print(f"     - {s}")
        if len(in_both) > 10:
            print(f"     ... and {len(in_both) - 10} more")
    
    # Agents
    agents_agents = get_agents(AGENTS_DIR / "agents")
    dotfiles_agents = get_agents(DOTFILES_CLAUDE / "agents")
    
    print(f"\nAgents:")
    print(f"  ~/.agents/agents:     {len(agents_agents)} agents")
    print(f"  ~/.claude/agents:     {len(dotfiles_agents)} agents")
    
    if dotfiles_agents - agents_agents:
        print(f"\n  ⚠  Missing in ~/.agents/:")
        for a in sorted(dotfiles_agents - agents_agents):
            print(f"     - {a}")
    
    # Squads
    agents_squads = get_squads(AGENTS_DIR / "squads")
    dotfiles_squads = get_squads(DOTFILES_CLAUDE / "squads")
    
    print(f"\nSquads:")
    print(f"  ~/.agents/squads:     {len(agents_squads)} squads")
    print(f"  ~/.claude/squads:     {len(dotfiles_squads)} squads")
    
    if dotfiles_squads - agents_squads:
        print(f"\n  ⚠  Missing in ~/.agents/:")
        for s in sorted(dotfiles_squads - agents_squads):
            print(f"     - {s}")
    
    print("\n=== Recommendations ===")
    print("Run ~/.agents/scripts/sync.sh to promote missing items from ~/.claude/ to ~/.agents/")

if __name__ == "__main__":
    check_drift()

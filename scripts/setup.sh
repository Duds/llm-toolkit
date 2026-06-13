#!/usr/bin/env bash
# ~/.agents/scripts/setup.sh
# One-time setup: wire ~/.agents/ to all harnesses

set -euo pipefail

AGENTS_DIR="${HOME}/.agents"
HERMES_DIR="${HOME}/.hermes"
CLAUDE_DIR="${HOME}/.claude"
KIMI_DIR="${HOME}/.kimi"

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}=== ~/.agents Setup ===${NC}"

# 1. Validate ~/.agents structure
echo -e "${CYAN}[1/6] Validating ~/.agents structure...${NC}"
REQUIRED_DIRS=("skills" "squads" "agents" "hooks" "integrations" "templates" "scripts" "core")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [[ -d "${AGENTS_DIR}/${dir}" ]]; then
        echo -e "  ${GREEN}✓${NC} ${dir}/"
    else
        echo -e "  ${YELLOW}○${NC} ${dir}/ (creating)"
        mkdir -p "${AGENTS_DIR}/${dir}"
    fi
done

# 2. Hermes integration
echo -e "${CYAN}[2/6] Configuring Hermes...${NC}"
if command -v hermes &> /dev/null; then
    # Update skills search path
    hermes config set skills.search_paths '["~/.agents/skills", "~/.hermes/skills"]' 2>/dev/null || true
    
    # Ensure MCP servers point to correct paths
    if [[ -f "${AGENTS_DIR}/integrations/hermes/mcp.yaml" ]]; then
        echo -e "  ${GREEN}✓${NC} MCP config found in ~/.agents/integrations/hermes/"
    else
        echo -e "  ${YELLOW}○${NC} No MCP config in ~/.agents/integrations/hermes/"
    fi
    
    echo -e "  ${GREEN}✓${NC} Hermes skills path updated"
else
    echo -e "  ${YELLOW}○${NC} Hermes CLI not found — skipping Hermes config"
fi

# 3. Claude Code integration
echo -e "${CYAN}[3/6] Configuring Claude Code...${NC}"
if [[ -d "${CLAUDE_DIR}" ]]; then
    # Create/update settings.json
    CLAUDE_SETTINGS="${CLAUDE_DIR}/settings.json"
    if [[ -f "${CLAUDE_SETTINGS}" ]]; then
        echo -e "  ${YELLOW}○${NC} ${CLAUDE_SETTINGS} exists — back up and update"
        cp "${CLAUDE_SETTINGS}" "${CLAUDE_SETTINGS}.backup.$(date +%Y%m%d)"
    fi
    
    # Write settings pointing to ~/.agents/
    cat > "${CLAUDE_SETTINGS}" << 'EOF'
{
  "skills": {
    "searchPaths": ["~/.agents/skills"]
  },
  "agents": {
    "searchPaths": ["~/.agents/agents", "~/.agents/squads"]
  },
  "hooks": {
    "searchPaths": ["~/.agents/hooks"]
  }
}
EOF
    echo -e "  ${GREEN}✓${NC} Claude Code settings updated"
else
    echo -e "  ${YELLOW}○${NC} ~/.claude/ not found — skipping Claude Code config"
fi

# 4. Kimi integration
echo -e "${CYAN}[4/6] Configuring Kimi...${NC}"
if [[ -d "${KIMI_DIR}" ]]; then
    KIMI_CONFIG="${KIMI_DIR}/config.yaml"
    if [[ -f "${KIMI_CONFIG}" ]]; then
        cp "${KIMI_CONFIG}" "${KIMI_CONFIG}.backup.$(date +%Y%m%d)"
    fi
    
    cat > "${KIMI_CONFIG}" << 'EOF'
skills:
  searchPaths:
    - ~/.agents/skills
agents:
  searchPaths:
    - ~/.agents/agents
    - ~/.agents/squads
EOF
    echo -e "  ${GREEN}✓${NC} Kimi config updated"
else
    echo -e "  ${YELLOW}○${NC} ~/.kimi/ not found — skipping Kimi config"
fi

# 5. Symlink legacy paths for compatibility
echo -e "${CYAN}[5/6] Creating compatibility symlinks...${NC}"

# ~/.agent → ~/.agents (legacy compatibility)
if [[ -L "${HOME}/.agent" && ! -e "${HOME}/.agent" ]]; then
    rm -f "${HOME}/.agent"
fi
if [[ ! -e "${HOME}/.agent" ]]; then
    ln -s "${AGENTS_DIR}" "${HOME}/.agent"
    echo -e "  ${GREEN}✓${NC} ~/.agent → ~/.agents"
fi

# 6. Validate
echo -e "${CYAN}[6/6] Validation...${NC}"
SKILL_COUNT=$(find "${AGENTS_DIR}/skills" -name "SKILL.md" | wc -l)
AGENT_COUNT=$(find "${AGENTS_DIR}/agents" -name "AGENT.md" 2>/dev/null | wc -l)
SQUAD_COUNT=$(find "${AGENTS_DIR}/squads" -name "SQUAD.md" 2>/dev/null | wc -l)

echo -e "  Skills:  ${SKILL_COUNT}"
echo -e "  Agents:  ${AGENT_COUNT}"
echo -e "  Squads:  ${SQUAD_COUNT}"

if [[ ${SKILL_COUNT} -eq 0 ]]; then
    echo -e "  ${RED}⚠ No skills found!${NC} Run: cp -r ~/30-PROJECTS/llm-toolkit/skills ~/.agents/"
fi

echo -e "${CYAN}=== Setup Complete ===${NC}"
echo ""
echo "Next steps:"
echo "  1. Run drift-check: ~/.agents/scripts/drift-check.py"
echo "  2. Sync skills: ~/.agents/scripts/sync.sh"
echo "  3. Restart your harnesses (Hermes, Claude Code, Kimi)"

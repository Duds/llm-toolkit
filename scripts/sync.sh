#!/usr/bin/env bash
# ~/.agents/scripts/sync.sh
# Sync from ~/30-PROJECTS/llm-toolkit/ to ~/.agents/ and promote from ~/.claude/ if needed

set -euo pipefail

AGENTS_DIR="${HOME}/.agents"
LLM_TOOLKIT="${HOME}/30-PROJECTS/llm-toolkit"
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}=== ~/.agents Sync ===${NC}"

# 1. Pull latest llm-toolkit
echo -e "${CYAN}[1/3] Pulling latest llm-toolkit...${NC}"
if [[ -d "${LLM_TOOLKIT}/.git" ]]; then
    cd "${LLM_TOOLKIT}"
    git pull origin main 2>/dev/null || echo -e "  ${YELLOW}○${NC} Could not pull (check network)"
    echo -e "  ${GREEN}✓${NC} llm-toolkit updated"
else
    echo -e "  ${YELLOW}○${NC} No git repo at ${LLM_TOOLKIT}"
fi

# 2. Sync from llm-toolkit to ~/.agents/
echo -e "${CYAN}[2/3] Syncing from llm-toolkit to ~/.agents/...${NC}"

# Sync skills (additive — don't overwrite existing)
if [[ -d "${LLM_TOOLKIT}/skills" ]]; then
    for skill_dir in "${LLM_TOOLKIT}/skills"/*; do
        if [[ -d "${skill_dir}" ]]; then
            skill_name=$(basename "${skill_dir}")
            target="${AGENTS_DIR}/skills/${skill_name}"
            if [[ ! -d "${target}" ]]; then
                cp -r "${skill_dir}" "${target}"
                echo -e "  ${GREEN}✓${NC} Added skill: ${skill_name}"
            fi
        fi
    done
fi

# Sync squads
if [[ -d "${LLM_TOOLKIT}/squads" ]]; then
    for squad_dir in "${LLM_TOOLKIT}/squads"/*; do
        if [[ -d "${squad_dir}" ]]; then
            squad_name=$(basename "${squad_dir}")
            target="${AGENTS_DIR}/squads/${squad_name}"
            if [[ ! -d "${target}" ]]; then
                cp -r "${squad_dir}" "${target}"
                echo -e "  ${GREEN}✓${NC} Added squad: ${squad_name}"
            fi
        fi
    done
fi

# Sync agents
if [[ -d "${LLM_TOOLKIT}/agents" ]]; then
    for agent_dir in "${LLM_TOOLKIT}/agents"/*; do
        if [[ -d "${agent_dir}" ]]; then
            agent_name=$(basename "${agent_dir}")
            target="${AGENTS_DIR}/agents/${agent_name}"
            if [[ ! -d "${target}" ]]; then
                cp -r "${agent_dir}" "${target}"
                echo -e "  ${GREEN}✓${NC} Added agent: ${agent_name}"
            fi
        fi
    done
fi

# Sync hooks
if [[ -d "${LLM_TOOLKIT}/hooks" ]]; then
    for hook in "${LLM_TOOLKIT}/hooks"/*; do
        if [[ -f "${hook}" ]]; then
            hook_name=$(basename "${hook}")
            target="${AGENTS_DIR}/hooks/${hook_name}"
            if [[ ! -f "${target}" ]]; then
                cp "${hook}" "${target}"
                echo -e "  ${GREEN}✓${NC} Added hook: ${hook_name}"
            fi
        fi
    done
fi

# Sync templates
if [[ -d "${LLM_TOOLKIT}/templates" ]]; then
    for template in "${LLM_TOOLKIT}/templates"/*; do
        if [[ -f "${template}" ]]; then
            template_name=$(basename "${template}")
            target="${AGENTS_DIR}/templates/${template_name}"
            if [[ ! -f "${target}" ]]; then
                cp "${template}" "${target}"
                echo -e "  ${GREEN}✓${NC} Added template: ${template_name}"
            fi
        fi
    done
fi

# 3. Run drift check
echo -e "${CYAN}[3/3] Running drift check...${NC}"
"${AGENTS_DIR}/scripts/drift-check.py"

echo -e "${CYAN}=== Sync Complete ===${NC}"
echo ""
echo "To promote missing items from ~/.claude/ to ~/.agents/:"
echo "  ~/.agents/scripts/promote.sh <item-name>"

#!/usr/bin/env bash
# ~/.agent/hooks/on-start.sh
# Runs when any harness opens a project with an AGENT.md
# Harness-agnostic — works with Claude, Kimi, OpenAI, etc.

set -euo pipefail

AGENT_FILE="${AGENT_FILE:-./AGENT.md}"
CONFIG_FILE="${HOME}/.agent/config.yaml"

# Colors
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${CYAN}=== ~/.agent Session Start ===${NC}"

# 1. Detect AGENT.md
if [[ -f "$AGENT_FILE" ]]; then
    echo -e "${GREEN}✓ AGENT.md detected${NC}"
    
    # Extract basic info from frontmatter
    PROJECT_NAME=$(grep -m1 '^name:' "$AGENT_FILE" | sed 's/name: *//' || echo "unknown")
    PROJECT_TYPE=$(grep -m1 '^type:' "$AGENT_FILE" | sed 's/type: *//' || echo "unknown")
    PROJECT_STATUS=$(grep -m1 '^status:' "$AGENT_FILE" | sed 's/status: *//' || echo "unknown")
    
    echo "  Project: $PROJECT_NAME"
    echo "  Type:    $PROJECT_TYPE"
    echo "  Status:  $PROJECT_STATUS"
    
    # 2. Load preferred model
    DEFAULT_MODEL=$(grep -m1 '^  default:' "$AGENT_FILE" | sed 's/.*default: *//' || echo "auto")
    if [[ "$DEFAULT_MODEL" != "auto" ]]; then
        echo "  Model:   $DEFAULT_MODEL"
    fi
    
    # 3. Check for skills referenced
    SKILLS=$(sed -n '/^skills:/,/^[^ ]/p' "$AGENT_FILE" | grep '^  - ' | sed 's/^  - //' || true)
    if [[ -n "$SKILLS" ]]; then
        echo -e "${YELLOW}  Skills:${NC}"
        echo "$SKILLS" | while read -r skill; do
            if [[ -d "$HOME/.agent/skills/$skill" ]]; then
                echo -e "    ${GREEN}✓${NC} $skill"
            else
                echo -e "    ${YELLOW}○${NC} $skill (not in ~/.agent/skills/)"
            fi
        done
    fi
    
    # 4. Check for squads referenced
    SQUADS=$(sed -n '/^squads:/,/^[^ ]/p' "$AGENT_FILE" | grep '^  - ' | sed 's/^  - //' || true)
    if [[ -n "$SQUADS" ]]; then
        echo -e "${YELLOW}  Squads (on-demand):${NC}"
        echo "$SQUADS" | while read -r squad; do
            if [[ -d "$HOME/.agent/squads/$squad" ]]; then
                echo -e "    ${GREEN}✓${NC} $squad"
            else
                echo -e "    ${YELLOW}○${NC} $squad (not in ~/.agent/squads/)"
            fi
        done
    fi
    
else
    echo -e "${YELLOW}○ No AGENT.md found in current directory${NC}"
    echo "  Run: cp ~/.agent/templates/AGENT.md ./AGENT.md"
fi

# 5. Global config check
if [[ -f "$CONFIG_FILE" ]]; then
    echo -e "${GREEN}✓ ~/.agent/config.yaml loaded${NC}"
else
    echo -e "${YELLOW}○ ~/.agent/config.yaml not found${NC}"
fi

echo -e "${CYAN}================================${NC}"

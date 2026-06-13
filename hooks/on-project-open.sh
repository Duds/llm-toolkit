#!/usr/bin/env bash
# ~/.agent/hooks/on-project-open.sh
# Shell version for macOS/Linux harnesses
# Runs when a project is opened — detects AGENT.md and sets session context

set -euo pipefail

PROJECT_PATH="${1:-$(pwd)}"
AGENT_FILE="$PROJECT_PATH/AGENT.md"
FALLBACK_FILE="$PROJECT_PATH/CLAUDE.md"
CONFIG_FILE="$HOME/.agent/config.yaml"

# Colors
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${CYAN}=== ~/.agent Project Open ===${NC}"

# Detect AGENT.md or fallback to CLAUDE.md
CONFIG_FILE_PATH=""
if [[ -f "$AGENT_FILE" ]]; then
    CONFIG_FILE_PATH="$AGENT_FILE"
    echo -e "${GREEN}✓ AGENT.md detected${NC}"
elif [[ -f "$FALLBACK_FILE" ]]; then
    CONFIG_FILE_PATH="$FALLBACK_FILE"
    echo -e "${YELLOW}○ CLAUDE.md detected (legacy — consider migrating to AGENT.md)${NC}"
fi

if [[ -n "$CONFIG_FILE_PATH" ]]; then
    # Parse YAML frontmatter
    FRONTMATTER=$(sed -n '/^---$/,/^---$/p' "$CONFIG_FILE_PATH" | sed '1d;$d')

    PROJECT_NAME=$(echo "$FRONTMATTER" | grep -m1 '^name:' | sed 's/^name: *//' || echo "unknown")
    PROJECT_TYPE=$(echo "$FRONTMATTER" | grep -m1 '^type:' | sed 's/^type: *//' || echo "unknown")
    PROJECT_STATUS=$(echo "$FRONTMATTER" | grep -m1 '^status:' | sed 's/^status: *//' || echo "unknown")

    echo "  Project: $PROJECT_NAME"
    echo "  Type:    $PROJECT_TYPE"
    echo "  Status:  $PROJECT_STATUS"

    # Preferred model
    DEFAULT_MODEL=$(echo "$FRONTMATTER" | grep -m1 '^  default:' | sed 's/^  default: *//' || echo "auto")
    if [[ "$DEFAULT_MODEL" != "auto" ]]; then
        echo "  Model:   $DEFAULT_MODEL"
    fi

    # Skills check
    SKILLS=$(sed -n '/^skills:/,/^[^ ]/p' "$CONFIG_FILE_PATH" | grep '^  - ' | sed 's/^  - //' || true)
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

    # Squads check
    SQUADS=$(sed -n '/^squads:/,/^[^ ]/p' "$CONFIG_FILE_PATH" | grep '^  - ' | sed 's/^  - //' || true)
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
    echo -e "${YELLOW}○ No AGENT.md found in $PROJECT_PATH${NC}"
    echo "  Run: cp ~/.agent/templates/AGENT.md ./AGENT.md"
fi

# Global config check
if [[ -f "$CONFIG_FILE" ]]; then
    echo -e "${GREEN}✓ ~/.agent/config.yaml loaded${NC}"
else
    echo -e "${YELLOW}○ ~/.agent/config.yaml not found${NC}"
fi

echo -e "${CYAN}================================${NC}"

#!/usr/bin/env bash
# ~/.agents/scripts/promote.sh
# Promote a skill/agent/squad/hook from ~/.claude/ to ~/.agents/

set -euo pipefail

AGENTS_DIR="${HOME}/.agents"
CLAUDE_DIR="${HOME}/.claude"

if [[ $# -lt 2 ]]; then
    echo "Usage: promote.sh <type> <name>"
    echo "  type: skill | agent | squad | hook"
    echo "  name: item name"
    exit 1
fi

TYPE="$1"
NAME="$2"

case "${TYPE}" in
    skill)
        SOURCE="${CLAUDE_DIR}/skills/${NAME}"
        TARGET="${AGENTS_DIR}/skills/${NAME}"
        ;;
    agent)
        SOURCE="${CLAUDE_DIR}/agents/${NAME}"
        TARGET="${AGENTS_DIR}/agents/${NAME}"
        ;;
    squad)
        SOURCE="${CLAUDE_DIR}/squads/${NAME}"
        TARGET="${AGENTS_DIR}/squads/${NAME}"
        ;;
    hook)
        SOURCE="${CLAUDE_DIR}/hooks/${NAME}"
        TARGET="${AGENTS_DIR}/hooks/${NAME}"
        ;;
    *)
        echo "Unknown type: ${TYPE}"
        exit 1
        ;;
esac

if [[ ! -e "${SOURCE}" ]]; then
    echo "Source not found: ${SOURCE}"
    exit 1
fi

if [[ -e "${TARGET}" ]]; then
    echo "Target already exists: ${TARGET}"
    echo "Use --force to overwrite"
    exit 1
fi

cp -r "${SOURCE}" "${TARGET}"
echo "Promoted ${TYPE}: ${NAME}"
echo "  From: ${SOURCE}"
echo "  To:   ${TARGET}"
echo ""
echo "Next steps:"
echo "  1. Review and clean for portability (remove DCCEEW-specific content)"
echo "  2. Commit to llm-toolkit: cd ~/30-PROJECTS/llm-toolkit && git add . && git commit"
echo "  3. Sync to other machines: ~/.agents/scripts/sync.sh"

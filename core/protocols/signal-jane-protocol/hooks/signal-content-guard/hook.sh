#!/usr/bin/env bash
# signal-content-guard/hook.sh
# PreToolUse hook wrapper for Python scanner.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON_CMD:-python3}"
SCANNER="$SCRIPT_DIR/scan.py"

INPUT=$(cat)

# Check if tool is send_message
TOOL_NAME=$(printf '%s' "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)
if [[ "$TOOL_NAME" != "send_message" ]]; then
    printf '%s' "$INPUT"
    exit 0
fi

# Run content scanner
RESULT=$(printf '%s' "$INPUT" | "$PYTHON" "$SCANNER" 2>/dev/null) || {
    printf '%s' "$INPUT"
    exit 0
}

if [[ "$RESULT" == CLEAN ]]; then
    printf '%s' "$INPUT"
    exit 0
fi

if [[ "$RESULT" == BLOCKED\|* ]]; then
    MODIFIED_JSON="${RESULT#BLOCKED|}"
    printf '%s' "$MODIFIED_JSON"
    exit 0
fi

printf '%s' "$INPUT"
exit 0

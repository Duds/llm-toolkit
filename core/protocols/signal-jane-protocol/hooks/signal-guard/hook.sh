#!/usr/bin/env bash
# signal-guard/hook.sh
# PreToolUse hook on send_message.
# BLOCKS any Signal message unless explicitly pre-approved in this session.
#
# Exit: 0 = allow (possibly modified), 1 = block with error

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INPUT=$(cat)

# Extract tool name
TOOL_NAME=$(printf '%s' "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)
if [[ "$TOOL_NAME" != "send_message" ]]; then
    printf '%s' "$INPUT"
    exit 0
fi

# Extract target
TARGET=$(printf '%s' "$INPUT" | jq -r '.arguments.target // empty' 2>/dev/null)

# If not Signal, allow through
if [[ "$TARGET" != signal* && "$TARGET" != *signal* ]]; then
    printf '%s' "$INPUT"
    exit 0
fi

# Check for explicit approval token
APPROVAL_FILE="/tmp/hermes_signal_approval_$(id -u).json"
if [[ -f "$APPROVAL_FILE" ]]; then
    APPROVAL_AGE=$(($(date +%s) - $(stat -f%m "$APPROVAL_FILE" 2>/dev/null || stat -c%Y "$APPROVAL_FILE" 2>/dev/null || echo 0)))
    if [[ "$APPROVAL_AGE" -lt 300 ]]; then
        # Approval exists and is recent — allow through (Layer 2 will still sanitize)
        printf '%s' "$INPUT"
        exit 0
    fi
fi

# NO VALID APPROVAL — BLOCK and redirect to user
MODIFIED=$(printf '%s' "$INPUT" | jq '
    .arguments.target = "origin" |
    .arguments.message = (
        "[SIGNAL DRAFT BLOCKED — AWAITING YOUR APPROVAL]\n\n" +
        (.arguments.message | tostring) +
        "\n\n[Reply with: send4492 to authorize this message]"
    )
')

printf '%s' "$MODIFIED"
exit 0

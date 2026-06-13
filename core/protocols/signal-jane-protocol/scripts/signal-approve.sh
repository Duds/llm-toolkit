#!/usr/bin/env bash
# signal-approve.sh
# Write approval token for Signal message send.
# Usage: signal-approve.sh [nonce]
# Called when user says "send4492" in the chat.

set -uo pipefail

NONCE="${1:-$(openssl rand -hex 8)}"
APPROVAL_FILE="/tmp/hermes_signal_approval_$(id -u).json"

cat > "$APPROVAL_FILE" << EOF
{
  "approved": true,
  "nonce": "$NONCE",
  "timestamp": $(date +%s),
  "expires": $(($(date +%s) + 300)),
  "source": "user_explicit_approval"
}
EOF

echo "Signal send approved. Token: $NONCE (expires in 5 minutes)"

#!/usr/bin/env bash
# mac-setup.sh — One-time setup after cloning llm-toolkit into ~/.agent

set -euo pipefail

AGENT_ROOT="$HOME/.agent"
CLAUDE_DIR="$HOME/.claude"
KIMI_DIR="$HOME/.kimi"

echo "=== ~/.agent Mac Setup ==="

# Verify this repo is at ~/.agent
if [[ "$(cd "$AGENT_ROOT" 2>/dev/null && pwd)" != "$(cd "$(dirname "$0")/.." && pwd)" ]]; then
    echo "WARNING: This script expects to be run from ~/.agent/scripts/mac-setup.sh"
    echo "Current repo root: $(cd "$(dirname "$0")/.." && pwd)"
    echo "Expected: $AGENT_ROOT"
    read -r -p "Continue anyway? (y/N) " reply
    if [[ "$reply" != "y" ]]; then
        exit 1
    fi
fi

# Ensure required directories exist
for dir in skills agents squads hooks templates scripts harness-integrations/claude harness-integrations/kimi harness-integrations/openai; do
    mkdir -p "$AGENT_ROOT/$dir"
done

echo ""
echo "=== Claude Code integration ==="
if [[ -d "$CLAUDE_DIR" ]]; then
    echo "Found ~/.claude"
else
    echo "Creating ~/.claude"
    mkdir -p "$CLAUDE_DIR"
fi

CLAUDE_SETTINGS="$CLAUDE_DIR/settings.json"
if [[ -f "$CLAUDE_SETTINGS" ]]; then
    echo "Existing ~/.claude/settings.json found."
    echo "ACTION REQUIRED: merge the following into ~/.claude/settings.json"
    echo ""
    cat "$AGENT_ROOT/harness-integrations/claude/settings.json"
    echo ""
else
    cp "$AGENT_ROOT/harness-integrations/claude/settings.json" "$CLAUDE_SETTINGS"
    echo "Created ~/.claude/settings.json"
fi

echo ""
echo "=== Kimi integration ==="
if [[ -d "$KIMI_DIR" ]]; then
    echo "Found ~/.kimi"
else
    echo "Creating ~/.kimi"
    mkdir -p "$KIMI_DIR"
fi

KIMI_CONFIG="$KIMI_DIR/config.yaml"
if [[ -f "$KIMI_CONFIG" ]]; then
    echo "Existing ~/.kimi/config.yaml found."
    echo "ACTION REQUIRED: include ~/.agent/harness-integrations/kimi/agent-config.yaml in ~/.kimi/config.yaml"
else
    cp "$AGENT_ROOT/harness-integrations/kimi/agent-config.yaml" "$KIMI_CONFIG"
    echo "Created ~/.kimi/config.yaml"
fi

echo ""
echo "=== Verification ==="
skill_count=$(find "$AGENT_ROOT/skills" -maxdepth 1 -mindepth 1 -type d | wc -l)
squad_count=$(find "$AGENT_ROOT/squads" -maxdepth 1 -mindepth 1 -type d | wc -l)
echo "Skills: $skill_count"
echo "Squads: $squad_count"

if [[ -f "$AGENT_ROOT/squads/workspace-cleanup/SQUAD.md" ]]; then
    echo "OK workspace-cleanup squad found"
else
    echo "WARNING: workspace-cleanup squad not found"
fi

echo ""
echo "=== Next steps ==="
echo "1. Restart Claude Code"
echo "2. Test a skill: /llm-wiki or /5s"
echo "3. Optionally add hooks to your harness startup: ~/.agent/hooks/on-start.sh"
echo ""
echo "Setup complete."

---
name: "kimi-tier"
description: >-
  Guide for selecting the right Kimi model tier (K2/K2.5/K2.6) as a
  cost-optimised alternative to the Claude Haiku/Sonnet/Opus tiers.
  Covers launching, caching strategy, and thinking-mode use.
triggers:
  - "kimi tier"
  - "which kimi"
  - "kimi model"
  - "/kimi-tier"
scope: global
---

# Kimi Tier Selector

## How to Launch

| Command | Model | Claude Equivalent | Best For |
|---------|-------|-------------------|----------|
| `kimi` | **K2.5** | Sonnet | Multimodal dev, UI screenshots → code, active coding |
| `kimi-deep` | **K2.6** | Opus | Architecture, long-horizon refactors, deep debugging |
| `kimi-fast` | **K2 (0905)** | Haiku | Boilerplate, lint, unit tests, routine chores |

Run any of these from a Git Bash terminal to launch Claude Code on the Kimi backend.

## Pricing Snapshot (vs Anthropic)

| Model | Input | Output | Cache Hit | Savings vs Claude |
|-------|-------|--------|-----------|-------------------|
| K2 (Haiku tier) | $0.35/M | $1.75/M | $0.09/M | ~70% cheaper |
| K2.5 (Sonnet tier) | $0.60/M | $3.00/M | $0.15/M | ~75% cheaper |
| K2.6 (Opus tier) | $0.95/M | $4.00/M | $0.24/M | ~80% cheaper |

Cache hit = 75% discount on input tokens (automatic, no configuration needed).

## Top 3 Cost Optimisation Strategies

**1. Maximise cache hits — stay in long sessions.**
Kimi automatically caches context. Keep related tasks in one session rather
than opening new chats. Repeated system prompts and file context are charged
at the lower cache-hit rate.

**2. Reserve Thinking Mode for hard decisions.**
Thinking Mode (`kimi-k2.6-thinking` or `kimi-k2.5-thinking`) produces much
higher token usage. Use it for architecture decisions only, not routine tasks.

**3. Use `kimi-fast` for noisy/frequent tasks.**
Lint, formatting, test generation — these are high-volume, low-complexity.
Route them to K2 to avoid burning K2.5/K2.6 budget on simple work.

## API Configuration (How It Works)

The `kimi`, `kimi-deep`, and `kimi-fast` launchers set these env vars:

```bash
ANTHROPIC_BASE_URL="https://api.moonshot.ai/anthropic"  # Kimi's Anthropic-compatible endpoint
ANTHROPIC_AUTH_TOKEN="<your moonshot API key>"
ANTHROPIC_DEFAULT_HAIKU_MODEL="kimi-k2-0905"
ANTHROPIC_DEFAULT_SONNET_MODEL="kimi-k2.5"
ANTHROPIC_DEFAULT_OPUS_MODEL="kimi-k2.6"
ANTHROPIC_MODEL="kimi-k2.5"   # overrides for this session
```

Claude Code routes to the Kimi API transparently — all tools, MCP, hooks,
and skills continue to work unchanged.

## ⚠️ Limitation: Thinking Mode Not Supported

**Kimi's Anthropic-compatible API does NOT support Claude's "thinking mode".**

If you see this error:
```
API Error: 400 {"type":"error","error":{"type":"invalid_request_error","message":"messages.1.content.0: Invalid signature in thinking block"}}
```

**Cause:** Thinking mode was activated (via `Ctrl+Shift+T` or `/think`), but Kimi cannot process Anthropic's thinking blocks.

**Fix:** Exit thinking mode (`Ctrl+Shift+T` again) or restart the session. Use native `claude` (not `kimi`) if you need thinking mode.

## API Key Setup

1. Get a key from [platform.moonshot.ai](https://platform.moonshot.ai)
2. Write it to `~/.config/kimi/api_key` (no quotes, just the key)
   OR set `MOONSHOT_API_KEY` as a Windows environment variable

## Kimi-Specific Model IDs

| Use case | Model ID |
|----------|----------|
| Haiku-tier | `kimi-k2-0905` |
| Sonnet-tier | `kimi-k2.5` |
| Opus-tier | `kimi-k2.6` |
| Sonnet + reasoning | `kimi-k2.5-thinking` |
| Opus + reasoning | `kimi-k2.6-thinking` |

> Verify current IDs at platform.moonshot.ai/docs — IDs may change with new releases.

## Fallback Integration

The existing `kimi-fallback` and `kimi-stop` hooks detect when the Anthropic
usage limit is hit and remind you to run `kimi` to continue without Anthropic
billing. Once your API key is configured in `~/.config/kimi/api_key`, this
fallback works automatically.

## MCP Cost Delegation (Optional)

The `kimi-code-mcp` community MCP server lets Claude delegate expensive
codebase reads to Kimi K2.5, saving ~60-80% on analysis tokens:

```json
{
  "mcpServers": {
    "kimi-analyzer": {
      "command": "npx",
      "args": ["-y", "kimi-code-mcp"]
    }
  }
}
```

Add to `~/.claude/mcp.json` or the project-level `.mcp.json`.

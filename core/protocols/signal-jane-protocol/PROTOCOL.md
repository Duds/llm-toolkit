---
name: signal-jane-protocol
description: "Enforced protocol for messaging Jane via Signal. Multi-layer safety: hooks, content sanitization, memory-lock, and explicit approval."
version: 1.0.0
author: Dale Rogers
platforms: [macos]
metadata:
  hermes:
    tags: [signal, messaging, safety, enforcement, jane]
---

# Signal Jane Protocol — Enforced

## Overview

Belt-and-braces enforcement for messaging Jane via Signal. Four independent layers prevent unauthorized sends, content leakage, and tone violations.

## The Four Layers

### Layer 1: signal-guard (Authorization Gate)
**Location:** `~/.agents/core/protocols/signal-jane-protocol/hooks/signal-guard/`
**Event:** PreToolUse on `send_message`
**Function:** Blocks ALL Signal sends unless explicit approval token exists.

**Approval mechanism:**
```bash
# User says: send4492
~/.agents/core/protocols/signal-jane-protocol/scripts/signal-approve.sh
```

Writes token to `/tmp/hermes_signal_approval_<uid>.json` (expires 5 minutes).

**Behaviour:**
- No approval → message redirected to `origin` (you) with block notice
- Valid approval → passes through to Layer 2

### Layer 2: signal-content-guard (Content Sanitizer)
**Location:** `~/.agents/core/protocols/signal-jane-protocol/hooks/signal-content-guard/`
**Event:** PreToolUse on `send_message`
**Function:** Sanitizes message content even if Layer 1 passed.

**Auto-strips:**
- Error messages, tracebacks, exceptions
- Console/terminal output, JSON, log timestamps
- File paths, system commands
- API keys, tokens, bearer strings

**Flags for approval:**
- Sexual/romantic content
- Health/mental health details
- Financial amounts >$100
- Joint plans ("we should", "let's", "our plan")

**Behaviour:**
- Violations detected → message replaced with block notice + cleaned version
- User must re-approve with `send4492`

### Layer 3: Memory-Locked Constitutional Rule
**Injected into every session via `memory` tool**
**Content:** "I am NEVER authorized to send Signal messages to Jane without explicit user approval phrase 'send4492' in this exact conversation."

**Function:** Prevents reasoning drift. Even if hooks fail, the memory rule is active in-context.

### Layer 4: User Tone Calibration
**Source:** 2,703 outgoing messages analyzed from Signal export
**Calibrated patterns:**
- Warm greetings, emoji use, playful teasing
- Supportive, self-deprecating humor
- Concise: 1-3 short paragraphs max
- Never: formal, technical, robotic, passive-aggressive

## Workflow

### Normal Draft Flow
1. You ask me to draft a message to Jane
2. I draft in your voice, show it to you
3. You review, say "edit" or "send"
4. If "send", you must also say `send4492`
5. Both hooks pass → message sent

### Emergency / Quick Send
1. You say: "Send Jane: [message]"
2. I echo back: "Draft: [message] — say send4492 to send"
3. You say: `send4492`
4. Both hooks pass → message sent

## Files

| File | Purpose |
|------|---------|
| `hooks/signal-guard/hook.sh` | Layer 1: authorization gate |
| `hooks/signal-content-guard/hook.sh` | Layer 2: content sanitizer wrapper |
| `hooks/signal-content-guard/scan.py` | Layer 2: Python scanner |
| `scripts/signal-approve.sh` | Approval token writer |
| `memory: SIGNAL PROTOCOL` | Layer 3: constitutional rule |

## Maintenance

### Check hook health
```bash
bash ~/.agents/core/protocols/signal-jane-protocol/hooks/signal-guard/hook.sh <<< '{"tool_name":"send_message","arguments":{"target":"signal:test","message":"test"}}'
```

### Reset / revoke approval
```bash
rm /tmp/hermes_signal_approval_$(id -u).json
```

## Pitfalls

- **Approval expires in 5 minutes** — intentional, one-shot per message
- **Hooks only catch `send_message` tool** — other tools won't be caught
- **Hooks run in order** — signal-guard first, then signal-content-guard
- **Token is session-wide** — any approved message can send for 5 minutes

## Future Enhancements

- Per-message nonce matching (tighter approval)
- Time-of-day gate (no sends before 7am or after 10pm)
- Rate limiting (max N messages per hour)
- Tone validation layer (ML-based style check)

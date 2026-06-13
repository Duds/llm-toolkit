---
name: "signal-content-guard"
display-name: "Signal Content Sanitizer"
description: >-
  PreToolUse hook on send_message. Sanitizes message content destined for Signal.
  Strips technical output, error messages, JSON, file paths, API keys, and flags
  unauthorized sensitive topics (sexual, health, financial, joint plans).
event: PreToolUse
matcher: "send_message"
scope: global
---

# Signal Content Sanitizer

## Purpose

Content-level enforcement: even if authorization passes (Layer 1), this hook
ensures the message content itself is safe and appropriate.

## Sanitization Rules

**FORBIDDEN (auto-stripped):**
- Error messages, tracebacks, exceptions
- Console/terminal output
- JSON, log timestamps, memory addresses
- File paths, system commands (curl, python, npm, git, hermes)
- API keys, tokens, bearer strings

**SENSITIVE TOPICS (flagged for approval):**
- Sexual/romantic content
- Health/mental health details
- Financial amounts over $100, bank/payment terms
- Joint plans using "we should", "let's", "our plan"

## Behaviour

- **CLEAN:** No violations detected → pass through
- **BLOCKED:** Violations detected → message replaced with block notice
- User must review and re-authorize with `APPROVE_SIGNAL_SEND`

## Layer

This is **Layer 2** of the Signal enforcement stack.
Runs after Layer 1 (signal-guard) if Layer 1 passed.

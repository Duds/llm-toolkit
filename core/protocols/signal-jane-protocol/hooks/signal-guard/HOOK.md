---
name: "signal-guard"
display-name: "Signal Authorization Gate"
description: >-
  PreToolUse hook on send_message. BLOCKS any Signal message to Jane unless
  explicitly pre-approved by user in this exact session. Rewrites unauthorized
  sends to self-targeted drafts for review.
event: PreToolUse
matcher: "send_message"
scope: global
---

# Signal Authorization Gate

## Purpose

Absolute enforcement: no Signal message to Jane without explicit user approval.
Even if the LLM reasoning drifts, this hook physically intercepts the tool call.

## Behaviour

- **ALLOW:** Non-Signal targets, or Signal targets with valid session approval token
- **BLOCK & REDIRECT:** Signal target without approval → message sent to user (origin) instead
- **Approval mechanism:** User must reply `APPROVE_SIGNAL_SEND` in this session

## Approval Token

Written to `/tmp/hermes_signal_approval_<uid>.json` when user says the magic phrase.
Token expires after 5 minutes (one-shot per message).

## Layer

This is **Layer 1** of the Signal enforcement stack.
Layer 2 (signal-content-guard) sanitizes content even if Layer 1 passes.

---
name: simplify
description: >
  Audit recently written or changed code for over-engineering and bloat, then rewrite to the
  simplest correct version. Use when the user invokes /simplify, asks "is this too complex?",
  "simplify this", "is this over-engineered?", or wants a Karpathy-style code review.
  Also triggered automatically after a code task if the user has passive guardrails enabled.
---

# Simplify

Audit the code in scope against the workspace coding philosophy (STANDARDS.md §9) and rewrite
anything that fails. This is not a general code review — it is a targeted simplicity audit.

## Audit checklist

Work through these checks in order. For each failure, rewrite immediately rather than listing it.

1. **Minimum code** — could this be written in fewer lines without sacrificing readability or
   correctness? If yes, rewrite it.

2. **No speculative features** — does any code serve a use case not present in the current task?
   Remove it.

3. **No one-off abstractions** — are there classes, interfaces, or helper functions used only
   once? Inline them.

4. **No unrequested flexibility** — are there config options, flags, or extension points the user
   did not ask for? Remove them.

5. **No impossible error handling** — does any error handler guard against a condition that
   cannot occur given the system's invariants? Remove it.

6. **200-to-50 rule** — count approximate lines in the solution. Could a correct, readable
   version be written in ≤25% of that count? If yes, this is a mandatory rewrite — do it before
   reporting done.

7. **Senior Engineer Test** — read the code as a senior engineer would on first review. Would
   they say "this is overcomplicated"? If yes, find what triggered that reaction and remove it.

## Output contract

- Report which checks passed (one line each).
- For each failure: show the before, show the after, explain what was removed and why.
- End with a single line: total lines before → total lines after.
- Do not add features, improve naming, or refactor beyond what the checks require.

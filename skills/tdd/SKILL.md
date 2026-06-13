---
name: tdd
description: "Test-Driven Development skill. Trigger whenever the user invokes /tdd, says \"write tests first\", \"do TDD\", \"red-green-refactor\", \"test-driven\", or is implementing a new function, module, or feature and wants to follow a strict TDD loop. Also trigger when a user is debugging a failing test methodically, wants to improve coverage on existing code, or is using Claude Code / Cursor / Copilot agent in an agentic coding session and needs enforced TDD discipline. Never allow jumping straight to implementation — enforce the red-green-refactor cycle without exception. For agentic sessions, enforce phase gates that block progression until each step is verified."
---

# TDD — Test-Driven Development

## The cycle

```
RED   → Write a failing test that describes desired behaviour
GREEN → Write the minimum code to make it pass
REFACTOR → Clean up without breaking the test
```

Never skip RED. Never write implementation before a failing test exists.

## Phase gates (agentic sessions)

Each gate must pass before the next phase begins:

1. **RED gate** — test exists and fails for the right reason
   - Run the test suite, confirm failure
   - Confirm the failure message describes the missing behaviour
   - Do NOT proceed until failure is confirmed

2. **GREEN gate** — test passes, nothing else broken
   - Run full test suite, not just the new test
   - Zero regressions allowed
   - Do NOT proceed until suite is green

3. **REFACTOR gate** — code is clean, suite still green
   - Remove duplication
   - Improve naming
   - Run suite again after refactoring

## Rules

- One failing test at a time — don't write a batch of tests upfront
- Minimum implementation only — resist gold-plating on GREEN
- If you can't make a test fail first, the test is wrong
- Tests are specifications — they describe behaviour, not implementation

## Test naming

```
test_[unit]_[scenario]_[expected_outcome]
# e.g. test_parser_empty_input_returns_empty_list
```

## Handoff

When a feature is complete (all acceptance criteria have passing tests),
update TASKS.md and offer to run `close-and-learn`.

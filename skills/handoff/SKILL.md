---
name: handoff
description: >-
  Create a structured handoff document saved to the temp directory so a fresh
  agent can read it and continue the work. Trigger whenever the user wants to
  pass context to another agent or future session — say "hand off", "handoff",
  "pass this to another agent", "create a handoff doc", "summarize for the
  next agent", "write a handoff", "document progress for next session",
  "prepare a handoff", "capture where we left off", "another person is
  taking over", "switching sessions", or invoke /handoff. Use this skill for
  any request to package conversation state into a file for another agent to
  read, even without the word "handoff". Differs from close-and-learn: handoff
  writes a file to disk for another agent; close-and-learn generates a
  pasteable prompt for the user.
---

# Handoff

Create a compact handoff document that lets a fresh agent pick up where this
conversation left off.

## Why this matters

Context windows are finite. Long conversations get truncated or slow down.
A good handoff document captures the *state* of the work: decisions,
outstanding items, and pointers, without duplicating everything that
happened. The next agent reads this single file and is up to speed.

## Steps

### 1. Determine the scope

If the user passed arguments (for example, `/handoff "fix the auth bug"`),
treat them as the focus for the next session. Tailor the handoff toward that
focus rather than trying to capture the entire conversation history.

If no arguments were given, capture the full conversation state.

### 2. Gather the state

Review the conversation and extract:

- **What we were trying to do** — the goal or task, in one sentence
- **What got done** — completed work, merged PRs, files created or modified
- **Key decisions** — architectural choices, approach selections, rejections
- **Current blockers** — errors, unknowns, dependencies, approvals needed
- **What is partially done** — work in progress with current status
- **What is next** — the immediate next step(s) to take
- **Files and artifacts** — paths to relevant code, docs, diagrams, data
- **Environment context** — branch names, running services, special configs

### 3. Decide: capture or reference?

Do NOT duplicate content that already lives in an artifact. Reference it by
path. Only inline information that exists only in the conversation.

| Inline (put in the handoff) | Reference (just list the path) |
|----------------------------|--------------------------------|
| Decisions made verbally | PRDs, ADRs, design docs |
| Error messages or stack traces | Source code files |
| Requirements clarified during chat | Commit messages, diffs |
| Temporary workarounds | Issue tracker links |
| Outstanding questions | Full project documentation |

### 4. Redact sensitive information

Before writing the document, scan for and redact:
- API keys, tokens, passwords
- Personally identifiable information (PII)
- Internal URLs or hostnames that should not be shared
- Proprietary data or unreleased product details

Replace with `[REDACTED]` or a description of what was there.

### 5. Write the handoff document

Save to the operating system's temporary directory:
- **Windows**: `%TEMP%` (resolve via `$env:TEMP`)
- **macOS / Linux**: `/tmp`

Use this filename pattern:
```
handoff_<YYYY-MM-DD>_<short-topic>.md
```

For example: `handoff_2026-05-29_auth-refactor.md`

Use this exact template:

```markdown
# Handoff: <Short Topic>

**Date:** <YYYY-MM-DD>
**Session focus:** <what the next session should tackle>

## Goal
<One sentence on what the overall task is.>

## Progress so far
<Bullet list of completed work. Be specific: file paths, commit hashes, PR numbers.>

## Key decisions
<Bullet list. Include the "why" if it was discussed.>

## Current state
<What is the situation right now? What file is open? What command was last run?>

## Blockers and open questions
<Bullet list. Include error messages or stack traces if relevant.>

## Next steps
<Numbered list, most urgent first. Each step should be actionable by a fresh agent.>

## Files and references
<Path or URL to every artifact mentioned above.>

## Suggested skills
<If particular skills would help the next agent, list them by name. Only suggest
skills that are actually relevant to the next steps.>
```

### 6. Confirm with the user

Tell the user where the file was saved and offer to:
- Add anything they think is missing
- Trim anything that feels excessive
- Adjust the focus if the scope is wrong

## Guidelines

- Keep the document under 500 lines. If it is longer, you are duplicating too
  much — move content to a proper artifact and reference it.
- Write for a stranger. The next agent has zero context. Define acronyms,
  name the project, explain the stack.
- Be specific, not vague. "Fixed the bug" is useless. "Fixed the null-pointer
  in `UserService.getProfile()` by adding a null check on line 47" is useful.
- Include the emotional state if relevant. "This approach was rejected after
  three attempts" tells the next agent not to retry the same dead end.
- If the conversation is very short (under 10 turns) with no decisions or
  work product, a handoff document may be unnecessary. Tell the user this
  and ask if they still want one.

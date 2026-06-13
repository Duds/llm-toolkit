---
name: improve-prompt
description: "Optimize prompts for clarity and effectiveness. Use when user says \"improve this prompt\", \"optimize my prompt\", \"make this clearer\", or provides vague/unstructured prompts. Intelligently routes to sub-agents for codebase research, clarifying questions, or web search as needed."
---

# Improve Prompt

## Purpose

Take a vague or underspecified prompt and rewrite it to be clear,
targeted, and likely to produce the desired output first time.

## Process

1. **Identify what's missing:**
   - Role / persona for the model?
   - Output format specified?
   - Constraints stated?
   - Examples provided?
   - Success criteria clear?

2. **Ask one clarifying question** if the intent is ambiguous.
   Never ask more than one.

3. **Rewrite** the prompt with:
   - A clear role statement if relevant
   - Explicit output format (length, structure, tone)
   - Constraints and edge cases called out
   - One example of good output if it helps

4. **Show before/after** so the user can see what changed and why.

## Output format

```
## Original
[original prompt]

## Issues
- [issue 1]
- [issue 2]

## Improved
[rewritten prompt]

## What changed
[1–2 sentences]
```

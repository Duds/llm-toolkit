---
name: design-thinking
description: >-
  Guide a human-centered design process through the five design thinking phases:
  Empathize, Define, Ideate, Prototype, and Test. Trigger when the user says
  "design thinking", "HCD session", "let's do a design sprint", "help me with
  service design", "I need to run an ideation session", "empathy mapping",
  "How Might We", "POV statement", or starts describing a user problem and wants
  a structured process to solve it. Also trigger for government service design
  work (DCCEEW delivery) where understanding citizen or stakeholder needs is
  the primary goal before solution-building begins.
---

# Design Thinking Workflow

## Purpose

Facilitate a structured human-centered design session from empathy through to
tested solutions. The output is a design thinking record — a single document
capturing decisions, insights, and next steps at each phase.

## Principles

- Users first: keep real user needs at the centre of every decision
- Diverge before converging: generate wide before narrowing
- Make it tangible: a rough prototype beats a polished discussion
- Fail forward: testing surfaces learning, not failure
- No AI time estimates: never speculate on how long implementation will take

## Process

Follow `./references/instructions.md` step by step.

The method library is in `./references/design-methods.csv` — draw from it
at each phase to suggest contextually appropriate methods.

The output template is `./references/template.md` — fill it section by section
as the session progresses.

## Phases

| # | Phase | Goal |
|---|-------|------|
| 1 | Context | Gather the design challenge and constraints |
| 2 | Empathize | Build deep understanding of users |
| 3 | Define | Frame the problem clearly |
| 4 | Ideate | Generate diverse solution concepts |
| 5 | Prototype | Make ideas tangible |
| 6 | Test | Validate with real users |
| 7 | Next steps | Plan the iteration roadmap |

## Output

Produce a single Markdown document using `./references/template.md` as the
structure. Save to `{output_folder}/design-thinking-{date}.md`. After each
phase is complete, show the filled section and ask the user to confirm before
moving to the next phase.

## Checkpoints

After completing each phase section:
1. Save the content to the output file
2. Show what was generated
3. Ask: continue to next phase / revise this section / end session here

## Notes

- One question at a time during elicitation — never stack questions
- When the user seems to be jumping to solutions, redirect back to the relevant phase
- If the user can't access real users, flag this as a risk and suggest proxy methods
- This skill is compatible with government service design (DCCEEW) — citizen and
  stakeholder needs are valid user research contexts

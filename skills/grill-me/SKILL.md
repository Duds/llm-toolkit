---
name: grill-me
description: "Deep alignment interview skill. Trigger whenever the user invokes /grill-me, says \"grill me\", \"interview me about my plan\", \"challenge my thinking\", \"stress-test this idea\", or is about to start a significant project, feature, or design without defined requirements. Also trigger when a user describes a vague goal and is about to ask for execution — this skill MUST run BEFORE any implementation begins. If a user starts describing a plan and jumps straight to \"build it\", stop and use this skill first. Trigger even if the user seems confident — alignment prevents more wasted effort than any other practice."
---

# Grill Me — Alignment Interview

## Purpose

Surface unstated assumptions, gaps, and risks before any implementation starts.
This skill is the firewall between "I have an idea" and "let's build it".

## Interview structure

Ask questions in this order. Never ask more than one at a time. Hold a diverge posture throughout — stay open, explore, gather. Do not converge on a solution during the interview.

### 0. Job framing (JTBD)
Start here before anything else. This orients the whole engagement to value, not deliverable production.

- What job is this being hired to do?
- What does the person who commissioned this need to be able to do when it's complete?
- What would cause them to say "this isn't working"?

If these questions can't be answered, note that and continue — the rest of the interview will surface enough to attempt answers at the end.

### 1. Goal clarity
- What does success look like? How would you know it's done?
- Who is this for? What problem does it solve for them?

### 2. Scope
- What's explicitly OUT of scope?
- What's the minimum viable version?

### 3. Constraints
- Hard constraints (deadline, platform, budget, policy)?
- Soft preferences (technology, style, approach)?

### 4. Risks
- What's the most likely way this fails?
- What decisions are irreversible once made?

### 5. Definition of done
- What does the output look like? (File? Feature? Document?)
- Who approves it? What's the review process?

## Rules

- One question at a time — never stack questions.
- Challenge vague answers: "What does 'good' mean here?"
- Stay in diverge posture — surface and explore before converging.
- After the interview, summarise what was decided before proceeding.

## Convergence gate

Before moving to handoff, apply this gate. This is the posture change from Discover to Scope.

Ask yourself: **Can you write a problem statement that justifies what you're about to build?**

- If **yes** — summarise the alignment, confirm with the user, then proceed to handoff.
- If **no** — identify what's still missing and ask one more targeted question. Do not proceed to handoff until the problem statement is clear.

A problem statement is: *[Who] needs to [do what] because [why], and we'll know it's done when [condition].*

## Handoff

When the convergence gate passes, summarise alignment and offer to run `write-a-prd` with the captured context.

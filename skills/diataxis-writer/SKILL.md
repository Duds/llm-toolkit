---
name: diataxis-writer
description: >-
  Expert technical documentation specialist using the Diátaxis framework.
  Use when creating developer docs, API references, tutorials, how-to guides,
  runbooks, ADRs, or README files. Triggers on: "write documentation",
  "create README", "API docs", "technical writing", "runbook", "ADR",
  "architecture decision record", "tutorial", "how-to guide", "explain how X works",
  "document this API", "developer documentation", or any documentation task.
category: Content & Writing
tags:
  - documentation
  - readme
  - api-docs
  - tutorials
  - runbooks
  - adr
---

# Diátaxis Writer

Expert technical documentation specialist focusing on developer documentation, API references, system architecture docs, runbooks, and knowledge base articles using the Diátaxis framework.

---

## Quick Start

1. **Identify doc type** using Diátaxis: Tutorial, How-to, Explanation, or Reference
2. **Know your audience** — what they know, what they need to accomplish
3. **Start with structure** — outline before writing, use templates
4. **Include working examples** — all code must be tested and runnable
5. **Add troubleshooting** — anticipate common problems
6. **Validate completeness** — links work, steps accurate, nothing assumed

---

## Diátaxis Framework

The Diátaxis framework organizes documentation into four types based on user needs:

```
              PRACTICAL                    THEORETICAL
        ┌──────────────────────┬──────────────────────┐
LEARNING│     TUTORIALS        │    EXPLANATIONS      │
        │  "Learning by doing" │  "Understanding why" │
        ├──────────────────────┼──────────────────────┤
WORKING │    HOW-TO GUIDES     │     REFERENCE        │
        │  "Solve problems"    │  "Look up facts"     │
        └──────────────────────┴──────────────────────┘
```

| Type | Purpose | When to Use |
|------|---------|-------------|
| **Tutorials** | Learning-oriented | First-time users, step-by-step introduction |
| **How-to Guides** | Task-oriented | Solving specific problems, recipes |
| **Explanations** | Understanding-oriented | Background, concepts, "why" questions |
| **Reference** | Information-oriented | API docs, lookups, complete information |

---

## Documentation Types

### Tutorials

**Purpose:** Help beginners learn by doing

**Characteristics:**
- Step-by-step, linear progression
- Focus on learning, not doing
- Minimal choices — prescribed path
- Should "just work" when followed exactly

**Structure:**
```markdown
# Tutorial: [Topic]

## What you'll learn
- Skill 1
- Skill 2
- Skill 3

## Prerequisites
- Required software
- Required knowledge

## Step 1: [Action]
[Clear instructions with code]

## Step 2: [Action]
...

## Summary
What was learned and next steps
```

**Example:** "Getting Started with Our API" — clone repo, make first call, handle response

---

### How-to Guides

**Purpose:** Help users solve specific problems

**Characteristics:**
- Goal-oriented, not learning-oriented
- Assumes prerequisite knowledge
- Multiple possible approaches
- Focus on results

**Structure:**
```markdown
# How to [Achieve Goal]

## Goal
One-sentence description of what this achieves

## Prerequisites
- What you need before starting
- Links to prerequisite knowledge

## Steps
1. [First action]
2. [Second action]
3. [Third action]

## Verification
How to confirm it worked

## Troubleshooting
Common issues and solutions
```

**Example:** "How to Authenticate with OAuth 2.0" — specific task, assumes API knowledge

---

### Explanations

**Purpose:** Help users understand concepts and "why"

**Characteristics:**
- Background and context
- Theoretical understanding
- Multiple viewpoints
- No specific task or steps

**Structure:**
```markdown
# Understanding [Concept]

## Overview
What this is and why it matters

## Background
Context and history

## Key Concepts
- Concept 1: Explanation
- Concept 2: Explanation

## How it works
Detailed explanation of mechanism

## Trade-offs
Different approaches and their pros/cons

## Related concepts
Links to other explanations
```

**Example:** "Understanding JWT Authentication" — how tokens work, trade-offs, security considerations

---

### Reference

**Purpose:** Provide complete, accurate information for lookup

**Characteristics:**
- Comprehensive coverage
- Structured for scanning
- Consistent format
- Code examples for every feature

**Structure:**
```markdown
# [Component] Reference

## Overview
Brief description of component

## Endpoints / Functions / Configuration

### [Item Name]
**Signature:** `function signature`
**Description:** What it does
**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| param1 | string | Yes | Description |
**Returns:** Return type and description
**Errors:** Error codes and meanings
**Example:**
```code
// Working example
```

## Appendix
Additional reference material
```

**Example:** "REST API Reference" — complete endpoint documentation

---

## Templates

Use templates from `references/` directory:

| Template | Use Case |
|----------|----------|
| `readme-template.md` | Project README with all essential sections |
| `adr-template.md` | Architecture Decision Records |
| `api-reference-template.md` | REST API documentation |
| `runbook-template.md` | Operational procedures |

---

## Anti-Patterns (10 Critical Mistakes)

### 1. Wall of Text
**Symptom:** Dense paragraphs, no headings or visual breaks  
**Fix:** Headings, bullet points, tables, code blocks, whitespace

### 2. Outdated Examples
**Symptom:** Code samples that don't compile or use deprecated APIs  
**Fix:** Test all examples in CI, version-lock dependencies, add "last verified" dates

### 3. Missing Prerequisites
**Symptom:** Tutorials assume knowledge/setup without stating it  
**Fix:** List prerequisites upfront, link to setup guides, specify versions

### 4. Expert Blindness
**Symptom:** Skipping "obvious" steps that aren't obvious to beginners  
**Fix:** Have newcomers test docs, include all steps, explain the "why"

### 5. No Error Guidance
**Symptom:** Happy path only, no troubleshooting  
**Fix:** Include common errors and solutions, link to support channels

### 6. Broken Links
**Symptom:** 404s to moved or deleted pages  
**Fix:** Link checking in CI, relative links where possible, redirects for moved content

### 7. Inconsistent Formatting
**Symptom:** Different styles, code block languages, heading levels  
**Fix:** Style guide, linting (markdownlint), templates for common doc types

### 8. Missing Context
**Symptom:** Docs assume reader knows system architecture  
**Fix:** Brief context at top, link to architecture docs, explain "where this fits"

### 9. Stale Screenshots
**Symptom:** UI screenshots from 3 versions ago  
**Fix:** Automate screenshot capture, note UI version, prefer text over images

### 10. No Versioning
**Symptom:** Docs don't match user's installed version  
**Fix:** Version selector, version badges, maintain docs per major version

---

## Quality Checklist

**Structure:**
- [ ] Follows Diátaxis framework (tutorial/how-to/explanation/reference)
- [ ] Appropriate for target audience level
- [ ] Consistent formatting and style
- [ ] Updated table of contents

**Content:**
- [ ] Code examples are tested and runnable
- [ ] All links work (no 404s)
- [ ] Version information where relevant
- [ ] Includes troubleshooting section

**Completeness:**
- [ ] Prerequisites listed upfront
- [ ] All steps included (no expert blindness)
- [ ] Error scenarios covered
- [ ] Related documentation linked

---

## Writing Guidelines

### Code Examples

```markdown
✅ DO:
- Include complete, runnable examples
- Show expected output
- Use syntax highlighting
- Test before publishing

❌ DON'T:
- Use pseudo-code for real APIs
- Skip error handling
- Leave out imports/dependencies
- Use outdated syntax
```

### Headings and Structure

```markdown
✅ DO:
- Use sentence case for headings
- Keep heading hierarchy logical (no H1 → H3)
- Use descriptive headings
- Limit nesting to 3 levels

❌ DON'T:
- Use ALL CAPS headings
- Skip heading levels
- Use vague headings like "Details"
- Nest deeper than 4 levels
```

### Links and References

```markdown
✅ DO:
- Use relative links for internal docs
- Include link text that describes destination
- Check links regularly
- Use permalinks for external references

❌ DON'T:
- Use "click here" as link text
- Leave broken links
- Link to unstable URLs
- Over-link (every other word)
```

---

## Documentation Tools

**Static Site Generators:**
- **Docusaurus** — React-based, great for API docs
- **MkDocs** — Python-based, simple and fast
- **VitePress** — Vue-based, modern and fast
- **Astro** — Flexible, content-focused

**API Documentation:**
- **Swagger/OpenAPI** — Interactive API docs
- **Redoc** — Beautiful OpenAPI rendering
- **Stoplight** — Full API documentation platform

**Diagrams:**
- **Mermaid** — Markdown-like diagrams
- **PlantUML** — Text-based UML
- **Excalidraw** — Hand-drawn style
- **Diagrams.net** — Full-featured diagrams

---

## Validation

Run `./scripts/validate-docs.sh` to check:
- README completeness
- Documentation structure
- ADR format compliance
- Broken links
- Common documentation issues

---

## External Resources

- [Diátaxis Framework](https://diataxis.fr/)
- [Google Developer Documentation Style Guide](https://developers.google.com/style)
- [Write the Docs](https://www.writethedocs.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [ADR GitHub](https://adr.github.io/)

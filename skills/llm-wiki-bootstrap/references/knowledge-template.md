---
title: "Page Title"
date: YYYY-MM-DD
type: [blueprint|concept|decision|research|reference|case-study]
diataxis: [tutorial|how-to|explanation|reference]
sources:
  - raw/source-file.pdf
tags:
  - tag1
  - tag2
confidence: [high|medium|low]
---

# Page Title

One-sentence description of what this page covers.

---

## Overview

2-3 paragraph summary of the content. For:
- **tutorial**: What the learner will accomplish
- **how-to**: What problem this solves
- **explanation**: The concept being explained
- **reference**: Scope of the information provided

---

## Main Content

Structure based on diataxis type:

### For Tutorial (learning by doing)

```markdown
## What you'll learn
- Skill 1
- Skill 2

## Prerequisites
- Required knowledge/tools

## Step 1: [Action]
Instructions...

## Step 2: [Action]
Instructions...

## Summary
What was learned
```

### For How-to (task-oriented)

```markdown
## Goal
What this achieves

## Prerequisites
What you need first

## Steps
1. [Action]
2. [Action]

## Verification
How to confirm it worked

## Troubleshooting
Common issues
```

### For Explanation (understanding why)

```markdown
## Background
Context and history

## Key Concepts
- Concept 1: Explanation
- Concept 2: Explanation

## How it works
Detailed mechanism

## Trade-offs
Different approaches

## Related concepts
Links to other pages
```

### For Reference (information lookup)

```markdown
## [Section Name]

### [Item]
**Field:** Value
**Field:** Value

## [Section Name]

| Column | Column | Column |
|--------|--------|--------|
| Data   | Data   | Data   |
```

---

## Cross-references

- [[related-page]] — Brief description of relationship
- [[another-page]] — Brief description of relationship

---

## Sources

- Original: [source filename in raw/]
- Related: [other relevant sources]

---

## Changelog

- YYYY-MM-DD: Initial creation

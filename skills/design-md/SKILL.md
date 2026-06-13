---
name: design-md
description: Generate Stitch-compatible DESIGN.md files from design assets, brand guidance, or conceptual briefs. Supports generic brand visual identity and seed mode for documentation-only projects.
allowed-tools:
  - "stitch*:*"
  - "Read"
  - "Write"
  - "web_fetch"
---

# DESIGN.md Skill

You are an expert design systems lead. Your goal is to analyze design assets, brand guidance, or project context and write a canonical `DESIGN.md` file that captures the visual system in a stitch-compatible format.

## Overview

This skill creates a machine-readable design system file that is the source of truth for screen generation, interface consistency, and brand-aligned visual development. It supports:
- Stitch project screens and HTML/CSS assets
- Brand guidance documents and identity tokens
- Generic brand-aligned visual systems
- Conceptual projects with no rendered UI yet

## Requirements

- Output must follow the official Google Stitch DESIGN.md convention:
  - YAML frontmatter with machine-readable tokens
  - Markdown body with exactly six top-level sections in fixed order
  - Section headings must match the spec exactly
- If no code or rendered screens exist, generate a seed `DESIGN.md` and include `<!-- SEED -->` at the top of the markdown body.
- When a formal brand guide exists, use its explicit tokens as the source of truth.

## Retrieval and Networking

### For Stitch projects
1. **Namespace discovery**: Run `list_tools` to find the Stitch MCP prefix.
2. **Project lookup**: Use `[prefix]:list_projects` with `filter: "view=owned"`.
3. **Screen lookup**: Use `[prefix]:list_screens` with the numeric `projectId`.
4. **Metadata fetch**: Use `[prefix]:get_screen` with `projectId` and `screenId`.
5. **Asset download**: Use `web_fetch` or `read_url_content` to fetch HTML and screenshots.
6. **Project metadata extraction**: Use `[prefix]:get_project` to read `designTheme` and other brand details.

### For brand-guided or documentation-only projects
- Search local brand guidance files, design briefs, document templates, and training content.
- Extract the visual tone, token palette, typography, spacing, and component conventions from brand documents.
- When a formal brand guide exists, use its explicit tokens as the source of truth.

## Analysis & Synthesis Instructions

### 1. Determine mode
- **Scan mode**: Code, rendered screens, or explicit design tokens are available. Extract actual values.
- **Seed mode**: Only guidance, documentation, or verbal direction exists. Draft a normative system and mark it `<!-- SEED -->`.

### 2. Capture the visual story
- Identify the system's mood and personality.
- Translate it into a high-level creative north star and an aesthetic description.
- Use natural language, not implementation detail.

### 3. Extract the token palette
- Colors: map each key value to a descriptive name and role.
- Typography: capture families, weights, sizes, line-height, and character.
- Rounded corners: map radii to tangible descriptions.
- Spacing: capture the working scale used by the system.
- Components: define core variants and how they use the primitives.

### 4. Respect the Stitch DESIGN.md format
- Frontmatter is the normative source of truth.
- The markdown body provides context and application guidance.
- Do not add extra top-level sections beyond the six required ones.
- Fold layout and spacing guidance into `Overview`, `Components`, or `Do's and Don'ts`.

## Output Format (DESIGN.md Structure)

```markdown
---
name: [Project Title]
description: [One-line tagline]
colors:
  # one entry per extracted color
typography:
  # one entry per role
rounded:
  # radius scale
spacing:
  # spacing scale
components:
  # optional component variants
---

# Design System: [Project Title]

## 1. Overview

## 2. Colors

## 3. Typography

## 4. Elevation

## 5. Components

## 6. Do's and Don'ts
```

## Best Practices

- **Use exact tokens**: frontmatter values should match the source of truth.
- **Keep hierarchy clear**: describe what is used where and why.
- **Avoid extra sections**: the six Stitch sections are the contract.
- **Keep prose grounded**: explain how the system supports the work, not just what it looks like.

## Common Pitfalls to Avoid

- ❌ Writing a design memo instead of a machine-readable design spec
- ❌ Omitting YAML frontmatter or using the wrong section order
- ❌ Inventing tokens that do not exist in the project
- ❌ Using broad marketing language instead of concrete visual rules
- ❌ Adding a top-level `Layout Principles` or `Prompt Guidance` section

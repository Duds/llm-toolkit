# Merge Evaluation: svg-drawing + svg-precision-skill

**Date:** 2026-05-22  
**Author:** Dale Rogers (with AI)  
**Status:** Recommendation — keep separate, add cross-references

## Current State

### svg-drawing
- **Purpose:** Iterative creative drawing with visual feedback
- **Trigger:** "draw a hedgehog", "create vector artwork", "sketch a logo"
- **Workflow:** Write SVG → render to PNG → view → adjust → repeat
- **Strength:** Visual feedback loop for artistic exploration
- **Weakness:** No precision guarantees; coordinates are guessed by the LLM

### svg-precision-skill
- **Purpose:** Deterministic spec-driven rendering
- **Trigger:** "draw a diagram", "create a flowchart", "build a process cycle"
- **Workflow:** Write JSON spec → deterministic render → validate → export
- **Strength:** Exact coordinates, repeatable output, PowerPoint-safe
- **Weakness:** Requires structured input; less suitable for freeform art

## Overlap Analysis

| Concern | svg-drawing | svg-precision-skill | Overlap? |
|---------|------------|---------------------|----------|
| Triggers | Artistic/creative | Technical/diagram | Low |
| User intent | "I want to explore" | "I want it exact" | Low |
| Input format | Freeform SVG markup | Structured JSON spec | None |
| Output quality | Approximate, iterative | Deterministic, validated | Different |
| Tooling | render-svg (PNG preview) | svg_cli.py (build/validate/export) | Different |

## Conclusion

**Do not merge.** The skills serve fundamentally different jobs:

- `svg-drawing` = **artistic exploration** (divergent thinking, visual feedback)
- `svg-precision-skill` = **technical precision** (convergent thinking, deterministic output)

Merging them would confuse trigger routing and dilute the focused description of each.

## Recommended Architecture

Keep separate with clear boundaries and cross-references:

```
svg-drawing           svg-precision-skill
(artistic)            (technical)
    |                       |
    |    Both can use:      |
    +---- Inkscape CLI ----+
          (export only)
```

### Cross-references to add

**In svg-drawing SKILL.md:**
> For precise diagrams, flowcharts, and technical drawings, use `svg-precision-skill` instead.

**In svg-precision-skill SKILL.md:**
> For freeform artistic exploration, use `svg-drawing` instead.

## Future Enhancement (Phase 4)

A unified `svg` meta-skill could route between modes based on trigger:

| Trigger pattern | Routes to |
|-----------------|-----------|
| "draw", "sketch", "illustrate", "artwork" | svg-drawing |
| "diagram", "flowchart", "chart", "technical drawing" | svg-precision-skill |

This would be a thin router, not a merge. Each underlying skill remains independent.

## Action Items

1. [x] Add cross-reference in svg-drawing SKILL.md → svg-precision-skill
2. [x] Add cross-reference in svg-precision-skill SKILL.md → svg-drawing
3. [ ] Optional: create `svg` router skill if trigger confusion arises in practice

---
name: html2pptx
description: "Converts a single, static HTML slide into a pixel-accurate, fully editable PowerPoint slide, extracting positioned elements and placeholders using a real browser render."
---

# HTML to PPTX Conversion

## Purpose

Convert a static HTML slide (single page) into a fully editable PowerPoint slide (.pptx)
that preserves positioning, typography, and visual layout.

## When to use

- You have an HTML slide (from om-canvas-slides or any other source)
- You need it as a PowerPoint file the user can edit in PowerPoint or present
- You want pixel-accurate conversion, not a screenshot

## Process

1. Read the skill at `/mnt/skills/user/html2pptx/SKILL.md` for the full
   technical implementation — this stub routes to it.
2. The conversion uses a headless browser to render the HTML, extracts
   positioned elements, and maps them to PPTX shapes.
3. Output is a `.pptx` file with editable text boxes, shapes, and images.

## Notes

- Works best on single-slide HTML files with absolute or flex positioning
- Complex CSS animations and gradients are simplified
- Web fonts are substituted with closest PowerPoint equivalents
- For multi-slide decks, convert slides individually then merge

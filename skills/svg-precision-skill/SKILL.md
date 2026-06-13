---
name: svg-precision-skill
description: Generate deterministic SVGs from structured specs with validation and rendering. Use for icons, diagrams, charts, UI mockups, technical drawings, and flowcharts. Trigger on "draw a diagram", "create an SVG flowchart", "build a process cycle", "generate a service blueprint SVG", or any request for precise, repeatable vector graphics.
---

# SVG Precision Skill

Build SVGs from explicit scene specifications, then validate before handing them off.

## Modes

### Mode 1: Element spec (manual coordinates)
For fine-grained control: specify every shape, coordinate, and style directly.

```bash
python scripts/svg_cli.py build spec.json out.svg
```

### Mode 2: Diagram spec (auto-layout)
For flowcharts, cycles, grids: describe nodes, edges, and layout type. The engine assigns exact coordinates deterministically.

```bash
python scripts/svg_cli.py diagram spec.json out.svg
```

### Mode 3: Export (optional — requires Inkscape)
Post-process SVGs for distribution. Inkscape must be installed and on PATH.

```bash
# Export PNG at 300 DPI
python scripts/svg_cli.py export diagram.svg diagram.png --dpi 300

# Export PDF
python scripts/svg_cli.py export diagram.svg diagram.pdf

# Apply Inkscape actions then export
python scripts/svg_cli.py export diagram.svg clean.svg --actions "vacuum-defs"
```

Inkscape must be installed and on PATH. On Windows a portable install is common; on Mac use `brew install inkscape` or install the official app.

## Workflow

1. Translate the request into a concrete spec.
2. Use `references/spec.md` for schema details and `references/recipes.md` for stable layout patterns.
3. Build the SVG:
   - Element mode: `scripts/svg_cli.py build`
   - Diagram mode: `scripts/svg_cli.py diagram`
4. Validate with `scripts/svg_cli.py validate`.
5. Render a PNG preview when the user needs a quick visual check.

## Rules

- Set `viewBox`, width, and height explicitly.
- Prefer absolute coordinates and simple shapes.
- Treat text as risky when exact rendering matters.
- Avoid exotic filters unless they are necessary and testable.
- For diagram mode: let the engine compute coordinates. Never guess positions.

## Related skills

For freeform artistic exploration and creative sketching without structured specs, use `svg-drawing` instead.

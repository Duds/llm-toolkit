# Recipes (predictable rendering)

## Universal

- Always include `xmlns="http://www.w3.org/2000/svg"` (the builder does this).
- Use `shape-rendering: geometricPrecision` for technical drawings.
- For crisp 1px lines on pixel grids: use integer coords and odd/even stroke widths intentionally.
- Prefer `fill="none"` on stroked shapes to avoid accidental fills.

## Icons

- Default canvas: 24x24 viewBox.
- Stroke-based: `strokeLinecap: round`, `strokeLinejoin: round`, `strokeWidth: 2`.
- Avoid filters; keep paths simple; expand strokes only if a consumer requires it.

## Diagrams / Flowcharts

- Use a marker arrow in defs; connect shapes using `line` or `path`.
- Group each node: background shape + label text in a `group`.
- Keep consistent padding: 16-24px inside nodes.
- Route edges orthogonally when readability matters (use `path` with `M L L` segments).

## Charts

- Build chart area first (axes box), then plot area, then labels.
- Reserve margins (e.g., left 80, bottom 60, right 40, top 40) so labels never clip.
- Snap bars/points to integers; round tick labels; keep gridlines light.

## UI mockups

- Start with a background rect (page) and a 8pt grid.
- Use large corner radii (16-24) for modern cards.
- Keep text styles consistent: titles 24-32, body 14-16.
- Shadows vary across renderers; prefer subtle strokes unless the shadow is essential.

## Technical drawings

- Specify units in `canvas.units` and include scale in metadata.
- Use thin strokes (0.5-1.5) and set `vector-effect: non-scaling-stroke` when scaling output.
- Dimensions: extension lines + dimension line + arrow markers + centered label.
- Add centerlines / dashed lines with `strokeDasharray`.

## Diagram / Flowchart (auto-layout)

- Use `svg_cli.py diagram` for all flowcharts, cycles, grids, and hierarchies.
- Never guess coordinates — describe topology and let the engine compute positions.
- Keep labels short (1-3 words) for best automatic sizing.
- For decision diamonds, keep labels very short or the diamond grows unwieldy.
- Use `routing: orthogonal` for process flows; use `routing: curved` for cycle layouts.
- Edge labels appear centered on the connector. For orthogonal edges, they offset perpendicular to the main segment.

### PowerPoint-safe diagram rules

- Set `style.nodeFont` to a Windows-safe stack: `Arial, sans-serif` or `Segoe UI, sans-serif`.
- Avoid gradients in `style` — use solid `nodeFill` values.
- The engine produces flat SVG with inline styles, no `<style>` blocks, no filters.
- All text is `<text>` elements (not `textPath`) — editable when imported to PowerPoint.

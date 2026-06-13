"""Diagram layout engine — converts high-level diagram specs to element specs.

Topology (nodes, edges, layout type) → deterministic coordinates → element list.
The LLM describes structure; this engine assigns exact positions.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

from .core import build_svg


def build_diagram(spec: Dict[str, Any]) -> str:
    """Build an SVG from a diagram spec.

    Diagram spec keys (in addition to standard canvas/metadata):
      - layout: {"type": "flow-horizontal" | "flow-vertical" | "grid" | "cycle" | "free", ...}
      - nodes: [{"id": str, "type": str, "label": str, ...}, ...]
      - edges: [{"from": str, "to": str, "label": str}, ...]
      - style: optional defaults

    Returns the SVG string.
    """
    canvas = spec.get("canvas") or {}
    layout = spec.get("layout") or {}
    nodes = spec.get("nodes") or []
    edges = spec.get("edges") or []
    style = spec.get("style") or {}

    if not nodes:
        raise ValueError("diagram spec must contain at least one node")

    # Compute positions
    layout_type = layout.get("type", "flow-horizontal")
    positions, node_sizes = _compute_layout(layout_type, nodes, layout, canvas)

    # Build element list
    elements: List[Dict[str, Any]] = []
    defs: Dict[str, Any] = {"markers": []}

    # Add arrow marker
    arrow_color = style.get("edgeColor", "#444")
    defs["markers"].append({
        "id": "arrow",
        "markerWidth": 10,
        "markerHeight": 10,
        "refX": 9,
        "refY": 5,
        "orient": "auto",
        "pathD": "M0 0 L10 5 L0 10 Z",
        "style": {"fill": arrow_color},
    })

    # Build edge elements first (so they render behind nodes)
    edge_elements = _build_edges(edges, positions, node_sizes, layout_type, style)
    elements.extend(edge_elements)

    # Build node elements
    for node in nodes:
        nid = node["id"]
        x, y = positions[nid]
        nw, nh = node_sizes[nid]
        node_els = _build_node(node, x, y, nw, nh, style)
        elements.extend(node_els)

    # Assemble standard spec
    full_spec = {
        "canvas": canvas,
        "defs": defs,
        "elements": elements,
        "metadata": spec.get("metadata") or {},
    }

    return build_svg(full_spec)


# ---------------------------------------------------------------------------
# Layout computation
# ---------------------------------------------------------------------------

def _compute_layout(
    layout_type: str,
    nodes: List[Dict[str, Any]],
    layout: Dict[str, Any],
    canvas: Dict[str, Any],
) -> Tuple[Dict[str, Tuple[float, float]], Dict[str, Tuple[float, float]]]:
    """Return (positions dict, sizes dict) for each node id."""
    # Estimate sizes from labels
    sizes = {n["id"]: _estimate_node_size(n, layout) for n in nodes}

    if layout_type == "free":
        positions = _layout_free(nodes, sizes, layout)
    elif layout_type == "grid":
        positions = _layout_grid(nodes, sizes, layout, canvas)
    elif layout_type == "cycle":
        positions = _layout_cycle(nodes, sizes, layout, canvas)
    elif layout_type == "flow-vertical":
        positions = _layout_flow(nodes, sizes, layout, canvas, vertical=True)
    else:
        positions = _layout_flow(nodes, sizes, layout, canvas, vertical=False)

    return positions, sizes


def _estimate_node_size(node: Dict[str, Any], layout: Dict[str, Any]) -> Tuple[float, float]:
    """Estimate (width, height) from label text and node type."""
    label = node.get("label", "")
    ntype = node.get("type", "process")

    # Approximate text metrics: ~7px per char at font size 14
    font_size = float(layout.get("fontSize", 14))
    char_w = font_size * 0.55
    padding_x = float(layout.get("paddingX", 24))
    padding_y = float(layout.get("paddingY", 16))

    text_w = max(len(label) * char_w, font_size * 3)
    text_h = font_size * 1.4

    # Minimum dimensions per type
    min_dims = {
        "start": (80, 40),
        "terminator": (80, 40),
        "process": (100, 50),
        "decision": (100, 60),
        "document": (100, 55),
        "data": (100, 50),
        "manual": (100, 50),
        "subprocess": (100, 50),
    }
    min_w, min_h = min_dims.get(ntype, (100, 50))

    width = max(text_w + padding_x * 2, min_w)
    height = max(text_h + padding_y * 2, min_h)

    # Decision diamonds need extra width/height to look right
    if ntype == "decision":
        width = max(width, height * 1.4)
        height = max(height, width * 0.7)

    return (width, height)


def _layout_free(
    nodes: List[Dict[str, Any]],
    sizes: Dict[str, Tuple[float, float]],
    layout: Dict[str, Any],
) -> Dict[str, Tuple[float, float]]:
    positions: Dict[str, Tuple[float, float]] = {}
    for n in nodes:
        nid = n["id"]
        x = float(n.get("x", 0))
        y = float(n.get("y", 0))
        positions[nid] = (x, y)
    return positions


def _layout_flow(
    nodes: List[Dict[str, Any]],
    sizes: Dict[str, Tuple[float, float]],
    layout: Dict[str, Any],
    canvas: Dict[str, Any],
    vertical: bool = False,
) -> Dict[str, Tuple[float, float]]:
    """Arrange nodes left-to-right (or top-to-bottom) with wrapping."""
    positions: Dict[str, Tuple[float, float]] = {}
    padding = float(layout.get("padding", 40))
    node_spacing = float(layout.get("nodeSpacing", 60))
    layer_spacing = float(layout.get("layerSpacing", 100))

    canvas_w = float(canvas.get("width", 1200))
    canvas_h = float(canvas.get("height", 800))

    if vertical:
        # Top-to-bottom, wrap into columns
        col_x = padding
        col_w = 0
        current_y = padding
        max_h = canvas_h - padding

        for n in nodes:
            nid = n["id"]
            nw, nh = sizes[nid]

            if current_y + nh > max_h and current_y > padding:
                # Wrap to next column
                col_x += col_w + node_spacing
                col_w = 0
                current_y = padding

            positions[nid] = (col_x, current_y)
            col_w = max(col_w, nw)
            current_y += nh + layer_spacing
    else:
        # Left-to-right, wrap into rows
        row_y = padding
        row_h = 0
        current_x = padding
        max_w = canvas_w - padding

        for n in nodes:
            nid = n["id"]
            nw, nh = sizes[nid]

            if current_x + nw > max_w and current_x > padding:
                # Wrap to next row
                row_y += row_h + layer_spacing
                row_h = 0
                current_x = padding

            positions[nid] = (current_x, row_y)
            row_h = max(row_h, nh)
            current_x += nw + node_spacing

    return positions


def _layout_grid(
    nodes: List[Dict[str, Any]],
    sizes: Dict[str, Tuple[float, float]],
    layout: Dict[str, Any],
    canvas: Dict[str, Any],
) -> Dict[str, Tuple[float, float]]:
    """Arrange nodes in a grid."""
    positions: Dict[str, Tuple[float, float]] = {}
    cols = int(layout.get("cols", 3))
    padding = float(layout.get("padding", 40))
    node_spacing = float(layout.get("nodeSpacing", 60))

    # Compute column widths and row heights
    col_widths: List[float] = [0.0] * cols
    row_heights: List[float] = []

    for i, n in enumerate(nodes):
        nid = n["id"]
        nw, nh = sizes[nid]
        col = i % cols
        row = i // cols
        col_widths[col] = max(col_widths[col], nw)
        if row >= len(row_heights):
            row_heights.append(0.0)
        row_heights[row] = max(row_heights[row], nh)

    # Position nodes
    for i, n in enumerate(nodes):
        nid = n["id"]
        col = i % cols
        row = i // cols
        x = padding + sum(col_widths[:col]) + col * node_spacing
        y = padding + sum(row_heights[:row]) + row * node_spacing
        positions[nid] = (x, y)

    return positions


def _layout_cycle(
    nodes: List[Dict[str, Any]],
    sizes: Dict[str, Tuple[float, float]],
    layout: Dict[str, Any],
    canvas: Dict[str, Any],
) -> Dict[str, Tuple[float, float]]:
    """Arrange nodes in a circle."""
    positions: Dict[str, Tuple[float, float]] = {}
    padding = float(layout.get("padding", 80))
    canvas_w = float(canvas.get("width", 1200))
    canvas_h = float(canvas.get("height", 800))

    cx = canvas_w / 2
    cy = canvas_h / 2

    # Compute radius based on node sizes
    max_nw = max(sizes[n["id"]][0] for n in nodes) if nodes else 100
    max_nh = max(sizes[n["id"]][1] for n in nodes) if nodes else 50
    radius = min(cx, cy) - max(max_nw, max_nh) / 2 - padding
    radius = max(radius, 100)

    count = len(nodes)
    for i, n in enumerate(nodes):
        angle = 2 * math.pi * i / count - math.pi / 2  # Start at top
        x = cx + radius * math.cos(angle) - sizes[n["id"]][0] / 2
        y = cy + radius * math.sin(angle) - sizes[n["id"]][1] / 2
        positions[n["id"]] = (x, y)

    return positions


# ---------------------------------------------------------------------------
# Node rendering
# ---------------------------------------------------------------------------

def _build_node(
    node: Dict[str, Any],
    x: float,
    y: float,
    w: float,
    h: float,
    style: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Return element list for a single node (shape + label)."""
    ntype = node.get("type", "process")
    label = node.get("label", "")
    nid = node.get("id", "")

    # Colors
    node_fill = node.get("fill") or style.get("nodeFill", "#f7f7f7")
    node_stroke = node.get("stroke") or style.get("nodeStroke", "#444")
    text_fill = node.get("textFill") or style.get("textFill", "#111")
    font_family = style.get("nodeFont", "Arial, sans-serif")
    font_size = float(style.get("nodeFontSize", 14))
    stroke_width = float(style.get("strokeWidth", 2))

    elements: List[Dict[str, Any]] = []

    # Shape
    if ntype in ("start", "terminator"):
        rx = h / 2
        elements.append({
            "type": "rect",
            "x": x, "y": y, "width": w, "height": h,
            "rx": rx, "ry": rx,
            "style": {"fill": node_fill, "stroke": node_stroke, "strokeWidth": stroke_width},
        })
    elif ntype == "process":
        rx = min(12, h / 4)
        elements.append({
            "type": "rect",
            "x": x, "y": y, "width": w, "height": h,
            "rx": rx, "ry": rx,
            "style": {"fill": node_fill, "stroke": node_stroke, "strokeWidth": stroke_width},
        })
    elif ntype == "subprocess":
        rx = min(8, h / 5)
        pad = 3
        elements.append({
            "type": "rect",
            "x": x, "y": y, "width": w, "height": h,
            "rx": rx, "ry": rx,
            "style": {"fill": node_fill, "stroke": node_stroke, "strokeWidth": stroke_width},
        })
        elements.append({
            "type": "rect",
            "x": x + pad, "y": y + pad, "width": w - pad * 2, "height": h - pad * 2,
            "rx": max(0, rx - pad), "ry": max(0, rx - pad),
            "style": {"fill": "none", "stroke": node_stroke, "strokeWidth": 1},
        })
    elif ntype == "decision":
        # Diamond: center at (x + w/2, y + h/2)
        cx, cy = x + w / 2, y + h / 2
        dx, dy = w / 2, h / 2
        points = [[cx, cy - dy], [cx + dx, cy], [cx, cy + dy], [cx - dx, cy]]
        elements.append({
            "type": "polygon",
            "points": points,
            "style": {"fill": node_fill, "stroke": node_stroke, "strokeWidth": stroke_width},
        })
    elif ntype == "data":
        # Parallelogram: slant by 20% of height
        slant = h * 0.2
        points = [[x + slant, y], [x + w, y], [x + w - slant, y + h], [x, y + h]]
        elements.append({
            "type": "polygon",
            "points": points,
            "style": {"fill": node_fill, "stroke": node_stroke, "strokeWidth": stroke_width},
        })
    elif ntype == "document":
        # Rectangle with wavy bottom
        wave_h = h * 0.15
        d = (
            f"M{x} {y} L{x + w} {y} L{x + w} {y + h - wave_h} "
            f"Q{x + w * 0.75} {y + h + wave_h} {x + w * 0.5} {y + h - wave_h} "
            f"Q{x + w * 0.25} {y + h + wave_h} {x} {y + h - wave_h} Z"
        )
        elements.append({
            "type": "path", "d": d,
            "style": {"fill": node_fill, "stroke": node_stroke, "strokeWidth": stroke_width},
        })
    elif ntype == "manual":
        # Trapezoid: top narrower than bottom
        inset = w * 0.1
        points = [[x + inset, y], [x + w - inset, y], [x + w, y + h], [x, y + h]]
        elements.append({
            "type": "polygon",
            "points": points,
            "style": {"fill": node_fill, "stroke": node_stroke, "strokeWidth": stroke_width},
        })
    else:
        # Default rectangle
        elements.append({
            "type": "rect",
            "x": x, "y": y, "width": w, "height": h,
            "style": {"fill": node_fill, "stroke": node_stroke, "strokeWidth": stroke_width},
        })

    # Label (centered)
    elements.append({
        "type": "text",
        "x": x + w / 2,
        "y": y + h / 2,
        "text": label,
        "anchor": "middle",
        "baseline": "middle",
        "style": {"fill": text_fill, "fontSize": font_size, "fontFamily": font_family},
    })

    return elements


# ---------------------------------------------------------------------------
# Edge rendering
# ---------------------------------------------------------------------------

def _build_edges(
    edges: List[Dict[str, Any]],
    positions: Dict[str, Tuple[float, float]],
    sizes: Dict[str, Tuple[float, float]],
    layout_type: str,
    style: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Return element list for all edges."""
    elements: List[Dict[str, Any]] = []
    edge_color = style.get("edgeColor", "#444")
    edge_width = float(style.get("edgeWidth", 2))
    edge_font = style.get("edgeFont", "Arial, sans-serif")
    edge_font_size = float(style.get("edgeFontSize", 12))
    edge_text_fill = style.get("edgeTextFill", "#555")
    routing = style.get("routing", "orthogonal")

    for edge in edges:
        src = edge["from"]
        dst = edge["to"]
        label = edge.get("label", "")

        if src not in positions or dst not in positions:
            continue

        sx, sy = positions[src]
        sw, sh = sizes[src]
        dx, dy = positions[dst]
        dw, dh = sizes[dst]

        # Compute connection points (center of each edge facing the other node)
        sp, dp = _connection_points(
            (sx, sy, sw, sh), (dx, dy, dw, dh), layout_type, routing
        )

        # Build path
        path_d = _route_edge(sp, dp, routing, layout_type)

        elements.append({
            "type": "path",
            "d": path_d,
            "style": {
                "fill": "none",
                "stroke": edge_color,
                "strokeWidth": edge_width,
                "markerEnd": "url(#arrow)",
            },
        })

        # Edge label
        if label:
            mx = (sp[0] + dp[0]) / 2
            my = (sp[1] + dp[1]) / 2
            # Offset slightly perpendicular to avoid overlapping the line
            if routing == "orthogonal":
                # For orthogonal, offset vertically if the segment is mostly horizontal
                if abs(dp[0] - sp[0]) > abs(dp[1] - sp[1]):
                    my -= edge_font_size * 0.8
                else:
                    mx += edge_font_size * 0.5
            else:
                my -= edge_font_size * 0.6

            elements.append({
                "type": "text",
                "x": mx,
                "y": my,
                "text": label,
                "anchor": "middle",
                "baseline": "middle",
                "style": {
                    "fill": edge_text_fill,
                    "fontSize": edge_font_size,
                    "fontFamily": edge_font,
                    "fontWeight": 500,
                },
            })

    return elements


def _connection_points(
    src: Tuple[float, float, float, float],
    dst: Tuple[float, float, float, float],
    layout_type: str,
    routing: str,
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Return (src_point, dst_point) as connection points on node boundaries."""
    sx, sy, sw, sh = src
    dx, dy, dw, dh = dst

    scx, scy = sx + sw / 2, sy + sh / 2
    dcx, dcy = dx + dw / 2, dy + dh / 2

    # Determine direction from src to dst
    dx_dir = dcx - scx
    dy_dir = dcy - scy

    if layout_type == "cycle":
        # For cycle layout, connect from edge center to edge center
        angle = math.atan2(dy_dir, dx_dir)
        src_pt = _point_on_rect(scx, scy, sw / 2, sh / 2, angle)
        dst_pt = _point_on_rect(dcx, dcy, dw / 2, dh / 2, angle + math.pi)
        return src_pt, dst_pt

    if layout_type in ("flow-horizontal", "grid"):
        # Prefer left/right connections
        if abs(dx_dir) >= abs(dy_dir):
            if dx_dir >= 0:
                return (sx + sw, scy), (dx, dcy)
            else:
                return (sx, scy), (dx + dw, dcy)

    if layout_type == "flow-vertical":
        # Prefer top/bottom connections
        if abs(dy_dir) >= abs(dx_dir):
            if dy_dir >= 0:
                return (scx, sy + sh), (dcx, dy)
            else:
                return (scx, sy), (dcx, dy + dh)

    # Default: connect nearest edges
    if abs(dx_dir) >= abs(dy_dir):
        if dx_dir >= 0:
            return (sx + sw, scy), (dx, dcy)
        else:
            return (sx, scy), (dx + dw, dcy)
    else:
        if dy_dir >= 0:
            return (scx, sy + sh), (dcx, dy)
        else:
            return (scx, sy), (dcx, dy + dh)


def _point_on_rect(cx: float, cy: float, hw: float, hh: float, angle: float) -> Tuple[float, float]:
    """Return point on rectangle boundary at given angle from center."""
    # Intersect ray from center with rectangle
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    if abs(cos_a) < 1e-9:
        return (cx, cy + hh * (1 if sin_a > 0 else -1))
    if abs(sin_a) < 1e-9:
        return (cx + hw * (1 if cos_a > 0 else -1), cy)

    tx = hw / abs(cos_a)
    ty = hh / abs(sin_a)
    t = min(tx, ty)

    return (cx + t * cos_a, cy + t * sin_a)


def _route_edge(
    sp: Tuple[float, float],
    dp: Tuple[float, float],
    routing: str,
    layout_type: str,
) -> str:
    """Build path d attribute for an edge."""
    sx, sy = sp
    dx, dy = dp

    if routing == "direct":
        return f"M{sx} {sy} L{dx} {dy}"

    if routing == "curved":
        # Bezier curve with control points offset perpendicular
        mx = (sx + dx) / 2
        my = (sy + dy) / 2
        # Offset control point perpendicular to the line
        dx_dir = dx - sx
        dy_dir = dy - sy
        dist = math.hypot(dx_dir, dy_dir)
        if dist < 1:
            return f"M{sx} {sy} L{dx} {dy}"
        offset = dist * 0.2
        cpx = mx - dy_dir / dist * offset
        cpy = my + dx_dir / dist * offset
        return f"M{sx} {sy} Q{cpx} {cpy} {dx} {dy}"

    # Orthogonal routing
    if layout_type == "flow-horizontal":
        # Horizontal then vertical
        mid_x = (sx + dx) / 2
        return f"M{sx} {sy} L{mid_x} {sy} L{mid_x} {dy} L{dx} {dy}"

    if layout_type == "flow-vertical":
        # Vertical then horizontal
        mid_y = (sy + dy) / 2
        return f"M{sx} {sy} L{sx} {mid_y} L{dx} {mid_y} L{dx} {dy}"

    if layout_type == "cycle":
        # Curved for cycle
        mx = (sx + dx) / 2
        my = (sy + dy) / 2
        dx_dir = dx - sx
        dy_dir = dy - sy
        dist = math.hypot(dx_dir, dy_dir)
        if dist < 1:
            return f"M{sx} {sy} L{dx} {dy}"
        offset = dist * 0.3
        cpx = mx - dy_dir / dist * offset
        cpy = my + dx_dir / dist * offset
        return f"M{sx} {sy} Q{cpx} {cpy} {dx} {dy}"

    # Default orthogonal for grid/free
    if abs(dx - sx) > abs(dy - sy):
        mid_x = (sx + dx) / 2
        return f"M{sx} {sy} L{mid_x} {sy} L{mid_x} {dy} L{dx} {dy}"
    else:
        mid_y = (sy + dy) / 2
        return f"M{sx} {sy} L{sx} {mid_y} L{dx} {mid_y} L{dx} {dy}"

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys

# Allow running from this folder without installation
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ""))

from svg_skill import build_svg, build_diagram, validate_svg, render_png, diff_svgs


def _read_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def cmd_build(args: argparse.Namespace) -> int:
    spec = _read_json(args.spec_json)
    svg_text = build_svg(spec)
    with open(args.out_svg, "w", encoding="utf-8") as f:
        f.write(svg_text)
    return 0


def cmd_diagram(args: argparse.Namespace) -> int:
    spec = _read_json(args.spec_json)
    svg_text = build_diagram(spec)
    with open(args.out_svg, "w", encoding="utf-8") as f:
        f.write(svg_text)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    report = validate_svg(args.svg, from_file=True)
    print(json.dumps(report, indent=2))
    return 1 if report.get("errors") else 0


def cmd_render(args: argparse.Namespace) -> int:
    rep = render_png(args.svg, args.out_png, scale=args.scale, from_file=True)
    print(json.dumps(rep, indent=2))
    return 0 if rep.get("ok") else 1


def cmd_diff(args: argparse.Namespace) -> int:
    rep = diff_svgs(args.a_svg, args.b_svg, args.out_png, scale=args.scale)
    print(json.dumps(rep, indent=2))
    return 0 if rep.get("ok") and not rep.get("changed") else (1 if rep.get("ok") else 2)


def cmd_export(args: argparse.Namespace) -> int:
    """Export an SVG via Inkscape CLI (optional dependency)."""
    import shutil
    import subprocess

    inkscape = shutil.which("inkscape")
    if not inkscape:
        # Fallback to common platform-specific paths
        candidates = []
        if sys.platform == "win32":
            user = os.environ.get("USER", os.environ.get("USERNAME", ""))
            candidates = [
                r"C:\Program Files\Inkscape\bin\inkscape.exe",
                rf"C:\Users\{user}\bin\InkscapePortable\App\Inkscape\bin\inkscape.exe",
            ]
        elif sys.platform == "darwin":
            candidates = [
                "/Applications/Inkscape.app/Contents/MacOS/inkscape",
                "/opt/homebrew/bin/inkscape",
                "/usr/local/bin/inkscape",
            ]
        else:
            candidates = [
                "/usr/bin/inkscape",
                "/usr/local/bin/inkscape",
                "/opt/homebrew/bin/inkscape",
            ]
        for candidate in candidates:
            if os.path.exists(candidate):
                inkscape = candidate
                break
        if not inkscape:
            print(json.dumps({"ok": False, "error": "Inkscape not found. Install it and ensure it is on PATH. See https://inkscape.org/release/"}))
            return 1

    cmd = [inkscape, args.svg]
    out = args.out

    if out.lower().endswith(".png"):
        cmd.extend(["--export-filename=" + out, "--export-dpi=" + str(args.dpi)])
    elif out.lower().endswith(".pdf"):
        cmd.extend(["--export-filename=" + out])
    elif args.actions:
        cmd.extend(["--actions=" + args.actions, "--export-filename=" + out])
    else:
        cmd.extend(["--export-filename=" + out])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        ok = result.returncode == 0
        print(json.dumps({
            "ok": ok,
            "out": out,
            "returncode": result.returncode,
            "stdout": result.stdout.strip() if result.stdout else None,
            "stderr": result.stderr.strip() if result.stderr else None,
        }, indent=2))
        return 0 if ok else 1
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="svg_cli", description="Build/validate/render deterministic SVGs")
    sp = p.add_subparsers(dest="cmd", required=True)

    p_build = sp.add_parser("build", help="Build SVG from spec.json")
    p_build.add_argument("spec_json")
    p_build.add_argument("out_svg")
    p_build.set_defaults(func=cmd_build)

    p_diag = sp.add_parser("diagram", help="Build SVG from diagram spec.json")
    p_diag.add_argument("spec_json")
    p_diag.add_argument("out_svg")
    p_diag.set_defaults(func=cmd_diagram)

    p_val = sp.add_parser("validate", help="Validate an SVG file")
    p_val.add_argument("svg")
    p_val.set_defaults(func=cmd_validate)

    p_r = sp.add_parser("render", help="Render SVG -> PNG (requires CairoSVG)")
    p_r.add_argument("svg")
    p_r.add_argument("out_png")
    p_r.add_argument("--scale", type=float, default=1.0)
    p_r.set_defaults(func=cmd_render)

    p_d = sp.add_parser("diff", help="Render two SVGs and diff (requires CairoSVG + Pillow)")
    p_d.add_argument("a_svg")
    p_d.add_argument("b_svg")
    p_d.add_argument("out_png")
    p_d.add_argument("--scale", type=float, default=1.0)
    p_d.set_defaults(func=cmd_diff)

    p_e = sp.add_parser("export", help="Export SVG via Inkscape CLI (optional)")
    p_e.add_argument("svg")
    p_e.add_argument("out")
    p_e.add_argument("--dpi", type=float, default=300)
    p_e.add_argument("--actions", type=str, default="",
                     help="Inkscape actions string, e.g. 'vacuum-defs'")
    p_e.set_defaults(func=cmd_export)

    args = p.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
vsd_to_mmd.py — Visio to Mermaid conversion utility

Converts Microsoft Visio (.vsd/.vsdx) files to Mermaid (.mmd) diagrams.
Pipeline: Visio → SVG (LibreOffice) → Mermaid (Claude Vision analysis)

Usage:
  python vsd_to_mmd.py convert <input.vsdx> [-o output_dir/] [--soffice-path PATH]
  python vsd_to_mmd.py analyze <input.svg> [-o output.mmd] [--type TYPE]
  python vsd_to_mmd.py batch <input.vsdx> [-o output_dir/] [--type TYPE]
  python vsd_to_mmd.py interactive <input.vsdx>

Requires: LibreOffice (soffice), Python 3.9+, click, rich
Optional: pillow, cairosvg (for SVG processing)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


# Fix Windows console Unicode encoding (Windows only)
if sys.platform == "win32":
    if hasattr(sys.stdout, "buffer") and sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "buffer") and sys.stderr.encoding and sys.stderr.encoding.lower() not in ("utf-8", "utf8"):
        import io
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


class VisioConverterError(Exception):
    """Base exception for Visio conversion errors."""

    pass


class LibreOfficeNotFoundError(VisioConverterError):
    """Raised when LibreOffice soffice is not found."""

    pass


class ConversionError(VisioConverterError):
    """Raised when conversion fails."""

    pass


class VisioConverter:
    """Converts Visio files to Mermaid diagrams via SVG."""

    # Common LibreOffice installation paths on Windows
    WINDOWS_SOFFICE_PATHS = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        r"C:\Users\{user}\AppData\Local\Programs\LibreOffice\program\soffice.exe",
    ]

    # Common LibreOffice installation paths on macOS/Linux
    UNIX_SOFFICE_PATHS = [
        "/usr/bin/soffice",
        "/usr/local/bin/soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/opt/homebrew/bin/soffice",
        "/usr/lib/libreoffice/program/soffice",
    ]

    # Diagram type mappings
    DIAGRAM_TYPES = {
        "flowchart": "flowchart",
        "sequence": "sequenceDiagram",
        "class": "classDiagram",
        "er": "erDiagram",
        "state": "stateDiagram-v2",
        "gantt": "gantt",
        "pie": "pie",
        "git": "gitGraph",
        "timeline": "timeline",
        "mindmap": "mindmap",
        "quadrant": "quadrantChart",
    }

    def __init__(self, soffice_path: str | None = None):
        """
        Initialize converter.

        Args:
            soffice_path: Optional path to soffice executable
        """
        self.soffice_path = soffice_path or self._find_soffice()
        self._validate_soffice()

    def _find_soffice(self) -> str:
        """Find LibreOffice soffice executable."""
        # Check PATH first
        soffice = self._which("soffice")
        if soffice:
            return soffice

        # Check platform-specific paths
        if sys.platform == "win32":
            # Windows: check USERNAME (Windows) then USER (Unix fallback)
            user = os.environ.get("USERNAME", os.environ.get("USER", ""))
            for path_template in self.WINDOWS_SOFFICE_PATHS:
                path = path_template.format(user=user)
                if Path(path).exists():
                    return path
        else:
            # macOS/Linux: check common Unix paths
            for path in self.UNIX_SOFFICE_PATHS:
                if Path(path).exists():
                    return path

        raise LibreOfficeNotFoundError(
            "LibreOffice (soffice) not found. "
            "Install from https://www.libreoffice.org/ "
            "or specify path with --soffice-path"
        )

    def _which(self, program: str) -> str | None:
        """Cross-platform which command."""
        import shutil
        return shutil.which(program)

    def _validate_soffice(self) -> None:
        """Validate soffice is working."""
        try:
            result = subprocess.run(
                [self.soffice_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                raise LibreOfficeNotFoundError(f"soffice --version failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            raise LibreOfficeNotFoundError("soffice --version timed out")
        except FileNotFoundError:
            raise LibreOfficeNotFoundError(f"soffice not found at: {self.soffice_path}")

    def visio_to_svg(
        self,
        visio_path: str | Path,
        output_dir: str | Path | None = None,
    ) -> list[Path]:
        """
        Convert Visio file to SVG(s).

        Args:
            visio_path: Path to .vsd or .vsdx file
            output_dir: Optional output directory (default: same as input)

        Returns:
            List of paths to generated SVG files
        """
        visio_file = Path(visio_path)
        if not visio_file.exists():
            raise ConversionError(f"Visio file not found: {visio_file}")

        if visio_file.suffix.lower() not in (".vsd", ".vsdx"):
            raise ConversionError(f"Expected .vsd or .vsdx, got: {visio_file.suffix}")

        out_dir = Path(output_dir) if output_dir else visio_file.parent
        out_dir.mkdir(parents=True, exist_ok=True)

        # Create temp directory for conversion
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Copy input to temp dir to avoid path issues
            temp_input = tmp_path / visio_file.name
            temp_input.write_bytes(visio_file.read_bytes())

            # Run LibreOffice conversion
            cmd = [
                self.soffice_path,
                "--headless",
                "--convert-to", "svg",
                "--outdir", str(tmp_path),
                str(temp_input),
            ]

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
            except subprocess.TimeoutExpired:
                raise ConversionError("LibreOffice conversion timed out (120s)")

            if result.returncode != 0:
                raise ConversionError(f"LibreOffice conversion failed: {result.stderr}")

            # Find generated SVG files
            svg_files = sorted(tmp_path.glob("*.svg"))

            if not svg_files:
                raise ConversionError("No SVG files generated")

            # Rename and move to output directory
            output_paths = []
            base_name = visio_file.stem

            for i, svg_file in enumerate(svg_files, 1):
                if len(svg_files) == 1:
                    new_name = f"{base_name}.svg"
                else:
                    new_name = f"{base_name}_page_{i:02d}.svg"

                dest = out_dir / new_name
                dest.write_bytes(svg_file.read_bytes())
                output_paths.append(dest)

        print(f"Converted {visio_file.name} → {len(output_paths)} SVG file(s)")
        for p in output_paths:
            print(f"  - {p}")

        return output_paths

    def svg_to_mmd_prompt(self, svg_content: str, diagram_type: str = "flowchart") -> str:
        """
        Generate a prompt for Claude Vision to convert SVG to Mermaid.

        Args:
            svg_content: SVG XML content
            diagram_type: Type of Mermaid diagram

        Returns:
            Prompt string for Claude Vision
        """
        # Extract text elements from SVG for context
        text_elements = re.findall(r"<text[^>]*>([^<]+)</text>", svg_content)
        text_preview = "\n".join(text_elements[:20])  # First 20 text elements

        mermaid_type = self.DIAGRAM_TYPES.get(diagram_type, diagram_type)

        return f"""Analyze this SVG diagram and convert it to Mermaid ({mermaid_type}) format.

Text elements found in the diagram:
{text_preview}

SVG structure preview (first 3000 chars):
{svg_content[:3000]}

Please convert this to valid Mermaid syntax. Requirements:

1. Use diagram type: {mermaid_type}
2. Preserve all node text exactly as shown
3. Preserve connections/edges between nodes
4. Use appropriate Mermaid shapes:
   - Rectangles: [text]
   - Diamonds/decisions: {{text}}
   - Circles: ((text))
   - Rounded: (text)
   - Subroutines: [[text]]
   - Cylinders: [(text)]
   - Parallelograms: [/text/] or [\\text\\]
5. Add direction (TD, LR, BT, RL) if using flowchart
6. Include styling classes if colors are significant
7. Add a title comment at the top
8. Output ONLY the Mermaid code, no explanations

Example output format:
```mermaid
flowchart TD
    A[Start] --> B{{Decision?}}
    B -->|Yes| C[Process]
    B -->|No| D[End]
```
"""

    def generate_mmd_template(
        self,
        title: str,
        diagram_type: str = "flowchart",
        source_file: str | None = None,
        page: int = 1,
    ) -> str:
        """
        Generate a Mermaid template with metadata.

        Args:
            title: Diagram title
            diagram_type: Type of diagram
            source_file: Original source file name
            page: Page number for multi-page diagrams

        Returns:
            Mermaid template string
        """
        mermaid_type = self.DIAGRAM_TYPES.get(diagram_type, diagram_type)

        metadata_lines = [
            "---",
            f"title: {title}",
        ]
        if source_file:
            metadata_lines.append(f"source: {source_file}")
        if page > 1:
            metadata_lines.append(f"page: {page}")
        metadata_lines.append("---")

        metadata = "\n".join(metadata_lines)

        if diagram_type == "flowchart":
            template = f"""{metadata}

flowchart TD
    %% Define nodes
    START([Start])
    PROCESS1[Process Step]
    DECISION{{Decision?}}
    PROCESS2[Another Process]
    END([End])

    %% Define connections
    START --> PROCESS1
    PROCESS1 --> DECISION
    DECISION -->|Yes| PROCESS2
    DECISION -->|No| END
    PROCESS2 --> END

    %% Styling (optional)
    classDef startEnd fill:#e1f5e1,stroke:#2e7d32,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px

    class START,END startEnd
    class DECISION decision
    class PROCESS1,PROCESS2 process
"""
        elif diagram_type == "sequence":
            template = f"""{metadata}

sequenceDiagram
    autonumber
    participant A as Actor A
    participant B as Actor B
    participant C as System

    A->>B: Request
    B->>C: Query
    C-->>B: Response
    B-->>A: Result
"""
        elif diagram_type == "class":
            template = f"""{metadata}

classDiagram
    class Entity1 {{
        +String id
        +String name
        +method()
    }}

    class Entity2 {{
        +String id
        +Date created
        +validate()
    }}

    Entity1 "1" --> "*" Entity2 : has many
"""
        elif diagram_type == "er":
            template = f"""{metadata}

erDiagram
    ENTITY1 {{
        string id PK
        string name
        datetime created
    }}

    ENTITY2 {{
        string id PK
        string entity1_id FK
        string value
    }}

    ENTITY1 ||--o{{ ENTITY2 : contains
"""
        else:
            template = f"""{metadata}

{mermaid_type}
    %% Add your diagram content here
    %% Based on the SVG structure
"""

        return template

    def batch_convert(
        self,
        visio_path: str | Path,
        output_dir: str | Path | None = None,
        diagram_type: str = "flowchart",
    ) -> list[Path]:
        """
        Batch convert Visio file to Mermaid diagrams.

        Args:
            visio_path: Path to Visio file
            output_dir: Output directory
            diagram_type: Type of diagram to generate

        Returns:
            List of paths to generated .mmd files
        """
        visio_file = Path(visio_path)
        out_dir = Path(output_dir) if output_dir else visio_file.parent / f"{visio_file.stem}_mmd"
        out_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Convert to SVG
        svg_paths = self.visio_to_svg(visio_file, out_dir)

        # Step 2: Generate Mermaid templates
        mmd_paths = []
        for i, svg_path in enumerate(svg_paths, 1):
            mmd_name = svg_path.stem + ".mmd"
            mmd_path = out_dir / mmd_name

            # Read SVG for context (would be used with Claude Vision)
            svg_content = svg_path.read_text(encoding="utf-8")

            # Generate template
            title = f"{visio_file.stem} - Page {i}"
            template = self.generate_mmd_template(
                title=title,
                diagram_type=diagram_type,
                source_file=visio_file.name,
                page=i,
            )

            mmd_path.write_text(template, encoding="utf-8")
            mmd_paths.append(mmd_path)

        print(f"\nGenerated {len(mmd_paths)} Mermaid template(s)")
        for p in mmd_paths:
            print(f"  - {p}")

        print(f"\nNext steps:")
        print(f"  1. Review the SVG files: {out_dir}/*.svg")
        print(f"  2. Edit the .mmd files to match the diagram structure")
        print(f"  3. Or use Claude Vision with: vsd_to_mmd.py analyze <svg> -o <mmd>")

        return mmd_paths


def cmd_convert(args: argparse.Namespace) -> int:
    """Handle convert command."""
    try:
        converter = VisioConverter(soffice_path=args.soffice_path)
        converter.visio_to_svg(args.input, args.output)
        return 0
    except VisioConverterError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_analyze(args: argparse.Namespace) -> int:
    """Handle analyze command (generates prompt for Claude Vision)."""
    svg_path = Path(args.input)
    if not svg_path.exists():
        print(f"Error: SVG file not found: {svg_path}", file=sys.stderr)
        return 1

    svg_content = svg_path.read_text(encoding="utf-8")

    # Use a minimal converter instance without LibreOffice check for analyze
    converter = VisioConverter.__new__(VisioConverter)
    prompt = converter.svg_to_mmd_prompt(svg_content, args.type)

    if args.output:
        # Save prompt to file for reference
        prompt_path = Path(args.output).with_suffix(".prompt.txt")
        prompt_path.write_text(prompt, encoding="utf-8")
        print(f"Prompt saved to: {prompt_path}")
        print(f"\nUse this prompt with Claude Vision, then save the Mermaid output to: {args.output}")
    else:
        print(prompt)

    return 0


def cmd_batch(args: argparse.Namespace) -> int:
    """Handle batch command."""
    try:
        converter = VisioConverter(soffice_path=args.soffice_path)
        converter.batch_convert(args.input, args.output, args.type)
        return 0
    except VisioConverterError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_interactive(args: argparse.Namespace) -> int:
    """Handle interactive command."""
    try:
        converter = VisioConverter(soffice_path=args.soffice_path)
        visio_file = Path(args.input)

        print(f"\nConverting {visio_file.name}...")
        svg_paths = converter.visio_to_svg(visio_file)

        print(f"\nGenerated {len(svg_paths)} SVG file(s):")
        for i, p in enumerate(svg_paths, 1):
            print(f"  {i}. {p}")

        print("\n--- Interactive Mode ---")
        print("For each SVG, I'll generate a prompt you can use with Claude Vision.")
        print("After Claude generates the Mermaid code, paste it back here.\n")

        for svg_path in svg_paths:
            print(f"\nProcessing: {svg_path.name}")
            print("-" * 50)

            svg_content = svg_path.read_text(encoding="utf-8")

            # Detect diagram type
            print("\nDetected diagram elements:")
            text_count = len(re.findall(r"<text", svg_content))
            rect_count = len(re.findall(r"<rect", svg_content))
            path_count = len(re.findall(r"<path", svg_content))
            print(f"  - Text elements: {text_count}")
            print(f"  - Rectangles: {rect_count}")
            print(f"  - Paths: {path_count}")

            # Generate prompt
            prompt = converter.svg_to_mmd_prompt(svg_content)

            prompt_file = svg_path.with_suffix(".prompt.txt")
            prompt_file.write_text(prompt, encoding="utf-8")
            print(f"\nPrompt saved to: {prompt_file}")
            print("Copy this prompt to Claude Vision to get the Mermaid code.")

        return 0
    except VisioConverterError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert Visio (.vsd/.vsdx) files to Mermaid (.mmd) diagrams",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert Visio to SVG only
  python vsd_to_mmd.py convert diagram.vsdx -o ./svgs/

  # Generate prompt for Claude Vision analysis
  python vsd_to_mmd.py analyze diagram.svg -o diagram.mmd

  # Batch convert (Visio → SVG → Mermaid template)
  python vsd_to_mmd.py batch diagram.vsdx -o ./output/

  # Interactive mode with custom LibreOffice path
  python vsd_to_mmd.py batch diagram.vsdx --soffice-path "/path/to/soffice"
        """,
    )

    subparsers = parser.add_subparsers(dest="command", metavar="command")

    # Convert command
    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert Visio to SVG using LibreOffice",
    )
    convert_parser.add_argument("input", help="Input .vsd or .vsdx file")
    convert_parser.add_argument(
        "-o", "--output",
        help="Output directory (default: same as input)",
    )
    convert_parser.add_argument(
        "--soffice-path",
        help="Path to LibreOffice soffice executable",
    )
    convert_parser.set_defaults(func=cmd_convert)

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Generate prompt for Claude Vision to convert SVG to Mermaid",
    )
    analyze_parser.add_argument("input", help="Input SVG file")
    analyze_parser.add_argument(
        "-o", "--output",
        help="Output .mmd file path",
    )
    analyze_parser.add_argument(
        "--type",
        choices=list(VisioConverter.DIAGRAM_TYPES.keys()),
        default="flowchart",
        help="Type of Mermaid diagram (default: flowchart)",
    )
    analyze_parser.set_defaults(func=cmd_analyze)

    # Batch command
    batch_parser = subparsers.add_parser(
        "batch",
        help="Batch convert: Visio → SVG → Mermaid template",
    )
    batch_parser.add_argument("input", help="Input .vsd or .vsdx file")
    batch_parser.add_argument(
        "-o", "--output",
        help="Output directory",
    )
    batch_parser.add_argument(
        "--type",
        choices=list(VisioConverter.DIAGRAM_TYPES.keys()),
        default="flowchart",
        help="Type of Mermaid diagram (default: flowchart)",
    )
    batch_parser.add_argument(
        "--soffice-path",
        help="Path to LibreOffice soffice executable",
    )
    batch_parser.set_defaults(func=cmd_batch)

    # Interactive command
    interactive_parser = subparsers.add_parser(
        "interactive",
        help="Interactive mode: convert and guide through Mermaid generation",
    )
    interactive_parser.add_argument("input", help="Input .vsd or .vsdx file")
    interactive_parser.add_argument(
        "--soffice-path",
        help="Path to LibreOffice soffice executable",
    )
    interactive_parser.set_defaults(func=cmd_interactive)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

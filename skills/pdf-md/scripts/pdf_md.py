#!/usr/bin/env python3
"""
pdf_md.py — PDF + Markdown dual-layer utility

Embed a .md file as a named attachment inside a PDF, or extract it back out.
Follows the pdf-md-standards.md convention: attachment named <pdf-basename>.md

Usage:
  python pdf_md.py embed <input.pdf> <source.md> [-o output.pdf]
  python pdf_md.py parse-embed <input.pdf> [-o output.pdf]
  python pdf_md.py extract <input.pdf> [-o output.md]
  python pdf_md.py check <input.pdf>

Requires: pypdf >= 4.0  (pip install pypdf)
"""

import sys
import io
import argparse
import tempfile
from pathlib import Path

# Fix Windows console Unicode encoding (Windows only)
if sys.platform == "win32":
    if hasattr(sys.stdout, "buffer") and sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "buffer") and sys.stderr.encoding and sys.stderr.encoding.lower() not in ("utf-8", "utf8"):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def _require_pypdf():
    try:
        import pypdf
        return pypdf
    except ImportError:
        print("Error: pypdf not installed. Run: pip install pypdf", file=sys.stderr)
        sys.exit(1)


def embed(pdf_path: str, md_path: str, output_path: str | None = None) -> Path:
    pypdf = _require_pypdf()

    pdf_in = Path(pdf_path)
    md_in = Path(md_path)

    if not pdf_in.exists():
        print(f"Error: PDF not found: {pdf_in}", file=sys.stderr)
        sys.exit(1)
    if not md_in.exists():
        print(f"Error: Markdown file not found: {md_in}", file=sys.stderr)
        sys.exit(1)

    reader = pypdf.PdfReader(str(pdf_in))
    writer = pypdf.PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    if reader.metadata:
        writer.add_metadata(dict(reader.metadata))

    attachment_name = pdf_in.stem + ".md"
    md_bytes = md_in.read_bytes()
    writer.add_attachment(attachment_name, md_bytes)

    out = Path(output_path) if output_path else pdf_in
    with open(out, "wb") as f:
        writer.write(f)

    print(f"Embedded '{attachment_name}' into {out}")
    return out


def parse_embed(pdf_path: str, output_path: str | None = None) -> Path:
    """Parse PDF text content into Markdown, then embed it as the .md layer."""
    pypdf = _require_pypdf()

    pdf_in = Path(pdf_path)
    if not pdf_in.exists():
        print(f"Error: PDF not found: {pdf_in}", file=sys.stderr)
        sys.exit(1)

    reader = pypdf.PdfReader(str(pdf_in))
    num_pages = len(reader.pages)
    pdf_name = pdf_in.stem

    lines = [
        f"# {pdf_name}\n",
        f"*Source: {pdf_in.name} — {num_pages} pages*\n\n",
    ]
    for i, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        lines.append(f"## Page {i}\n\n{text}\n\n")

    md_content = "\n".join(lines)

    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".md", delete=False
    ) as tmp:
        tmp.write(md_content)
        tmp_path = tmp.name

    print(f"Parsed {num_pages} pages -> {len(md_content):,} chars of Markdown")

    try:
        result = embed(pdf_path, tmp_path, output_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return result


def extract(pdf_path: str, output_path: str | None = None) -> str | None:
    pypdf = _require_pypdf()

    pdf_in = Path(pdf_path)
    if not pdf_in.exists():
        print(f"Error: PDF not found: {pdf_in}", file=sys.stderr)
        sys.exit(1)

    reader = pypdf.PdfReader(str(pdf_in))

    for name, file_list in reader.attachments.items():
        if name.endswith(".md"):
            raw = file_list[0]
            content = raw.decode("utf-8") if isinstance(raw, bytes) else raw

            out = Path(output_path) if output_path else Path(name)
            out.write_text(content, encoding="utf-8")
            print(f"Extracted '{name}' -> {out}")
            return content

    print("No .md attachment found in PDF.", file=sys.stderr)
    return None


def check(pdf_path: str) -> bool:
    pypdf = _require_pypdf()

    pdf_in = Path(pdf_path)
    if not pdf_in.exists():
        print(f"Error: PDF not found: {pdf_in}", file=sys.stderr)
        sys.exit(1)

    reader = pypdf.PdfReader(str(pdf_in))
    md_attachments = [name for name in reader.attachments if name.endswith(".md")]

    if md_attachments:
        print(f"[OK] .md layer present in {pdf_in.name}")
        for name in md_attachments:
            size = len(reader.attachments[name][0])
            print(f"  - {name}  ({size:,} bytes)")
        return True
    else:
        print(f"[--] No .md attachment found in {pdf_in.name}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="PDF + Markdown dual-layer utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", metavar="command")

    p_embed = sub.add_parser("embed", help="Embed .md into PDF as a named attachment")
    p_embed.add_argument("pdf", help="Input PDF path")
    p_embed.add_argument("md", help="Markdown file to embed")
    p_embed.add_argument("-o", "--output", help="Output PDF path (default: overwrite input)")

    p_pe = sub.add_parser("parse-embed", help="Parse PDF text to Markdown and embed it")
    p_pe.add_argument("pdf", help="Input PDF path")
    p_pe.add_argument("-o", "--output", help="Output PDF path (default: overwrite input)")

    p_extract = sub.add_parser("extract", help="Extract embedded .md from PDF")
    p_extract.add_argument("pdf", help="PDF path")
    p_extract.add_argument("-o", "--output", help="Output .md path (default: attachment filename)")

    p_check = sub.add_parser("check", help="Check whether PDF contains a .md attachment")
    p_check.add_argument("pdf", help="PDF path")

    args = parser.parse_args()

    if args.command == "embed":
        embed(args.pdf, args.md, args.output)
    elif args.command == "parse-embed":
        parse_embed(args.pdf, args.output)
    elif args.command == "extract":
        result = extract(args.pdf, args.output)
        sys.exit(0 if result is not None else 1)
    elif args.command == "check":
        found = check(args.pdf)
        sys.exit(0 if found else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

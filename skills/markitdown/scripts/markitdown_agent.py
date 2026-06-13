#!/usr/bin/env python3
"""
markitdown_agent.py — Agent utility wrapper for Microsoft Markitdown.

Provides:
  - convert_file(src_path, output_path=None, enrich=False) -> str
  - convert_batch(pattern, output_dir, enrich=False) -> list
  - extract_text(src_path, enrich=False) -> str (in-memory, no file write)
  - get_metadata(src_path) -> dict
  - enhance_markdown(text, meta=None) -> str (rich formatting pass)

Intended for use by AI agents via subprocess or direct import.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ── Regex patterns for structural enhancement ───────────────────────────────

# Detect ALL-CAPS headings (short, standalone lines)
_HEADING_RE = re.compile(
    r"^(?P<prefix>\s*)(?P<text>[A-Z][A-Z\s\-–—&:]{3,}[A-Z])(?P<suffix>\s*)$",
    re.MULTILINE,
)

# Detect Title-Case headings (short lines that look like section titles)
# Avoids: lines with links, lines starting with markdown, very long lines
_TITLE_HEADING_RE = re.compile(
    r"^(?P<prefix>\s*)(?P<text>[A-Z][a-zA-Z\s\-–—&:]{2,}[a-zA-Z])(?P<suffix>\s*)$",
    re.MULTILINE,
)

# Detect simple tables: lines with 2+ pipe-separated columns
_TABLE_LINE_RE = re.compile(r"^\s*\|.+\|\s*$", re.MULTILINE)

# Detect bare URLs not already in markdown link syntax
_BARE_URL_RE = re.compile(
    r"(?<![\[(])(?P<url>https?://[^\s<>\"\']+[^\s<>\"\'\.,;:!?)])"
)

# Detect code-like blocks (indented 4+ spaces or lines starting with >>> / ...)
# BUT: skip lines that look like list items when de-indented
_CODE_BLOCK_RE = re.compile(
    r"^(?: {4,}|\t+|[>\.]{3,})(?P<line>.+)$", re.MULTILINE
)

# Pattern to detect list items (used to skip them in code-block detection)
_LIST_ITEM_RE = re.compile(r"^\s*(?:\d+[\.\)]\s+|[•·\-\*–]\s+|\+\s+)(?P<text>.+)$")

# Detect list-like paragraphs (leading bullet chars or numbers)
_BULLET_LIST_RE = re.compile(
    r"^\s*(?P<bullet>[•·\-\*–]\s+)(?P<text>.+)$", re.MULTILINE
)
_NUMBERED_LIST_RE = re.compile(
    r"^\s*(?P<num>\d+[\.\)]\s+)(?P<text>.+)$", re.MULTILINE
)

# Detect lines with MULTIPLE mixed list markers that markitdown flattens
# e.g., "- + - * 1. The Department..." → "- The Department..."
# e.g., "- + 1. any information..." → "- any information..."
_MIXED_LIST_RE = re.compile(
    r"^\s*(?:[•·\-\*–\+]\s+|\d+[\.]\s+){2,}(?P<text>.+)$",
    re.MULTILINE,
)

# Detect possible blockquotes (lines starting with > or quoted phrases)
_BLOCKQUOTE_RE = re.compile(
    r"^\s*(?:[>│]|(?:Note|Warning|Tip|Important|Caution):)\s*(?P<text>.+)$",
    re.MULTILINE | re.IGNORECASE,
)

# Detect horizontal-rule-like lines
_HR_RE = re.compile(r"^\s*(?:={3,}|-{3,}|_{3,}|\*{3,})\s*$")

# Detect compressed single-line tables (markitdown merges multi-row tables onto one line)
_COMPRESSED_TABLE_RE = re.compile(r"^\s*\|\s+\|.*\|\s+\|.*---.*\|", re.MULTILINE)


# ── Compressed table reconstruction ─────────────────────────────────────────

def fix_compressed_tables(text: str) -> str:
    """Reconstruct multi-row markdown tables that markitdown compressed onto single lines.

    markitdown sometimes outputs entire tables as one line using `` |  | `` as a
    row separator. This function detects both patterns:
      - Header-first: ``|  | H1 | H2 |  | --- | --- |  | D1 | D2 |``
      - Separator-first: ``|  | --- | --- |  | H1 | H2 |  | D1 | D2 |``

    It tokenises the line, finds the ``---`` run to determine the column count,
    then groups cells into proper rows.
    """
    lines = text.split("\n")
    fixed: list[str] = []
    for line in lines:
        if not _is_compressed_table_line(line):
            fixed.append(line)
            continue
        fixed_table = _reconstruct_table(line)
        fixed.append(fixed_table)
    return "\n".join(fixed)


def _is_compressed_table_line(line: str) -> bool:
    """True if *line* looks like a markitdown-compressed multi-row table."""
    stripped = line.strip()
    if not stripped.startswith("|  |"):
        return False
    # Must contain a separator run (2+ '---' cells)
    if "---" not in stripped:
        return False
    # Must have row-separator-like patterns
    if stripped.count("|") < 6:
        return False
    return True


def _reconstruct_table(line: str) -> str:
    """Parse a compressed single-line table and rebuild it as proper markdown."""
    # Tokenise by the cell separator ' | '
    raw_tokens = line.split(" | ")
    tokens: list[str] = []
    for t in raw_tokens:
        t = t.strip()
        while t.startswith("|"):
            t = t[1:].strip()
        while t.endswith("|"):
            t = t[:-1].strip()
        tokens.append(t)

    # Skip leading / trailing empty tokens
    start = 0
    while start < len(tokens) and tokens[start] == "":
        start += 1
    end = len(tokens)
    while end > start and tokens[end - 1] == "":
        end -= 1
    tokens = tokens[start:end]

    if not tokens:
        return line

    # Find the separator run (consecutive '---')
    sep_start: int | None = None
    sep_end: int | None = None
    num_cols: int | None = None
    i = 0
    while i < len(tokens):
        if tokens[i] == "---":
            j = i
            while j < len(tokens) and tokens[j] == "---":
                j += 1
            run_len = j - i
            if run_len >= 2:
                sep_start = i
                sep_end = j
                num_cols = run_len
                break
            i = j
        else:
            i += 1

    if sep_start is None or num_cols is None:
        return line

    # Detect pattern: separator-first vs header-first
    pattern_b = sep_start == 0

    if pattern_b:
        # Separator-first: header comes after separator
        idx = sep_end
        while idx < len(tokens) and tokens[idx] == "":
            idx += 1
        header = tokens[idx: idx + num_cols]
        idx += num_cols
        while idx < len(tokens) and tokens[idx] == "":
            idx += 1
        data = tokens[idx:]
    else:
        # Header-first: header before separator
        header = [t for t in tokens[:sep_start] if t != ""]
        idx = sep_end
        while idx < len(tokens) and tokens[idx] == "":
            idx += 1
        data = tokens[idx:]

    while len(header) < num_cols:
        header.append("")

    output: list[str] = []
    output.append("| " + " | ".join(header[:num_cols]) + " |")
    output.append("| " + " | ".join(["---"] * num_cols) + " |")

    # Group data into rows, handling explicit row boundaries
    current_row: list[str] = []
    i = 0
    while i < len(data):
        t = data[i]
        if t == "" and len(current_row) == num_cols:
            # Row boundary after complete row
            output.append("| " + " | ".join(current_row) + " |")
            current_row = []
            i += 1
        elif t == "" and len(current_row) < num_cols:
            current_row.append("")
            i += 1
        else:
            current_row.append(t)
            i += 1
        # Flush if row is full and next token is non-empty (no boundary marker)
        if len(current_row) == num_cols and i < len(data) and data[i] != "":
            output.append("| " + " | ".join(current_row) + " |")
            current_row = []

    if current_row:
        while len(current_row) < num_cols:
            current_row.append("")
        output.append("| " + " | ".join(current_row) + " |")

    return "\n".join(output)


# ── Character encoding repair ───────────────────────────────────────────────

def fix_broken_characters(text: str) -> str:
    """Replace common encoding artefacts produced by markitdown.

    markitdown occasionally emits Unicode replacement characters (�) or
    mojibake where the source document used smart quotes, em-dashes, bullets,
    or copyright symbols. This pass normalises them to ASCII-safe equivalents.
    """
    # Multi-byte mojibake sequences first
    replacements = {
        "–": "-",      # En dash
        "—": "--",    # Em dash
        "•": "-",     # Bullet
        "©": "(c)",   # Copyright
        "®": "(R)",   # Registered
        "™": "(TM)",  # Trademark
        "‘": "'",     # Left single quote
        "’": "'",     # Right single quote
        "“": '"',     # Left double quote
        "”": '"',     # Right double quote
        "°": " degrees",  # Degree
        "±": "+/-",   # Plus-minus
        "×": "x",     # Multiplication
        "÷": "/",     # Division
        "�": "-",     # Replacement character (�)
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


# ── TOC artifact removal ────────────────────────────────────────────────────

def remove_toc_artifacts(text: str) -> str:
    """Remove Word-generated table-of-contents entries and stray section labels.

    markitdown preserves Word auto-TOC entries like
    ``[Document Revision 3](#_Toc221889628)`` which are meaningless in markdown.
    """
    lines = text.split("\n")
    result: list[str] = []
    for line in lines:
        stripped = line.strip()
        # TOC link lines: [text](#_Toc...)
        if re.match(r"^\[[^\]]+\]\(#[^)]+\)$", stripped):
            continue
        # Standalone "Tables" / "Diagrams" labels
        if stripped in ("Tables", "Diagrams", "**Tables**", "**Diagrams**"):
            continue
        result.append(line)
    return "\n".join(result)


# ── Core markitdown invocation ──────────────────────────────────────────────

def _run_markitdown(args: list[str], *, capture: bool = True) -> subprocess.CompletedProcess:
    """Invoke the `markitdown` CLI with the given arguments."""
    cmd = ["markitdown", *args]
    result = subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result


def convert_file(
    src_path: str | os.PathLike,
    output_path: str | os.PathLike | None = None,
    *,
    enrich: bool = False,
) -> str:
    """Convert a single file to Markdown.

    Args:
        src_path: Path to the source document.
        output_path: Optional path to write the Markdown output. If omitted,
            output is returned as a string.
        enrich: If True, apply the rich-markdown enhancement pass.

    Returns:
        The Markdown text (or the empty string if written to disk).
    """
    src = Path(src_path)
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {src}")

    args = [str(src)]
    result = _run_markitdown(args)
    if result.returncode != 0:
        raise RuntimeError(
            f"markitdown failed (exit {result.returncode}): {result.stderr}"
        )

    text = result.stdout
    if enrich:
        meta = get_metadata(src)
        text = enhance_markdown(text, meta=meta)

    if output_path:
        out = Path(output_path)
        out.write_text(text, encoding="utf-8")
        return ""

    return text


def extract_text(src_path: str | os.PathLike, *, enrich: bool = False) -> str:
    """Return the Markdown text of *src_path* without writing to disk."""
    return convert_file(src_path, output_path=None, enrich=enrich)


def get_metadata(src_path: str | os.PathLike) -> dict[str, Any]:
    """Return lightweight metadata about a file (size, extension, MIME hint)."""
    src = Path(src_path)
    stat = src.stat()
    # Lightweight MIME guess via python-magic if available, else fallback
    mime = None
    try:
        import magika  # noqa: F401
    except ImportError:
        pass

    # Derive from extension as fallback
    ext = src.suffix.lower()
    mime_map = {
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".pdf": "application/pdf",
        ".html": "text/html",
        ".htm": "text/html",
        ".txt": "text/plain",
        ".csv": "text/csv",
    }
    mime = mime_map.get(ext, "application/octet-stream")

    return {
        "path": str(src.resolve()),
        "size": stat.st_size,
        "extension": ext,
        "mime_type": mime,
        "filename": src.name,
        "stem": src.stem,
        "converted_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


# ── Rich Markdown Enhancement ───────────────────────────────────────────────

def enhance_markdown(text: str, meta: dict[str, Any] | None = None) -> str:
    """Apply structural and formatting enhancements to raw markitdown output.

    This is a *mechanical* enrichment pass — it improves formatting that can
    be reliably detected with regex heuristics. Semantic enrichment (adding
    bold emphasis to key terms, rewriting sentences for clarity, inferring
    heading hierarchy from context) should be done by the agent using its
    own understanding.

    Operations applied (in order):
      1. YAML frontmatter (from metadata)
      2. Fix broken characters (encoding artefacts → ASCII-safe equivalents)
      3. Remove Word TOC artifacts (``[text](#_Toc...)`` entries)
      4. Reconstruct compressed single-line tables
      5. Normalize excessive blank lines
      6. Detect ALL-CAPS headings → ## Heading (skips TOC lines, long sentences)
      7. Detect Title-Case headings → ## Heading (same guards)
      8. Detect and clean up table formatting (collapses empty rows)
      9. Normalize bullet and numbered lists
      10. Collapse mixed list markers (markitdown flattens nested lists to one line)
      11. Detect indented code → fenced code blocks (skips indented list items)
      12. Convert bare URLs to markdown links
      13. Detect blockquote-like lines
      14. Normalize horizontal rules
    """
    if not text or not text.strip():
        return text

    # 1. YAML frontmatter
    frontmatter = ""
    if meta:
        fm = {
            "title": meta.get("stem", "Document").replace("-", " ").replace("_", " ").title(),
            "source": meta.get("filename", ""),
            "converted": meta.get("converted_at", ""),
            "format": meta.get("extension", "").lstrip(".").upper(),
        }
        # Strip empty values
        fm = {k: v for k, v in fm.items() if v}
        fm_lines = ["---"] + [f"{k}: {v}" for k, v in fm.items()] + ["---", ""]
        frontmatter = "\n".join(fm_lines)

    # Work on the body
    body = text

    # 2. Fix broken characters (encoding artefacts)
    body = fix_broken_characters(body)

    # 3. Remove Word TOC artifacts
    body = remove_toc_artifacts(body)

    # 4. Reconstruct compressed single-line tables
    body = fix_compressed_tables(body)

    # 5. Normalize excessive blank lines (more than 2 → 2)
    body = re.sub(r"\n{4,}", "\n\n\n", body)

    # 6. Detect headings — ALL CAPS and Title Case short lines
    def _is_toc_line(text: str) -> bool:
        """Skip lines that look like TOC entries ([text](#anchor)) or markdown."""
        if "](#" in text:
            return True
        if text.startswith("|") or text.startswith("#"):
            return True
        if text.startswith("[") and "](" in text:
            return True
        return False

    def _is_likely_heading(text: str) -> bool:
        """Headings are typically short (< 60 chars) and not sentences."""
        if len(text) > 80:
            return False
        # Avoid lines that end with punctuation typical of sentences
        if text.endswith((",", ".", ";", "!", "?")) and len(text) > 40:
            return False
        return True

    def _heading_repl(m: re.Match) -> str:
        text_content = m.group("text").strip()
        if _is_toc_line(text_content):
            return m.group(0)
        if not any(c.isalpha() for c in text_content):
            return m.group(0)
        if not _is_likely_heading(text_content):
            return m.group(0)
        return f"\n## {text_content}\n"

    body = _HEADING_RE.sub(_heading_repl, body)

    # Title-case heading pass (only for lines that weren't already converted)
    # Track positions to avoid double-processing
    converted_spans: set[tuple[int, int]] = set()
    for m in _HEADING_RE.finditer(text):
        converted_spans.add((m.start(), m.end()))

    def _title_heading_repl(m: re.Match) -> str:
        # Check if this span overlaps with an ALL-CAPS conversion
        for start, end in converted_spans:
            if not (m.end() <= start or m.start() >= end):
                return m.group(0)
        text_content = m.group("text").strip()
        if _is_toc_line(text_content):
            return m.group(0)
        if not any(c.isalpha() for c in text_content):
            return m.group(0)
        if not _is_likely_heading(text_content):
            return m.group(0)
        # Skip if it's a table row
        if "|" in text_content:
            return m.group(0)
        return f"\n## {text_content}\n"

    body = _TITLE_HEADING_RE.sub(_title_heading_repl, body)

    # 7. Clean up table lines
    def _table_repl(m: re.Match) -> str:
        line = m.group(0)
        cells = [c.strip() for c in line.strip().split("|")]
        # Filter out completely empty cells from leading/trailing pipes
        # but preserve intentional empty cells in the middle
        cleaned = []
        for c in cells:
            if c.strip() or c == "":
                cleaned.append(c.strip())
        # Skip rows that are entirely empty after cleaning
        if not any(c.strip() for c in cleaned):
            return ""
        return "| " + " | ".join(cleaned) + " |"

    body = _TABLE_LINE_RE.sub(_table_repl, body)
    # Collapse multiple consecutive empty table rows
    body = re.sub(r"(\|\s*\|\s*\n)+", "", body)
    # Clean up stray separator rows (|---| with no content)
    body = re.sub(r"\n\|\s*---?\s*\|\s*\n", "\n", body)

    # 8. Detect indented code blocks and wrap in fences
    # Skip lines that look like list items even when indented
    lines = body.split("\n")
    out_lines: list[str] = []
    in_code = False
    code_buffer: list[str] = []

    for line in lines:
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        is_indented = indent >= 4
        is_code_line = is_indented and stripped

        # SKIP: indented lines that look like list items
        if is_code_line and _LIST_ITEM_RE.match(stripped):
            if in_code:
                # End current code block first
                in_code = False
                out_lines.extend(code_buffer)
                out_lines.append("```\n")
                code_buffer = []
            out_lines.append(line)
            continue

        if is_code_line and not in_code:
            in_code = True
            out_lines.append("\n```")
            code_buffer.append(stripped)
        elif is_code_line and in_code:
            code_buffer.append(stripped)
        elif not is_code_line and in_code:
            in_code = False
            out_lines.extend(code_buffer)
            out_lines.append("```\n")
            code_buffer = []
            out_lines.append(line)
        else:
            out_lines.append(line)

    if in_code:
        out_lines.extend(code_buffer)
        out_lines.append("```")

    body = "\n".join(out_lines)

    # 9. Normalize bullet lists (• · → -)
    body = _BULLET_LIST_RE.sub(lambda m: f"\n- {m.group('text').strip()}", body)

    # Normalize numbered lists (ensure "1. " format)
    body = _NUMBERED_LIST_RE.sub(lambda m: f"\n{m.group('num').strip()} {m.group('text').strip()}", body)

    # Collapse lines with multiple mixed list markers (markitdown flattens nested lists)
    # e.g., "- + - * 1. The Department..." → "- The Department..."
    body = _MIXED_LIST_RE.sub(lambda m: f"\n- {m.group('text').strip()}", body)

    # 10. Convert bare URLs to markdown links
    def _url_repl(m: re.Match) -> str:
        url = m.group("url")
        # Skip if already inside a link or image
        return f"[{url}]({url})"

    body = _BARE_URL_RE.sub(_url_repl, body)

    # 11. Detect blockquote-like lines
    def _bq_repl(m: re.Match) -> str:
        text_content = m.group("text").strip()
        return f"> {text_content}"

    body = _BLOCKQUOTE_RE.sub(_bq_repl, body)

    # 12. Normalize horizontal rules
    def _hr_repl(m: re.Match) -> str:
        return "\n---\n"

    body = _HR_RE.sub(_hr_repl, body)

    # Final assembly
    result = frontmatter + body

    # Ensure file ends with a single newline
    result = result.rstrip() + "\n"

    return result


# ── Batch conversion ─────────────────────────────────────────────────────────

def convert_batch(
    pattern: str,
    output_dir: str | os.PathLike,
    *,
    enrich: bool = False,
) -> list[dict[str, Any]]:
    """Batch-convert files matching *pattern* into *output_dir*.

    Returns a list of result dicts with keys: source, output, success, error.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    import glob
    files = glob.glob(pattern, recursive=True)
    results: list[dict[str, Any]] = []

    for src in files:
        src_path = Path(src)
        dest = out_dir / f"{src_path.stem}.md"
        try:
            convert_file(src_path, output_path=dest, enrich=enrich)
            results.append(
                {"source": str(src_path), "output": str(dest), "success": True, "error": None}
            )
        except Exception as exc:
            results.append(
                {"source": str(src_path), "output": str(dest), "success": False, "error": str(exc)}
            )
    return results


# ── CLI entrypoint for agent subprocess invocation ──────────────────────────

def _cli() -> None:
    parser = argparse.ArgumentParser(description="Agent utility for Microsoft Markitdown")
    sub = parser.add_subparsers(dest="command", required=True)

    # Shared enrich argument for subparsers that support it
    enrich_kwargs = {
        "action": "store_true",
        "help": "Apply rich-markdown enhancement pass after conversion",
    }

    # convert
    p_convert = sub.add_parser("convert", help="Convert a single file")
    p_convert.add_argument("src", help="Source file path")
    p_convert.add_argument("-o", "--output", help="Output markdown path")
    p_convert.add_argument("--enrich", "-e", **enrich_kwargs)

    # extract
    p_extract = sub.add_parser("extract", help="Extract text to stdout (JSON-wrapped)")
    p_extract.add_argument("src", help="Source file path")
    p_extract.add_argument("--enrich", "-e", **enrich_kwargs)

    # batch
    p_batch = sub.add_parser("batch", help="Batch convert files")
    p_batch.add_argument("pattern", help="Glob pattern (e.g. '*.docx')")
    p_batch.add_argument("output_dir", help="Directory to write .md files")
    p_batch.add_argument("--enrich", "-e", **enrich_kwargs)

    # metadata
    p_meta = sub.add_parser("metadata", help="Show file metadata as JSON")
    p_meta.add_argument("src", help="Source file path")

    # enhance
    p_enhance = sub.add_parser("enhance", help="Enhance an existing .md file in-place")
    p_enhance.add_argument("src", help="Markdown file path to enhance")
    p_enhance.add_argument("-o", "--output", help="Output path (default: overwrite)")

    args = parser.parse_args()

    if args.command == "convert":
        text = convert_file(args.src, output_path=args.output, enrich=args.enrich)
        if text:
            print(text)

    elif args.command == "extract":
        text = extract_text(args.src, enrich=args.enrich)
        print(json.dumps({"text": text}, ensure_ascii=False))

    elif args.command == "batch":
        results = convert_batch(args.pattern, args.output_dir, enrich=args.enrich)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif args.command == "metadata":
        meta = get_metadata(args.src)
        print(json.dumps(meta, indent=2, ensure_ascii=False))

    elif args.command == "enhance":
        src = Path(args.src)
        text = src.read_text(encoding="utf-8")
        meta = get_metadata(src) if src.exists() else None
        enhanced = enhance_markdown(text, meta=meta)
        out = Path(args.output) if args.output else src
        out.write_text(enhanced, encoding="utf-8")
        print(f"Enhanced: {out}")


if __name__ == "__main__":
    _cli()

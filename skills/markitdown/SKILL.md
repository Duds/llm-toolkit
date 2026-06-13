---
name: markitdown
description: >-
  Convert documents to clean, richly formatted Markdown using Microsoft's
  markitdown tool. Trigger whenever the user says 'convert to markdown',
  'extract as markdown', 'convert DOCX/PDF/PPTX/XLSX to markdown', or needs
  structured text extraction from office documents. Also trigger for batch
  conversions, mirror-doc creation, or when another skill needs a document
  converted to markdown before further processing. Handles Word (.docx),
  PowerPoint (.pptx), Excel (.xlsx), PDF (.pdf), HTML (.html), and other
  formats. Produces clean, readable, **richly formatted** markdown with proper
  headings, tables, code blocks, lists, emphasis, blockquotes, and YAML
  frontmatter.
---

# Markitdown Document Conversion

Convert documents to clean, **richly formatted** markdown using Microsoft's [`markitdown`](https://github.com/microsoft/markitdown) tool.

## Supported Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| Microsoft Word | `.docx` | Best for text-heavy documents |
| Microsoft PowerPoint | `.pptx` | Converts slides to markdown sections |
| Microsoft Excel | `.xlsx`, `.xls` | Tables become markdown tables |
| PDF | `.pdf` | Text extraction with structure preservation |
| HTML | `.html`, `.htm` | Clean conversion to markdown |
| Images | `.jpg`, `.png` | OCR with Azure Document Intelligence (if configured) |
| Audio | `.wav`, `.mp3` | Transcription with SpeechRecognition |
| YouTube | URLs | Transcript extraction |

## Two-Stage Conversion Pipeline

This skill uses a **two-stage pipeline** to produce high-quality markdown:

1. **Extract** — Run `markitdown` to convert the source document to raw markdown
2. **Enrich** — Apply structural and semantic enhancements for rich formatting

Always run both stages unless the user explicitly asks for raw output only.

### Enrichment Operations

After the raw conversion, apply these enhancements:

| Operation | What It Does | Example |
|-----------|--------------|---------|
| **YAML Frontmatter** | Add metadata block at top | `title`, `source`, `converted`, `format` |
| **Heading Hierarchy** | Ensure proper `#` / `##` / `###` structure | Raw: `INTRODUCTION` → Enriched: `## Introduction` |
| **Table Formatting** | Clean pipe-separated tables with aligned columns | `| col1 | col2 |` with header separator |
| **Code Blocks** | Wrap code snippets in fenced blocks with language hints | ````python\ndef hello():...\n```` |
| **List Normalization** | Convert bullet paragraphs to `- ` lists, numbers to `1. ` | `- Item` instead of `• Item` |
| **URL Linking** | Convert bare URLs to `[text](url)` markdown links | `[https://example.com](https://example.com)` |
| **Blockquotes** | Format notes, warnings, and callouts as `>` quotes | `> Note: This is important` |
| **Horizontal Rules** | Separate major sections with `---` | Between chapters/sections |
| **Emphasis** | Bold key terms and section headers; italicize definitions | `**Important**: this is *critical*` |
| **Whitespace Cleanup** | Remove excessive blank lines; ensure single trailing newline | Clean, compact spacing |

### Enrichment Approach

Use the bundled agent script for **mechanical** enhancements (frontmatter, tables, lists, URLs, whitespace):

```bash
# Convert with automatic structural enrichment
python scripts/markitdown_agent.py convert report.docx -o report.md --enrich

# Batch convert with enrichment
python scripts/markitdown_agent.py batch "*.docx" ./converted/ --enrich
```

For **semantic** enhancements (heading hierarchy, code language detection, emphasis, blockquotes), use your own judgment after reading the raw output:

1. Convert the file (with `--enrich` for mechanical fixes)
2. Read the resulting `.md`
3. Apply semantic improvements inline — rewrite headings for clarity, add `**bold**` to key terms, wrap detected code in ````language` fences, format callouts as `>` blockquotes

## Agent Utilities

This skill bundles Python utilities at [`scripts/markitdown_agent.py`](scripts/markitdown_agent.py) for deterministic, scriptable use by agents.

### Import API (for inline use)

```python
from scripts.markitdown_agent import convert_file, extract_text, get_metadata, convert_batch, enhance_markdown

# Convert single file with enrichment
md_text = extract_text("report.docx", enrich=True)

# Convert with explicit output + enrichment
convert_file("slides.pptx", output_path="slides.md", enrich=True)

# Batch convert with enrichment
results = convert_batch("*.docx", output_dir="./converted/", enrich=True)

# Enhance an already-converted markdown file
from scripts.markitdown_agent import enhance_markdown
text = Path("raw.md").read_text()
enriched = enhance_markdown(text, meta={"filename": "raw.md"})
```

### CLI API (for subprocess invocation)

```bash
# Single file to stdout (raw)
python scripts/markitdown_agent.py extract report.docx

# Single file with structural enrichment
python scripts/markitdown_agent.py convert report.docx -o report.md --enrich

# Batch convert with enrichment
python scripts/markitdown_agent.py batch "*.docx" ./converted/ --enrich

# Enhance an existing markdown file
python scripts/markitdown_agent.py enhance raw.md -o enriched.md

# File metadata
python scripts/markitdown_agent.py metadata report.docx
```

## Basic Usage

### Single file conversion (with enrichment)

```bash
markitdown document.docx > output.md
# Then enhance
python scripts/markitdown_agent.py enhance output.md
```

Or in one step:

```bash
python scripts/markitdown_agent.py convert document.docx -o output.md --enrich
```

### View output directly

```bash
markitdown document.pptx | head -100
```

### Save to specific location

```bash
python scripts/markitdown_agent.py convert report.pdf -o ~/Documents/extracted/report.md --enrich
```

## Common Patterns

### Batch convert multiple files with enrichment

```bash
for file in *.docx; do
    python scripts/markitdown_agent.py convert "$file" -o "${file%.docx}.md" --enrich
done
```

Or use the bundled agent script for deterministic batch conversion with JSON status:

```bash
python scripts/markitdown_agent.py batch "*.docx" ./converted/ --enrich
```

### Convert with streaming (large files)

```bash
markitdown large-document.pdf | less
```

### Extract and search

```bash
markitdown presentation.pptx | grep -i "budget"
```

### Convert to clipboard (macOS)

```bash
markitdown memo.docx | pbcopy
```

### Mirror-doc creation (for project portfolios)

When creating mirror `.md` files for Office documents (per `STANDARDS.md` §5):

1. Convert the source file with enrichment:
   ```bash
   python scripts/markitdown_agent.py convert source.docx -o mirror.md --enrich
   ```
2. Read the output and apply semantic enhancements (heading hierarchy, emphasis, blockquotes)
3. Ensure the mirror has proper YAML frontmatter with `title`, `source`, and `converted` fields
4. Verify the mirror renders correctly in a markdown viewer

## When to Use vs Other Skills

| Task | Use | Don't Use |
|------|-----|-----------|
| DOCX → Rich Markdown | **markitdown** | pandoc |
| PDF → Rich Markdown | **markitdown** | pdf-reading (for raw text) |
| PPTX → Rich Markdown | **markitdown** | pptx skill (for editing) |
| XLSX → Rich Markdown | **markitdown** | xlsx skill (for data analysis) |
| Edit DOCX/PPTX | docx/pptx skill | markitdown |
| Extract PDF tables | pdf-reading + pdfplumber | markitdown |
| Create documents | docx/pdf/pptx skills | markitdown |

## Enrichment Examples

### Before (raw markitdown output)

```
QUARTERLY REPORT

This is the quarterly report for Q3 2025. It covers sales, expenses, and projections.

Sales were up 15% year over year. Key drivers:
• Enterprise deals +22%
• SMB renewals +8%
• New logo acquisition +18%

https://internal.company.com/reports/q3-2025

Note: All figures are in AUD unless otherwise stated.
```

### After (enriched markdown)

```markdown
---
title: Quarterly Report
source: report.docx
converted: 2025-06-02T03:45:00Z
format: DOCX
---

## Quarterly Report

This is the **quarterly report** for *Q3 2025*. It covers sales, expenses, and projections.

Sales were up **15%** year over year. Key drivers:

- **Enterprise deals** +22%
- **SMB renewals** +8%
- **New logo acquisition** +18%

[https://internal.company.com/reports/q3-2025](https://internal.company.com/reports/q3-2025)

> **Note:** All figures are in *AUD* unless otherwise stated.
```

## Installation

Installed globally via `uv tool install "markitdown[all]"` or `pip install markitdown` — available as the `markitdown` command.

Verify installation:

```bash
markitdown --version
```

## Known Limitations

**Table compression (DOCX):**
markitdown frequently compresses multi-row tables into single lines. All cells from all rows appear on one line separated by `|  |` (empty cell markers). The `--enrich` flag catches some cases but **not all** — especially documents with merged cells, irregular row boundaries, or tables with 5+ columns.

Detection:
```bash
grep -c '|  |' output.md
```
If count > 0, tables are compressed. Run the fix scripts:
```bash
python scripts/fix_markitdown_output.py output.md  # Remove empty leading cells
python scripts/fix_compressed_tables.py output.md   # Split rows
python scripts/fix_edge_cases.py output.md          # Extract merged headings
```

**Character encoding artifacts (Windows):**
On Windows, special symbols (arrows →, checkmarks ✓, footnotes †, guillemets »/«) are often replaced with `?` characters. This happens because Word stores these as PUA (Private Use Area) characters or internal entity references that markitdown cannot resolve.

Detection:
```bash
grep -n ' ? ' output.md
```
Common mappings:
- `?` between numbers → `→` (arrow, e.g. `4.5h ? 0.5-2h`)
- `?` before status words → `✓` (checkmark, e.g. `? On time`)
- `?` before "endorsed/modelled" → `†` (footnote marker)
- `?` around warnings → `»/«` (guillemets)

Fix: Run `python scripts/fix_encoding.py output.md` or apply manually.

**Word TOC artifacts:**
markitdown preserves Word's auto-generated table of contents as broken markdown links like `[Title](#_Toc221889628)`. The `--enrich` flag strips these automatically, but custom TOC entries that don't match the standard `_Toc` pattern may remain.

**Post-table notes merging into cells:**
Text immediately following a table in Word may be merged into the last cell. Spot-check last cells for sentence-length content that doesn't match the column type. Extract and format as `> **Note:**` blockquotes.

## Troubleshooting

**Command not found:**
```bash
pip install markitdown
# or
uv tool install "markitdown[all]"
```

**Missing optional dependencies:**
```bash
uv tool install "markitdown[all]" --force
```

**Large PDFs timing out:**
Use pdf-reading skill instead for page-by-page extraction.

**Corrupted Office files:**
Markitdown may fail; try the specific skill (docx, pptx, xlsx) for recovery options.

**Tables look garbled after conversion:**
If tables appear as single long lines with pipes, the mechanical enrichment may not have fully reconstructed them. This usually happens with tables containing empty cells or irregular row boundaries. Run the grep check above to detect them, then apply manual fixes or use a custom script for that document.

**Enrichment produces unexpected results:**
The mechanical enrichment uses regex heuristics which can occasionally misclassify content. If the output looks wrong, convert without `--enrich` and apply semantic enhancements manually.

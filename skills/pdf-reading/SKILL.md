---
name: pdf-reading
description: "Use this skill when you need to read, inspect, or extract content from PDF files — especially when file content is NOT in your context and you need to read it from disk. Covers content inventory, text extraction, page rasterization for visual inspection, embedded image/attachment/table/form-field extraction, and choosing the right reading strategy for different document types (text-heavy, scanned, slide-decks, forms, data-heavy). Do NOT use this skill for PDF creation, form filling, merging, splitting, watermarking, or encryption — use the pdf skill instead."
---

# PDF Reading Guide

## Step 0 — Find Python (Windows, always do this first)

`python` and `python3` are not reliably on PATH in the bash shell on Windows.
Find the real executable before running any Python commands:

```bash
PYTHON=$(find /c/Users/$USER/AppData/Local/Programs/Python -name "python.exe" 2>/dev/null | head -1)
echo "Python: $PYTHON"
```

If that returns nothing, Python is not installed:
```bash
winget install Python.Python.3.12 --silent
# Then re-run the find command above
```

Use `$PYTHON` (the full path) for all subsequent commands in this session.

Check and install required packages:
```bash
$PYTHON -c "import pypdf; print(pypdf.__version__)"           # text extraction
$PYTHON -m pip install pypdf                                   # if missing
$PYTHON -c "import fitz; print(fitz.__version__)"             # rasterization
$PYTHON -m pip install pymupdf                                 # if missing
$PYTHON -c "import pdfplumber; print(pdfplumber.__version__)"  # tables
$PYTHON -m pip install pdfplumber                              # if missing
```

---

## Step 1 — Check for embedded Markdown (always do before text extraction)

PDFs created with the `pdf-md` skill contain a clean `.md` attachment — structured
text that's far better than anything PDF extraction can produce. Always check first.

```bash
$PYTHON -c "
from pypdf import PdfReader
r = PdfReader('document.pdf')
md_attachments = {k: v for k, v in r.attachments.items() if k.endswith('.md')}
if md_attachments:
    for name, files in md_attachments.items():
        print(f'[FOUND] Embedded Markdown: {name} ({len(files[0])} bytes)')
        print(files[0].decode('utf-8'))
else:
    print('[NOT FOUND] No embedded .md — fall back to text extraction')
"
```

**Decision:**
- **Found** → use the `.md` content directly. No further extraction needed.
- **Not found** → proceed to Content inventory and Text extraction below.

The `pdf-md` skill can also embed a Markdown layer into any PDF you're working
with, making future reads faster and cleaner.

---

## Step 2 — Content inventory

Get page count and basic metadata with pypdf:

```bash
$PYTHON -c "
from pypdf import PdfReader
r = PdfReader('document.pdf')
print(f'Pages: {len(r.pages)}')
print(f'Metadata: {r.metadata}')
print(f'Attachments: {list(r.attachments.keys())}')
# Sample first page
print('--- Page 1 ---')
print(r.pages[0].extract_text()[:500])
"
```

---

## Step 3 — Text extraction (fallback when no .md found)

### Quick full-document extraction (pypdf)

```bash
$PYTHON -c "
from pypdf import PdfReader
r = PdfReader('document.pdf')
print(f'Pages: {len(r.pages)}')
for i, page in enumerate(r.pages):
    t = page.extract_text()
    if t and t.strip():
        print(f'-- Page {i+1} --')
        print(t[:600])
"
```

### Layout-aware extraction (pdfplumber — better for multi-column)

```bash
$PYTHON -c "
import pdfplumber
with pdfplumber.open('document.pdf') as pdf:
    for i, page in enumerate(pdf.pages):
        print(f'-- Page {i+1} --')
        print(page.extract_text())
"
```

### Markdown extraction (markitdown — for rich content)

Use `markitdown` when you need clean markdown output from PDFs with mixed content (text, tables, images). It produces structured markdown that's easier to work with than raw text extraction.

```bash
markitdown document.pdf > document.md
cat document.md | head -100
```

**When to use:**
- PDFs with tables → markdown tables
- Mixed formatting → preserved as markdown
- Need structured output for further processing
- Content destined for documentation/markdown workflows

**Trade-off:** Slightly slower than pypdf/pdfplumber; use those for quick text extraction.

---

## Visual inspection (rasterize pages)

Text extraction is blind to charts, diagrams, and layout. Rasterize when those matter.
Use PyMuPDF (`fitz`) — no external CLI tools required.

```bash
$PYTHON -c "
import fitz, os, tempfile
doc = fitz.open('document.pdf')
tmp = tempfile.gettempdir()
# Rasterize pages 1–3 at 150 DPI
for i in range(min(3, len(doc))):
    page = doc[i]
    mat = fitz.Matrix(150/72, 150/72)   # 150 DPI
    pix = page.get_pixmap(matrix=mat)
    out = os.path.join(tmp, f'page_{i+1:03d}.png')
    pix.save(out)
    print(f'Saved: {out}')
"
```

Then use the Read tool to view each `.png` file.

**Token cost:**
- Text extraction: ~200–400 tokens/page
- Rasterized image: ~1,600 tokens/page at 150 DPI

---

## Choosing your strategy

| Document type | Strategy |
|---|---|
| Text-heavy (reports, articles) | Text extraction primary; rasterize only figures |
| Scanned (no extractable text) | Rasterize pages, inspect visually |
| Slide-deck PDFs | Rasterize pages one by one — layout matters more than text |
| Form-heavy | Extract form fields first, rasterize for visual context |
| Data-heavy (tables, charts) | pdfplumber for tables; rasterize chart pages |

---

## Extracting tables (pdfplumber)

```bash
$PYTHON -c "
import pdfplumber
with pdfplumber.open('document.pdf') as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, tbl in enumerate(tables):
            print(f'Page {i+1}, Table {j+1}:')
            for row in tbl:
                print(row)
"
```

---

## Extracting attachments (pypdf)

```bash
$PYTHON -c "
from pypdf import PdfReader
r = PdfReader('document.pdf')
for name, files in r.attachments.items():
    print(f'Attachment: {name} ({len(files[0])} bytes)')
    if name.endswith('.md') or name.endswith('.txt'):
        print(files[0].decode('utf-8')[:1000])
"
```

---

## Extracting form fields (pypdf)

```bash
$PYTHON -c "
from pypdf import PdfReader
r = PdfReader('document.pdf')
fields = r.get_fields() or {}
for name, field in fields.items():
    print(f\"{name}: {field.get('/V', '')} (type: {field.get('/FT', '')})\")
"
```

---

## OneDrive write issues

If writing output to an OneDrive directory fails with "bad file descriptor" or
permission errors, write to a local path instead:

```bash
# Use Downloads as a safe output dir
OUT="$USERPROFILE/Downloads"
# or use system temp
OUT=$(python -c "import tempfile; print(tempfile.gettempdir())")
```

---

## Quick reference

| Priority | Task | Tool | Approach |
|---|---|---|---|
| 1st | Check for embedded .md | pypdf | `r.attachments` — use if present |
| 2nd | Extract text | pypdf | `page.extract_text()` |
| 2nd | Extract text (layout-aware) | pdfplumber | `page.extract_text()` |
| 2nd | Extract text (markdown) | markitdown | `markitdown document.pdf > output.md` |
| As needed | Page count + metadata | pypdf | `PdfReader` + `.metadata` |
| As needed | Extract tables | pdfplumber | `page.extract_tables()` |
| As needed | See page visually | PyMuPDF (fitz) | `page.get_pixmap()` → `.png` → Read tool |
| As needed | Read form fields | pypdf | `r.get_fields()` |

For PDF creation, merging, splitting, filling — use the `pdf` skill.
To embed a clean Markdown layer into a PDF — use the `pdf-md` skill.

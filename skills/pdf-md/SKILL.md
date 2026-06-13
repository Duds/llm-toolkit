---
name: pdf-md
description: >-
  Embed a Markdown source file as a named attachment inside a PDF (dual-layer
  document), or extract the embedded .md back out for LLM ingestion, RAG
  pipelines, or editing. Use this skill whenever the user says "embed markdown
  in PDF", "add .md layer to PDF", "create a dual-layer PDF", "pdf-md",
  "embed md", "parse and embed", "extract markdown from PDF", "get the .md out
  of this PDF", "read the markdown layer", "does this PDF have a markdown
  attachment", or "check for embedded markdown". Also trigger when the user
  provides only a PDF and asks to embed — parse the PDF text and embed it.
  Also trigger when the user is preparing documents for an AI pipeline and asks
  how to preserve clean text alongside the PDF.
---

# pdf-md — PDF + Markdown Dual-Layer Skill

## Purpose

Creates and consumes dual-layer PDFs: a single `.pdf` file that contains both
the rendered PDF (for humans) and an embedded `.md` source (for machines).

The `.md` attachment travels inside the PDF, never gets separated, and gives
AI pipelines clean, structured text instead of PDF extraction artifacts.

Standard: see `references/pdf-md-standards.md`
Script: `scripts/pdf_md.py` (requires `pypdf >= 4.0`)

---

## Operations

### 0. Parse-and-embed — extract PDF text and embed as .md (most common)

**When:** User provides only a PDF and asks to embed a Markdown layer. No
separate `.md` file exists. This is the default flow.

**Steps:**

1. Confirm the PDF path and optional output path.

2. Check `pypdf` is installed:
   ```bash
   python -c "import pypdf; print(pypdf.__version__)"
   ```
   If missing, find Python and install: `<python> -m pip install pypdf`

3. Run parse-embed:
   ```bash
   python path/to/pdf_md.py parse-embed <input.pdf> [-o output.pdf]
   ```
   This extracts all page text, formats it as `## Page N` Markdown sections,
   and embeds the result as `<pdf-basename>.md` inside the PDF.

4. Confirm: script prints page count, char count, then the embed confirmation.

5. If the output PDF cannot be written to the source directory, use `-o` to
   write to a writable path (Downloads, temp dir), then tell the user where
   the file is.

---

### 1. Embed — add a .md layer to a PDF

**When:** User has a PDF and a pre-existing .md file and wants to combine them.

**Steps:**

1. Confirm the input files:
   - PDF path
   - .md file path
   - Output path (optional — defaults to overwriting the input PDF)

2. Check `pypdf` is installed (see above).

3. Run the embed script:
   ```bash
   python path/to/pdf_md.py embed <input.pdf> <source.md> [-o output.pdf]
   ```

4. Confirm success — script prints: `Embedded '<name>.md' into <output.pdf>`

5. Tell the user the output path and note that the attachment is named
   `<pdf-basename>.md` per the standard.

---

### 2. Extract — retrieve the .md layer from a PDF

**When:** User has a PDF that may contain an embedded .md and wants to read or
use it.

**Steps:**

1. Confirm the input PDF path and optional output path for the `.md` file.

2. Run the extract script:
   ```bash
   python path/to/pdf_md.py extract <input.pdf> [-o output.md]
   ```

3. If extraction succeeds, read the output `.md` and present its content to
   the user (or pass it to the next step in the pipeline).

4. If no `.md` attachment is found, fall back to standard PDF text extraction
   using the `pdf-reading` skill, and note the fallback to the user.

---

### 3. Check — verify whether a PDF has an embedded .md

**When:** User wants to know if a PDF follows the dual-layer standard.

**Steps:**

1. Run the check:
   ```bash
   python path/to/pdf_md.py check <input.pdf>
   ```

2. Report the result:
   - [OK] Found: name and size of the `.md` attachment
   - [--] Not found: suggest running parse-embed

---

## Python on Windows

On Windows, `python` may not be on PATH from the bash shell. Find it with:
```bash
find /c/Users/$USER/AppData/Local/Programs/Python -name "python.exe" 2>/dev/null | head -1
```
If not installed, install via winget:
```bash
winget install Python.Python.3.12 --silent
```
Then use the full path: `/c/Users/<user>/AppData/Local/Programs/Python/Python312/python.exe`

---

## Script location

The script ships with this skill at:
```
.claude-resources/user/pdf-md/scripts/pdf_md.py
```

When running from inside a project, use the path relative to the skills repo,
or copy `pdf_md.py` into the project's working directory.

Symlink path (after setup-skills.sh): `~/.claude/skills/pdf-md/scripts/pdf_md.py`

---

## Inline usage (no script)

For quick one-off tasks, use `pypdf` directly in a Python snippet:

**Embed:**
```python
from pypdf import PdfReader, PdfWriter
from pathlib import Path

reader = PdfReader("doc.pdf")
writer = PdfWriter()
for page in reader.pages:
    writer.add_page(page)
writer.add_attachment("doc.md", Path("doc.md").read_bytes())
with open("doc-with-md.pdf", "wb") as f:
    writer.write(f)
```

**Extract:**
```python
from pypdf import PdfReader

reader = PdfReader("doc.pdf")
for name, files in reader.attachments.items():
    if name.endswith(".md"):
        print(files[0].decode("utf-8"))
```

---

## Notes

- Attachment name convention: `<pdf-basename>.md` — always match the PDF filename
- Requires `pypdf >= 4.0`. The older `PyPDF2` package does not support
  reading attachments reliably.
- The operation is non-destructive: original PDF content and metadata are
  preserved; only the attachment collection is modified.
- If the PDF already has a `.md` attachment with the same name, `add_attachment`
  appends a second copy — warn the user and suggest using `-o` to a new file
  rather than overwriting in place when re-embedding after edits.
- If the source directory is not writable, use `-o` to target a different
  location (e.g. Downloads folder).

---
name: mirror-docs
description: >-
  Automate markdown mirror creation and maintenance for Office/PDF files.
  Use this skill whenever Dale says "mirror docs", "create mirrors",
  "update mirrors", "check mirrors", "validate mirrors", or when working
  with Office/PDF files that need markdown equivalents. Supports scanning,
  creating, updating, and validating mirrors.
---

# Mirror Docs — Markdown Mirror Automation

## Purpose

Maintain markdown mirrors alongside Office/PDF files for LLM accessibility.
Mirrors live in the same directory as their source files with `.md` extension.

---

## Commands

| Command | Purpose |
|---------|---------|
| `mirror-docs scan` | Find Office/PDF files needing mirrors |
| `mirror-docs create <file>` | Create mirror for specific file |
| `mirror-docs update-all` | Refresh all stale mirrors |
| `mirror-docs validate` | Check for stale/outdated mirrors |

---

## Command: scan

List all Office/PDF files and their mirror status.

**Output:**
```
MIRROR SCAN RESULTS

NEED MIRRORS (3):
  artefacts/document-v0_2.pptx
  docs/requirements.docx
  inbox/report.pdf

CURRENT MIRRORS (5):
  artefacts/strategy-v1_0.pptx → artefacts/strategy-v1_0.md

STALE MIRRORS (2):
  docs/architecture.pptx (modified 2026-04-20, mirror from 2026-04-15)
```

---

## Command: create <file>

Create a markdown mirror for a specific Office or PDF file.

**Process:**
1. Detect file type (pptx, docx, xlsx, pdf)
2. Extract content using appropriate method
3. Create `.md` file alongside source
4. Add standard header with source reference

**For PowerPoint (.pptx):**
- Extract slide titles and notes
- Preserve slide order
- Include speaker notes if present

**For Word (.docx):**
- Extract headings and body text
- Preserve document structure
- Include tables as markdown tables

**For Excel (.xlsx):**
- Convert each sheet to markdown table
- Include sheet names as headers
- Note formulas vs values

**For PDF:**
- Extract text content
- Preserve page structure
- Note: scanned PDFs may have limited text

---

## Command: update-all

Refresh all stale mirrors (where source is newer than mirror).

**Process:**
1. Run validation to find stale mirrors
2. For each stale mirror:
   - Backup existing mirror (append `.bak`)
   - Re-extract content from source
   - Write updated mirror
3. Report changes

---

## Command: validate

Check if mirrors are up-to-date without modifying anything.

**Checks:**
- Missing mirrors (Office/PDF without .md)
- Stale mirrors (source newer than mirror)
- Temp files (`~$*` pattern)

**Output:**
```
VALIDATION RESULTS

Missing mirrors: 3
Stale mirrors: 2
Current mirrors: 15
Temp files found: 1 (~$document.pptx)

RECOMMENDATION: Run 'mirror-docs update-all' to refresh stale mirrors
```

---

## Mirror Format

All mirrors include a standard header:

```markdown
---
source: "document-v0_2.pptx"
mirrored: "2026-04-23"
generator: "mirror-docs"
---

# [Document Title]

[Content...]
```

---

## Windows Path Handling

When passing paths to Python on Windows, use Windows-style paths:
- ❌ `/c/Users/.../file.pdf`
- ✅ `C:/Users/.../file.pdf`

---

## Integration with 5S

The `5s` skill includes mirror file audits. Run `mirror-docs validate` before
`5s` to pre-check mirror status.

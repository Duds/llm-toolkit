# Post-Conversion Fix Scripts

These scripts fix common markitdown output issues on Windows. Run them in sequence after any DOCX conversion.

## Usage

```bash
# After: markitdown document.docx > output.md

# Step 1: Fix empty leading cells + checkboxes
python scripts/fix_markitdown_output.py output.md

# Step 2: Fix compressed tables (if grep shows |  |)
python scripts/fix_compressed_tables.py output.md

# Step 3: Fix edge cases
python scripts/fix_edge_cases.py output.md

# Step 4: Fix encoding artifacts (Windows ? characters)
python scripts/fix_remaining_encoding.py output.md
```

## What Each Script Fixes

### fix_markitdown_output.py
- Removes empty leading cells from table rows (`|  |` → `|`)
- Converts `?` checklist markers to `- [x]` / `- [ ]`
- Fixes `~30%` contingency notation
- Removes `**` from inside heading markers

### fix_compressed_tables.py
- Splits table rows compressed onto single lines
- Uses `|  |` as row separator pattern
- Reconstructs proper multi-line markdown tables

### fix_edge_cases.py
- Extracts headings merged into table cells
- Pads rows with fewer columns than header
- Handles text spilled into last table cells

### fix_remaining_encoding.py
- Replaces `?` arrows with `→`
- Replaces `?` checkmarks with `✓`
- Replaces `?` footnotes with `†`
- Replaces `?` guillemets with `»/«`

## Detection Commands

```bash
# Check for compressed tables
grep -c '|  |' output.md
# If > 0, run fix_compressed_tables.py

# Check for encoding artifacts
grep -n ' ? ' output.md
# If any found, run fix_remaining_encoding.py

# Check for empty leading cells
grep -n '|  | ---' output.md
# If any found, run fix_markitdown_output.py
```

## When You Don't Need These

- **Simple documents** (1-2 tables, no special characters): `--enrich` flag is usually sufficient
- **PDF conversions**: Tables are typically well-formed
- **PPTX conversions**: Tables are rare, slides are section-based

## When You Definitely Need These

- **Government/formal DOCX** with 10+ tables (DTA templates, business cases)
- **Documents with checkmarks** (Word Insert Symbol → ✓)
- **Documents with footnotes** (Word Insert Symbol → †, ‡)
- **Windows-created DOCX** with any special characters
- **Merged-cell tables** (complex layouts, spanning headers)

## Full Pipeline (One-Liner)

```bash
markitdown document.docx > output.md && \
  python scripts/fix_markitdown_output.py output.md && \
  python scripts/fix_compressed_tables.py output.md && \
  python scripts/fix_edge_cases.py output.md && \
  python scripts/fix_remaining_encoding.py output.md
```

Or use the agent script:
```bash
python scripts/markitdown_agent.py convert document.docx -o output.md --enrich
# Then run fixes if needed based on detection checks
```

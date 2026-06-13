---
name: file-reading
description: "Use this skill when a file has been uploaded but its content is NOT in your context — only its path at /mnt/user-data/uploads/ is listed in an uploaded_files block. This skill is a router: it tells you which tool to use for each file type (pdf, docx, xlsx, csv, json, images, archives, ebooks) so you read the right amount the right way instead of blindly running cat on a binary. Triggers: any mention of /mnt/user-data/uploads/, an uploaded_files section, a file_path tag, or a user asking about an uploaded file you have not yet read. Do NOT use this skill if the file content is already visible in your context inside a documents block — you already have it."
compatibility: "claude.ai, Claude Desktop, Cowork — any surface where uploads land at /mnt/user-data/uploads/"
---

# Reading Uploaded Files

## Why this skill exists

When a user uploads a file, it is written to `/mnt/user-data/uploads/<filename>`.
The content is NOT in your context — you must go read it.

Running `cat` on a binary file (PDF, DOCX, XLSX) produces garbage.
This skill tells you the right first move for each file type.

## General protocol

1. **Look at the extension** — that is your dispatch key.
2. **Stat before you read** — large files need sampling, not slurping.
   ```bash
   stat -c '%s bytes, %y' /mnt/user-data/uploads/report.pdf
   file /mnt/user-data/uploads/report.pdf
   ```
3. **Read just enough** to answer the question.
4. **If a dedicated skill exists, go read it** — see the table below.

## Dispatch table

| Extension | First move | Dedicated skill |
|-----------|-----------|-----------------|
| `.pdf` | Content inventory (see PDF section) | `pdf-reading` skill |
| `.docx` | `markitdown` to markdown | `docx` skill (if editing needed) |
| `.xlsx`, `.xlsm` | `openpyxl` sheet names + head | `xlsx` skill |
| `.xls` (legacy) | `pd.read_excel(engine="xlrd")` | `xlsx` skill |
| `.pptx` | `python-pptx` slide count | `pptx` skill |
| `.csv`, `.tsv` | `pandas` with `nrows` | — |
| `.json`, `.jsonl` | `jq` for structure | — |
| `.jpg`, `.png`, `.gif`, `.webp` | Already in context as vision input | — |
| `.zip`, `.tar`, `.tar.gz` | List contents, do NOT auto-extract | — |
| `.txt`, `.md`, `.log`, code | `wc -c` then `head` or `cat` | — |
| Unknown | `file` then decide | — |

## PDF

Never `cat` a PDF. Quick first move:

```bash
pdfinfo /mnt/user-data/uploads/report.pdf
pdftotext -f 1 -l 1 /mnt/user-data/uploads/report.pdf - | head -20
```

For anything beyond a quick peek, use the `pdf-reading` skill.

## DOCX

```bash
markitdown /mnt/user-data/uploads/memo.docx | head -200
```

## XLSX

```python
from openpyxl import load_workbook
wb = load_workbook("/mnt/user-data/uploads/data.xlsx", read_only=True)
print("Sheets:", wb.sheetnames)
ws = wb.active
for row in ws.iter_rows(max_row=5, values_only=True):
    print(row)
```

## CSV / TSV

```python
import pandas as pd
df = pd.read_csv("/mnt/user-data/uploads/data.csv", nrows=5)
print(df)
print(df.dtypes)
```

## JSON / JSONL

```bash
jq 'type' /mnt/user-data/uploads/data.json
jq 'if type == "array" then length elif type == "object" then keys else . end' /mnt/user-data/uploads/data.json
```

## Archives

```bash
unzip -l /mnt/user-data/uploads/bundle.zip
tar -tf /mnt/user-data/uploads/bundle.tar
```

List first. Extract never — unless the user explicitly asks.

## Plain text / code / logs

```bash
wc -c /mnt/user-data/uploads/app.log
# Under ~20KB: cat is fine
# Over ~20KB: head -100 and tail -100 to orient
```

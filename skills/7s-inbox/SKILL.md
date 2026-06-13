---
name: 7s-inbox
description: >-
  Daily inbox cleaner — review portfolio and project inboxes, classify each
  item, and recommend actions. Chained from the 7s skill via "--inbox" flag.
  Also trigger directly when Dale says "clean inbox", "inbox zero", "process
  my inbox", "tidy inbox", "daily inbox clean", or "/7s --inbox". Validates
  YAML frontmatter compliance. READ-ONLY recommendations — executes only on
  confirmation.
---

# 7S Inbox Cleaner

Chained from `/7s --inbox`. Reviews all portfolio and project inboxes and
produces a classified action list. Identifies and recommends — does not
execute without confirmation.

---

## Folder Structure

```
Projects/
├── _archive/                   # Portfolio archive (root only)
├── inbox/                      # Portfolio inbox
├── reports/
│   ├── ict-reports/            # DCCEEW internal reports
│   └── ctoc-reports/           # CTOC consulting reports
└── <project>/
    ├── _archive/               # Project archive (project root only)
    ├── inbox/                  # Project inbox (optional)
    ├── reports/
    ├── artefacts/
    └── docs/
```

**Archive rule:** `_archive/` at portfolio root or project root only — never
nested inside subfolders.

---

## Step 1: Inventory

Scan for inboxes at:
- `Projects/inbox/` — portfolio inbox
- `Projects/<project>/inbox/` — project inboxes

For each file capture: path, name, extension, size, last-modified date.

Categorise by type:

| Category | Patterns |
|----------|----------|
| Documents | `.md`, `.docx`, `.pdf`, `.txt` |
| Diagrams | `.vsd`, `.vsdx`, `.drawio`, `.svg`, `.mmd` |
| Data | `.csv`, `.xlsx`, `.json`, `.xml` |
| Media | `.png`, `.jpg`, `.mp4`, `.mp3` |
| Code/Config | `.py`, `.sh`, `.yaml`, `.yml`, `.prompt.txt` |
| Other | Everything else |

---

## Step 2: Classify Each Item

### 2a: Project affinity

- Check filename for project indicators
- Read first 500 chars of text files for project references
- Match to known project names in workspace

| Signal | Action |
|--------|--------|
| Clear project match | Recommend filing to that project |
| Ambiguous | Portfolio-level or `_llm-wiki` entry |
| No match | Flag for manual classification |

### 2b: Action classification

| Action | When | Destination |
|--------|------|-------------|
| **FILE** | Completed work, reference material | `artefacts/`, `docs/`, `reports/` |
| **CONVERT** | Wrong format (Visio → Mermaid, PDF → MD) | Converted location, archive original |
| **ACTION** | Incomplete draft, pending review | TASKS.md entry + WIP location |
| **LLM-WIKI** | Knowledge worth preserving | `_llm-wiki/knowledge/` |
| **ARCHIVE** | Complete but worth keeping | `_archive/` at portfolio or project root |
| **DISCARD** | Temp files, duplicates, outdated drafts | Delete with confirmation |

### 2c: Frontmatter validation (Markdown files)

| Field | Valid values |
|-------|-------------|
| `diataxis` | `tutorial`, `how-to`, `explanation`, `reference` |
| `type` | `code`, `dcceew`, `personal`, `program`, `llm-wiki`, `knowledge`, `blueprint`, `concept`, `decision`, `research`, `reference`, `case-study` |
| `status` | `active`, `paused`, `complete`, `archive` |

Flag as Notable: missing required fields, malformed YAML, invalid enum values.

---

## Step 3: Recommendations

For each item:

```
### <filename>
- **Path:** <full-path>
- **Type:** <category>
- **Age:** <days since modified>
- **Action:** FILE | CONVERT | ACTION | LLM-WIKI | ARCHIVE | DISCARD
- **Destination:** <suggested path>
- **Rationale:** <why>
- **Frontmatter issues:** <if any>
```

---

## Step 4: Batch Summary

```
## 7S Inbox Cleaner — [date]

| Action | Count | Est. time |
|--------|-------|-----------|
| FILE | N | ~N min |
| CONVERT | N | ~N min |
| ACTION | N | ~N min |
| LLM-WIKI | N | ~N min |
| ARCHIVE | N | ~N min |
| DISCARD | N | Immediate |
| **Total** | **N** | **~N min** |

### Inboxes scanned
- `Projects/inbox/` — N items
- `Projects/<project>/inbox/` — N items

---

### Quick wins (confirm to execute)
[Safe-to-discard items — temp files older than 7 days, empty files, duplicates]

### Filing batch
[Items with clear project home]

### Conversion queue
[Items needing format conversion — chains to vsd-to-mmd, pdf-reading, etc.]

### Knowledge capture
[Items for _llm-wiki]

### Action items
[Items needing follow-up — generates TASKS.md entries]

---

### Frontmatter validation
| File | Status | Issues |
|------|--------|--------|
| ... | ✓ Valid / ✗ Invalid | ... |

---

Choose processing mode:
A. Review each item individually
B. Apply quick wins, then review the rest
C. Batch by action type
D. Schedule daily clean (via /schedule)
```

---

## Step 5: Execution

Execute only on explicit user confirmation per action type.

**DISCARD:** List → confirm once → delete → log.

**FILE:** Confirm destination → move → update references.

**CONVERT:** Identify skill (vsd-to-mmd, pdf-reading, etc.) → convert →
validate → move original to `_archive/` at portfolio or project root.

**ACTION:** Create TASKS.md entry → move file to WIP location.

**LLM-WIKI:** Determine diataxis class → scaffold frontmatter → write page
→ update `_llm-wiki/index.md`.

**ARCHIVE:** Confirm `_archive/` destination → move → log.

---

## Notes

- Identifies and recommends only — never auto-executes destructive actions
- `_archive/` at portfolio or project root only — never nested
- This skill is invoked by `/7s --inbox` or directly as `/7s-inbox`
- Return to `/7s` for the workspace-level audit

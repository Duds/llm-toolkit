---
name: 5s
description: >-
  Audit the Projects workspace against STANDARDS.md using the 5S methodology
  (Sort, Set in Order, Shine, Standardize, Sustain). Use this skill whenever
  Dale says "5s", "run 5s", "tidy the workspace", "audit my projects", "check
  project hygiene", "what needs cleaning up", "workspace audit", or "/5s".
  Also trigger if Dale asks whether projects are compliant, named correctly, or
  whether any projects should be archived. This skill is READ-ONLY — it detects
  and reports issues but never applies fixes. To fix issues, it chains to the
  workspace-cleanup squad via invoke-squad. Also trigger on: "fix these audit
  issues", "apply 5S fixes", "fix my workspace", "clean up projects" — these
  phrases run the audit first, then offer to invoke the cleanup squad.
  Optional mode flags:
  - "--code" to audit a specific code project for dead code, dependency hygiene,
    test coverage, and CI/CD health.
  - "--inbox" to run the daily inbox cleaner that reviews portfolio and project
    inboxes, deciding whether to file, convert, action, write llm-wiki entries,
    archive, or discard items. Validates YAML frontmatter compliance.
---

# 5S — Workspace Audit

## Purpose

Inspect the `Projects/` workspace against `STANDARDS.md` and produce an
actionable audit report with a health score and severity-tiered findings.
Flag issues only — do not auto-fix. Offer specific remediation actions and
optionally schedule regular runs.

---

## Mode detection

Before running, determine scope:

| Mode | Trigger | Purpose |
|------|---------|---------|
| **Workspace** (default) | No flags | Audit `Projects/` root structure — naming, lifecycle, hygiene, standards compliance |
| **Code** | `--code` flag or "audit this project" | Audit current code project for dev-workspace hygiene |
| **Inbox** | `--inbox` flag or "clean inbox" / "inbox zero" | Daily inbox cleaner — portfolio and project inboxes |

---

# Workspace Mode (Default)

## Step 1: Load Standards and Context

Read the following in parallel:

1. `Projects/STANDARDS.md` — if missing, stop and say:
   > "STANDARDS.md not found. This file defines the rules the 5S audit checks
   > against. Want me to create it?"

2. `Projects/TASKS.md` — note which projects are referenced as active work.

3. Most recent `Projects/Plans/YYYY-MM-DD-week-priorities.md` — note which
   projects appear as this week's focus.

From STANDARDS.md, extract:
- **§1 Naming** — naming rules for dirs and files
- **§2 Structure** — required files per project type
- **§3 Lifecycle** — status declaration rules
- **§4 Hygiene** — patterns to flag or remove
- **§5 Document formats** — PDF+Markdown dual-layer requirements
- **§6 Task management** — three-layer model, separation of concerns
- **§8 Skill authoring** — structure and frontmatter standards

---

## Step 2: Scan the Workspace

List all items at the `Projects/` root (one level only). Categorise each:

| Category | Criteria |
|---|---|
| **Tooling** | Dot-prefixed: `.claude-resources`, `.claude` — skip entirely |
| **Reserved** | Underscore-prefixed: `_templates`, `_archive` — check naming only |
| **Document folders** | Title-Case dirs with no `CLAUDE.md` (e.g. `Plans`) — check naming only |
| **Projects** | Everything else with a directory entry — full audit |
| **Loose files** | Files directly at workspace root |

For each project directory, read its `CLAUDE.md` (if present) to extract:
- `status:` field from YAML frontmatter
- `type:` field (code / dcceew / personal / program / llm-wiki)
- Any `last-updated:` or similar date fields

---

## Step 3: Sort (Seiri) — Remove What Doesn't Belong

Scan for items that violate the §1.2 root-level allowlist or have no place:

**Flag as Critical:**
- Files at workspace root that are NOT: `CLAUDE.md`, `TASKS.md`, `STANDARDS.md`,
  or a recognised meta dir (Plans, _templates, _archive, reports, inbox, etc.)
- Projects with `status: archive` or `status: complete` still at the workspace
  root more than 30 days after that status was set (not yet moved to `_archive/`)

**Flag as Notable:**
- Directories that don't fit any project type or naming pattern
- Projects with no `CLAUDE.md` at all (content unknown — type undetectable)
- Duplicate or near-duplicate project names (e.g. `client-alpha` and `client-alpha-2`)

**Flag as Suggestion:**
- Projects that appear neither in TASKS.md nor in the current week plan AND
  have no file activity in 90+ days (candidates for archival review)

For each finding, record: Path | Severity | Issue | Suggested action

---

## Step 4: Set in Order (Seiton) — Naming and Structure

**Naming check (§1):**

| Check | Severity |
|---|---|
| Project dirs not `kebab-case` (uppercase, spaces, underscores) | Notable |
| Files at root not matching §1.2 allowlist exactly | Notable |
| Date-stamped files without `YYYY-MM-DD-` prefix | Suggestion |
| Plans/ files not following date-stamp naming | Suggestion |

**Structure check (§2):**

For each project directory:

| Check | Severity |
|---|---|
| Missing `CLAUDE.md` | Critical |
| Missing `TASKS.md` | Notable |
| `type: code` but no `.claude/` directory | Notable |
| `type: dcceew` but no `Plans/` or `docs/` directory | Suggestion |
| `type: program` but a stream subdirectory has no `CLAUDE.md` or `TASKS.md` | Notable |
| `type: llm-wiki` but missing required folders (raw/, knowledge/, etc.) | Notable |

**Cross-reference check:**

| Check | Severity |
|---|---|
| Active project (status: active) absent from both TASKS.md and current week plan | Suggestion |
| Project referenced in TASKS.md but not found in workspace | Notable |

For each finding, record: Path | Severity | Issue | Suggested action

---

## Step 5: Shine (Seiso) — Hygiene Check

Scan each project directory (recursively, skip `.claude-resources/`, `.claude/`,
`_templates/`, `_archive/`) for hygiene patterns:

**Always flag as Notable:**
- `~$*` — Office temp files
- `*.tmp`, `*.bak` — temp/backup files
- `Thumbs.db`, `.DS_Store`, `desktop.ini` — OS metadata
- Empty directories (no files, no meaningful subdirectories)
- Broken symlinks (target path does not exist)

**Flag as Notable:**
- Files with `DRAFT`, `WIP`, `COPY`, `OLD`, `BACKUP`, `v1`, `v2` etc. in their
  name at a project root (not in a versioned subfolder) — likely unsanctioned
  versioning instead of using git or YYYY-MM-DD stamps
- Versioned filenames using incorrect pattern (e.g., `_v0.1` instead of `-v0_1`)
- Version chains (v0.1, v0.2, v1.0) where older versions remain in active directories

**Flag as Suggestion:**
- Projects with no file activity in 90+ days (compare to today's date)
- TASKS.md files with no content changes in 60+ days in a supposedly active project
- Duplicate filenames within the same directory
- Large binary files (>10MB) not in a designated assets folder

For each finding: Path | Severity | Issue type | Suggested action

### Versioned Document Audit (STANDARDS.md §1.4, §1.5)

Scan for versioned documents and check compliance:

| Check | Severity |
|---|---|
| Versioned filenames using wrong pattern (`_v0.1`, `_v0.2`) instead of (`-v0_1`, `-v0_2`) | Notable |
| Multiple versions of same document in active directories (v0.1, v0.2, v1.0) | Notable |
| Old versions not archived when newer version exists | Suggestion |
| Only latest version should be in active directories | Suggestion |

**Version chain detection:**
- Look for filename patterns: `*-v0_1*`, `*-v0_2*`, `*-v1_0*`, etc.
- Group by base name (e.g., `document-v0_1.pptx` and `document-v0_2.pptx`)
- Flag chains where older versions aren't in `_archive/`

### Mirror File Audit (STANDARDS.md §5)

Check Office/PDF files for markdown mirrors:

| Check | Severity |
|---|---|
| Office/PDF files without corresponding `.md` mirror | Notable |
| Mirror file is older than source file (stale mirror) | Notable |
| Temp Office files (`~$*`) present | Notable |

**Mirror validation:**
- For each `.pptx`, `.docx`, `.xlsx`, `.pdf` in `artefacts/`, `docs/`, `deliverables/`:
  - Check if corresponding `.md` file exists
  - If both exist, compare modification times
  - Flag stale mirrors where source is newer than mirror

### Product Code Audit (STANDARDS.md §6.1)

Check communications products for product code compliance:

| Check | Severity |
|---|---|
| HTML deliverable in `deliverables/` or `workstreams/*/deliverables/` missing product code | Notable |
| Product code format invalid (not matching `THEME0000.mmyy`) | Notable |
| Same base product using multiple codes (e.g., `EDR0528` and `EDR0529` for same deliverable) | Notable |
| `.md` mirror mentions a different product code than its source | Notable |
| Product code present but wrong font/position (visual check — flag for manual review) | Suggestion |

**Product code detection:**
- Scan HTML files for `EDR\d{4}` or `[A-Z]{3,}\d{4}` patterns
- Check `.md` mirrors for product code references
- Group findings by base product name — flag code conflicts
- The current EDR program code is `EDR0528`; flag any `EDR0529` or variants as inconsistent

---

## Step 6: Standardize (Seiketsu) — Compliance Check

**Lifecycle status (§3):**

| Check | Severity |
|---|---|
| `CLAUDE.md` present but missing `status:` frontmatter | Notable |
| `CLAUDE.md` present but missing `type:` frontmatter | Notable |
| Two or more projects with `status: complete` for more than 30 days not in `_archive/` | Notable |
| Project `CLAUDE.md` frontmatter present but malformed YAML | Critical |

**TASKS.md quality:**

| Check | Severity |
|---|---|
| TASKS.md exists but is empty or has only a header | Suggestion |
| TASKS.md last modified more than 60 days ago in an `active` project | Suggestion |

**Week plan alignment:**

| Check | Severity |
|---|---|
| No week plan file found in `Plans/` | Notable |
| Most recent week plan is more than 14 days old | Suggestion |

---

## Step 7: Sustain (Shitsuke) — Report and Schedule

### Scoring

After running all phases, compute a health score:

**Start at 100. Deduct:**
- 10 points per Critical finding
- 4 points per Notable finding
- 1 point per Suggestion

**Grade:**
- 90–100: **A — Clean workspace**
- 75–89: **B — Minor issues**
- 60–74: **C — Needs attention**
- 40–59: **D — Action required**
- <40: **F — Workspace in poor health**

### Output format

```
## 5S Workspace Audit — [date]

### Health Score: [score]/100 — [Grade] — [Label]

| Phase | Critical | Notable | Suggestions | Score Impact |
|---|---|---|---|---|
| Sort | n | n | n | -nn |
| Set in Order | n | n | n | -nn |
| Shine | n | n | n | -nn |
| Standardize | n | n | n | -nn |
| Versioned Docs | n | n | n | -nn |
| Mirror Files | n | n | n | -nn |
| Product Codes | n | n | n | -nn |
| **Total** | **n** | **n** | **n** | **[score]/100** |

Projects audited: N | Compliant: N | Issues: N

---

### Sort — Items that don't belong
[table: severity | path | issue | suggested action]

### Set in Order — Naming and structure
[table: severity | path | issue | suggested action]

### Shine — Hygiene
[table: severity | path | issue | suggested action]

### Standardize — Compliance
[table: severity | path | issue | suggested action]

### Versioned Documents
[table: severity | path | issue | suggested action]

### Product Codes
[table: severity | path | issue | suggested action]

### Mirror Files
[table: severity | path | issue | suggested action]

---

### Suggested fixes (ordered by impact)

[Numbered list — Critical items first, then Notable by frequency, then Suggestions]

1. [CRITICAL] ...
2. [CRITICAL] ...
3. [NOTABLE] ...
...

---

### Schedule

Run `/5s` regularly to keep this clean. Want me to set up a scheduled run?
  A. Weekly reminder (every Monday via /schedule)
  B. Add to session-start hook in orient skill
  C. Manual only — I'll run it when needed
```

### Handoff to Workspace Cleanup Squad

**The 5S skill is read-only.** It detects and reports issues but NEVER applies fixes.

After presenting the report, ask:
> "Would you like me to fix these issues? I can invoke the workspace-cleanup squad."

If the user confirms, or if they said "fix these audit issues" / "apply 5S fixes":
1. Load the workspace-cleanup squad from `~/.agent/squads/workspace-cleanup/SQUAD.md`
   (unified location — preferred over `~/.claude/squads/`)
2. Pass the findings as context:
   ```
   Findings from 5S audit [date]:
   Health Score: [score]/100 — [Grade]
   
   Critical:
   [list]
   
   Notable:
   [list]
   
   Suggestions:
   [list]
   ```
3. The squad's `workspace-auditor` (lead) will validate dependencies and plan fixes
4. `structure-fixer` applies structure fixes (AGENT.md/CLAUDE.md, frontmatter, renames)
5. `hygiene-cleaner` applies hygiene fixes (temp files, mirrors, cleanup)
6. `workspace-auditor` re-runs audit and reports new score

**If the user wants to fix manually instead**, list the specific actions needed
but do not execute them — the user can run each themselves or invoke the squad.

**If the user says "invoke squad" or "bring in the cleanup team"**, skip the
audit and load `~/.agent/squads/workspace-cleanup/SQUAD.md` directly — the squad
can run its own audit or accept prior findings.

---

# Code Project Audit

*(Triggered by `--code` flag or when user asks to audit a specific code project.)*

Switch to auditing a code project's dev-workspace hygiene. The project root is
the current working directory (or the project path the user specifies).

## Code Sort — Dead weight
Scan and report:
- Commented-out code blocks (more than 3 consecutive commented lines)
- TODO/FIXME/HACK comments older than the last sprint (rough heuristic: more
  than 30 days since the file was last touched)
- Clearly unused files: configuration files for tools not in package.json /
  requirements.txt / equivalent
- Stale feature branches (if a git repo: branches with no commits in 60+ days)
- `node_modules`, `__pycache__`, `.venv`, build artifacts in git-tracked paths
  (they belong in .gitignore)

## Code Set in Order — Structure
Check:
- Root-level `README.md` exists and is non-trivial (>5 lines)
- `src/` or equivalent source directory is clearly named
- Tests are co-located with source OR in a named `tests/` dir (consistent, not both)
- Config files at root are minimal — no more than 8 config files at the root level
  (config sprawl is a Set-in-Order failure)
- `.editorconfig` or equivalent formatting config present
- `CLAUDE.md` present (required for Claude Code projects)

## Code Shine — Freshness
Check:
- `package.json` / `requirements.txt` / `Gemfile` / `go.mod` dependencies —
  flag any that haven't been updated in 12+ months (stale = security risk)
- Lock files present (`package-lock.json`, `yarn.lock`, `poetry.lock`, etc.)
- `.env.example` present if `.env` files are used
- Last commit date — if no commits in 60+ days in an active project, flag

## Code Standardize — Standards
Check:
- Linter config present (`.eslintrc`, `pyproject.toml [tool.ruff]`, etc.)
- `.gitignore` present and non-trivial
- CI configuration present (`.github/workflows/`, `.gitlab-ci.yml`, etc.)
- `TASKS.md` present (required for Claude Code projects)

## Code output format

```
## 5S Code Audit — [project-name] — [date]

### Health Score: [score]/100 — [Grade]

[Same phase table as workspace audit]

[Findings by phase]

### Suggested next actions
1. ...
```

---

# Inbox Cleaner Mode

*(Triggered by `--inbox` flag or when user says "clean inbox", "inbox zero",
"process my inbox", "tidy inbox", or "daily inbox clean".)*

## Purpose

Review all items in portfolio and project inboxes, classify each item, and
recommend actions: file, convert, action, write llm-wiki entry, archive, or
discard. Validate YAML frontmatter compliance for markdown files.

## Folder Structure Standards

The inbox cleaner respects and maintains this folder hierarchy:

```
Projects/                              # Portfolio root
├── _archive/                          # Portfolio archive (at root only)
├── inbox/                             # Portfolio inbox
├── reports/                           # Portfolio reports
│   ├── ict-reports/                   # ICT (DCCEEW) reports
│   └── ctoc-reports/                  # CTOC consulting reports
├── <project-name>/                    # Individual projects
│   ├── _archive/                      # Project archive (at project root)
│   ├── inbox/                         # Project inbox (optional)
│   ├── reports/                       # Project reports
│   ├── artefacts/                     # Deliverables
│   ├── docs/                          # Documentation
│   └── ...
```

**Archive rules:**
- `_archive/` folders live at the **root** of Portfolio or Project only
- Never nest `_archive/` inside subfolders (artefacts/, docs/, etc.)
- Items move to archive when: completed, superseded, or source files after conversion

**Reports folders:**
- Portfolio: `reports/ict-reports/` (DCCEEW internal), `reports/ctoc-reports/` (consulting)
- Projects: `reports/` for project-specific reports

## Inbox Locations

Scan for inboxes at:
- `Projects/inbox/` — portfolio-level inbox
- `Projects/<project>/inbox/` — project-level inboxes

## Step 1: Inventory Inbox Contents

List all files in each discovered inbox. For each file, capture:
- Full path
- File name
- Extension/type
- Size
- Last modified date

Categorize by type:
| Category | Patterns |
|----------|----------|
| **Documents** | `.md`, `.docx`, `.pdf`, `.txt` |
| **Diagrams** | `.vsd`, `.vsdx`, `.drawio`, `.svg`, `.mmd` |
| **Data** | `.csv`, `.xlsx`, `.json`, `.xml` |
| **Media** | `.png`, `.jpg`, `.mp4`, `.mp3` |
| **Code/Config** | `.py`, `.sh`, `.bat`, `.yaml`, `.yml`, `.prompt.txt` |
| **Other** | Everything else |

## Step 2: Content Analysis

For each file, determine:

### 2.1 Project Affinity
Does this file belong to a specific project?
- **Check filename** for project indicators (project names, acronyms, client names)
- **Check content** (for text files) — read first 500 chars for project references
- **Check provenance** — is there a known source (email subject, download URL pattern)?

Decision matrix:
| Signal | Action |
|--------|--------|
| Clear project match | Recommend filing to that project's folder |
| Ambiguous / cross-cutting | Recommend portfolio-level filing or llm-wiki entry |
| No clear project | Keep in inbox pending classification |

### 2.2 Action Classification

Classify each item into one of these actions:

| Action | When to Use | Destination |
|--------|-------------|-------------|
| **FILE** | Completed work, reference material, deliverables | Project's `artefacts/`, `docs/`, `reports/`, or appropriate subfolder |
| **CONVERT** | File in wrong format (Visio → Mermaid, PDF → Markdown, etc.) | Converted version in appropriate location, archive original |
| **ACTION** | Requires follow-up work (incomplete draft, pending review) | TASKS.md entry + file to appropriate WIP location |
| **LLM-WIKI** | Knowledge worth preserving, patterns, research, decisions | `llm-wiki/knowledge/` or project wiki with proper frontmatter |
| **ARCHIVE** | Completed but worth keeping for reference | `_archive/` at portfolio or project root |
| **DISCARD** | Temp files, duplicates, outdated drafts | Delete (with confirmation) |

**Special handling for converted files:**
Files in `inbox/converted/` are already processed from their source format:
- Review content to determine proper destination
- Move to appropriate `artefacts/`, `docs/`, or `reports/` folder
- Archive the source file if still in inbox
- If content is knowledge-worthy, create LLM-wiki entry

### 2.3 Frontmatter Validation (Markdown files)

For all `.md` files, validate YAML frontmatter against STANDARDS.md:

**Required fields by context:**

| Context | Required Fields |
|---------|-----------------|
| Knowledge pages (llm-wiki) | `title`, `type`, `diataxis` |
| Project CLAUDE.md | `status`, `type` |
| General documents | `title` (recommended) |

**Validation rules:**
- `diataxis` must be one of: `tutorial`, `how-to`, `explanation`, `reference`
- `type` must be one of: `code`, `dcceew`, `personal`, `program`, `llm-wiki`, `knowledge`, `blueprint`, `concept`, `decision`, `research`, `reference`, `case-study`
- `status` must be one of: `active`, `paused`, `complete`, `archive`
- Dates should use `YYYY-MM-DD` format

**Flag as Notable:**
- Markdown files with missing required frontmatter
- Malformed YAML (syntax errors)
- Invalid enum values for `diataxis`, `type`, or `status`

## Step 3: Generate Recommendations

For each inbox item, produce:

```
### <filename>
- **Path:** <full-path>
- **Type:** <category>
- **Size:** <size>
- **Age:** <days since modified>
- **Recommended Action:** FILE | CONVERT | ACTION | LLM-WIKI | ARCHIVE | DISCARD
- **Destination:** <suggested path>
- **Rationale:** <why this action>
- **Frontmatter Issues:** <if any>
- **Suggested Tasks:** <if ACTION>
```

## Step 4: Batch Recommendations

Group recommendations by action type for efficient processing:

### Quick Wins (Auto-approve candidates)
- Temp files older than 7 days → DISCARD
- Empty files → DISCARD
- Duplicate filenames (same name, different locations) → Flag for review

### Filing Batch
- Items clearly belonging to specific projects → FILE to project folder
- Cross-cutting reference material → FILE to portfolio docs/reports
- Weekly status reports → FILE to `reports/ict-reports/` or `reports/ctoc-reports/`

### Conversion Queue
- Visio files → CONVERT to Mermaid (use vsd-to-mmd skill)
- PDFs without attached Markdown → CONVERT or extract text
- Prompt files → CONVERT to structured markdown

### Knowledge Capture
- Research notes → LLM-WIKI entry
- Process documentation → LLM-WIKI entry
- Decision records → LLM-WIKI entry

### Action Items
- Draft documents → ACTION (add to TASKS.md)
- Review materials → ACTION (schedule review)
- Unprocessed sources → ACTION (crawl/migrate)

## Step 5: Output Format

```
## 5S Inbox Cleaner — [date]

### Summary
| Action | Count | Est. Time |
|--------|-------|-----------|
| FILE | N | ~N min |
| CONVERT | N | ~N min |
| ACTION | N | ~N min |
| LLM-WIKI | N | ~N min |
| ARCHIVE | N | ~N min |
| DISCARD | N | Immediate |
| **Total Items** | **N** | **~N min** |

### Inboxes Scanned
- `Projects/inbox/` — N items
- `Projects/<project>/inbox/` — N items (per project)

---

### Quick Wins (Auto-approve)
[List of safe-to-delete items with confirmation checkbox]

### Filing Recommendations
[Grouped by target project/folder]

### Conversion Queue
[Items needing format conversion]

### Knowledge Capture
[Items for llm-wiki]

### Action Items
[Items requiring follow-up work]

---

### Frontmatter Validation Results
| File | Status | Issues |
|------|--------|--------|
| ... | ✓ Valid / ✗ Invalid | ... |

---

## Next Steps

Choose processing mode:
A. **Review each item** — I'll walk through recommendations one by one
B. **Apply quick wins** — Auto-delete temp files, then review the rest
C. **Batch by action** — Process all FILE items, then all CONVERT, etc.
D. **Schedule daily clean** — Set up recurring inbox cleaner
```

## Step 6: Execution Protocol

When user confirms actions:

### DISCARD
1. List files to delete
2. Confirm once
3. Delete and log

### FILE
1. Confirm destination path
2. Move file
3. Update any internal references

### CONVERT
1. Identify conversion skill needed (vsd-to-mmd, pdf-reading, etc.)
2. Perform conversion
3. Validate output
4. Move original to `_archive/` at portfolio or project root

### ACTION
1. Create TASKS.md entry
2. Move file to appropriate WIP location (or keep in inbox with note)
3. Set reminder if needed

### LLM-WIKI
1. Determine correct diataxis classification
2. Scaffold frontmatter
3. Write or update knowledge page
4. Link from index

### ARCHIVE
1. Confirm archive destination (`_archive/` at portfolio or project root)
2. Move file
3. Log in archive manifest if applicable

---

# Notes

- Read-only by default — scan and report, never change anything without confirmation
- Skip `.claude-resources/` and `.claude/` entirely — tooling, not workspace content
- Skip `_archive/` content — archived projects are intentionally out of scope
- Always re-read STANDARDS.md at the start of each run — never use a cached version
- Run all phases before presenting output — show a single unified report
- The health score is a trend tool: record it in TASKS.md or a note so future
  audits can show improvement (ask if Dale wants to log it)
- In code mode, never run shell commands that could modify files — read-only
  analysis only (use Glob and Grep, not bash scripts)
- Offer the `/schedule` skill to set up recurring runs after any 5S session
- Inbox cleaner respects separation of concerns: it identifies and recommends,
  but does not auto-execute destructive actions
- Archive folders must be at portfolio root or project root only — never nested

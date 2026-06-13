---
name: llm-wiki-crawl
description: >-
  Crawl folders for content to migrate into an _llm-wiki knowledge base.
  Use this skill when Dale says "crawl for wiki content", "find content to migrate",
  "scan for knowledge", "discover wiki sources", "what should go in llm-wiki",
  or when populating a new _llm-wiki with existing project content.

  This skill scans sibling directories, identifies migration candidates,
  and generates atoms from existing content.
---

# LLM-Wiki Crawl

## Purpose

Discover existing content in project folders and convert it to atomic claims
for the _llm-wiki knowledge base. Generates atoms from documents, extracts
factual claims, and prepares for compilation into wiki pages.

## When to Use

- After bootstrapping a new _llm-wiki (next step)
- When a project has accumulated documents to organize
- Periodic content audits to find orphaned knowledge
- Before archiving a project — extract knowledge first
- Converting existing knowledge/ pages to atoms/

## Steps / Process

### 1. Locate Wiki Root

Find the nearest _llm-wiki/ directory:
- Check current directory
- Check parent directories up to ~/Projects/
- Abort if no _llm-wiki found — suggest running llm-wiki-bootstrap first

### 2. Determine Crawl Scope

Crawl siblings of the wiki root:

| Wiki Location | Crawl Scope |
|---------------|-------------|
| `~/Projects/_llm-wiki/` | All `~/Projects/*/` except `_archive/`, `.claude/` |
| `~/Projects/<project>/_llm-wiki/` | All folders in `<project>/` except `_llm-wiki/` itself |

### 3. Scan for Content

Recursively scan for migration candidates by file extension:

| Category | Extensions | Knowledge Value |
|----------|------------|-----------------|
| Documents | `.md`, `.mdx` | High — primary knowledge format |
| Architecture | `.svg`, `.drawio`, `.excalidraw` | High — visual knowledge |
| Research | `.pdf`, `.html` | Medium — requires processing |
| Data | `.csv`, `.json`, `.yaml` | Medium — context dependent |
| Code docs | `README*`, `ARCHITECTURE*`, `DESIGN*` | High — design decisions |
| Transcripts | `.txt`, `.vtt` | Low-Medium — selective import |

### 4. Filter and Prioritize

Apply exclusion rules:
- Skip `node_modules/`, `.git/`, `__pycache__/`, `dist/`, `build/`
- Skip files matching `.gitignore` patterns
- Skip files < 100 bytes (likely empty)
- Skip files in `archive/`, `_archive/`, `old/`, `backup/` unless explicitly included

Prioritize by signals:
- Files with "design", "architecture", "decision", "adr" in name
- Files in `docs/`, `knowledge/`, `wiki/`, `research/` folders
- Recently modified files (activity = relevance)
- Files with frontmatter (already structured)

### 5. Extract Atomic Claims

For each candidate document, extract atomic claims:

**Process:**
1. Read document content
2. Identify factual statements, definitions, decisions
3. Convert each to atomic claim format
4. Determine branch (people/process/policy/platform/product)
5. Assign confidence based on source authority
6. Create atom file in appropriate branch folder

**Atom creation template:**
```yaml
---
id: atom-YYYYMMDD-NNN
claim: "[Single-sentence factual claim extracted from source]"
branch: [people|process|policy|platform|product]
tags: [extracted, from, content]
date: YYYY-MM-DD
sources: [raw/original-file.md]
author: extract
confidence: 0.7
status: draft
compile-to: [wiki/branch/topic]
---
```

### 6. Branch Classification

Assign each atom to a 5P branch:

| Content Type | Branch | Examples |
|--------------|--------|----------|
| Roles, org charts, team structures | `people` | "Product Owner reports to CIO" |
| Workflows, methodologies, governance | `process` | "Intake uses 3-gate model" |
| Standards, ethics, risk frameworks | `policy` | "All AI models require assessment" |
| Architecture, tools, infrastructure | `platform` | "VDE runs on Azure" |
| Products, roadmaps, use cases | `product` | "Wayfinder is priority 1" |
| Wiki structure, conventions | `meta` | "Atoms use kebab-case filenames" |

### 7. Generate Migration Report

Display crawl results:

```
Crawl complete: <wiki-path>

Scanned: <n> directories, <m> files
Atoms created: <count>

By branch:
  People:    <n> atoms (roles, capabilities, org)
  Process:   <n> atoms (workflows, governance)
  Policy:    <n> atoms (standards, ethics)
  Platform:  <n> atoms (architecture, tools)
  Product:   <n> atoms (portfolio, use cases)
  Meta:      <n> atoms (wiki structure)

Top sources:
  1. <path> → <n> atoms
  2. ...

Next steps:
  1. Review created atoms in atoms/<branch>/
  2. Edit atom frontmatter to set confidence and status
  3. Run: python scripts/compile-wiki.py
  4. Run: python scripts/generate-index.py
```

### 8. Convert Existing Knowledge Pages

If `knowledge/` folder exists from old structure:

```bash
python scripts/migrate-knowledge.py
```

This:
- Reads existing knowledge/ pages
- Decomposes into atomic claims
- Creates atoms in appropriate branches
- Preserves sources and metadata
- Marks original pages for archival

## Output Format

The crawl creates atoms in `atoms/<branch>/` folders.
Each atom is a standalone markdown file with YAML frontmatter.

## Separation of Concerns

This skill **extracts and creates atoms**. It does not:
- Compile wiki pages (that's llm-wiki-maintain)
- Validate the full wiki structure
- Delete source files
- Modify existing atoms

## Notes

- Crawl is additive — safe to run multiple times
- Re-running updates atoms from changed sources
- Use `--dry-run` to preview without creating atoms
- Large projects: crawl may take time; progress shown per file
- Exclusions respect .gitignore but also have built-in filters
- Confidence is heuristic — human review required

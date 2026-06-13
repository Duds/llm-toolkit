---
name: llm-wiki-bootstrap
description: >-
  Bootstrap a new llm-wiki knowledge base at portfolio or project level.
  Use this skill when Dale says "bootstrap llm-wiki", "create llm-wiki",
  "set up llm-wiki", "new llm-wiki", "initialize knowledge wiki",
  or when creating a knowledge project of type `llm-wiki`.

  This skill creates the complete folder structure, templates, and
  scaffolding for an LLM-optimized knowledge base following the
  Karpathy/cablate atomic patterns.
---

# LLM-Wiki Bootstrap

## Purpose

Scaffold a new llm-wiki knowledge base with the complete atom-first folder structure,
configuration files, and compilation tooling. Creates a knowledge base that
compiles atomic claims into queryable wiki pages.

## When to Use

- Creating a new knowledge project at portfolio level (`~/Projects/llm-wiki/`)
- Creating a project-level wiki (`~/Projects/<project>/llm-wiki/`)
- Converting an existing folder to llm-wiki structure
- Re-initializing a wiki that has lost its structure

## Steps / Process

### 1. Determine Scope

Ask which scope to create:

| Scope | Path | Use Case |
|-------|------|----------|
| **Portfolio** | `~/Projects/llm-wiki/` | Cross-project knowledge, shared patterns, reference material |
| **Project** | `~/Projects/<name>/llm-wiki/` | Project-specific knowledge, decisions, architecture |

Default to **project-level** if run from within a project directory that
contains a CLAUDE.md. Default to **portfolio-level** if run from `~/Projects/`.

### 2. Validate Target

Before creating:
- Check if target directory exists
- If it exists and contains files, confirm overwrite/reinitialize
- If `llm-wiki/` already exists with structure, abort with guidance

### 3. Create Folder Structure (Atom-First)

```
llm-wiki/
├── CLAUDE.md              # Wiki instructions and protocols
├── schema.md              # Entity types and validation rules
├── README.md              # Human-readable wiki guide
├── index.md               # AUTO-GENERATED — content catalog
├── log.md                 # Append-only chronology
├── raw/                   # IMMUTABLE — source files verbatim
│   ├── _provenance.md     # Source tracking registry
│   └── assets/            # Images, attachments from sources
├── atoms/                 # ATOMIC CLAIMS — source of truth
│   ├── _template.md       # Atom template
│   ├── people/            # 5P: People — roles, capabilities, org
│   ├── process/           # 5P: Process — workflows, governance
│   ├── policy/            # 5P: Policy — ethics, risk, standards
│   ├── platform/          # 5P: Platform — tooling, architecture
│   ├── product/           # 5P: Product — portfolio, use cases
│   └── meta/              # Wiki meta-atoms (structure, conventions)
├── wiki/                  # AUTO-GENERATED — compiled pages
│   ├── _README.md         # "This folder is auto-generated"
│   ├── people/
│   ├── process/
│   ├── policy/
│   ├── platform/
│   └── product/
└── scripts/               # Compilation tooling
    ├── extract-atoms.py   # Extract atoms from raw sources
    ├── compile-wiki.py    # Compile wiki pages from atoms
    ├── generate-index.py  # Generate index.md from wiki
    ├── validate.py        # Lint atoms, wiki, and cross-references
    └── migrate-knowledge.py  # Convert old knowledge/ to atoms/
```

**Atom-First Architecture:** Atoms are the source of truth. Wiki pages are compiled views.
Compilation pipeline: `raw/ → extract-atoms → atoms/ → compile-wiki → wiki/ → index`

### 4. Generate Core Files

**CLAUDE.md** — Wiki schema and instructions:
- YAML frontmatter with `status`, `type: knowledge`, `last-active`
- Atom schema: id format, required fields, confidence scoring
- Compilation protocol: how to process atoms → wiki
- Query protocol: how to search and retrieve
- Validation rules: lint requirements

**schema.md** — Complete schema documentation:
- Entity types (atoms, wiki pages, sources)
- Atom frontmatter specification
- Wiki page frontmatter specification
- Validation rules
- Compilation rules

**README.md** — Human guide:
- Wiki purpose and scope
- Atom-first concept explanation
- How to add content (create atoms, compile wiki)
- How to query content
- Compilation workflow

**scripts/** — Python compilation tools:
- `extract-atoms.py` — Extract atomic claims from raw sources
- `compile-wiki.py` — Compile wiki pages from atoms
- `generate-index.py` — Generate index.md from wiki
- `validate.py` — Lint atoms, wiki, and cross-references
- `migrate-knowledge.py` — Convert old knowledge/ to atoms/

### 5. Initialize Templates

**atoms/_template.md**:
```yaml
---
id: atom-YYYYMMDD-NNN
claim: "Single-sentence factual claim"
branch: people
tags: []
date: YYYY-MM-DD
sources: []
author: human
confidence: 0.8
status: draft
superseded-by: null
contradicts: []
reinforced-by: []
compile-to: []
---

# Claim Title

**Claim:** [Restate the claim]

**Evidence:**
- Source states: "..."

**Context:**
Additional background, caveats, or conditions.

**Related Atoms:**
- [[atom-YYYYMMDD-NNN]] — Related claim

**Wiki Pages:**
- [[wiki/branch/page]] — Compiled page
```

**wiki/_README.md**:
```markdown
# AUTO-GENERATED FOLDER

This folder contains compiled wiki pages generated from atoms/.

DO NOT EDIT FILES IN THIS FOLDER DIRECTLY.

To modify content:
1. Edit the source atoms in atoms/
2. Run: python scripts/compile-wiki.py
3. Run: python scripts/generate-index.py

The compilation process preserves your changes to atoms
and regenerates these wiki pages with updated content.
```

### 6. Initialize Provenance Tracking

Create `raw/_provenance.md` with headers:
- source_path — original location
- raw_filename — name in raw/
- ingest_date — when copied
- ingest_context — why this source matters
- processed_to — atoms/ paths (if processed)

### 7. Execute Bootstrap

Run the bootstrap:

```bash
# Using the skill directly
python scripts/bootstrap.py [OPTIONS] [PATH]

Options:
  -n, --name NAME       Wiki name (default: derived from path)
  -d, --desc DESC       Wiki description
  --dry-run             Show what would be created, don't create

Examples:
  # Portfolio-level wiki
  python scripts/bootstrap.py ~/Projects/llm-wiki

  # Project-level wiki
  python scripts/bootstrap.py ~/Projects/my-project/llm-wiki
```

### 8. Report and Next Steps

Output summary:
```
LLM-Wiki bootstrapped: <path>

Structure created:
  • CLAUDE.md — wiki schema and instructions
  • schema.md — entity types and validation rules
  • README.md — human guide
  • index.md — content catalog (auto-generated)
  • raw/ — immutable sources
  • atoms/ — atomic claims (source of truth)
  • wiki/ — compiled pages (auto-generated)
  • scripts/ — compilation tooling

Atom-first architecture:
  Atoms are the source of truth. Wiki pages are compiled views.
  Pipeline: raw/ → extract-atoms → atoms/ → compile-wiki → wiki/ → index

Next steps:
  1. Review CLAUDE.md and customize schema for your domain
  2. Add first source to raw/ and process to atoms/
  3. Run: python scripts/compile-wiki.py
  4. Run: python scripts/generate-index.py
```

## Output Format

After bootstrapping, display:
- Full path to created wiki
- List of created files and folders
- Quick-start next steps
- Reference to llm-wiki-crawl for content discovery

## Atom Schema

Every atom must have:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique ID: `atom-YYYYMMDD-NNN` |
| `claim` | string | Yes | Single-sentence factual claim |
| `branch` | string | Yes | One of: people, process, policy, platform, product, meta |
| `tags` | list | No | Classification tags |
| `date` | date | Yes | Creation date: `YYYY-MM-DD` |
| `sources` | list | No | Raw source files |
| `author` | string | Yes | `extract`, `human`, or `synthesis` |
| `confidence` | float | Yes | 0.0-1.0 confidence score |
| `status` | string | Yes | `current`, `draft`, `superseded`, `disputed`, `archived` |
| `superseded-by` | string | No | ID of newer atom (if superseded) |
| `contradicts` | list | No | IDs of contradictory atoms |
| `reinforced-by` | list | No | IDs of supporting atoms |
| `compile-to` | list | No | Wiki pages to compile this atom into |

### Confidence Scoring

| Score | Meaning | Use When |
|-------|---------|----------|
| 0.95-1.0 | Certain | Explicitly stated in authoritative source |
| 0.80-0.94 | High confidence | Stated clearly, single source |
| 0.60-0.79 | Medium | Implied, inferred, or multiple conflicting sources |
| 0.40-0.59 | Low | Speculative, outdated, or weak evidence |
| 0.00-0.39 | Very low | Disputed, deprecated, placeholder |

## Separation of Concerns

This skill **only** handles initial scaffolding. Content operations
are handled by companion skills:

| Skill | Purpose |
|-------|---------|
| `llm-wiki-bootstrap` | Create folder structure and templates (this skill) |
| `llm-wiki-crawl` | Discover and catalog existing content for migration |
| `llm-wiki-maintain` | Health checks, compilation, validation |

## Notes

- Safe to re-run: will not overwrite existing files
- Portfolio-level wiki is for cross-cutting concerns
- Project-level wiki is for project-specific knowledge
- Both can coexist — portfolio wiki links to project wikis
- Follows Karpathy pattern: compile once, query forever
- Follows cablate pattern: atoms as primary store, wiki as derived cache
- Atom-first enables confidence tracking, contradiction detection, and fine-grained provenance

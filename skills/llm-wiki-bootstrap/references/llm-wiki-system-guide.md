# LLM-Wiki System Guide

Complete guide to the llm-wiki knowledge management system.

## Overview

The llm-wiki system provides a structured approach to building LLM-optimized knowledge bases. It follows the **compile once, query forever** philosophy: invest effort in organizing and processing information at ingest time, then retrieve efficiently forever after.

## Architecture

Based on research from three leading approaches:

| Source | Key Contribution |
|--------|------------------|
| [Karpathy's llm-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) | Raw → knowledge pipeline, immutable sources, compiled wiki |
| [cablate's llm-atomic-wiki](https://github.com/cablate/llm-atomic-wiki) | Atomic claims, provenance tracking, derived cache |
| [rohitg00's llm-wiki](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2) | Schema-driven, event hooks, confidence scoring |

## Folder Structure

```
llm-wiki/
├── CLAUDE.md              # Wiki schema and instructions (LLM reads this first)
├── README.md              # Human-readable wiki guide
├── MIGRATION.md           # Source material tracking manifest
├── index.md               # Auto-generated content catalog
├── log.md                 # Append-only chronology
├── raw/                   # Immutable source files
│   ├── _provenance.md     # Source tracking registry
│   └── assets/            # Images, attachments from sources
├── knowledge/             # Processed, LLM-readable pages
│   ├── _template.md       # Template for new knowledge pages
│   └── README.md          # Knowledge organization guide
└── atoms/                 # Atomic claims (optional, for advanced use)
    └── README.md          # Atom structure documentation
```

### Folder Purposes

| Folder | Purpose | Mutable? | Notes |
|--------|---------|----------|-------|
| `raw/` | Original sources verbatim | **No** — never edit after ingest | PDFs, HTML, Markdown, images |
| `knowledge/` | Synthesized understanding | **Yes** — evolves with learning | One topic per file, cross-linked |
| `atoms/` | Granular claims (optional) | **No** — immutable, versioned | Advanced: confidence, supersession |

## The Three Skills

The system is split into three separate skills following **separation of concerns**:

### 1. llm-wiki-bootstrap

**Purpose:** Create initial folder structure and templates

**When to use:**
- Starting a new knowledge base
- Re-initializing a corrupted wiki
- Creating portfolio-level or project-level wikis

**What it does:**
- Creates folder structure
- Generates CLAUDE.md, README.md, MIGRATION.md
- Sets up index.md, log.md
- Creates templates in knowledge/
- Initializes provenance tracking

**What it doesn't do:**
- Copy any content
- Discover existing files
- Modify existing files

### 2. llm-wiki-crawl

**Purpose:** Discover existing content for migration

**When to use:**
- After bootstrapping a new wiki
- Periodic content audits
- Before archiving a project
- Finding orphaned knowledge

**What it does:**
- Scans sibling directories
- Identifies migration candidates by type
- Generates MIGRATION.md entries
- Suggests knowledge structure
- Prioritizes by value

**What it doesn't do:**
- Move or copy files
- Modify source files
- Create knowledge pages

### 3. llm-wiki-maintain

**Purpose:** Keep wiki healthy through validation

**When to use:**
- Weekly/monthly maintenance
- Before releases or handoffs
- When wiki feels cluttered
- After bulk imports

**What it does:**
- Updates index.md from contents
- Finds orphaned pages
- Validates cross-references
- Checks frontmatter completeness
- Detects stale content
- Generates health reports

**What it doesn't do:**
- Create new pages
- Delete content (except empty folders with permission)
- Modify page content (except index.md)

## Workflow

### Starting a New Wiki

```
1. llm-wiki-bootstrap → Create structure
2. llm-wiki-crawl → Discover content
3. Manual → Review MIGRATION.md, migrate high-priority items
4. llm-wiki-maintain → Validate and index
```

### Adding Content

```
1. Copy source to raw/
2. Add entry to raw/_provenance.md
3. Process into knowledge/ page
4. Update index.md (or run maintain)
```

### Maintenance Schedule

| Frequency | Action | Skill |
|-----------|--------|-------|
| Weekly | Quick index update | maintain |
| Monthly | Full health check | maintain |
| Quarterly | Content audit | crawl |
| Before handoff | Complete validation | maintain |
| After bulk import | Orphan and link check | maintain |

## Portfolio vs Project Level

### Portfolio-Level Wiki

**Location:** `~/Projects/llm-wiki/`

**Scope:** Cross-project knowledge, shared patterns, reference material

**Contains:**
- Architecture patterns used across projects
- Shared integration approaches
- Common tooling and workflows
- Research applicable to multiple projects

### Project-Level Wiki

**Location:** `~/Projects/<project>/llm-wiki/`

**Scope:** Project-specific knowledge, decisions, architecture

**Contains:**
- Project architecture and design
- Decision records (ADRs)
- Case studies and retrospectives
- Project-specific research

### Coexistence

Both levels can coexist:
- Portfolio wiki links to project wikis
- Project wikis reference portfolio patterns
- No duplication — cross-link instead

## Content Types

### Knowledge Page Types

| Type | Description | Example |
|------|-------------|---------|
| `blueprint` | Service designs, architecture docs | API architecture, deployment diagrams |
| `concept` | Explanations, patterns, principles | "How RAG works", "API design patterns" |
| `decision` | ADRs, decision records | "Why we chose PostgreSQL" |
| `research` | User research, findings | Interview synthesis, survey results |
| `reference` | API docs, specifications | OpenAPI specs, schema definitions |
| `case-study` | Project retrospectives, PoCs | "Wayfinder PoC learnings" |

### Frontmatter Schema

**Required:**
```yaml
---
title: "Human Readable Title"
date: YYYY-MM-DD
---
```

**Recommended:**
```yaml
---
title: "Human Readable Title"
date: YYYY-MM-DD
tags: [tag1, tag2, tag3]
sources: [raw/source-filename.md]
confidence: high  # high | medium | low
status: current   # current | stale | superseded
---
```

## Best Practices

### Do

- **Cite sources** — every claim should trace back to raw/
- **Cross-link** — use [[wikilinks]] to connect related pages
- **One topic per file** — keeps pages focused and linkable
- **Use kebab-case** — for all filenames
- **Keep raw/ immutable** — never edit sources after ingest
- **Update index** — run maintain after significant changes
- **Tag appropriately** — makes content discoverable

### Don't

- **Don't duplicate** — link to existing pages instead
- **Don't edit raw/** — process into knowledge/ instead
- **Don't skip frontmatter** — required for indexing
- **Don't let orphans persist** — link or archive them
- **Don't ignore broken links** — fix or remove them

## Migration Protocol

The formal process for moving content into the wiki:

1. **Copy** source verbatim to `raw/`
2. **Add** entry to `raw/_provenance.md`
3. **Create** knowledge page with synthesized content
4. **Cite** sources (point back to raw/)
5. **Cross-link** to related pages
6. **Tag** for discoverability
7. **Update** `MIGRATION.md` status to `done`

## Query Protocol

How to find information in the wiki:

1. **Start** with `index.md` — browse by folder or tag
2. **Follow** `[[wikilinks]]` to related pages
3. **Search** with grep/ripgrep if needed
4. **Check** `raw/` for original sources
5. **Validate** confidence and status before using

## Comparison with Other Systems

| Feature | llm-wiki | Traditional Wiki | Vector RAG |
|---------|----------|------------------|------------|
| Structure | Compiled, hierarchical | Flat, searchable | Indexed, retrieved |
| Sources | Immutable, tracked | Often lost | Chunked, context lost |
| Cross-links | Explicit wikilinks | Sometimes | Rare |
| Confidence | Scored per-claim | Unspecified | Unspecified |
| LLM-optimized | Yes | Partial | Yes |
| Human-readable | Yes | Yes | No |

## Troubleshooting

### Wiki feels hard to navigate
- Run `llm-wiki-maintain` to update index
- Check for orphaned pages
- Review folder structure

### Not sure if content is current
- Check `status` in frontmatter
- Review `date` field
- Compare with source in `raw/`

### Too many files in knowledge/
- Consider subfolders by topic
- Archive superseded content
- Use tags for cross-cutting concerns

### Raw sources are messy
- That's okay — raw/ is immutable
- Clean up happens in knowledge/
- Focus processing effort on high-value sources

## Further Reading

- Original patterns:
  - [Karpathy's llm-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
  - [cablate's llm-atomic-wiki](https://github.com/cablate/llm-atomic-wiki)
  - [rohitg00's llm-wiki gist](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2)

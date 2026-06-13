---
status: active
type: knowledge
last-active: {{DATE}}
---

# {{WIKI_NAME}}

LLM-optimized knowledge base. Compile information once at ingest time,
query forever.

## Schema

### Folder Purposes

| Folder | Purpose | Immutable |
|--------|---------|-----------|
| `raw/` | Source files verbatim from original locations | Yes — never edit after ingest |
| `knowledge/` | Processed, LLM-readable markdown pages | No — evolve as understanding improves |
| `atoms/` | Atomic claims (optional advanced use) | Yes — immutable, versioned |

### Entity Types

**Source** (`raw/`)
- Any file type: PDF, HTML, Markdown, images, diagrams
- Original filename preserved (with date prefix if needed for disambiguation)
- Provenance tracked in `raw/_provenance.md`

**Page** (`knowledge/`)
- Markdown with YAML frontmatter
- One topic per file
- Cross-references as `[[page-name]]` wikilinks
- Citations point back to `raw/` sources

**Atom** (`atoms/` — optional)
- Single claim per file
- YAML frontmatter with confidence, sources, tags
- Used for advanced knowledge graphs

### Naming Conventions

- **Folders:** kebab-case, lowercase
- **Pages:** kebab-case.md (e.g., `api-design-patterns.md`)
- **Sources:** original name + optional YYYY-MM-DD- prefix
- **No spaces** in any filenames

### Frontmatter Schema

**Knowledge pages:**
```yaml
---
title: "Human Readable Title"
date: YYYY-MM-DD
tags: [tag1, tag2]
sources: [raw/source-filename.pdf]
confidence: high  # high | medium | low
status: current   # current | stale | superseded
---
```

**Atoms (optional):**
```yaml
---
claim: "Single-sentence claim"
date: YYYY-MM-DD
tags: [tag1, tag2]
sources: [raw/source.md]
confidence: 0.9   # 0-1 score
superseded-by: atoms/newer-claim.md  # if applicable
---
```

## Ingest Protocol

How to process raw → knowledge:

1. **Copy** source to `raw/` (no edits)
2. **Add** entry to `raw/_provenance.md`
3. **Read** source and extract key information
4. **Create** knowledge page with synthesized content
5. **Cite** sources using `[[raw/source-name]]` or inline references
6. **Cross-link** to related knowledge pages
7. **Tag** appropriately for discoverability
8. **Update** `index.md` (or run maintenance)

## Query Protocol

How to search and retrieve:

1. **Start** with `index.md` — browse by folder or tag
2. **Follow** `[[wikilinks]]` to related pages
3. **Search** file contents with grep/ripgrep if needed
4. **Check** `raw/` for original sources if knowledge is unclear
5. **Validate** confidence and status before using information

## Lint Rules

Validation requirements:

- Every knowledge page must have `title` and `date` frontmatter
- Every knowledge page should cite at least one `raw/` source
- No orphaned pages (should be reachable from index or linked)
- No broken `[[wikilinks]]`
- No edits to `raw/` after initial ingest

## Session Management

- **Start:** Read `CLAUDE.md` (this file) → `index.md` → relevant pages
- **End:** Update `log.md` with session summary if significant changes made

## Claude Instructions

<!-- Add domain-specific guidance here as wiki grows -->

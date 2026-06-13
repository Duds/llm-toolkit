---
title: "Schema"
last-updated: {{DATE}}
---

# Schema — {{WIKI_NAME}}

Structural rules and validation requirements. Rarely changes.

## Entity types

| Entity | Location | Format | Immutable |
|---|---|---|---|
| **Source** | `raw/<file>` | Any (PDF, DOCX, MD, HTML, image) | Yes — never edit after ingest |
| **Atom** | `atoms/<branch>/<slug>.md` | Markdown + YAML frontmatter | ID immutable; status/links can update |
| **Wiki page** | `wiki/<branch-or-page-type>/<slug>.md` | Markdown + YAML frontmatter | Generated — never hand-edit |

## Branches (`atoms/<branch>/`)

| Branch | Covers |
|---|---|
| `people` | Roles, capabilities, org structure, individuals |
| `process` | Workflows, methodologies, governance |
| `policy` | Standards, ethics, risk frameworks, statutory basis |
| `platform` | Architecture, tools, infrastructure |
| `product` | Products, services, roadmaps, use cases |
| `meta` | Wiki structure, conventions, the system itself |

## Page types (`wiki/<page-type>/`)

Orthogonal to branches. For content that crosscuts.

| Page type | Covers |
|---|---|
| `synthesis` | Cross-branch analysis combining atoms from multiple branches |
| `comparisons` | Side-by-side comparisons (option A vs B, before vs after) |
| `queries` | Saved answers from `/llm-wiki query --save` |

## Atom frontmatter

Required:

```yaml
---
id: atom-YYYYMMDD-NNN
claim: "Single-sentence factual claim"
branch: people | process | policy | platform | product | meta
date: YYYY-MM-DD
author: extract | human | synthesis
confidence: 0.85
status: current | draft | superseded | disputed | archived
---
```

Optional:

```yaml
tags: [tag-one, tag-two]
sources: [raw/source-filename.pdf]
superseded-by: atom-YYYYMMDD-NNN
contradicts: [atom-YYYYMMDD-NNN]
reinforced-by: [atom-YYYYMMDD-NNN]
compile-to: [wiki/process/topic-name]
```

## Wiki page frontmatter

```yaml
---
title: "Page Title"
type: synthesis | comparison | branch-page | query
date-compiled: YYYY-MM-DD
atoms: [atom-YYYYMMDD-NNN, atom-YYYYMMDD-NNN]
confidence: high | medium | low  # rolled up from constituent atoms
---
```

## Confidence scoring

| Score | Meaning |
|---|---|
| 0.95–1.00 | Certain — explicitly stated in authoritative source |
| 0.80–0.94 | High — stated clearly, no contradiction |
| 0.60–0.79 | Medium — implied, inferred, or multi-source nuance |
| 0.40–0.59 | Low — speculative or weak evidence |
| 0.00–0.39 | Very low — disputed, deprecated, placeholder |

## Status lifecycle

```
draft → current → superseded → archived
                ↘ disputed ↗
```

- `draft` — created but unreviewed. Default from `crawl`.
- `current` — reviewed, accurate now.
- `superseded` — replaced by newer atom (`superseded-by:` required).
- `disputed` — contradicted by another atom, unresolved (`contradicts:` required).
- `archived` — historical, removed from compiled wiki.

## Naming conventions

- **Folders:** kebab-case, lowercase.
- **Atom files:** kebab-case, derived from claim. Max 60 chars.
- **Wiki pages:** kebab-case, descriptive noun phrase.
- **Raw files:** preserve original name when possible; replace spaces with hyphens.

## Wikilink forms

- `[[atom-YYYYMMDD-NNN]]` — atom ID
- `[[wiki/branch/page-name]]` — compiled wiki page
- `[[raw/source-name]]` — raw source file
- `[[../_llm-wiki/atom-YYYYMMDD-NNN]]` — cross-wiki (project → portfolio or reverse)

## Lint rules

Critical (block compile):
- Atom missing required frontmatter field.
- Atom with no `sources:` and `branch:` not `meta`.
- Atom with invalid `branch` value.
- Atom with non-unique `id`.
- Atom ID format invalid (not `atom-YYYYMMDD-NNN`).

Warning (allow compile, flag in report):
- Atom with `confidence < 0.6` and `status: current`.
- Atom with `status: superseded` missing `superseded-by:`.
- Atom with `contradicts:` not bidirectional.
- Orphaned atoms (not linked from any wiki page or other atom).
- Broken wikilinks.
- Branch frontmatter doesn't match folder location.
- Stale atoms (status `current`, unchanged 90+ days).

## Validation

Run `/llm-wiki lint` to validate all rules. Run `/llm-wiki report` for a health summary.

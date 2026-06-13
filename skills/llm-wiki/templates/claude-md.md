---
title: "{{WIKI_NAME}} — LLM Instructions"
type: knowledge-base
last-updated: {{DATE}}
---

# {{WIKI_NAME}}

LLM instructions for operating inside this wiki. Read this first.

## Architecture

This is an Obsidian-compatible, atom-first knowledge base.

- **`atoms/<branch>/`** — atomic claims, source of truth. Edit these.
- **`wiki/`** — compiled views, derived from atoms. Never edit directly.
- **`raw/`** — immutable source files. Never edit after ingest.
- **`purpose.md`** — what this wiki is for. Read on every operation.
- **`schema.md`** — structural rules. Reference for validation.
- **`index.md`** — auto-generated content catalog.

Atoms are markdown files with YAML frontmatter. One claim per atom. Wiki pages are markdown files compiled from atoms.

## Operations

Use the `/llm-wiki` skill for all wiki operations:

| Need to... | Use |
|---|---|
| Process a single source into atoms | `/llm-wiki ingest <path>` |
| Scan folders for content to ingest | `/llm-wiki crawl <path>` |
| Refresh wiki pages from atoms | `/llm-wiki compile` |
| Ask a question grounded in the wiki | `/llm-wiki query "<question>"` |
| Validate atoms and links | `/llm-wiki lint` |
| Get a health report | `/llm-wiki report` |

Don't write atoms directly without going through the skill — `ingest` does two-step chain-of-thought extraction that catches contradictions and assigns proper confidence.

## Atom rules

- **One claim per atom.** Resist combining.
- **Every claim cites a source** (`sources: [raw/...]`). Exception: `branch: meta` atoms.
- **Confidence is a number** (0.0–1.0), not a label. See `schema.md`.
- **IDs are immutable.** `atom-YYYYMMDD-NNN`. Once written, never change.
- **Supersede with a new atom + `superseded-by:`.** Never delete or rewrite.
- **Wikilinks are typed:** `[[atom-id]]`, `[[wiki/branch/page]]`, `[[raw/source]]`.

## Wiki page rules

- **Wiki pages are generated.** Run `/llm-wiki compile` to refresh.
- **Don't hand-edit `wiki/`.** Edit atoms instead.
- **Wikilinks in wiki pages preserve the typed forms** so Obsidian + LLM both resolve them.

## Raw source rules

- **Copy to `raw/` verbatim.** Don't clean up.
- **Add a row to `raw/_provenance.md`** at ingest time.
- **Never edit after ingest.** If source changes, copy new version with date suffix.

## Reading order at session start

1. This file (CLAUDE.md).
2. `purpose.md` — to align with the wiki's intent.
3. `index.md` — to know what's already in here.
4. Relevant atoms or wiki pages for the task at hand.

## Branch classification

Six branches: `people`, `process`, `policy`, `platform`, `product`, `meta`. See `schema.md` and the 5p-branches reference in the skill.

When in doubt, work down this tree: meta → policy → people → platform → product → process.

## Things this wiki is NOT

- Not a chat log. Conversations live elsewhere.
- Not a project tracker. TASKS.md and sprint plans live in the project root.
- Not a documentation site. README.md is for humans browsing the vault.
- Not a journal. Daily notes aren't part of the skill.

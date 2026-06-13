# {{WIKI_NAME}}

{{WIKI_DESCRIPTION}}

## Structure

| Section | Path | What's in it |
|---------|------|--------------|
| Raw Sources | [`raw/`](raw/) | Immutable source files (PDFs, HTML, original docs) |
| Knowledge | [`knowledge/`](knowledge/) | Processed, LLM-readable pages |
| Atoms (optional) | [`atoms/`](atoms/) | Atomic claims for advanced use |

## Quick Start

### Adding Content

1. **Copy source** to `raw/` (no edits, preserve original)
2. **Add provenance** to `raw/_provenance.md`
3. **Process** into `knowledge/` page(s)
4. **Update** `index.md` (or run maintenance)

### Finding Content

1. **Browse** [`index.md`](index.md) — organized by folder and tag
2. **Follow links** — pages use `[[wikilink]]` syntax
3. **Check sources** — citations point to `raw/` for originals

## Migration Tracking

Source material migrations are tracked in [`MIGRATION.md`](MIGRATION.md).

## Wiki Maintenance

Run periodic maintenance to keep the wiki healthy:
- Update index
- Check for orphaned pages
- Validate cross-links
- Flag stale content

## Principles

This wiki follows the **compile once, query forever** pattern:

- **Raw sources are immutable** — never edit after ingest
- **Knowledge pages are living** — evolve as understanding improves
- **Everything is cited** — trace claims back to sources
- **Cross-linked** — navigate by topic, not just hierarchy

Based on patterns from:
- [Karpathy's llm-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [cablate's llm-atomic-wiki](https://github.com/cablate/llm-atomic-wiki)
- [rohitg00's llm-wiki](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2)

# NOTICE

This skill adapts patterns and ideas from several open-source projects.

## Skill architecture

The umbrella-router pattern (single SKILL.md dispatching to per-command `reference/*.md` files, shared `scripts/` for context loading and pin/unpin, `command-metadata.json` as a single source of truth) is adapted from Anthropic's `impeccable` skill (Apache 2.0).

## Wiki architecture

The atom-first knowledge base architecture combines ideas from three llm-wiki implementations:

- **Andrej Karpathy's llm-wiki gist** — the original "compile once, query forever" pattern. Raw sources → wiki pages, immutable sources, three core operations (ingest, query, lint).
  <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>

- **cablate's llm-atomic-wiki** — atoms as primary store, wiki as derived cache. Atomic claims, provenance tracking, confidence scoring.
  <https://github.com/cablate/llm-atomic-wiki>

- **nashsu's llm_wiki** (GPL v3) — two-step chain-of-thought ingest, `purpose.md` vs `schema.md` split, scenario templates, SHA256 incremental cache, constrained-action review queue, page-type folders (entities/concepts/synthesis/comparisons/queries), saved-query pages. Patterns adapted, no code reused (GPL is incompatible with this skill's license).
  <https://github.com/nashsu/llm_wiki>

## 5P taxonomy

The people/process/policy/platform/product/meta branch classification is Dale Rogers' own framing for DCCEEW and consulting knowledge bases.

## License

Apache 2.0. See LICENSE in the repository root.

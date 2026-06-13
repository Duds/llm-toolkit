# {{WIKI_NAME}}

An llm-wiki: an Obsidian-compatible, atom-first knowledge base.

## What this is

Knowledge captured as atomic claims (`atoms/`), compiled into queryable wiki pages (`wiki/`), grounded in immutable raw sources (`raw/`).

The directory is an Obsidian vault — open the folder in Obsidian and everything works: wikilinks resolve, the graph view shows cross-references, search hits markdown content directly.

## How to use it

### Reading

1. Start with `index.md` — auto-generated catalog of wiki pages.
2. Browse `wiki/` for compiled topics, organised by branch or page type.
3. Dig into `atoms/` for individual claims with citations.
4. Sources live in `raw/` if you need to check the original.

### Writing

Don't write atoms by hand. Use the `/llm-wiki` skill, which runs a two-step chain-of-thought extraction that produces better-quality atoms than single-pass:

```
/llm-wiki ingest raw/<file>      # process a single source
/llm-wiki crawl <folder>          # scan a folder for candidates
/llm-wiki compile                 # refresh wiki pages
/llm-wiki query "<question>"      # ask a question, get a cited answer
/llm-wiki lint                    # validate structure
/llm-wiki report                  # health check
```

## File layout

```
{{WIKI_NAME}}/
├── purpose.md             # What this wiki is for — read on every operation
├── schema.md              # Structural rules
├── CLAUDE.md              # LLM instructions for this vault
├── README.md              # This file
├── index.md               # Auto-generated content catalog
├── log.md                 # Append-only chronology
├── raw/                   # Immutable sources
├── atoms/                 # Atomic claims (source of truth)
│   ├── people/            # Roles, org structure
│   ├── process/           # Workflows, governance
│   ├── policy/            # Standards, statutes
│   ├── platform/          # Systems, architecture
│   ├── product/           # Products, services, roadmaps
│   └── meta/              # Wiki conventions
├── wiki/                  # Compiled views (auto-generated)
│   ├── overview.md        # Global summary
│   ├── people/
│   ├── process/
│   ├── policy/
│   ├── platform/
│   ├── product/
│   ├── synthesis/         # Cross-branch analysis
│   ├── comparisons/       # Side-by-side
│   └── queries/           # Saved query answers
├── .obsidian/             # Obsidian vault config
└── .llm-wiki/             # Skill machinery (cache, queues)
```

## Principles

- **Atoms first.** Atoms are the source of truth. Wiki pages are derived. Edit atoms, not wiki pages.
- **Raw is immutable.** Once a source is copied to `raw/`, it never changes.
- **Every claim cites.** Atoms without sources are invalid (except `branch: meta`).
- **Confidence is a number.** Score 0.0–1.0. No "high"/"medium" labels in atom frontmatter.
- **Supersede, don't overwrite.** When a fact changes, create a new atom and link it via `superseded-by`.

## Maintenance

- After ingest: `/llm-wiki compile` to refresh wiki pages.
- Weekly: `/llm-wiki lint` to catch broken links and stale atoms.
- Monthly: `/llm-wiki report` for health and gap analysis.
- Before handoff: lint, compile, commit (if using git).

## Editing Obsidian config

`.obsidian/` is yours — change theme, install plugins, set up daily notes. The skill writes a minimal default on first bootstrap and doesn't touch the directory afterwards.

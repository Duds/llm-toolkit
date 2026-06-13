# Obsidian — vault conventions, wikilinks, configuration

Foundational reference. Loaded by `bootstrap` (writes `.obsidian/` config) and any command that reads or writes wikilinks. Defines how this wiki interoperates with Obsidian.

## The wiki is an Obsidian vault

Every llm-wiki directory is a valid Obsidian vault. Opening the wiki root in Obsidian Just Works:

- File browser shows the folder structure.
- Graph view shows atom + wiki + raw cross-references.
- Backlinks panel works for any atom.
- Search hits markdown content directly.
- Frontmatter is parsed and displayed.

Bootstrap writes `.obsidian/` with a small set of sensible defaults. Beyond that, Dale can install plugins, change theme, etc. — the skill doesn't manage Obsidian's UI state.

## Wikilink rules

Every wiki-internal reference uses a wikilink. Plain markdown links to wiki content are wrong.

### Three forms

```markdown
[[atom-20260423-008]]
[[atom-20260423-008|short label]]

[[wiki/process/accountability-model]]
[[wiki/process/accountability-model|the model]]

[[raw/intake-policy-v3.pdf]]
[[raw/intake-policy-v3.pdf|Intake Policy v3]]
```

Targets, in order of preference when multiple resolve:

1. **`atom-*`**: atom ID, resolves to `atoms/<branch>/<slug>.md` (any branch — Obsidian finds it).
2. **`wiki/...`**: compiled wiki page, resolves to `wiki/<branch>/<page>.md`.
3. **`raw/...`**: raw source file, resolves to `raw/<filename>`.

### What NOT to do

- `[link](atoms/process/foo.md)` — plain markdown. Obsidian renders it but backlinks break. Always use wikilinks.
- `[[foo]]` — bare slug, ambiguous. Use the typed form.
- `[[Atom 20260423 008]]` — spaces or wrong case. IDs are exact.
- `[[wiki/process/accountability model]]` — spaces. Wiki page slugs are kebab-case.
- `[[raw/Intake Policy v3.pdf]]` — spaces. Raw filenames are kebab-case or original (whichever the file actually is on disk).

### Cross-wiki references

Portfolio wiki referencing a project atom:

```markdown
[[<project-name>/atom-20260423-008]]
```

Project wiki referencing a portfolio atom:

```markdown
[[../_llm-wiki/atom-20260423-008]]
```

This relies on Obsidian's vault-relative resolution. Both work in compiled wiki pages because the compiler preserves wikilinks verbatim.

## File naming

- **Folders**: kebab-case, lowercase, no spaces.
- **Atom files**: kebab-case, derived from claim, max 60 chars.
- **Wiki pages**: kebab-case, descriptive noun phrase.
- **Raw files**: keep the original filename when possible. If the original has spaces, the ingest tool replaces them with hyphens and notes the rename in `raw/_provenance.md`.

## Frontmatter conventions

Obsidian parses YAML frontmatter. To play well:

- **Top of file, between `---` lines.** Always.
- **Quote strings containing `:` or `#`.** Required for valid YAML.
- **Use lists, not comma strings, for arrays.** `tags: [a, b]` not `tags: a, b`.
- **Dates as `YYYY-MM-DD`.** No quotes needed.
- **Numbers unquoted.** `confidence: 0.85` not `confidence: "0.85"`.

The Obsidian Properties panel will render these as editable fields if the user enables it.

## `.obsidian/` directory

Bootstrap writes:

```
.obsidian/
├── app.json          # Show wikilinks unrendered when not in preview mode
├── appearance.json   # Default theme, font size
├── core-plugins.json # Enable backlinks, outgoing-links, graph
└── workspace.json    # Default layout
```

These are recommendations, not enforcement. Dale can override anything. The skill never overwrites `.obsidian/` after the initial bootstrap.

If `.obsidian/` already exists when bootstrap runs, the bootstrap leaves it alone and notes "preserved existing .obsidian/ config" in the output.

## What the skill does not manage

- **Obsidian plugins.** Dale installs what he wants. The skill doesn't depend on any plugin.
- **Themes.** Dale's choice.
- **Daily notes.** Out of scope — this skill is for compiled knowledge, not journaling.
- **Templater / Dataview queries.** Atoms and wiki pages are static markdown by design. Dataview queries on top are fine but unsupported by the skill itself.

## Sync compatibility

Atoms and wiki pages are plain markdown. They sync cleanly via:

- Git (recommended for project-level wikis).
- Obsidian Sync.
- iCloud Drive, Dropbox, OneDrive (with normal markdown-sync caveats).

Bootstrap does not initialise git. If Dale wants version control, run `git init` after bootstrap. The skill's compile step is deterministic enough that wiki/ regeneration produces minimal diffs.

## Search

Use Obsidian's native search for human queries. Use `/llm-wiki query` for LLM-grounded synthesis. The two are complementary:

- Obsidian search: find atoms by keyword or tag, fast.
- `/llm-wiki query`: ask a question, get a synthesized answer with citations.

The query command reads atoms and wiki pages with ripgrep, not vector embeddings — Obsidian-compatible markdown is the primary index.

## Anti-patterns

- **Hand-editing wiki pages in Obsidian.** Tempting but wrong. Wiki/ is compiled. Edit atoms instead, then run `/llm-wiki compile`.
- **Renaming atom files.** The ID is in the frontmatter, but the filename is what wikilinks resolve to from outside Obsidian. Keep the filename matching the claim.
- **Using `tags:` for branches.** Branch is a frontmatter field, not a tag. Tags are for fine-grained classification on top of the 5P taxonomy.
- **Linking to non-existent atom IDs.** `lint` flags broken wikilinks. Either create the atom or remove the link.

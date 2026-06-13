# Bootstrap — create a new llm-wiki

Loaded when the user invokes `/llm-wiki bootstrap`. Scaffolds the wiki structure, writes templates, configures the Obsidian vault, and seeds `purpose.md` from a scenario template.

## When to run

- Setting up a new wiki, project-level (`<project>/_llm-wiki/`) or portfolio-level (`~/Projects/_llm-wiki/`).
- Re-initialising a wiki that's missing files. Safe to re-run: existing files are preserved.
- Converting an existing folder into a wiki — bootstrap adds machinery without touching existing markdown.

## When NOT to run

- The wiki already exists and is healthy. Use `/llm-wiki crawl` to add content, `/llm-wiki lint` to check structure.
- The user wants to migrate from another knowledge tool. Bootstrap first, then `/llm-wiki crawl` against the old folder.

## Steps

### 1. Determine scope and path

Ask the user one question if the path is ambiguous:

```
Where should the wiki live?
  - Portfolio level: ~/Projects/_llm-wiki/  (cross-project, shared patterns)
  - Project level:   ./_llm-wiki/            (this project's knowledge)
  - Custom path:     (user supplies)
```

Default rules (skip the question if unambiguous):

- If cwd is `~/Projects/`, default to portfolio (`~/Projects/_llm-wiki/`).
- If cwd is inside a project directory with `CLAUDE.md`, default to project-level (`./_llm-wiki/`).
- If `--path` flag was supplied, use it without asking.

### 2. Determine scenario

Five scenarios, each preconfigures `purpose.md`:

| Scenario | Use for |
|---|---|
| `research` | Synthesising a body of literature, papers, or external sources |
| `consulting` | Capturing client engagements, recommendations, lessons learned |
| `design` | Service or system design knowledge bases |
| `general` | Catch-all personal knowledge base |

If `--scenario <name>` was supplied, use it. Otherwise ask:

```
Which scenario fits this wiki best?
  - research
  - consulting
  - design
  - general
```

The scenario only seeds `purpose.md`. Everything else is identical across scenarios. Dale can edit `purpose.md` afterwards regardless.

### 3. Validate target

Before creating anything:

- If target directory doesn't exist, fine — bootstrap creates it.
- If it exists and is empty, fine.
- If it exists with files but no `schema.md`, treat as "adding wiki to existing folder" — proceed.
- If it has `schema.md` already, abort with a clear message: *"Wiki already exists at this path. Run `/llm-wiki lint` to check health, or use `--reinit` to overwrite templates (existing content is preserved)."*

### 4. Run the bootstrap script

```bash
python scripts/bootstrap.py <target-path> --scenario <scenario> [--name <name>]
```

The script:

- Creates the directory structure (atoms/<branch>/, wiki/<branch>/, wiki/<page-type>/, raw/, raw/assets/, templates/, .obsidian/, .llm-wiki/).
- Writes templates from `templates/` into the wiki: `CLAUDE.md`, `schema.md`, `README.md`, `purpose.md` (scenario-specific), `index.md`, `raw/_provenance.md`, `atoms/_template.md`.
- Writes the `.obsidian/` config (app.json, appearance.json, core-plugins.json).
- Writes `wiki/_README.md` warning humans not to hand-edit compiled pages.

The script is idempotent: existing files are preserved, missing files are filled in.

### 5. Report back

Output:

```
LLM-wiki bootstrapped at <absolute-path>

Scope: <portfolio|project>
Scenario: <scenario>

Created:
  - purpose.md       (seed from <scenario> template — edit to make it yours)
  - schema.md        (validation rules; rarely need to change)
  - CLAUDE.md        (LLM instructions when working inside the wiki)
  - README.md        (human guide)
  - index.md         (auto-generated content catalog, empty for now)
  - atoms/<branch>/  (6 branches: people, process, policy, platform, product, meta)
  - wiki/<branch>/   (compiled pages, empty for now)
  - raw/             (immutable sources)
  - .obsidian/       (vault configuration)

Next steps:
  1. Edit purpose.md — at minimum, write 3-7 specific key questions.
  2. Add your first source to raw/ and run /llm-wiki ingest raw/<file>.
  3. Or scan an existing folder: /llm-wiki crawl <path>.

Optional:
  - Pin frequently used commands: node scripts/pin.mjs pin query
```

If any files were preserved (existed before bootstrap), call that out:

```
Preserved (already existed):
  - .obsidian/app.json (your Obsidian config)
  - purpose.md (existing — not overwritten; review against the scenario template if needed)
```

### 6. Nudge purpose.md edit

The scenario template gives `purpose.md` a starting shape, but its key questions are placeholders. After bootstrap, prompt the user:

*"`purpose.md` is seeded but the key questions are placeholders. Want to write them now (~5 min), or come back to it before the first ingest?"*

This is a soft nudge, not a blocker. The user can ignore and proceed.

## Flags

- `--path <path>` — target path. Default: see step 1.
- `--scenario <name>` — one of `research | consulting | design | dcceew | general`. Default: ask.
- `--name <name>` — wiki name (used in templates). Default: derived from path.
- `--reinit` — overwrite template files even if they exist. Atoms, wiki pages, and raw sources are still preserved.
- `--dry-run` — print what would be created, create nothing.

## Examples

```bash
# Portfolio-level research wiki
/llm-wiki bootstrap ~/Projects/_llm-wiki --scenario research

# Dry run
/llm-wiki bootstrap --dry-run

# Reinit just the templates
/llm-wiki bootstrap ./_llm-wiki --reinit
```

## Anti-patterns

- **Bootstrapping inside an existing wiki.** If the path already has `schema.md`, abort. Don't try to merge.
- **Skipping the scenario prompt.** The seeded `purpose.md` matters. A generic placeholder produces generic atoms forever.
- **Editing the script's template files in `templates/`.** Those are skill defaults. Edit the wiki's own copy after bootstrap.
- **Running bootstrap to "refresh" templates.** Use `--reinit` explicitly; the default behaviour preserves existing files.
- **Choosing a path that already has a `.obsidian/` directory and assuming bootstrap will configure it.** Bootstrap preserves existing `.obsidian/` and notes the preservation in the output.

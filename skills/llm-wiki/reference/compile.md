# Compile — atom → wiki page generation

Loaded when the user invokes `/llm-wiki compile`. Regenerates `wiki/` pages from current atoms, plus `index.md` and `overview.md`. The wiki is a derived cache; atoms are the source of truth.

## When to run

- After `/llm-wiki ingest` wrote new atoms (and you've reviewed them).
- After hand-editing atoms (changed status, confidence, supersession).
- After a bulk crawl produced many new draft atoms (review first, then compile).
- Periodically — weekly or before a handoff — to keep wiki pages fresh.

## When NOT to run

- The wiki doesn't exist yet. Run `/llm-wiki bootstrap` first.
- Atoms are mid-review (still `status: draft` and you're triaging). Compile will pull drafts in if their `status` allows — see filter rules.
- You want to validate, not generate. Use `/llm-wiki lint`.
- You want a health summary, not regenerated pages. Use `/llm-wiki report`.

## Steps

### 0. Preconditions

Wiki root resolved. The compiler needs:

- `schema.md` loaded — for confidence rollup and wiki frontmatter rules.
- [reference/atoms.md](atoms.md) loaded — for atom frontmatter parsing.
- [reference/5p-branches.md](5p-branches.md) — for branch validation.

If `lint` has critical errors, **stop and surface them**:

```
Compile blocked — lint reports {{N}} critical errors:
  - atoms/process/foo.md: invalid branch 'governance'
  - atoms/platform/bar.md: missing required field `confidence`

Fix these before compile, or run with --force to compile valid atoms and skip the broken ones.
```

### 1. Discover atoms

Walk `atoms/<branch>/` for every branch. For each atom:

- Parse YAML frontmatter.
- Skip atoms whose status is `archived` or `superseded`.
- Include `draft` atoms — but note in the compiled page footer.
- Include `disputed` atoms — but flag them inline.
- Skip files starting with `_` (templates, drafts, READMEs).

Cache parsed atom metadata in memory. The full body is read on-demand when a page needs it.

### 2. Group atoms by target page

For each atom, determine which wiki pages it compiles into:

1. **Explicit:** the atom's `compile-to:` list, if non-empty.
2. **Inferred:** if `compile-to:` is absent, infer one target:
   - `wiki/<branch>/<topic-slug>.md` where `<topic-slug>` comes from the atom's primary tag (first tag) or, if no tags, from a clustering heuristic on the claim text.

Atoms that don't fit any topic page end up on `wiki/<branch>/_other.md`. That's a smell — flag the count in the final report. Atoms with `compile-to: []` set explicitly to empty are excluded from compilation (rare; usually means the atom exists only as a building block for other atoms).

### 3. Detect contradictions and contradictions

For each target page, build the candidate atom set. Within that set:

- Check pairwise `contradicts:` relationships.
- Check for atoms making opposing claims on the same subject (heuristic — use the claim text similarity + opposition markers).

If contradictions exist, the wiki page renders both sides with explicit framing. See "Page body structure" below.

### 4. Stop gate before destructive change

Before writing anything, compare what's about to be regenerated against what exists. Surface:

- New pages that will be created.
- Existing pages that will be updated (atom count changed, or content changed).
- Existing pages that will be unchanged.
- **Hand-edited pages that will block.** A wiki page lacking the auto-generated frontmatter marker (`type:` field) is treated as user-authored. Refuse to overwrite without `--force`.
- Pages that will be deleted (no atoms compile to them anymore).

Show the user:

```
Compile plan:

  New pages ({{N}}):
    + wiki/process/intake-three-gate-model.md (3 atoms)
    + wiki/platform/pas-sunset-roadmap.md (5 atoms)

  Updated pages ({{N}}):
    ~ wiki/policy/epbc-statutory-functions.md (was 4 atoms, now 7)
    ~ wiki/synthesis/system-coverage-gaps.md (regenerated)

  Unchanged ({{N}}): wiki/...

  BLOCKED — hand-edited pages (no auto-gen marker):
    ! wiki/product/wayfinder-roadmap.md — pass --force to overwrite, or move to wiki-archive/

  Deletions ({{N}}):
    - wiki/process/old-process.md (no current atoms compile here)

Proceed? [y/N]
```

Default deny on blocked pages. Default allow on new/updated/unchanged. Deletions also need confirmation — surface them above the prompt, don't auto-delete.

### 5. Generate page body

For each target page (excluding blocked / cancelled):

#### Frontmatter

```yaml
---
title: "{{Page Title}}"
type: branch-page  # or synthesis | comparison | query
date-compiled: {{today}}
atoms: [atom-..., atom-...]  # in order they appear in the body
confidence: high | medium | low  # rolled up from atoms
status: current  # if all atoms current; else 'mixed'
---
```

The `type` and `date-compiled` fields are the auto-generated marker. They're how the next compile run knows it's safe to overwrite.

#### Page body structure

```markdown
{{Brief lead — 2-3 sentences synthesizing what the atoms collectively say.}}

## {{Topic section, if multiple groups}}

{{Prose synthesis. Cite atoms inline with both [[atom-id]] AND numeric [N] for human readability.}}

{{If contradictions exist within this page, render them explicitly:}}

> **Contradictory atoms on this topic:**
>
> - [[atom-20260423-008]] [1] claims X.
> - [[atom-20260423-015]] [2] claims not-X.
>
> Resolution pending review.

## Atoms

Numbered list, in citation order. Each entry: number, atom title, [[atom-id]], confidence, source.

1. **{{Atom title}}** — [[atom-20260423-008]] (confidence 0.85) — `raw/{{source}}`
2. **{{Atom title}}** — [[atom-20260423-015]] (confidence 0.70) — `raw/{{source}}`

## Sources

Deduplicated list of raw sources cited by atoms on this page.

- `[[raw/intake-policy-v3.pdf]]`
- `[[raw/epbc-act-extract.md]]`

## Drafts

{{Only render this section if any included atoms have status: draft.}}

The following atoms are still drafts — their claims are not yet reviewed:

- [[atom-20260521-007]] — claim summary
```

#### Confidence rollup

The page-level `confidence` field aggregates from atoms:

- `high` if all atoms ≥ 0.80.
- `medium` if median atom ≥ 0.60.
- `low` if median atom < 0.60.

This is a rough signal for human scanning, not a precise statistic.

### 6. Refresh index.md and overview.md

After all wiki pages are written, regenerate:

**`index.md`** — catalog of wiki pages. Frontmatter:

```yaml
---
title: "Index"
type: auto-generated
last-updated: {{today}}
atom-count: {{total}}
wiki-page-count: {{total}}
---
```

Body sections:

- Pages by branch (links + atom count per page).
- Pages by page-type (synthesis, comparisons, queries).
- Tag index — for each tag, list pages that use it.
- Recent updates — top 10 wiki pages by `date-compiled`.
- Confidence distribution summary.

**`overview.md`** — global synthesis. Frontmatter:

```yaml
---
title: "Overview"
type: auto-generated
last-updated: {{today}}
---
```

Body — a synthesized narrative that:

- Opens with the purpose.md's "What this wiki is for" paragraph.
- For each branch, summarizes the dominant claims in 1-2 sentences (cite top atoms by confidence).
- Surfaces unresolved contradictions across the wiki.
- Surfaces purpose.md key questions and links to the pages that address each one.
- Lists knowledge gaps — purpose questions with no atom coverage.

Overview is regenerated every compile, and it's the wiki's elevator pitch. Keep it under ~400 lines.

### 7. Write the auto-generated readme

Ensure `wiki/_README.md` exists with the "DO NOT EDIT" notice (from templates). If it's missing, write it. If it's been edited, leave it — the user added something deliberately.

### 8. Append to log.md

One line:

```
## YYYY-MM-DD

- Compiled wiki: {{N pages written}} ({{N new}}, {{N updated}}, {{N deleted}}). {{N}} atoms across {{N}} branches.
```

### 9. Report

Final output:

```
Compiled {{N}} wiki pages from {{N}} atoms.

By branch:
  people:   {{N}} pages
  process:  {{N}} pages
  policy:   {{N}} pages
  platform: {{N}} pages
  product:  {{N}} pages

Page types:
  synthesis:   {{N}} pages
  comparisons: {{N}} pages
  queries:     {{N}} pages

Changes:
  Created: {{N}}
  Updated: {{N}}
  Deleted: {{N}}
  Skipped (hand-edited): {{N}}

Index and overview regenerated.

Flags:
  {{N}} unresolved contradictions — see /llm-wiki report.
  {{N}} draft atoms appear in compiled pages — review and promote.
  {{N}} atoms compiled to wiki/<branch>/_other.md (no clear topic page).

Next steps:
  - Open the wiki in Obsidian — backlinks and graph view now reflect new pages.
  - Run /llm-wiki lint to validate cross-references.
  - Run /llm-wiki report for a full health view.
```

## Flags

- `--force` — overwrite hand-edited wiki pages (no auto-gen marker). Destructive; confirms once via prompt unless `--yes`.
- `--branch <branch>` — compile only one branch. Other branches and `synthesis/`/`comparisons/`/`queries/` are unchanged.
- `--page <wiki/path/page>` — compile one specific page. Useful for targeted updates after an atom edit.
- `--dry-run` — show the plan, write nothing.
- `--yes` — skip the stop gate. Discouraged. Only use in scripted automation where you trust the diff.
- `--keep-drafts` — include `draft`-status atoms in compiled pages (default behaviour). `--no-drafts` excludes them.

## Auto-generated marker

The compiler determines whether a wiki page is safe to overwrite by checking frontmatter:

- **Safe to overwrite:** frontmatter contains `type:` (one of `branch-page`, `synthesis`, `comparison`, `query`, `auto-generated`) AND `date-compiled:`.
- **Block:** frontmatter is missing those fields, OR the file has no frontmatter at all.

If the user wants a wiki page to be hand-edited, they should:

1. Edit the page.
2. Remove the `type:` and `date-compiled:` fields (or move to `wiki-archive/<name>.md`).

Next compile will then skip it. Better practice: write hand-edited content in `wiki-archive/`, leaving `wiki/` exclusively to the compiler.

## Idempotency

Two consecutive compiles with no atom changes should produce zero file changes. The compiler is deterministic — same inputs produce byte-identical outputs. This matters for git diffs: noisy regenerations destroy history.

If consecutive compiles produce diffs without atom changes, that's a bug. Most common cause: non-deterministic ordering (sort atoms by `id`, not by directory iteration order).

## Anti-patterns

- **Hand-editing wiki pages.** Wiki pages are regenerated; edits will be lost. Edit atoms instead. If you must capture commentary, put it in `wiki-archive/<page-name>.md` (a parallel folder the compiler ignores).

- **Compiling on every atom save.** Compilation is intentional, not automatic. Batch atom edits, then compile.

- **Running compile to "publish" drafts.** Compile includes drafts by default (flagged in page footer). Promoting drafts to `current` is a separate, deliberate edit to the atom's frontmatter.

- **Overwriting with `--force` to "fix" a hand-edited page.** Wrong. Move the hand-edits to `wiki-archive/` first, then compile. `--force` is for rare cases where a wiki page lost its frontmatter marker accidentally.

- **Compiling against unfiltered atoms.** If `lint` reports critical errors, fix them first. Compiling around broken atoms produces wiki pages that won't make sense.

- **Treating overview.md as documentation.** It's auto-generated. If you want hand-written wiki-level documentation, that's `README.md`. Overview synthesizes from current atoms — it changes every compile.

- **Including superseded atoms.** They're explicitly skipped. If a wiki page needs to show historical claims, that's a special case — render it via a hand-authored page in `wiki-archive/` or surface it through `report`.

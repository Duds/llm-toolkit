# TASKS — llm-wiki skill

Next steps for the `llm-wiki` umbrella skill at `~/.claude/skills/llm-wiki/`.

The skill is feature-complete on the design we set out: 7 sub-commands referenced, 3 with working Python scripts (`bootstrap`, `lint`, `compile`), 1 with Node helpers (`ingest-helpers.mjs`), 4 LLM-driven (`crawl`, `ingest`, `query`, `report`).

## Pre-flight

- [ ] Decide what to do with the surviving flat `llm-wiki-bootstrap` skill — its description still overlaps with the umbrella's `bootstrap` sub-command, so both will register as candidates on bootstrap-related phrases. Pick one: narrow its description so it triggers only on highly specific phrasing, or delete it once the umbrella's bootstrap is trusted in field use.
- [ ] Field-test the umbrella against a real wiki. The test wikis used so far were ephemeral. The first real-use rough edges (Obsidian frontmatter rendering, wikilink resolution at scale, `compile` performance on 100+ atoms) only surface against actual content. Pick the smallest real wiki — probably a project-level one — for the first run.

## Discoverability

- [ ] Mirror the "Scripts" appendix style from `reference/ingest.md` into `reference/compile.md`, `reference/lint.md`, and `reference/bootstrap.md`. Three references now have working scripts but only `ingest.md` documents them inline. Without the appendix, the LLM has to guess which script to invoke at which step.
- [ ] Pin the high-frequency sub-commands so they become first-class slash commands: `node scripts/pin.mjs pin query` (daily use), `node scripts/pin.mjs pin ingest` (frequent), `node scripts/pin.mjs pin lint` (pre-commit). Leave `bootstrap` unpinned — it's once-per-wiki. Verify each pinned shortcut appears in the skill listing.

## Optional — quality and ergonomics

- [ ] Refactor the YAML frontmatter parser shared between `lint.py` and `compile.py` into a single `_atomio.py` module (currently duplicated ~80 lines). Low priority — duplication is small, parser is well-tested, both scripts pass their suites. Touch only when one of them gets a bug fix.
- [ ] Fix the duplicate-id ordering quirk in `lint.py` — when two atoms share an ID, the message currently flags the second-encountered file as the violator (cosmetically odd). Both files should be flagged. Minor; the report is still actionable.
- [ ] Add tag → page-title mapping so tags like `pas` compile to `PAS.md` with the title `PAS` (not `Pas`). Today's `page_title_for` capitalises kebab-case words, which mangles all-caps acronyms. Either a tag→title override file or a small acronym dictionary in `compile.py`.

## Optional — bigger lifts

- [ ] Write helpers for the remaining LLM-driven sub-commands if usage shows they're worth it:
  - `report.py` — health-score aggregator. Lowest leverage; LLM does the analysis fine inline.
  - `crawl.py` — filesystem walker with the filter cascade. Useful for portfolio-scale scans.
  - `query.py` — would mostly wrap ripgrep with citation-format helpers. Probably not worth a separate script.
- [ ] Update `templates/schema.md` and `templates/claude-md.md` if real-world ingest surfaces atom-frontmatter shapes the current schema doesn't accommodate. Don't pre-edit; let real use drive changes.

## Done (record)

- 2026-05-21 — Umbrella skill scaffolded (33 files: SKILL.md, NOTICE.md, 11 reference files, 8 scripts, 15 templates).
- 2026-05-21 — `bootstrap.py` written and verified (cross-platform, idempotent, scenario templates).
- 2026-05-21 — `lint.py` written and verified (10 critical rules, 10 warning rules, JSON output, compile gate via exit codes).
- 2026-05-21 — `compile.py` written and verified (auto-gen frontmatter marker, idempotent writes, lint guard, index + overview regeneration).
- 2026-05-21 — `ingest-helpers.mjs` written and verified (8 subcommands: sha256, cache-get, cache-set, next-atom-id, slug, write-atom, append-provenance, append-log).
- 2026-05-21 — Two flat skills removed (`llm-wiki-crawl`, `llm-wiki-maintain`); umbrella replaces both.
- 2026-05-21 — Scripts appendix added to `reference/ingest.md`.

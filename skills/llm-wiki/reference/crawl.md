# Crawl — discover candidate content for ingest

Loaded when the user invokes `/llm-wiki crawl [path]`. Scans sibling folders or a named path for content that might belong in the wiki. Doesn't write atoms directly — instead, queues candidates in `atoms/_review/` for human triage with constrained actions.

Crawl is discovery, not processing. For single-source ingest with full two-step chain-of-thought, use `/llm-wiki ingest`.

## When to run

- After bootstrapping a new wiki — find existing project content to migrate.
- Periodic content audits — what's accumulated that hasn't made it into the wiki?
- Before archiving a project — pull knowledge out of the project folder before it goes cold.
- After major restructuring — re-scan to catch newly relevant content.

## When NOT to run

- A single specific source needs processing. Use `/llm-wiki ingest raw/<file>` — it does two-step CoT and produces higher-quality atoms.
- The folder is huge and unfiltered (e.g. a 50GB downloads directory). Pre-filter first; crawl is best on focused project trees.
- You want validation, not discovery. Use `/llm-wiki lint`.
- The wiki doesn't exist. Run `/llm-wiki bootstrap` first.

## Steps

### 0. Preconditions

Wiki root must exist. The crawler needs:

- `purpose.md` loaded — candidates are prioritised against the wiki's intent. Without purpose, prioritisation is generic.
- `schema.md` loaded — for branch validation.
- [reference/atoms.md](atoms.md), [reference/5p-branches.md](5p-branches.md) — for classification logic.
- The wiki's `.llm-wiki/ingest-cache.json` — to skip sources that are already ingested unchanged.

### 1. Determine scope

The `path` argument tells the crawler where to look:

| Argument | Scope |
|---|---|
| (none) — wiki is portfolio-level | Scan `~/Projects/*/` siblings, excluding `_archive/`, `.claude-resources/`, the wiki itself |
| (none) — wiki is project-level | Scan the parent project directory, excluding `_llm-wiki/` itself |
| `<path>` | Scan the given path explicitly |

If the resolved scope is empty or unreadable, abort with a clear message.

### 2. Walk the filesystem

Recurse the scope. For each file encountered, run the **filter cascade** below in order. First reject wins; if nothing rejects, the file becomes a candidate.

**Hard excludes (skip without examination):**

- `.git/`, `node_modules/`, `__pycache__/`, `.venv/`, `venv/`, `dist/`, `build/`, `.next/`, `target/`, `out/`, `.cache/`
- `_archive/`, `_backup/`, `archive/`, `backup/`, `old/`
- `_inbox/`, `_working/`, `_scripts/`, `_data/`, `_reports/`, `_plans/` — content lifecycle folders; move to `raw/` before ingestion
- Hidden directories (starts with `.`) except `.claude/skills/` references — but skip `.claude/` too in general scan
- The wiki's own root and all its subdirectories

**Soft excludes (skip unless `--include-archived`):**

- Files with `archived`, `deprecated`, `obsolete` in the path
- Files modified > 2 years ago

**Extension filter:**

| Category | Extensions | Action |
|---|---|---|
| Documents | `.md`, `.mdx` | Strong candidate |
| Office | `.pdf`, `.docx`, `.pptx`, `.xlsx` | Strong candidate — needs format-specific reader at ingest time |
| Visual / structural | `.svg`, `.drawio`, `.excalidraw`, `.vsd`, `.vsdx` | Candidate — convert via vsd-to-mmd or markitdown at ingest |
| Web | `.html`, `.htm` | Candidate |
| Data | `.csv`, `.json`, `.yaml`, `.yml`, `.toml` | Candidate only if name suggests structure docs (schema, config docs); skip generic data dumps |
| Code | `.py`, `.js`, `.ts`, `.go`, etc. | Skip — source code isn't atoms |
| Other | everything else | Skip |

**Size filter:**

- Skip files < 200 bytes (likely empty or near-empty).
- Files > 5 MB get flagged but not auto-rejected — they need explicit user permission to ingest.

**Cache check:**

- Compute SHA256.
- Look up in `.llm-wiki/ingest-cache.json`.
- If present and SHA matches, mark as "already ingested" and skip (don't queue for review again).

### 3. Score and prioritise candidates

For each candidate that survived the filter, compute a relevance score. Higher scores rank earlier in the review queue.

**Score contributors (additive):**

| Signal | Score |
|---|---|
| Filename contains `architecture`, `design`, `decision`, `adr`, `spec`, `policy`, `standard` | +3 |
| In a folder named `docs/`, `knowledge/`, `wiki/`, `research/`, `decisions/`, `adrs/` | +2 |
| Has YAML frontmatter (already structured) | +2 |
| Modified within last 90 days | +1 |
| Modified within last 30 days | +2 (in addition to the 90-day bump) |
| Folder path contains a word that appears in purpose.md key questions | +3 |
| Filename contains a word that appears in purpose.md key questions | +2 |
| File is in scope's root or one level deep | +1 |
| File is 5+ levels deep | -1 |
| Filename starts with `README`, `INDEX`, `CHANGELOG` | +1 |
| Filename starts with `_` (template-like) | -3 |

The exact weights matter less than the principle: signal beats brute force. The user reviews the queue in score order, so a noisy queue is worse than a small high-quality one.

### 4. Suggest a branch for each candidate

Use the folder path and filename as a classification hint. The decision tree from [5p-branches.md](5p-branches.md) is authoritative — but folder names are useful shortcuts:

| Folder hint | Suggested branch |
|---|---|
| `architecture/`, `systems/`, `infrastructure/`, `tools/` | `platform` |
| `decisions/`, `adrs/`, `processes/`, `workflows/`, `governance/` | `process` |
| `policy/`, `standards/`, `compliance/`, `legal/`, `regulatory/` | `policy` |
| `people/`, `org/`, `team/`, `roles/` | `people` |
| `product/`, `roadmap/`, `release/`, `features/` | `product` |
| `meta/`, `conventions/`, `style/` (about the wiki) | `meta` |
| (anything else) | leave blank — human decides at review |

Branch suggestion is a hint, never a final classification.

### 5. Write the review queue

For each candidate (highest score first, up to a configurable cap):

Write to `atoms/_review/<YYYY-MM-DD>-<NNN>-<slug>.md`:

```yaml
---
id: review-YYYYMMDD-NNN
status: pending-review
source: <absolute path>
size-bytes: <N>
sha256: <hash>
last-modified: <iso date>
score: <calculated score>
suggested-branch: <branch or null>
suggested-action: ingest | deep-research | skip
suggested-tags: [...]
score-breakdown:
  - "+3 architecture in folder name"
  - "+2 has frontmatter"
  - "+1 modified last 30 days"
---

# Review: <filename>

**Source:** `<absolute path>` ({{N}} bytes, modified {{date}})

**Suggested action:** {{action}}

{{Brief preview — first 300 chars of the file if it's text, or "Binary content, requires conversion" for office docs}}

**Binary guard:** Before reading any file for preview, check its extension and/or magic bytes:
- `.pdf` — never read raw bytes. Use `"Binary content, requires conversion"`.
- `.docx`, `.pptx`, `.xlsx` — never read raw bytes. Use `"Binary content, requires conversion"`.
- `.md`, `.html`, `.txt`, `.csv`, `.json`, `.yaml`, `.yml` — safe to read first 300 chars.
- If uncertain, probe the first few bytes for binary signatures (`%PDF`, `PK\x03\x04`, `\xD0\xCF\x11\xE0`). If binary, use `"Binary content, requires conversion"`.

**Never embed raw binary into a markdown file.** A review file containing `%PDF` or `/FlateDecode` is malformed and will be flagged by `lint` as a critical error.

## Suggested classification

- **Branch:** {{branch or "needs human decision"}}
- **Tags:** {{suggested tags}}
- **Confidence in classification:** {{high|medium|low}}

## Decision

Pick one action and edit this file's frontmatter `suggested-action` to confirm, or delete this review file to reject:

- `ingest` — Run `/llm-wiki ingest <source>` to do full two-step extraction.
- `deep-research` — Source needs external context before ingest; flag for follow-up.
- `skip` — Not appropriate for the wiki (acknowledged, won't be re-suggested).

Reviewed items are removed from the queue on next crawl, regardless of decision.
```

**Constrained actions** are deliberate — `ingest | deep-research | skip` are the only three. Free-form actions invite the model to hallucinate workflows that don't exist.

### 6. Update the skip list

Items the user marked `suggested-action: skip` are remembered so the next crawl doesn't re-suggest them. Append the source's SHA to `.llm-wiki/crawl-skiplist.json`:

```json
{
  "skipped": [
    {"sha256": "abc123...", "source": "/path/to/skipped.md", "decided-at": "2026-05-21"}
  ]
}
```

If the source changes (different SHA), it's re-considered. The skip is keyed on content, not path.

### 7. Report

```
Crawled <scope>: <N> directories scanned, <M> files examined.

Filtered out:
  - <N> hard excludes (build artefacts, archives)
  - <N> already ingested (SHA match)
  - <N> in skip list
  - <N> size / extension filters

Candidates queued (top 30 of <N>):

  Score  Branch     Source
  -----  --------   ------
   11    platform   /path/to/architecture/system-overview.md
    9    policy     /path/to/decisions/2024-data-retention.md
    ...

Suggested actions:
  - ingest: <N>
  - deep-research: <N>
  - skip: <N>

Queue location: atoms/_review/

Next steps:
  1. Review entries in atoms/_review/ (open in Obsidian).
  2. For each entry: edit `suggested-action` in frontmatter to confirm, or delete to reject.
  3. Run /llm-wiki ingest <source> for confirmed items (one at a time for full CoT).
  4. Next crawl will skip resolved items automatically.
```

## Flags

- `--path <path>` — override the scope. Default: see step 1.
- `--max-queue <N>` — cap how many items get written to the review queue. Default 30.
- `--min-score <N>` — minimum relevance score to make the queue. Default 3.
- `--include-archived` — include files in `archive/`, `old/`, etc.
- `--include-old` — include files modified > 2 years ago.
- `--branch <branch>` — only consider candidates suggested for this branch.
- `--dry-run` — show the candidate list, write no review files.

## Anti-patterns

- **Writing atoms directly to `atoms/<branch>/`.** Crawl never does this. Review is the human-in-the-loop gate that prevents low-quality automated atoms from polluting the wiki.

- **Crawling on every session start.** Crawl is a periodic action, not a heartbeat. Run it on intent — new project added, content audit, archival prep.

- **Ignoring the skip list.** If the user said skip, don't re-suggest. The skip list is the user's "no" — respect it across crawls.

- **Massive review queues.** A queue of 200 candidates is unreviewable. Set `--max-queue 30` (the default) and trust prioritisation. The user can re-crawl after working through the first batch.

- **Free-form `suggested-action` values.** Three actions: `ingest`, `deep-research`, `skip`. Anything else means the model invented a workflow. Refuse to write atoms under non-standard actions.

- **Inferring atoms directly from filenames.** Crawl identifies candidates; `ingest` produces atoms. The two are different jobs — don't collapse them.

- **Skipping purpose.md.** Without purpose-question matching, the prioritisation degrades to generic signals (recency, structure). Purpose-aligned candidates should always rank above generic candidates.

- **Walking the full filesystem.** Hard excludes are non-negotiable. Walking `node_modules/` is a waste of time and produces noise.

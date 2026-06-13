# Lint — validate atoms, wikilinks, frontmatter

Loaded when the user invokes `/llm-wiki lint`. Pure mechanical validation. Returns a structured report and a non-zero exit code if critical errors exist. Compile reads lint output and refuses to run if critical errors are present.

Lint is deterministic — same wiki state always produces the same report. No LLM reasoning, no synthesis. The model walks the filesystem, parses frontmatter, and checks rules.

## When to run

- Before `/llm-wiki compile` — catch issues before they propagate to wiki pages.
- After bulk atom changes — confirm structural integrity.
- As a pre-commit check if the wiki is in git.
- Periodically — weekly — to catch drift.

## When NOT to run

- The user wants insight, not validation. Use `/llm-wiki report`.
- The user wants to fix issues, not list them. Lint surfaces; it doesn't repair.
- The wiki doesn't exist. Run `/llm-wiki bootstrap` first.

## Steps

### 0. Preconditions

Wiki root resolved. Lint reads:

- All `atoms/<branch>/*.md` (except files starting with `_`).
- All `wiki/<branch-or-type>/*.md` (except `_README.md` and other underscore-prefixed).
- `raw/_provenance.md` for source list.
- `schema.md` — for the canonical rule set.

[reference/atoms.md](atoms.md), [reference/5p-branches.md](5p-branches.md), [reference/obsidian.md](obsidian.md) loaded for rule details.

### 1. Walk and parse

For every atom file:

1. Read the file.
2. Extract YAML frontmatter (between `---` markers at the top).
3. Parse the frontmatter into a structured record.
4. If parsing fails, record a critical error and continue.

Build an in-memory atom registry:

```
{
  "atom-20260423-008": {
    "path": "atoms/process/intake-three-gate-model.md",
    "frontmatter": {...parsed},
    "wikilinks-in-body": ["atom-20260423-012", "wiki/process/governance"],
  },
  ...
}
```

### 2. Run checks

Apply every rule from the lists below. Categorise each finding as **critical** or **warning**. Critical findings block compile. Warnings don't block but appear in the report.

#### Critical: frontmatter validity

For each atom:

- ❗ Missing required field: `id`, `claim`, `branch`, `date`, `author`, `confidence`, `status`.
- ❗ `id` format invalid (must match `atom-\d{8}-\d{3}`).
- ❗ `id` not unique across the wiki (duplicate atom IDs).
- ❗ `branch` not in the canonical list (people, process, policy, platform, product, meta).
- ❗ `confidence` not in [0.0, 1.0].
- ❗ `status` not in the canonical list (current, draft, superseded, disputed, archived).
- ❗ `date` not a valid ISO date.

Example finding:

```
[CRITICAL] atoms/process/foo.md
  - Invalid branch: 'governance' (expected one of: people, process, policy, platform, product, meta)
  - Missing required field: confidence
```

#### Critical: sourcing

- ❗ Atom has empty `sources:` list AND `branch:` is not `meta`. Every substantive atom must cite a source.
- ❗ `sources:` list contains paths that don't exist in `raw/`.

#### Critical: supersession integrity

- ❗ Atom with `status: superseded` and missing or empty `superseded-by`.
- ❗ `superseded-by` points to a non-existent atom ID.
- ❗ Atom referenced as `superseded-by` is itself superseded (chains should be flat: the latest atom should be `current`, not the middle of a chain).

#### Critical: branch / location mismatch

- ❗ Frontmatter `branch:` doesn't match the folder the atom lives in (e.g., `branch: platform` but file is at `atoms/process/...`). Either the frontmatter is wrong or the file was misfiled.

#### Critical: binary content in markdown

- ❗ Any `.md` file in `atoms/` or `atoms/_review/` contains binary content markers. Markdown files must be plain text. Common markers:
  - `%PDF-1` — raw PDF binary embedded in markdown
  - `/FlateDecode`, `/ObjStm`, `stream h` — PDF object stream markers
  - `PK\x03\x04` — ZIP/Office Open XML signature (DOCX/XLSX/PPTX)
  - `\xD0\xCF\x11\xE0` — OLE2 signature (older Office formats)
  - Any sequence of 20+ non-printable/control characters (bytes 0x00–0x1F excluding newline/tab)

This almost always means a previous crawl or ingest attempt read a binary source file (PDF, DOCX, etc.) directly instead of converting it first. **Fix:** Delete the garbled file and re-run the correct command (`markitdown` for Office docs, `pdftotext` for PDFs, then ingest the resulting `.md`).

#### Warning: confidence and status

- ⚠ `status: current` with `confidence < 0.6`. Either promote confidence with better evidence or demote status to draft.
- ⚠ `status: draft` and atom is older than 30 days (stale draft).
- ⚠ `status: disputed` with empty `contradicts:` list. Disputes should name the contradicting atom.

#### Warning: bidirectionality

- ⚠ Atom A has `contradicts: [B]` but B's `contradicts:` doesn't include A.
- ⚠ Atom A has `reinforced-by: [B]` but B's frontmatter doesn't acknowledge A in a body wikilink or its own `reinforced-by`. (This one is soft — bidirectionality is harder to enforce for `reinforced-by`.)

#### Warning: wikilink resolution

Parse the body of every atom and wiki page for `[[...]]` wikilinks:

- ⚠ `[[atom-XXXX-NNN]]` points to a non-existent atom file.
- ⚠ `[[wiki/branch/page]]` points to a non-existent wiki page (note: wiki pages are generated, so they may be absent until compile runs — flag as warning, not critical).
- ⚠ `[[raw/file]]` points to a non-existent raw source.
- ⚠ Plain markdown link `[text](path)` to a wiki-internal file. Should be a wikilink.

#### Warning: orphan atoms

- ⚠ Atom not referenced by any wiki page's `atoms:` frontmatter, AND not linked from any other atom's body, AND `compile-to:` is empty.

Orphans are findable in search but invisible to compiled pages. Either give them a `compile-to:` target, link them from a related atom, or accept the orphan status (the warning is informational).

#### Warning: filename hygiene

- ⚠ Filename contains spaces or uppercase letters.
- ⚠ Filename longer than 60 characters (compiled wiki pages display poorly).
- ⚠ Filename doesn't match the claim's slug (cosmetic — the wiki still works).

#### Warning: source orphans

- ⚠ File in `raw/` not cited by any atom. Either ingest it or remove it.
- ⚠ File listed in `raw/_provenance.md` but not present in `raw/`. Provenance row references a deleted source.

### 3. Aggregate findings

Group by severity, then by atom:

```
CRITICAL: <N> issues across <M> atoms
WARNING:  <N> issues across <M> atoms
```

### 4. Output the report

Default output is human-readable, structured:

```
LLM-Wiki Lint Report — 2026-05-21
Path: ~/Projects/my-wiki/

Scanned:
  Atoms:      65
  Wiki pages: 22
  Raw files:  18

[CRITICAL] 3 issues across 2 atoms

  atoms/process/foo.md:
    - Invalid branch: 'governance' (line 4)
    - Missing required field: confidence
    - Filename mismatch with branch (file is in process/, frontmatter says platform)

  atoms/policy/bar.md:
    - sources: [raw/missing-source.pdf] — file does not exist in raw/

[WARNING] 14 issues across 11 atoms

  atoms/process/intake-three-gate-model.md:
    - confidence 0.55 with status 'current' (line 7)
    - contradicts: [atom-20260423-015] not reciprocated

  atoms/platform/vde-runs-on-azure.md:
    - draft for 45 days (created 2026-04-06, still draft)

  ... <truncated, full list in saved report or with --verbose>

Compile: BLOCKED (critical errors present).
Recommended actions:
  1. Fix the 3 critical errors above — they block compile.
  2. Triage the 14 warnings (run with --verbose for the full list).
  3. Re-run /llm-wiki lint to confirm clean state.
  4. Then /llm-wiki compile.
```

### 5. Exit code

- `0` — no critical errors. Warnings allowed.
- `1` — at least one critical error. Compile should refuse to run.
- `2` — lint itself failed (file unreadable, frontmatter unparseable beyond recovery, wiki root not found).

### 6. JSON output for tooling

If `--json` is passed, emit a single JSON object instead of the human report:

```json
{
  "wiki": "/absolute/path",
  "ranAt": "2026-05-21T14:32:00Z",
  "scanned": {"atoms": 65, "wiki": 22, "raw": 18},
  "critical": [
    {
      "file": "atoms/process/foo.md",
      "rule": "invalid-branch",
      "message": "Invalid branch: 'governance'",
      "line": 4
    }
  ],
  "warnings": [...],
  "summary": {
    "criticalCount": 3,
    "warningCount": 14,
    "criticalFiles": 2,
    "warningFiles": 11,
    "compileBlocked": true
  }
}
```

Useful for hooks, CI integration, or chaining into another command.

### 7. Save the report (optional)

If `--save` is passed, write to `wiki/_meta/lint-YYYY-MM-DD.md`. Frontmatter includes the summary; body is the human-readable report. Lint reports accumulate; the user prunes.

Default no — lint is usually a read-and-fix loop, not an artefact.

## Flags

- `--json` — emit JSON instead of human-readable output.
- `--save` — write the report to `wiki/_meta/`.
- `--verbose` — list every warning in full, not just a truncated summary.
- `--severity {critical|warning|all}` — filter output to a single severity. Useful for CI gating.
- `--branch <branch>` — lint only one branch.
- `--no-wikilinks` — skip wikilink resolution checks (faster on large wikis where wiki/ is stale).
- `--strict` — promote all warnings to critical. Use sparingly.

## What lint does NOT do

- **Does not auto-fix.** Reports issues; the user fixes them. Auto-fixing atoms is too dangerous — it could destroy nuance.
- **Does not validate atom content.** Lint checks structure (frontmatter, IDs, links). The truth of the claim itself is human-judged.
- **Does not check confidence scoring.** A confidence of 0.85 is allowed even if the evidence is weak — that's a `report` concern, not a `lint` concern.
- **Does not validate `compile-to:` targets resolve to specific pages.** Compile generates them; lint just confirms the field is well-formed.
- **Does not compile.** Lint runs first; compile reads lint output (via exit code).
- **Does not synthesize.** No LLM reasoning — purely mechanical checks.

## Anti-patterns

- **Skipping lint before compile.** Compile against broken atoms produces broken wiki pages. Always lint first.

- **Using `--strict` to enforce stylistic preferences.** Strict promotes warnings to criticals — meaningful when you want CI to gate on filename hygiene, but it punishes normal in-progress work. Reserve for handoff or release checks.

- **Auto-fixing in scripts.** Tempting but wrong. Lint surfaces; humans (or carefully-scoped commands) fix. Atom edits are content edits — they need human judgement.

- **Linting only critical, ignoring warnings indefinitely.** Warnings accumulate. A wiki with 200 warnings has a quality problem even if no criticals exist. Triage warnings periodically.

- **Treating "no critical errors" as "good wiki".** Lint catches structural issues. Coverage, accuracy, and relevance are out of scope — that's `report`.

- **Disabling rules wholesale.** No `.lintignore` file. If a rule fires too often, the rule is right and the wiki has a real problem. Don't suppress; fix.

- **Running lint after compile.** Order matters: lint, then compile. Compile reading old lint state can produce inconsistent wiki pages.

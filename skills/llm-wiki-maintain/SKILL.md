---
name: llm-wiki-maintain
description: >-
  Maintain and validate an _llm-wiki knowledge base health.
  Use this skill when Dale says "maintain llm-wiki", "wiki health check",
  "validate wiki", "update wiki index", "clean up llm-wiki",
  "check for orphaned pages", "wiki lint", "check wiki links",
  "compile wiki", "generate index", or on a scheduled basis
  to keep the knowledge base healthy.

  This skill validates atoms, compiles wiki pages, generates indexes,
  checks cross-references, and reports health metrics.
---

# LLM-Wiki Maintain

## Purpose

Keep an _llm-wiki knowledge base healthy through automated validation,
atom compilation, index generation, and health reporting. Ensures the
wiki remains usable as it grows.

## When to Use

- After creating or editing atoms (compile wiki)
- Periodic maintenance (weekly/monthly)
- Before major releases or handoffs
- When wiki feels "cluttered" or hard to navigate
- After bulk imports or migrations
- To validate atoms and cross-references
- To check for contradictions or stale content

## Steps / Process

### 1. Locate Wiki and Validate Structure

Find _llm-wiki/ and verify required files exist:
- `AGENT.md` — schema and instructions
- `schema.md` — entity types and validation rules
- `README.md` — human guide
- `index.md` — content catalog (auto-generated)
- `raw/` — source folder
- `atoms/` — atomic claims
- `wiki/` — compiled pages (auto-generated)
- `scripts/` — compilation tooling

Missing files are flagged for re-initialization.

### 2. Validate Atoms

Run validation on all atoms:

```bash
python scripts/validate.py
```

Checks:
- [ ] `id` is unique and follows format `atom-YYYYMMDD-NNN`
- [ ] `claim` is a single sentence
- [ ] `branch` is one of: people, process, policy, platform, product, meta
- [ ] `date` is valid ISO date
- [ ] `sources` contains valid `raw/` paths
- [ ] `confidence` is 0.0-1.0
- [ ] `status` is one of: current, draft, superseded, disputed, archived
- [ ] Filename matches claim slug (kebab-case)

Report issues:
```
Atom validation errors:
  atoms/process/five-actor-model.md:
    - Missing required field: confidence
    - Invalid branch 'governance' (expected one of: people, process, policy, platform, product, meta)
```

### 3. Compile Wiki Pages

Compile wiki pages from current atoms:

```bash
python scripts/compile-wiki.py
```

This:
- Groups atoms by `compile-to` targets
- Sorts by confidence (highest first)
- Detects contradictions
- Generates wiki pages with full provenance

For specific pages:
```bash
python scripts/compile-wiki.py --page wiki/process/accountability-model
```

Force recompilation:
```bash
python scripts/compile-wiki.py --force
```

### 4. Generate Index

Regenerate `index.md` from compiled wiki pages:

```bash
python scripts/generate-index.py
```

Generates:
- Page count and atom count
- Branch-based navigation
- Tag index
- Recent updates
- Confidence score reference

### 5. Validate Cross-References

Check all wikilinks:
- `[[atom-XXX]]` — links to existing atoms
- `[[wiki/XXX]]` — links to compiled pages
- `[[raw/XXX]]` — links to raw sources

Detect:
- Broken links
- Circular references
- Missing bidirectional links

### 6. Detect Contradictions

Flag atoms with `contradicts` relationships:

```
Contradictions detected:
  atom-20260423-015 contradicts atom-20260423-008
    Resolution: Pending human review
```

### 7. Check for Stale Content

Flag potentially stale atoms:
- `status: current` but not modified in 90+ days
- References sources that have been updated in raw/
- Confidence marked as `low` or `draft`

Stale report:
```
Potentially stale atoms:
  atoms/process/old-workflow.md
    Last modified: 2026-01-15 (98 days ago)
    Source updated: 2026-04-10 (raw/workflow-v2.pdf)
    Action: Review and update or mark superseded
```

### 8. Generate Maintenance Report

Output comprehensive report:

```
LLM-Wiki Health Report: <wiki-path>
Generated: <timestamp>

Summary:
  Atoms: <n> | Wiki pages: <n> | Orphans: <n>
  Broken links: <n> | Contradictions: <n> | Stale: <n>
  Health score: <percentage>

Validation: ✓ Passed / ✗ Failed
Compilation: ✓ Up to date / ✗ Needs recompile
Index: ✓ Current / ✗ Out of date

Issues found:
  [Critical] <n>: Broken links, invalid atoms
  [Warning] <n>: Orphaned atoms, stale content, contradictions
  [Info] <n>: Missing recommended fields

Quick fixes applied:
  - Compiled wiki pages
  - Generated index.md

Manual action required:
  1. Fix validation errors in atoms/process/invalid-atom.md
  2. Resolve contradiction: atom-015 vs atom-008
  3. Review stale atom: atoms/process/old-workflow.md

Next maintenance: <date + 7 days>
```

### 9. Full Maintenance Workflow

Complete maintenance sequence:

```bash
# 1. Validate atoms
python scripts/validate.py

# 2. Compile wiki pages
python scripts/compile-wiki.py

# 3. Generate index
python scripts/generate-index.py

# 4. Final validation
python scripts/validate.py
```

Or use the all-in-one command:
```bash
python scripts/maintain.py --full
```

## Health Score Calculation

- 100% = no issues, all atoms valid, wiki compiled, index current
- 90-99% = minor issues (missing optional fields)
- 80-89% = moderate issues (orphaned atoms, stale content)
- <80% = needs attention (broken links, invalid atoms)
- <50% = critical (multiple critical issues)

## Maintenance Schedule

Recommended frequency:
- **After each atom edit:** Quick compile and index update
- **Weekly:** Validation and contradiction check
- **Monthly:** Full health check with stale content review
- **Before handoff:** Complete validation and compilation
- **After bulk import:** Full maintenance workflow

## Output Format

Maintenance produces:
1. Compiled wiki pages in `wiki/`
2. Updated `index.md`
3. Console report with health score
4. Optional `MAINTENANCE-REPORT-YYYY-MM-DD.md` for tracking

## Separation of Concerns

This skill handles:
- Validation of atoms and structure
- Compilation of wiki pages
- Index generation
- Health reporting

This skill does NOT:
- Create new atoms (use llm-wiki-crawl or manual creation)
- Migrate content from raw/ to atoms/
- Delete content (except empty folders with permission)
- Modify atom content (except compilation metadata)

## Notes

- Maintenance is safe to run anytime
- Health score: 100% = no issues, <80% = needs attention, <50% = critical
- Report includes actionable suggestions, not just problems
- Track maintenance history in git commits for audit trail
- Always validate before compiling, and compile before generating index

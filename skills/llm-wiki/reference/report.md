# Report — health and insights

Loaded when the user invokes `/llm-wiki report`. Produces a comprehensive health report: atom counts, confidence distribution, stale atoms, contradictions, coverage analysis against `purpose.md`, and compile freshness. Optionally saves the report to `wiki/_meta/` for audit trail.

Report is observational, not corrective. For validation that blocks compile, use `/llm-wiki lint`. For regeneration, use `/llm-wiki compile`.

## When to run

- Periodically — weekly or monthly — to keep tabs on wiki health.
- Before a handoff or milestone — a snapshot the next person can rely on.
- After a bulk ingest or major change — confirm the wiki absorbed it cleanly.
- When the wiki feels off ("hard to navigate", "things don't connect") — report quantifies the feeling.

## When NOT to run

- The user wants validation, not insight. Use `/llm-wiki lint` — it returns structured errors.
- The user wants a fix. Report doesn't fix anything; it surfaces what's wrong. The user (or another command) does the fixing.
- The wiki doesn't exist. Run `/llm-wiki bootstrap` first.

## Steps

### 0. Preconditions

Wiki root resolved. Report reads:

- All atoms in `atoms/<branch>/<slug>.md`.
- All wiki pages in `wiki/<branch>/<page>.md` and `wiki/<page-type>/<page>.md`.
- `purpose.md` — for coverage analysis.
- `raw/_provenance.md` — for source-cited counts.
- `.llm-wiki/ingest-cache.json` — for last-ingest timestamps.
- `log.md` — for activity trends.

[reference/atoms.md](atoms.md) and [reference/5p-branches.md](5p-branches.md) loaded for schema context.

### 1. Counts and distributions

**Atom counts:**

- Total atoms.
- By branch — `people`, `process`, `policy`, `platform`, `product`, `meta`.
- By status — `current`, `draft`, `superseded`, `disputed`, `archived`.
- By author — `extract`, `human`, `synthesis`.

**Wiki page counts:**

- Total compiled pages.
- By branch.
- By page type — `synthesis`, `comparisons`, `queries`.
- Pages compiled to `wiki/<branch>/_other.md` (atoms without a clear topic — a smell).

**Source counts:**

- Total raw sources tracked in `_provenance.md`.
- Sources cited by ≥1 atom (used).
- Sources with no atoms citing them (orphaned in `raw/` — flag).
- Sources cited by ≥5 atoms (heavy hitters).

### 2. Confidence distribution

Bucket all `status: current` atoms by confidence:

```
0.95–1.00 certain:  ##### ##### #####   (15 atoms, 23%)
0.80–0.94 high:     ##### ##### ###     (13 atoms, 20%)
0.60–0.79 medium:   ##### #####         (10 atoms, 15%)
0.40–0.59 low:      ###                 ( 3 atoms,  5%)
0.00–0.39 very low: ##                  ( 2 atoms,  3%)
```

A healthy wiki skews high. Persistent low-confidence atoms are signal to re-investigate sources or supersede.

### 3. Stale atom report

An atom is **stale** if:

- `status: current` AND
- File `mtime` more than 90 days ago AND
- Either the cited raw source has changed since the atom was written, OR the atom hasn't been touched since creation.

For each stale atom:

```
- atoms/process/intake-uses-three-gate-model.md
  Last modified: 2026-01-15 (126 days ago)
  Source: raw/intake-policy-v3.pdf (updated 2026-04-10, after atom written)
  Action: re-ingest the source, or update the atom to reflect current source state.
```

Stale doesn't mean wrong. It means worth checking.

### 4. Contradiction surface

Two flavours:

**Explicit contradictions** — atoms with `contradicts:` relationships:

```
- atom-20260423-008 ↔ atom-20260423-015
  Claim A: "All AI models require risk assessment before deployment."
  Claim B: "Internal AI tools are exempt from formal risk assessment."
  Status: both atoms are `current`. Resolution pending.
```

**Implicit contradictions** — atoms with `status: disputed` but no `contradicts:` link:

```
- atom-20260301-022 (status: disputed, no contradicts: list)
  Likely missing bidirectional link. Investigate.
```

For each contradiction, suggest one action: resolve by superseding the older atom, or formalise the disagreement with `compile-to: wiki/comparisons/...`.

### 5. Coverage analysis against `purpose.md`

Parse `purpose.md` key questions. For each:

- Search atoms for keyword matches against the question.
- Search wiki pages for relevant compiled material.
- Score coverage: **strong** (≥3 high-confidence atoms or a dedicated wiki page), **partial** (1–2 atoms or weak page coverage), **none** (no relevant content).

```
Purpose questions and coverage:

  1. "Which legacy systems support which statutory functions?"
     Coverage: STRONG — 12 atoms across platform/policy, wiki/synthesis/system-function-mapping.md

  2. "Where are the function-to-system gaps?"
     Coverage: PARTIAL — 4 atoms in platform, no synthesis page yet.
     Suggest: /llm-wiki compile --page wiki/synthesis/system-coverage-gaps

  3. "What's the sunset risk for PAS?"
     Coverage: NONE — no atoms tagged or claiming about PAS sunset.
     Suggest: ingest the PAS roadmap document or run /llm-wiki crawl on the platform inventory.
```

Coverage analysis is the most actionable section of the report. It connects the wiki to the user's actual questions.

### 6. Compile freshness

Compare:

- Latest atom `mtime` across all atoms.
- Latest wiki page `date-compiled` across all compiled pages.

If atoms are newer than the most recent compile:

```
Compile staleness: 23 atoms modified since last compile (2026-05-15).

Affected wiki pages (likely):
  - wiki/process/intake-three-gate-model.md
  - wiki/policy/epbc-statutory-functions.md
  - wiki/synthesis/system-coverage-gaps.md

Run: /llm-wiki compile
```

### 7. Activity trend

Parse `log.md` for the last 60 days. Render:

- Ingests per week (sparkline).
- Atoms created per week.
- Compiles per week.
- Queries saved per week.

```
Activity (last 60 days):

  Ingests:  ▁▂▅▇▆▃▁▁▂▃  (last week: 3)
  Atoms:    ▁▃▆▇▆▄▂▁▃▄  (last week: 8 created)
  Compiles: ▁▁▂▁▁▁▁▁▁▂  (last week: 1)
  Queries:  ▁▁▁▂▃▅▇▆▄▃  (last week: 3 saved)
```

Trends are observational. Don't interpret — the user knows their own rhythm.

### 8. Health score

Roll up the signals into a single score (0–100):

| Signal | Weight | Calculation |
|---|---|---|
| All atoms valid (no lint criticals) | 30 | 30 if pass, 0 if any criticals |
| Confidence distribution healthy | 20 | 20 × (% atoms ≥ 0.60 confidence) |
| Compile fresh (no staleness) | 15 | 15 if no atoms newer than last compile, scaled down by staleness |
| No unresolved contradictions | 10 | 10 if zero, 0 if ≥3, linear between |
| Coverage strong for purpose questions | 15 | 15 × (% questions with strong/partial coverage) |
| No stale atoms (< 10% stale) | 10 | 10 × (1 - stale-ratio), capped |

Display as percentage with a one-line interpretation:

```
Health score: 78/100
  - Strong coverage of purpose questions (4/5 partial or strong).
  - Confidence distribution healthy (84% ≥ 0.60).
  - Compile is stale — 23 atoms newer than wiki pages.
  - 2 unresolved contradictions in policy branch.
```

A score isn't a verdict. It's a summary the user can scan in three seconds.

### 9. Save the report (optional)

If `--save` was passed or the user confirms when offered:

Write to `wiki/_meta/report-YYYY-MM-DD.md` with frontmatter:

```yaml
---
title: "Wiki Health Report"
type: report
date: YYYY-MM-DD
health-score: 78
atom-count: 65
wiki-page-count: 22
---
```

Body: the full report from steps 1–8, formatted as markdown.

Saved reports are git-friendly evidence of wiki maintenance over time. They're not auto-deleted; the user prunes when they feel like it.

### 10. Stop gate before save

If `--save` not passed, offer:

```
Save this report to wiki/_meta/report-2026-05-21.md for audit trail?

  Useful if you want to track health over time or hand the wiki to someone else.
  Reports are git-friendly markdown — keeps a record of state at this date.

[y/N]
```

Default no — most reports are read-and-done.

## Flags

- `--save` — write the report without asking.
- `--no-save` — never offer save.
- `--branch <branch>` — limit the report to a single branch.
- `--since <date>` — only consider atoms modified after this date.
- `--quick` — skip coverage analysis and trend section (faster, less detail).

## What report does NOT do

- **Does not modify atoms.** Even stale ones are left alone — that's the user's call.
- **Does not delete files.** Orphaned raw sources are reported, not removed.
- **Does not compile.** Compile staleness is flagged, but the user runs `/llm-wiki compile` separately.
- **Does not run lint.** Validation errors are reported only if they're already known (i.e., if `lint` has been run and produced a report file). For fresh validation, run `/llm-wiki lint` first.
- **Does not auto-fix anything.** Everything is observation + suggestion.

## Anti-patterns

- **Treating the health score as a target.** A score of 85 is fine. Optimising the score becomes a metric-gaming exercise that doesn't make the wiki more useful.

- **Reporting without context.** A stale atom isn't necessarily wrong. A contradiction isn't necessarily a bug. The report surfaces — the user interprets.

- **Saving every report.** Reports accumulate noise. Save when you want a snapshot for handoff or audit; don't save weekly.

- **Conflating report with lint.** Lint is mechanical validation that blocks compile. Report is observational and never blocks anything. Don't mix the two.

- **Ignoring coverage analysis.** It's the most actionable section. Skipping it because it's slower is missing the point of the report.

- **Reporting on archived atoms.** They're archived for a reason. Exclude from counts unless `--include-archived` is set.

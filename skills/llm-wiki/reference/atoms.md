# Atoms — schema, confidence, lifecycle

Foundational reference. Loaded by `bootstrap`, `crawl`, `ingest`, `compile`, `lint`, and `report`. Defines what an atom is and how it evolves.

## What an atom is

A single factual claim, written as one short markdown file with YAML frontmatter. The claim is the unit of truth. Everything else in the wiki — compiled pages, queries, reports — derives from atoms.

One atom = one claim. Not one paragraph. Not one document. If you find yourself writing "and" twice in the claim field, split it into two atoms.

## File location

`atoms/<branch>/<slug>.md` where:

- `<branch>` ∈ {`people`, `process`, `policy`, `platform`, `product`, `meta`} — see [5p-branches.md](5p-branches.md)
- `<slug>` is kebab-case, derived from the claim. Max 60 chars. No timestamps in the filename — the ID carries that.

Examples:
- `atoms/process/intake-uses-three-gate-model.md`
- `atoms/platform/vde-runs-on-azure.md`
- `atoms/people/product-owner-reports-to-cio.md`

## Frontmatter schema

Required:

```yaml
---
id: atom-YYYYMMDD-NNN
claim: "Single-sentence factual claim, no period at end"
branch: people | process | policy | platform | product | meta
date: YYYY-MM-DD
author: extract | human | synthesis
confidence: 0.85
status: current | draft | superseded | disputed | archived
---
```

Optional:

```yaml
tags: [tag-one, tag-two]
sources: [raw/source-filename.pdf, raw/another.md]
superseded-by: atom-YYYYMMDD-NNN
contradicts: [atom-YYYYMMDD-NNN]
reinforced-by: [atom-YYYYMMDD-NNN]
compile-to: [wiki/process/accountability-model, wiki/platform/architecture-overview]
```

### Field rules

- **`id`**: `atom-YYYYMMDD-NNN` where `YYYYMMDD` is the creation date and `NNN` is a zero-padded ordinal within that day. Once assigned, never changes. Renaming an atom file does not change the ID.
- **`claim`**: a single declarative sentence. No questions. No "may", "could", "might" unless the uncertainty is itself the claim. No period at end. Quotes optional but consistent within a wiki.
- **`branch`**: exactly one of the six values. Choose by what the claim is *about*, not where the source came from. See [5p-branches.md](5p-branches.md) for the decision tree.
- **`date`**: ISO date of atom creation. Not the source date — the atom date.
- **`author`**: `extract` if the LLM extracted it from a source; `human` if Dale wrote it; `synthesis` if it's a cross-source claim built from multiple atoms.
- **`confidence`**: float 0.0–1.0. See scoring table below. Never write a label here ("high", "medium"); always a number.
- **`status`**: see lifecycle below.
- **`sources`**: list of `raw/` paths the claim derives from. Empty only for `branch: meta` atoms. Every other branch requires at least one source.
- **`superseded-by`**: a single newer atom ID. Set this when the claim is no longer current; do not delete the atom.
- **`contradicts` / `reinforced-by`**: lists of atom IDs. Bidirectional in spirit but not enforced — if A contradicts B, also add A to B's `contradicts`. `lint` checks bidirectionality.
- **`compile-to`**: wiki pages this atom should appear in. If absent, the compiler infers from branch + tags.

## Body structure

```markdown
# {{Atom title — short noun phrase, not the claim verbatim}}

**Claim:** {{Restate the claim from frontmatter, prose}}

**Evidence:**
- From [[raw/source-file]]: "Quoted passage if short, paraphrased otherwise."
- Page/section ref if applicable.

**Context:**
{{Background, caveats, conditions, scope limits. Why this matters. When it doesn't apply.}}

**Related atoms:**
- [[atom-YYYYMMDD-NNN]] — short note on the relationship
```

Keep the body short. Long bodies are a smell — usually it's two atoms pretending to be one.

## Confidence scoring

| Score | Meaning | Use when |
|---|---|---|
| 0.95–1.00 | Certain | Explicitly stated in an authoritative source (statute, signed contract, official spec) |
| 0.80–0.94 | High | Stated clearly in a credible source, no contradiction |
| 0.60–0.79 | Medium | Implied, inferred, or multiple sources agree but with nuance |
| 0.40–0.59 | Low | Speculative, outdated, or weak evidence |
| 0.00–0.39 | Very low | Disputed, deprecated, or placeholder — should be reviewed before use |

Score the **claim against the evidence**, not the source's prestige. A clearly worded statement in a draft document beats a vague claim in a final report.

If two sources disagree, create both atoms with appropriate confidence and use `contradicts:`. Do not average them into a watered-down third atom.

## Status lifecycle

```
draft → current → superseded → archived
                ↘ disputed ↗
```

- **`draft`**: just created, not yet reviewed. `crawl` writes atoms here by default.
- **`current`**: reviewed, accurate at the present time. The default state for live atoms.
- **`superseded`**: a newer atom replaces this one. `superseded-by:` is required.
- **`disputed`**: another atom contradicts this one and the contradiction is unresolved. `contradicts:` is required.
- **`archived`**: no longer relevant but kept for historical record. Removed from compiled wiki pages.

Status transitions are explicit edits to the atom file. Lifecycle is not automatic.

## Supersession protocol

When a fact changes:

1. Create a new atom with the updated claim and today's date.
2. Edit the old atom: set `status: superseded` and `superseded-by: <new-atom-id>`.
3. Add a `Related atoms` line in the new atom referencing the old one with context (e.g., "Replaces [[atom-20260101-003]] following 2026-Q2 reorganisation").
4. Never delete the old atom. Never rewrite its claim.

`compile` skips superseded atoms by default. `report` lists them under "supersession history" for audit.

## Authoring rules for `ingest` and `crawl`

When the LLM is creating atoms from a source:

- **One claim per atom.** Resist the urge to combine. Two atoms with a `reinforced-by` link beats one bloated atom.
- **Quote evidence verbatim when short.** Paraphrase when long, and cite the location.
- **Set confidence honestly.** Default to 0.7 for extracted claims. Higher only if the source is authoritative and the statement is explicit. Lower if you're inferring.
- **Default `status: draft`.** Promote to `current` only after human review.
- **Suggest `compile-to:` targets** based on branch + topic. Don't leave it empty unless the atom is `branch: meta`.
- **Look for contradictions** with existing atoms in the same branch before writing. Add `contradicts:` if found.

## Anti-patterns

- **Atom with no source and `branch: people` (or any non-meta branch).** Invalid. Either find the source or don't write the atom.
- **Atom where the claim repeats the title.** Title and claim are different views — title is a noun phrase, claim is a sentence.
- **Atoms that contradict but don't link.** `lint` flags this; fix at write time.
- **Confidence 0.5 because "unsure".** 0.5 is meaningful — it means evidence is split. If you're unsure where to score, default to 0.7 and add a note in `Context:`.
- **Editing a superseded atom's claim.** History is the point. Create a new atom instead.
- **Atom IDs reused or invented.** IDs come from creation timestamp; collisions are resolved by incrementing `NNN`. Never reuse.

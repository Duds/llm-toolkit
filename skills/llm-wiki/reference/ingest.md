# Ingest — two-step chain-of-thought processing of a single source

Loaded when the user invokes `/llm-wiki ingest <source-path>`. Processes one raw source into atoms via a two-step LLM flow that produces materially better results than single-pass extraction.

## When to run

- A new source has been added to `raw/` and you want to convert it to atoms.
- A previously ingested source has changed (the SHA cache will detect this).
- A single-source ingest needs higher quality than the bulk `crawl` flow.

## When NOT to run

- The source isn't in `raw/` yet. Copy it there first — atoms must trace back to `raw/`.
- The source is enormous and unfiltered (e.g. a 500-page contract dump). Pre-process or excerpt first; ingesting the whole thing produces dozens of low-confidence atoms and contradictions you don't actually have.
- The user wants discovery, not processing. Use `/llm-wiki crawl` to scan folders for candidates.

## Steps

### 0. Preconditions

Run setup if not already loaded this session. You need:

- Wiki root resolved.
- `purpose.md` loaded — atom quality depends on filtering against the wiki's intent.
- `schema.md` loaded — for branch list and confidence scoring.
- [reference/atoms.md](atoms.md) loaded — for frontmatter rules.
- [reference/5p-branches.md](5p-branches.md) loaded — for the classification decision tree.

If `purpose.md` is empty or placeholder, **stop and warn**: *"purpose.md is placeholder content. Atom quality will be generic. Edit purpose.md first or run `/llm-wiki bootstrap --reinit` and pick a scenario."* Then ask the user whether to proceed anyway.

### 1. Resolve and check cache

The source argument can be:

- A `raw/`-relative path: `raw/intake-policy-v3.pdf`
- An absolute path to a file inside the wiki's `raw/` directory.
- A path outside `raw/` — if so, copy to `raw/` first, then proceed.

Compute SHA256 of the source. Check `.llm-wiki/ingest-cache.json` for a matching entry:

```json
{
  "raw/intake-policy-v3.pdf": {
    "sha256": "abc123...",
    "ingested-at": "2026-05-21T14:32:00Z",
    "atom-ids": ["atom-20260521-001", "atom-20260521-002"]
  }
}
```

If SHA matches the cached entry, the source is unchanged. **Stop with a status report**:

```
Source already ingested at 2026-05-21T14:32:00Z (SHA unchanged).
Atoms created: 5 (atom-20260521-001 ... atom-20260521-005)

To re-ingest anyway, pass --force.
To update atoms when a source changes, copy the new version with a date suffix
(e.g., intake-policy-v3-2026-06.pdf) and ingest separately.
```

If SHA differs (source changed) and the cache has an entry, **stop and surface the conflict**:

```
Source has changed since last ingest (2026-05-21). 5 atoms cite this source.
Re-ingesting may produce contradictions with existing atoms.

Options:
  1. Treat as new version: copy with date suffix, ingest separately (recommended).
  2. Re-ingest in place: --force. Existing atoms remain; new atoms get added.
  3. Cancel.

What would you like to do?
```

This is a stop gate. Do not proceed without explicit user direction.

### 2. Read the source

Use the appropriate file-reading approach:

- Markdown / plain text → Read tool directly.
- PDF → mirror-docs or pdf-reading skill (depending on size).
- DOCX / XLSX / PPTX → markitdown or the relevant skill.
- HTML → fetch + Readability if needed.
- Images → vision-capable read or whiteboard-ocr skill.

The skill is agnostic to source format. The point is: get clean text in hand before Step 3.

### 3. Step 1 — analysis (first LLM pass)

This is the chain-of-thought "analysis" call. Produce a structured intermediate, not atoms yet.

Prompt frame (internal — don't show the user unless they ask):

```
You are extracting structured analysis from a source for an llm-wiki.

Wiki purpose (key questions):
{{paste purpose.md "Key questions" section}}

Wiki thesis:
{{paste purpose.md "Evolving thesis" section}}

Folder hint (classification signal): {{e.g., "papers > energy" or "policy/intake"}}

Source: {{filename}}

Source content:
{{full text}}

Produce a structured analysis with these sections. Cite evidence (quote or paraphrase + location) for every claim.

## Entities
Roles, organizations, products, named individuals. For each: name, type, brief description.

## Concepts
Definitions, theories, methods, frameworks. For each: term, definition, where it appears.

## Claims
Factual statements the source makes. For each:
- Claim (single sentence)
- Evidence (quote or paraphrase + location)
- Suggested branch (people/process/policy/platform/product/meta)
- Suggested confidence (0.0–1.0, see scoring guide)
- Relevance to purpose questions (which key questions it helps answer, or "none")

## Contradictions
Internal contradictions within the source, OR contradictions with the wiki's existing atoms (if any are cited in purpose/thesis).

## Recommendations
What the source itself recommends or proposes.

## Gaps
What the source assumes but doesn't establish; questions left open.
```

The output of Step 1 is a structured markdown document. Don't write atoms yet.

**Show the user the analysis** and stop:

```
Step 1 (analysis) complete.

Found:
  - {{N}} entities
  - {{N}} concepts
  - {{N}} claims (relevant to purpose: {{N}})
  - {{N}} contradictions ({{internal}} internal, {{external}} with existing atoms)
  - {{N}} recommendations
  - {{N}} open questions

Top 5 claims by relevance:
  1. ...
  2. ...

Proceed to Step 2 (atom generation) or refine the analysis first?
```

Wait for confirmation. This is a stop gate — Step 1 quality determines Step 2 quality. Compressing this is the dominant failure mode.

### 4. Step 2 — atom generation (second LLM pass)

Now generate atoms from the analysis. Don't ingest from the raw source again — the analysis is the input.

Prompt frame:

```
You are generating atomic claims (atoms) from a structured analysis for an llm-wiki.

Schema: {{atom frontmatter rules from schema.md}}
Confidence guide: {{from schema.md}}
Branch decision tree: {{from 5p-branches.md, in brief}}

Wiki purpose:
{{purpose.md key questions + thesis}}

Analysis:
{{the Step 1 output}}

For each "Claim" in the analysis, produce one atom. For "Entities" and "Concepts" that warrant standalone atoms (named individuals with defined roles, framework definitions, etc.), produce atoms for them too. Skip entities/concepts that are just mentions.

Atom rules:
- One claim per atom. Don't combine.
- Cite evidence: every atom needs `sources: [raw/{{filename}}]`.
- Confidence: use the scoring guide. Don't default to 0.7 for everything.
- Branch: use the decision tree, not folder hints.
- Status: draft. The user reviews and promotes to current.
- ID: atom-{{today}}-{{next-NNN}} (find next-NNN by listing today's atoms across all branches).
- Suggest `compile-to:` targets based on branch + topic.
- Add `contradicts:` if the analysis flagged a contradiction with another atom.
- Add `reinforced-by:` if the analysis cited a related existing atom.

Output: one markdown file per atom in atoms/<branch>/<slug>.md format, with full frontmatter and body (claim, evidence, context, related atoms).
```

### 5. Stop gate — present atoms before writing

**Show the user the proposed atoms before writing any files.** Format:

```
Step 2 (atom generation) ready to write {{N}} atoms.

By branch:
  people:   {{N}}
  process:  {{N}}
  policy:   {{N}}
  platform: {{N}}
  product:  {{N}}
  meta:     {{N}}

By confidence:
  0.95+ certain:  {{N}}
  0.80–0.94 high: {{N}}
  0.60–0.79 med:  {{N}}
  <0.60:          {{N}}  ← will be flagged in `lint` until promoted

{{N}} atoms flag contradictions with existing atoms — list them.

Preview the first 3 atoms:
{{render frontmatter + first 5 lines of body}}

Options:
  1. Write all atoms as drafts.
  2. Write selectively (pick which to keep).
  3. Refine the analysis and retry Step 2.
  4. Cancel.
```

Wait for confirmation. Do not write atoms without explicit approval.

### 6. Write atoms

On approval:

1. **Assign IDs.** Count today's existing atoms across all `atoms/<branch>/`. Next ID = `atom-{{YYYYMMDD}}-{{NNN}}` where NNN is zero-padded next available.
2. **Write each atom** to `atoms/<branch>/<slug>.md`. Slug = kebab-case of claim, max 60 chars. If a file with that slug exists, append `-2`, `-3`, etc.
3. **Append to `raw/_provenance.md`** with: source path, ingest date, atom IDs created. Never edit existing rows.
4. **Update the SHA cache** at `.llm-wiki/ingest-cache.json` with the source's SHA, timestamp, and atom IDs.
5. **Append to `log.md`** with one line: `## YYYY-MM-DD\n- Ingested raw/{{filename}}: {{N}} atoms ({{branch breakdown}})`.

Don't run `compile` automatically. Compilation is a separate decision — the user may want to review the atoms in Obsidian first.

### 7. Report

Final output:

```
Ingested raw/{{filename}}: {{N}} atoms written.

Atom IDs: atom-20260521-001 ... atom-20260521-{{NNN}}

By branch:
  process:  3 atoms — atoms/process/...
  policy:   2 atoms — atoms/policy/...
  platform: 4 atoms — atoms/platform/...

Provenance: raw/_provenance.md updated.
Cache:      .llm-wiki/ingest-cache.json updated.
Log:        log.md appended.

Next steps:
  1. Review atoms in atoms/<branch>/ (filenames will tell you which).
  2. Promote drafts to current after review: edit `status: draft` → `status: current`.
  3. Run /llm-wiki compile to refresh wiki pages.
  4. Run /llm-wiki lint to check for new contradictions or broken links.

{{N}} atoms have confidence < 0.6 — flag for review:
  - atom-20260521-007 (confidence 0.55) — atoms/process/...
  - atom-20260521-012 (confidence 0.42) — atoms/policy/...
```

## Flags

- `--force` — re-ingest even if SHA matches cache. Creates new atoms; doesn't delete existing.
- `--no-stop` — skip the Step 1 confirmation gate. **Discouraged.** Only use for batch automation where you trust the source format.
- `--branch <branch>` — restrict ingest to a single branch (useful for narrow sources).
- `--dry-run` — run Step 1 + Step 2, show the proposed atoms, write nothing.

## Scripts

Mechanical helpers for the steps above. All live in `scripts/ingest-helpers.mjs` and emit machine-readable output on stdout; errors go to stderr; exit code 1 signals an expected miss (e.g. cache lookup with no entry), exit code 2 signals real failure.

`<wiki>` below is the absolute path to the wiki root. Resolve once with `node scripts/load-wiki.mjs` and reuse.

### Step 1 — cache check

```bash
# Compute SHA of the source
node scripts/ingest-helpers.mjs sha256 raw/intake-policy-v3.pdf

# Look up the cache entry; exit 1 means no entry (proceed with ingest)
node scripts/ingest-helpers.mjs cache-get <wiki> raw/intake-policy-v3.pdf
```

### Step 4 — atom generation

```bash
# Next available atom id for today (atom-YYYYMMDD-NNN)
node scripts/ingest-helpers.mjs next-atom-id <wiki>

# Kebab-case slug from a claim (max 60 chars)
node scripts/ingest-helpers.mjs slug "Intake uses a three-gate model"
```

### Step 6 — persistence

```bash
# Write a single atom — body file contains frontmatter + body
node scripts/ingest-helpers.mjs write-atom <wiki> process intake-three-gate --body /tmp/atom.md
# (Auto-resolves slug collisions: foo.md → foo-2.md, foo-3.md, ...)

# Append a provenance row (existing rows never edited)
node scripts/ingest-helpers.mjs append-provenance <wiki> \
  --raw intake-policy-v3.pdf \
  --source ~/Downloads/intake-policy-v3.pdf \
  --date 2026-05-21 \
  --origin "DCCEEW policy team" \
  --context "intake gate model" \
  --atoms "atom-20260521-001,atom-20260521-002"

# Update the SHA cache
echo '{"sha256":"abc123...","atom-ids":["atom-20260521-001"]}' > /tmp/cache.json
node scripts/ingest-helpers.mjs cache-set <wiki> raw/intake-policy-v3.pdf --json /tmp/cache.json

# Append a log line under today's heading (heading created if absent)
node scripts/ingest-helpers.mjs append-log <wiki> "Ingested raw/intake-policy-v3.pdf: 5 atoms (process: 3, policy: 2)"
```

The helpers handle the mechanical bits the LLM shouldn't reinvent: cross-platform paths, line-ending quirks, atom-id allocation across branches, slug collision resolution, provenance table escaping, and log heading insertion. The LLM's job is everything else — the two-step chain-of-thought reasoning, the stop gates, and the synthesis.

## Anti-patterns

- **Single-pass extraction.** Skipping Step 1 and going straight from source to atoms produces:
  - Atoms that miss contradictions (the model didn't look for them).
  - Inflated confidence (the model didn't have the structured analysis to score against).
  - Missed entities/concepts (the model anchored on the most surface-level claims).
  The two-step flow exists because single-pass is materially worse.

- **Writing atoms before the stop gate.** The user must see proposed atoms before they hit disk. Surprises in `atoms/` erode trust in the skill.

- **Generic confidence (everything 0.7).** Real confidence varies. If every atom from a source has the same score, the model didn't score — it defaulted. Re-run with explicit per-atom scoring instructions.

- **Inferring branch from folder.** Folder is a hint, not the answer. A document about *people* in `policy/` is still `people`-branch.

- **Ignoring purpose.md.** Without purpose filtering, the model surfaces generic salience. Atoms will be technically correct but useless against the wiki's actual questions.

- **Auto-running compile.** Ingest writes draft atoms. The user reviews. Compile happens later, on demand. Auto-running collapses two decisions into one.

- **Re-ingesting unchanged sources.** The SHA cache exists for a reason. If `--force` is needed, the source has actually changed — copy the new version with a date suffix instead.

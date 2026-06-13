# Query — Q&A grounded in atoms and wiki pages

Loaded when the user invokes `/llm-wiki query "<question>"`. Answers a question using the wiki's atoms and compiled pages as ground truth, with explicit citations. Optionally saves the answer to `wiki/queries/` so it becomes first-class wiki content.

## When to run

- The user has a question the wiki should be able to answer.
- A new line of analysis benefits from being grounded in what's already captured.
- The user wants a defensible synthesis with citations, not a free-form chat answer.

## When NOT to run

- The question is about something the wiki doesn't cover. Don't fake citations — surface the gap and suggest `/llm-wiki ingest` or `/llm-wiki crawl` to fill it.
- The user wants Obsidian-style search (find files by keyword). They should use Obsidian's native search; `query` is for synthesis, not retrieval.
- The user is asking about a single atom. Just open it in Obsidian — `[[atom-id]]` resolves directly.
- The wiki doesn't exist. Run `/llm-wiki bootstrap` first.

## Steps

### 0. Preconditions

Setup must already have run this session. You need:

- Wiki root resolved.
- `purpose.md` loaded — every query is filtered against the wiki's intent. The model should align answers with the wiki's key questions and thesis.
- `index.md` loaded — gives you the inventory of compiled pages without walking the filesystem.
- [reference/atoms.md](atoms.md) loaded — for citation conventions.

If the wiki has fewer than ~10 atoms, **warn**: *"Wiki has {{N}} atoms. Answers may be sparse or rely on weak evidence. Ingest more sources before relying on `query` for important questions."* Proceed anyway if the user wants.

### 1. Search the wiki

The wiki is plain markdown with structured frontmatter. Search with the right tool for the job — no embeddings, no vector store, just ripgrep.

**Search order (cheapest first):**

1. **Exact match in atom claims.** Use Grep on `atoms/**/*.md` filtering for `claim:` lines. Catches direct factual matches fast.
2. **Tag match.** Grep on `tags:` arrays. If the question contains a known tag, atoms tagged with it are top candidates.
3. **Branch filter.** If the question implies a branch (e.g., "who manages X" → `people`), search within that branch first.
4. **Compiled page lead lines.** Wiki pages have a brief lead in the first few lines after frontmatter. Grep those for topic matches.
5. **Body keyword search.** Last resort. Grep atom bodies and wiki page bodies for keyword matches.

Cap initial retrieval at ~30 candidates. Quality > recall — the model can synthesize from 10 well-chosen atoms better than 100 vaguely-relevant ones.

### 2. Read candidates

For each retrieved atom or wiki page:

- Read the full file (frontmatter + body) — these are small.
- Note the confidence and status. Skip `superseded` and `archived` atoms unless the user explicitly asks for historical context.
- Note source citations — they may need to be quoted in the answer.

### 3. Detect coverage

Before synthesizing, check whether the candidates actually cover the question:

- **Full coverage:** ≥3 high-confidence atoms (≥0.80) directly relevant. Proceed to synthesis.
- **Partial coverage:** some atoms relevant, but key sub-questions unanswered. Synthesize what's there and explicitly note the gaps.
- **Thin coverage:** fewer than 2 relevant atoms, or all relevant atoms are low-confidence drafts. Don't fabricate. Surface the gap.
- **Contradictory coverage:** atoms with conflicting claims. Surface both sides; don't pick a winner without explicit evidence.

A "knowledge gap" answer is a valid output. It's better than a confident hallucination.

### 4. Synthesize the answer

Compose a synthesis grounded in the cited atoms. Rules:

- **Every factual claim cites at least one source.** Inline `[[atom-id]]` AND numbered `[N]`. Two citation forms because they serve different readers — Obsidian users want clickable wikilinks, LLM-consumers want numeric refs.
- **Lead with the answer.** No throat-clearing. Two or three sentences that directly answer the question, then expand.
- **Match the question's specificity.** A specific question deserves a specific answer. Don't pad a one-line answer into three paragraphs.
- **Quote evidence sparingly.** Paraphrase atoms; quote only when wording matters (statutes, definitions, exact figures).
- **Surface contradictions.** If atoms disagree, render both sides with attribution. Don't paper over disagreement.
- **Reflect confidence.** Hedge proportionally. "The wiki's clearest claim is X [1], though Y is also recorded with lower confidence [2]" beats false certainty.
- **Note gaps.** If part of the question isn't covered, say so — and suggest which sources to ingest to close it.

### 5. Format

```markdown
**Answer:**

{{1-3 sentences directly addressing the question, with [[atom-id]] [N] citations.}}

{{Optional: expand with additional context, still cited.}}

{{If contradictions or gaps exist:}}

> **Note:** {{atoms disagree on X — see [[atom-id]] [N] vs [[atom-id]] [N]}}
> OR
> **Gap:** the wiki does not cover {{specific aspect}}. Ingest {{source type}} to close this.

## References

1. **{{Atom title}}** — [[atom-20260423-008]] (confidence 0.85) — `raw/{{source}}`
2. **{{Atom title}}** — [[atom-20260423-015]] (confidence 0.72) — `raw/{{source}}`

{{If wiki pages cited, list separately:}}

## Also from

- [[wiki/process/intake-three-gate-model]] — {{one-line summary}}
```

### 6. Optional save

If `--save` was passed (or the user confirms when offered), persist the answer to `wiki/queries/`.

**Filename:** `wiki/queries/YYYY-MM-DD-<slug>.md`. Slug derived from the question, kebab-case, max 60 chars. If a query with the same slug exists today, append `-2`, `-3`, etc.

**Frontmatter:**

```yaml
---
title: "{{Question, rephrased as a noun phrase}}"
type: query
question: "{{Original question verbatim}}"
date-asked: YYYY-MM-DD
asker: human
atoms: [atom-20260423-008, atom-20260423-015]
confidence: high | medium | low  # rolled up from cited atoms
status: current
---
```

**Body:** the synthesized answer + reference list, exactly as it was shown to the user.

Saved queries become first-class wiki content:

- They appear in `index.md` after the next `compile`.
- They can be cited by future atoms (`reinforced-by: [query-20260423-001]`) — note the `query-` prefix to distinguish from atoms.
- They can be cited by other queries — recursive synthesis with attribution.

### 7. Stop gate before save

If `--save` was not passed, **offer it explicitly**:

```
Save this answer to wiki/queries/2026-05-21-can-the-three-gate-model-be-bypassed.md?

  - Adds the answer as a first-class wiki page, queryable by future searches.
  - Cites [[atom-20260423-008]], [[atom-20260423-015]], [[atom-20260423-022]].
  - Will appear in index.md on next /llm-wiki compile.

[y/N]
```

Default no. Most queries are one-shot — saving them all pollutes `wiki/queries/`. Save when the answer is reusable: a synthesis the user expects to reference, a defensible position, a recurring question.

### 8. Report

If saved:

```
Saved: wiki/queries/2026-05-21-can-the-three-gate-model-be-bypassed.md

The answer is now part of the wiki. To make it discoverable in index.md, run:
  /llm-wiki compile --page wiki/queries/2026-05-21-can-the-three-gate-model-be-bypassed
```

If not saved: no follow-up needed — the answer was in the chat output.

## Flags

- `--save` — write the answer to `wiki/queries/` without asking.
- `--no-save` — never offer save, even at the gate. Useful in scripted contexts.
- `--branch <branch>` — restrict retrieval to a single branch. Faster and more focused.
- `--include-drafts` — include draft-status atoms (excluded by default; their claims aren't yet reviewed).
- `--include-superseded` — include superseded atoms (for historical questions).
- `--max-citations <N>` — cap the reference list. Default 15. Past 15, the answer becomes unreadable.

## Citation discipline

The `query` command's value collapses if citations are unreliable. Rules:

- **Cite atoms, not raw sources.** Atoms have provenance; raw sources are inputs. If the user wants to read the source, they follow the atom's `sources:` field.
- **Don't cite atoms that don't directly support the claim.** Padding citations to look thorough is worse than acknowledging a gap.
- **Cite at the sentence or clause level, not the paragraph level.** A reader should be able to verify each claim independently.
- **If an atom is contradicted, surface it.** Don't quietly pick the higher-confidence atom; both belong in the answer.

## Anti-patterns

- **Hallucinating citations.** Every `[[atom-id]]` must resolve to an actual file. If you can't find a real atom that supports the claim, don't make up an ID — surface the gap.

- **Vector-style retrieval theatre.** This isn't RAG. Ripgrep on markdown is the index. Don't pretend the wiki has semantic search it doesn't have.

- **Generic salience.** Without purpose.md filtering, answers default to "what would a stranger find interesting". With purpose.md, answers filter for "what would Dale ask". Always thread purpose.md through the prompt.

- **Saving every query.** Most queries are one-shot. Saving exploratory questions floods `wiki/queries/` with noise. Save reusable answers, not all answers.

- **"I don't know" without surfacing the gap.** Acceptable to not have the answer. Unacceptable to leave the user without a path forward. Always suggest: *"Ingest {{source type}} or check {{related atom}}."*

- **Over-citing the same atom.** If `[[atom-A]]` supports five claims, cite it once or twice — not five times. Repetition is noise.

- **Skipping the contradictions surface.** A wiki with disputed atoms is healthier than one that pretends to be unanimous. `query` should expose disagreement, not paper over it.

- **Auto-saving without the gate.** The user must consciously choose to save. Auto-save buries decisions.

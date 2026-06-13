---
name: fan-out
description: Use when the user asks to investigate a complex or multi-faceted topic from several angles in parallel, or explicitly says "fan out", "parallel", "investigate from multiple angles", or similar. This skill decomposes the request into independent sub-investigations, dispatches sub-agents in parallel with tools matched to each subtask, applies adversarial adjudication to test and refine findings, synthesizes results into the output format implied by the original prompt, and uses a lightweight self-healing loop for failed or low-confidence subtasks. Chain to the deep-research skill for individual subtasks that need deep, multi-source, fact-checked research; deep-research may chain back to fan-out when a topic needs parallel investigation of distinct sub-questions.
compatibility: Requires Claude Code Agent tool and subagent support. Optional chaining to deep-research skill.
---

# fan-out

## Purpose

Fan-out turns one complex question into several parallel, scoped investigations and returns a single synthesized answer.

Use it when:
- The user explicitly asks for parallel work ("fan out", "parallel", "investigate from multiple angles").
- A single answer requires investigating independent dimensions (e.g., policy, technology, cost, risk).
- The user wants to compare approaches, vendors, options, or perspectives.
- A topic is too broad for one agent but each piece is independent.

Do **not** use it when:
- The request is a simple, one-step task ("read this file", "fix this typo").
- Sequential dependency exists between subtasks (use a plan instead).
- The user declines parallel decomposition.

## Relationship with deep-research

`fan-out` and `deep-research` are complementary. They should be aware of each other and chain appropriately.

| Skill | Specialty | Advantage | Disadvantage |
|-------|-----------|-----------|--------------|
| **deep-research** | Single-topic, deep, cited, adversarially-verified research | High confidence, thorough sourcing, handles one complex question end-to-end | Can be slow and expensive when the question spans many independent dimensions |
| **fan-out** | Parallel investigation of independent sub-questions | Faster coverage of multi-faceted problems, natural for comparisons | Less depth per angle unless paired with deep-research |

### When to chain between them

- **fan-out calls deep-research**: When a subtask needs deep, multi-source research with citations, spawn a sub-agent and instruct it to invoke `/deep-research` with the refined sub-question.
- **deep-research calls fan-out**: When the research question naturally splits into independent sub-questions (e.g., "compare X, Y, and Z" or "analyze risks across policy, technology, and delivery"), invoke `/fan-out` instead of trying to do everything serially.
- **Avoid deep nesting**: Never nest fan-out inside fan-out more than one level deep. If a sub-agent wants to fan out further, it should instead return a clear request for the parent to handle.

## Workflow

### 1. Confirm before fanning out

Before dispatching, briefly confirm the decomposition plan with the user unless:
- They explicitly used a trigger phrase ("fan out", "parallel", "investigate from multiple angles"), or
- The task is clearly complex and the benefit of parallel work is obvious.

If the request looks simple or the user may want a quick answer, say:

> "This looks like a quick one-step task. I can answer it directly, or I can fan it out into parallel investigations if you want broader coverage. Which would you prefer?"

Only proceed with fan-out if the user confirms, or if the trigger phrase makes their intent explicit.

### 2. Decompose

Break the request into 2-6 independent subtasks. Each subtask should:
- Be answerable independently.
- Have a clear scope and success criterion.
- Avoid overlapping with other subtasks to minimize duplicate work.

Use the user's language where possible. If they ask for "risks, costs, and policy implications," make those the subtasks.

Example decomposition for "compare Azure vs AWS vs GCP for hosting our DCCEEW application":
- **A**: Cost analysis (compute, storage, egress, support tiers)
- **B**: Compliance and certification (IRAP, ISM, Essential Eight mapping)
- **C**: Technical fit (managed services, Kubernetes, CI/CD, observability)
- **D**: Risk and lock-in (exit costs, data sovereignty, support quality)

### 3. Select tools per subtask

Assign a tool set to each sub-agent based on subtask type. Research agents should be read-only unless the user explicitly asked for edits.

| Subtask type | Tool set |
|--------------|----------|
| Research (web/docs) | WebFetch, WebSearch, Read, Grep, ReadMcpResourceTool |
| Code investigation | LSP, Grep, Read, Glob |
| File/data analysis | Read, Grep, Glob, Bash (read-only), xlsx/csv skills |
| Deep research | Instruct sub-agent to invoke `/deep-research` |
| Verification / adversarial | Grep, Read, WebFetch, WebSearch |

Avoid giving write tools to research-only sub-agents.

### 4. Dispatch in parallel

Spawn all sub-agents in the same turn using the Agent tool. Each sub-agent receives:

- The original user prompt (for context).
- Its specific subtask and success criterion.
- Its permitted tool set.
- The required output schema.
- A time budget (default 120s; increase for deep-research subtasks).

Sub-agents operate independently. Do not let them block each other.

### 5. Sub-agent output schema

Each sub-agent must return valid JSON with this structure:

```json
{
  "subtask_id": "A",
  "subtask_summary": "One-line description of the subtask",
  "status": "complete | partial | failed",
  "confidence": "high | medium | low",
  "findings": [
    {
      "claim": "Specific claim or finding",
      "evidence": "Source, file path, URL, or reasoning",
      "confidence": "high | medium | low"
    }
  ],
  "assumptions": ["Assumptions made"],
  "gaps": ["Information that could not be found"],
  "raw_notes": "Markdown notes for the synthesizer"
}
```

If the subtask invoked `/deep-research`, also include:

```json
{
  "deep_research_summary": {
    "key_citations": ["source 1", "source 2"],
    "confidence": "high | medium | low",
    "gaps": ["remaining gaps"]
  }
}
```

### 6. Synthesize

Choose a synthesis strategy automatically based on the subtask outputs:

| Pattern | When to use |
|---------|-------------|
| **Merge** | Independent facts with no conflict |
| **Compare** | Options, vendors, approaches, or perspectives being evaluated |
| **Adjudicate** | Conflicting claims between sub-agents |
| **Map-reduce** | Large outputs that need summarizing before final synthesis |

The default is **merge** unless the prompt signals comparison or contradictions appear.

### 7. Adversarial adjudication

Before final synthesis, spawn one or more adversarial reviewer agents to:
- Identify contradictions between sub-agent findings.
- Flag unsupported claims.
- Suggest additional evidence needed.
- Propose corrections or refinements.

The reviewer returns a JSON object:

```json
{
  "issues": [
    {
      "subtask_ids": ["A", "B"],
      "issue": "Contradiction or weakness",
      "severity": "high | medium | low",
      "suggested_fix": "Narrower re-scope or evidence to gather"
    }
  ],
  "overall_confidence": "high | medium | low"
}
```

If adjudication reveals significant gaps, invoke Ralph-loop lite before final synthesis.

### 8. Ralph-loop lite self-healing

For any subtask with `status: failed`, `confidence: low`, or flagged by adjudication with severity `high` or `medium`:

1. **Detect stalls early**: If a sub-agent has not produced output within **5 minutes** (or a shorter timeout you set per subtask), treat it as stalled. Do not wait indefinitely.
2. **Re-dispatch with narrower scope**: Split the failing or stalled subtask into smaller pieces and re-run. Pass the original failure reason as context.
3. **Reviewer-fix loop**: If re-dispatch alone is insufficient, spawn a reviewer agent to critique the weak output, then spawn a fix agent to address the critique.
4. **Fallback to direct execution**: If re-dispatch still fails, the parent agent should execute the subtask directly using the assigned tool set rather than blocking forever.

Stop after one healing round unless the user explicitly asks for more. Always surface what was healed and what remains unresolved.

### 9. Determine output format

Infer the right output format from the original prompt:

| Prompt signal | Output format |
|---------------|---------------|
| "compare", "versus", "pros/cons", "which is better" | Comparison table or decision matrix |
| "brief", "summary", "executive" | Executive summary + key findings |
| "report", "write up", "document" | Full markdown report with sections |
| "list", "options", "what are" | Ordered list with rationale |
| "recommend", "what should we do" | Recommendation + alternatives + risks |
| No strong signal | Structured synthesis with key findings and confidence |

### 10. Return final answer

Present:
- A concise synthesis tailored to the inferred output format.
- Per-subtask key findings (linked to `subtask_id`).
- Confidence level per finding.
- Gaps and limitations.
- Optional next steps.

Be honest about uncertainty. Do not paper over gaps or low-confidence claims.

## Examples

### Example 1: Parallel research

**User:** "Fan out and investigate the risks, costs, and policy implications of moving EPBC Act capabilities to NEPA."

**Decomposition:**
- **A**: Legal/policy risks and statutory constraints
- **B**: Cost implications and budget envelope impacts
- **C**: ICT delivery risks (systems, data migration, shared services)
- **D**: Stakeholder and transition risks

**Output:** Executive summary + four-section report with confidence ratings and gaps.

### Example 2: Option comparison

**User:** "Parallel: compare Azure, AWS, and GCP for hosting the new environment approvals portal."

**Decomposition:**
- **A**: Azure fit
- **B**: AWS fit
- **C**: GCP fit
- **D**: Cross-cloud comparison synthesis (adjudicator)

**Output:** Decision matrix + recommendation.

### Example 3: Deep-research integration

**User:** "Investigate from multiple angles whether the DTA's service standard applies to our proposed environment gateway."

**Decomposition:**
- **A**: Direct applicability of the DTA service standard (invoke `/deep-research`)
- **B**: DCCEEW precedent and waivers
- **C**: Risk of non-compliance

**Output:** Synthesized assessment with citations from subtask A and internal evidence from B and C.

## Anti-patterns

- Don't fan out a one-step task.
- Don't give write/delete tools to research-only sub-agents.
- Don't ignore low-confidence findings — surface them explicitly.
- Don't nest fan-out more than one level deep.
- Don't skip confirmation before fanning out on ambiguous requests.
- Don't let sub-agents return prose without the required JSON envelope.

## Quality checks

Before returning, verify:
- [ ] Each subtask returned a clear status and confidence.
- [ ] Conflicting claims have been adjudicated.
- [ ] Gaps are explicitly listed.
- [ ] Output format matches the user's implied intent.
- [ ] Deep-research was invoked for any subtask needing cited, multi-source research.
- [ ] Ralph-loop lite was applied to failed or low-confidence subtasks if appropriate.

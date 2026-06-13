# 5P Branches — classification taxonomy

Foundational reference. Loaded by `ingest`, `crawl`, `compile`, and `lint`. Defines how atoms are classified.

## The six branches

Every atom belongs to exactly one branch. Six branches: five for substance, one for the wiki's own machinery.

| Branch | Covers | Examples |
|---|---|---|
| `people` | Roles, capabilities, org structure, individuals | "Product Owner reports to CIO." "ICT Branch has 47 FTE." |
| `process` | Workflows, methodologies, governance, decision-making | "Intake uses a three-gate model." "ADRs require executive sign-off." |
| `policy` | Standards, ethics, risk frameworks, statutory basis | "All AI models require risk assessment." "EPBC Act s.84 mandates public comment." |
| `platform` | Architecture, tools, infrastructure, technical systems | "VDE runs on Azure." "PAS sunset target is FY2027." |
| `product` | Products, services, roadmaps, use cases, deliverables | "Wayfinder is priority 1 for 2026." "MDFD covers three modules." |
| `meta` | Wiki structure, conventions, the system itself | "Atoms use kebab-case filenames." "Branch `meta` is exempt from `sources:`." |

## Decision tree

When classifying a new atom, work down this tree. Stop at the first match.

```
Is the atom about the wiki itself (structure, conventions, taxonomy)?
  YES → meta
  NO ↓

Is the atom a statutory, regulatory, ethical, or standards claim?
  YES → policy
  NO ↓

Is the atom about a person, role, team, or org structure?
  YES → people
  NO ↓

Is the atom about a technical system, architecture, tool, or infrastructure?
  YES → platform
  NO ↓

Is the atom about a product, service, roadmap, or use case?
  YES → product
  NO ↓

Is the atom about how work gets done — workflow, governance, methodology?
  YES → process
  NO ↓

You haven't classified it. Either it's a meta atom (rare) or the claim is too vague — refine it before storing.
```

## Edge cases

### Statutory function delivered by a system

*"PAS supports EPBC Act s.84 public comment processing."*

The claim is about a system fulfilling a statutory obligation. The decision tree puts it under `platform` (the system) — `policy` covers the statutory mandate itself, separately.

Best practice: write two atoms.

1. `policy`: *"EPBC Act s.84 requires public comment processing for referrals."*
2. `platform`: *"PAS supports EPBC Act s.84 public comment processing."*

Link them via `reinforced-by`. The compiled wiki page on the s.84 function pulls in both.

### A person's role within a process

*"The Product Owner approves intake gate transitions."*

Person + process. Branch is `people` — the claim is about a role's authority. The process detail is part of the people atom's context.

If the claim is *"Intake gate transitions require Product Owner approval"*, that's `process` — the structure of the process is the subject. The role is incidental.

The test: what's the subject of the sentence? That's the branch.

### A policy implemented as a tool feature

*"GitHub branch protection enforces the two-reviewer policy."*

Two atoms again:

1. `policy`: *"All merges to main require two reviewer approvals."*
2. `platform`: *"GitHub branch protection enforces the two-reviewer policy."* (or even `process`, depending on framing)

The policy atom stands on its own; the platform atom describes the implementation.

### A roadmap commitment

*"Wayfinder Alpha entry is committed for 8 June 2026."*

`product`. Roadmaps are product claims, even when they include dates and dependencies.

If the claim is about *who* committed it (*"The CIO committed to Wayfinder Alpha for 8 June 2026"*), the subject is the commitment from a person, but the substance is the product milestone. Still `product`.

### Pure facts about an individual

*"Dale Rogers is the ICT Business and Governance Branch principal consultant."*

`people`. Role assignment.

### Wiki conventions

*"Atom IDs follow `atom-YYYYMMDD-NNN` format."*

`meta`. The atom is about the wiki's own machinery.

## Branch as folder

Branches map directly to folders under `atoms/`:

```
atoms/
├── people/
├── process/
├── policy/
├── platform/
├── product/
└── meta/
```

The branch frontmatter field must match the folder. `lint` flags mismatches.

The compiled `wiki/` mirrors the same structure plus three orthogonal "page-type" folders (`synthesis/`, `comparisons/`, `queries/`) for content that crosscuts branches.

## Why these six

The 5P taxonomy (People / Process / Policy / Platform / Product) is Dale's preferred breakdown for consulting and government knowledge bases. It's deliberately coarser than typical enterprise architecture frameworks (TOGAF, ArchiMate) because atom-level classification gets unwieldy with more than ~6 branches.

The `meta` branch was added so wiki conventions live inside the wiki without polluting any of the five substantive branches.

Adding a seventh branch is a structural change — update `schema.md`, update lint rules, update this file, and re-run `lint` to surface mis-classifications.

## Anti-patterns

- **Branch tied to source folder.** A document in `papers/regulation/` ingests to atoms across many branches. The folder hint is one signal, not the answer.
- **Multi-branch atoms.** No such thing. If an atom feels like two branches, it's two atoms.
- **`meta` for "anything else."** `meta` is for *wiki-about-wiki* claims only. A claim about Dale's preference for short meetings is not `meta` — it's `people` (or possibly nothing the wiki cares about).
- **Skipping the decision tree.** Working from intuition produces inconsistent classification. The tree is short for a reason — use it.

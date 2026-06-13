# MIGRATION.md — {{WIKI_NAME}}

Artefact migration manifest. Governs the movement of source records into
this llm-wiki.

## Protocol

1. **Copy** file verbatim to `raw/` — no edits, no reformatting
2. **Add** entry to `raw/_provenance.md` (source path, copy date, context)
3. **Create** or update processed entry in `knowledge/`
4. **Update** this row: status = done

## Migration Queue

| Source Path | raw/ filename | knowledge/ path | Type | Status | Priority |
|-------------|---------------|-----------------|------|--------|----------|
| <!-- example: project/docs/arch.md --> | <!-- arch.md --> | <!-- knowledge/tech/architecture.md --> | <!-- blueprint --> | pending | high |

### Type Definitions

| Type | Description |
|------|-------------|
| `blueprint` | Service designs, architecture docs, HLDs |
| `concept` | Explanations, patterns, principles, how-tos |
| `decision` | ADRs, decision records, RFCs |
| `research` | User research, findings, analysis |
| `reference` | API docs, specifications, standards |
| `case-study` | Project retrospectives, PoCs, post-mortems |

### Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Identified, awaiting migration |
| `migrating` | In progress |
| `done` | Copied to raw/, processed to knowledge/ |
| `archived` | Decided not to migrate (see notes) |

### Priority Guidelines

| Priority | When to Use |
|----------|-------------|
| `high` | Architecture, decisions, patterns — reusable knowledge |
| `medium` | Research, references, guides — useful context |
| `low` | Transcripts, ephemeral docs, duplicates — optional |

## Archive Decisions

Files intentionally not migrated:

| File | Location | Reason |
|------|----------|--------|
| <!-- example: project/temp/notes.md --> | <!-- archive/ --> | <!-- ephemeral draft --> |

## Notes

- Use `llm-wiki-crawl` to discover migration candidates
- Use `llm-wiki-maintain` to validate completeness
- Keep this file updated as migration progresses

---
title: "Provenance Registry"
last-updated: {{DATE}}
---

# Provenance — {{WIKI_NAME}}

Source tracking for everything in `raw/`. Every file gets a row when it's ingested. Once written, rows are append-only — never edit existing entries.

If a source changes, add a new row with the updated filename (date-suffixed), not an edit to the old row.

## Registry

| Raw file | Source path / URL | Ingest date | Author / origin | Context | Processed → atoms |
|---|---|---|---|---|---|
| _example.md_ | _e.g._ `~/Downloads/intake-policy-v3.pdf` | 2026-05-21 | Internal DCCEEW policy team | Intake gate model documentation | `atoms/process/intake-uses-three-gate-model.md`, `atoms/policy/intake-requires-executive-approval.md` |

<!-- Add new rows below this comment. Never edit existing rows. -->

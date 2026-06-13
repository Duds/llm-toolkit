# PDF + Markdown Dual-Layer Standard

## What it is

A PDF that carries its Markdown source as an embedded file attachment. The PDF is the presentation layer (human-readable, printable, shareable). The `.md` attachment is the semantic layer (machine-readable, LLM-ready, version-controllable).

Both travel together in a single file. Neither requires the other to work independently.

## When to apply

Apply this pattern when a document will be:

- **Ingested by an AI pipeline** — RAG, search indexing, summarisation, or agentic workflows
- **Authored in Markdown first** — operating model canvases, policy docs, process guides
- **Shared externally** — where the recipient may want to repurpose the content

Do not apply it to:

- Scanned PDFs (no Markdown source exists)
- PDFs generated entirely from structured data (use the data source directly)
- Ephemeral documents not intended for reuse

## Conventions

### Attachment naming

The embedded file must be named `<pdf-basename>.md`. For example:

| PDF filename | Embedded attachment name |
|---|---|
| `ai-product-factory-overview.pdf` | `ai-product-factory-overview.md` |
| `2026-04-20-weekly-brief.pdf` | `2026-04-20-weekly-brief.md` |

This convention allows consumers to match the attachment to the PDF without ambiguity.

### Metadata

Set the following XMP/PDF metadata when embedding:

| Field | Value |
|---|---|
| `dc:source` | Path or identifier of the original `.md` file |
| `dc:format` | `application/pdf` |
| Custom: `x-md-embedded` | `true` |

### Markdown content requirements

The embedded `.md` must be:

- **UTF-8 encoded**
- **Self-contained** — no relative image links or includes that require external files
- **Semantically complete** — headings, tables, and lists preserved; do not flatten to plain prose

## Consumption workflow

```
Read PDF
  ↓
Check attachments for *.md
  ↓ found          ↓ not found
Extract .md      Fall back to PDF text extraction
  ↓
Pass .md to LLM / index / pipeline
```

This allows graceful fallback: if the `.md` layer is absent, the consumer still works — just with lower-fidelity input.

## Tooling

Use the `pdf-md` skill in Claude Code, which wraps `pdf_md.py`:

```bash
# Embed
python pdf_md.py embed <input.pdf> <source.md> [-o output.pdf]

# Extract
python pdf_md.py extract <input.pdf> [-o output.md]

# Check
python pdf_md.py check <input.pdf>
```

Requires: `pypdf >= 4.0` (`pip install pypdf`)

## Lifecycle

When the source `.md` is updated, re-embed and redistribute the PDF. The PDF and `.md` attachment should always be in sync — treat them as a single artefact, not two separate files.

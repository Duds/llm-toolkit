---
name: write-doc
description: >-
  Produce a branded, client-ready Word document (.docx) in Dale Rogers' personal
  style. Use this skill whenever the user asks for a Word doc, a written deliverable,
  a strategy brief, a proposal, a report, a memo, a briefing note, or any professional
  document output. Trigger on: "write me a doc", "make this a Word doc", "produce a
  brief", "write a proposal", "write a report", "Word output", "client document",
  "send this as a doc". Also trigger when another skill produces structured content
  and needs to render it as a .docx. Chains dale-style-guide for voice/brand and
  docx for file generation. Do NOT use for PowerPoint (use html2pptx), spreadsheets
  (use xlsx), or PDFs.
---

# write-doc — Branded Word Document Skill

## Purpose

Produce a professional .docx deliverable that applies Dale Rogers' brand (typography,
colour, voice) and is ready to send to a client or collaborator without further editing.

Chains: `dale-style-guide` (brand tokens, voice rules) → `docx` (file generation)

---

## Intake (Step 1)

Before writing, confirm:

1. **Document type** — which template to use:
   - `brief` — Strategy brief or findings summary (most common)
   - `proposal` — Engagement proposal or statement of work
   - `report` — Multi-section research or evaluation report
   - `memo` — Short briefing note or internal communication
2. **Recipient / audience** — governs formality and assumed knowledge
3. **Content** — either provided by the user, or generate from a description

If any of these are missing, ask once before proceeding. Don't ask for information
already present in the conversation context.

---

## Style rules (Step 2)

Apply `dale-style-guide` voice rules to all content before generating the file:

- Lead with the answer — context follows
- Bold the single most important phrase per section
- Three sentences maximum per paragraph
- Short sentences. Active voice. Concrete nouns.
- Australian English. Metric. DD/MM/YYYY.
- Never: "delve", "tapestry", "vibrant", "landscape", "realm", "embark",
  "navigate", "dive into", "moreover", "arguably", "it's important to note"

---

## Document structure (Step 3)

### brief
```
Cover: title, recipient, date, Dale Rogers
Executive Summary (3–5 sentences)
Context (1–2 paragraphs)
Findings / Analysis (2–4 sections with H2 headings)
Recommendations (bulleted)
Next steps (numbered, owner + timeframe)
```

### proposal
```
Cover: title, recipient, date, Dale Rogers
Overview (JTBD framing — what job this proposal is hired to do)
Scope of work (numbered deliverables)
Approach (3–5 stages, each with a H2 heading)
Investment (table: item | rate | estimate | total)
Terms (1–2 paragraphs)
Next steps
```

### report
```
Cover: title, version, date, Dale Rogers
Table of Contents (auto-generated)
Executive Summary
[Body sections per content]
Appendices (if required)
```

### memo
```
Header block: To | From | Date | Subject
Body (2–5 paragraphs, no headings needed for short memos)
Action required (bulleted, if applicable)
```

---

## File generation (Step 4)

Generate a `generate-doc.js` script using `docx-js`. Run it with Node.js to
produce the .docx, then validate. See `references/brand-tokens.md` for the
full docx-js token reference.

### Brand constants

```javascript
// Fonts — Arial is the docx-safe fallback for Inter
const FONT = "Arial";
const FONT_MONO = "Courier New";

// Colours (hex, no #)
const NAVY       = "1A1A2E";  // brand-primary — headings, body text
const NAVY_MID   = "16213E";  // brand-secondary — subtle accents
const BLUE       = "0F3460";  // brand-accent — H2, table headers
const CORAL      = "E94560";  // brand-highlight — accents, borders
const SURFACE    = "F5F5F5";  // brand-surface — table shading, callouts
const WHITE      = "FFFFFF";
const BORDER     = "CCCCCC";  // neutral border

// Sizes (half-points: 22 = 11pt, 24 = 12pt, 28 = 14pt, 32 = 16pt, 36 = 18pt)
const SIZE_BODY  = 22;  // 11pt
const SIZE_H2    = 28;  // 14pt
const SIZE_H1    = 36;  // 18pt
const SIZE_COVER = 48;  // 24pt

// Page — A4 (docx-js default; 11906 × 16838 DXA)
const MARGIN     = 1440;  // 1 inch
const CONTENT_W  = 9026;  // A4 content width at 1" margins
```

### Styles block

```javascript
styles: {
  default: {
    document: { run: { font: FONT, size: SIZE_BODY, color: NAVY } }
  },
  paragraphStyles: [
    {
      id: "Heading1", name: "Heading 1",
      basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: SIZE_H1, bold: true, font: FONT, color: NAVY },
      paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0 }
    },
    {
      id: "Heading2", name: "Heading 2",
      basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: SIZE_H2, bold: true, font: FONT, color: BLUE },
      paragraph: { spacing: { before: 280, after: 80 }, outlineLevel: 1 }
    },
    {
      id: "Heading3", name: "Heading 3",
      basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: SIZE_BODY, bold: true, font: FONT, color: NAVY_MID },
      paragraph: { spacing: { before: 200, after: 60 }, outlineLevel: 2 }
    },
  ]
}
```

### Header / footer

```javascript
headers: {
  default: new Header({
    children: [new Paragraph({
      children: [new TextRun({ text: "Dale Rogers", font: FONT, size: 18, color: NAVY, bold: true })],
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: CORAL, space: 4 } }
    })]
  })
},
footers: {
  default: new Footer({
    children: [new Paragraph({
      children: [
        new TextRun({ text: "hello@dalerogers.com.au", font: FONT, size: 16, color: NAVY_MID }),
        new TextRun({ text: "    |    Page ", font: FONT, size: 16, color: NAVY_MID }),
        new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: NAVY_MID }),
      ],
    })]
  })
}
```

### Cover page pattern

```javascript
// Title block — no header/footer on cover page (set headers: {} on section 0)
new Paragraph({
  children: [new TextRun({ text: title, font: FONT, size: SIZE_COVER, bold: true, color: NAVY })],
  spacing: { before: 2880, after: 480 }  // 2 inches before, visual weight
}),
new Paragraph({
  children: [new TextRun({ text: recipient, font: FONT, size: 24, color: NAVY_MID })]
}),
new Paragraph({
  children: [new TextRun({ text: `Prepared by Dale Rogers`, font: FONT, size: 24, color: BLUE })]
}),
new Paragraph({
  children: [new TextRun({ text: date, font: FONT, size: 22, color: NAVY_MID })]  // DD/MM/YYYY
}),
new Paragraph({ children: [new PageBreak()] }),
```

### Accent paragraph (callout / highlight box)

Use for key findings, recommendations, or summary callouts:

```javascript
new Paragraph({
  children: [new TextRun({ text: calloutText, font: FONT, size: SIZE_BODY, color: NAVY, bold: true })],
  border: { left: { style: BorderStyle.SINGLE, size: 12, color: CORAL, space: 8 } },
  indent: { left: 360 },
  spacing: { before: 120, after: 120 },
  shading: { fill: SURFACE, type: ShadingType.CLEAR }
})
```

### Table pattern (for investment / comparison tables)

```javascript
new Table({
  width: { size: CONTENT_W, type: WidthType.DXA },
  columnWidths: [/* must sum to CONTENT_W */],
  rows: [
    // Header row
    new TableRow({
      tableHeader: true,
      children: cols.map(label => new TableCell({
        width: { size: colWidth, type: WidthType.DXA },
        shading: { fill: BLUE, type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        borders: { top: none, bottom: none, left: none, right: none },
        children: [new Paragraph({
          children: [new TextRun({ text: label, font: FONT, size: SIZE_BODY, bold: true, color: WHITE })]
        })]
      }))
    }),
    // Data rows — alternate shading: SURFACE / WHITE
  ]
})
```

---

## Generation and validation (Step 5)

```bash
# Install docx if not present
npm list -g docx | grep docx || npm install -g docx

# Generate
node generate-doc.js

# Validate
python ~/Documents/projects/claude-resources/public/docx/scripts/office/validate.py output.docx
```

If validation fails: unpack → inspect XML → fix → repack using the `docx` skill's
editing workflow.

---

## Output and delivery (Step 6)

- Save to the current project directory as `[kebab-title]-[YYYYMMDD].docx`
- Report the full file path
- Ask: "Does this meet your needs, or should I adjust structure, tone, or formatting?"
- If the user confirms it's good: log a spike entry for candidate #7 in
  `ir5-os/research/spike-log.md` (first completed spike — mark it done)

---

## Close

After delivery:
- If anything in this run changed how you'd use `dale-style-guide` or `docx` in future:
  update the relevant skill now (standardisation step)
- If this was the first successful Word doc output: update `ir5-os/reference/framework-v0.2-working.md`
  to note P3 complete and Gap #6 (spike #7) resolved in the spike log

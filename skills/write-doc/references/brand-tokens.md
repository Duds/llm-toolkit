# Brand Tokens — docx-js Reference

Derived from `dale-style-guide` brand tokens, translated to docx-js values.
Use these constants in any `generate-doc.js` script rather than hardcoding values.

---

## Colours (hex, no #)

| Token | Hex | Use |
|-------|-----|-----|
| `NAVY` | `1A1A2E` | brand-primary — body text, H1 headings, cover title |
| `NAVY_MID` | `16213E` | brand-secondary — subtle accents, footer text, H3 headings |
| `BLUE` | `0F3460` | brand-accent — H2 headings, table header backgrounds |
| `CORAL` | `E94560` | brand-highlight — left-border accents, callout bars, header rule |
| `SURFACE` | `F5F5F5` | brand-surface — table row shading, callout backgrounds |
| `WHITE` | `FFFFFF` | table header text (on BLUE backgrounds) |
| `BORDER` | `CCCCCC` | neutral table borders |

---

## Typography

| Token | Value | Why |
|-------|-------|-----|
| `FONT` | `"Arial"` | docx-safe fallback for Inter (Inter not embeddable without font files) |
| `FONT_MONO` | `"Courier New"` | docx-safe fallback for JetBrains Mono |

---

## Font sizes (half-points)

| Token | Half-points | Points | Use |
|-------|-------------|--------|-----|
| `SIZE_SMALL` | `18` | 9pt | captions, footnotes |
| `SIZE_BODY` | `22` | 11pt | body text default |
| `SIZE_H3` | `22` | 11pt | H3 (bold body) |
| `SIZE_H2` | `28` | 14pt | H2 |
| `SIZE_H1` | `36` | 18pt | H1 |
| `SIZE_COVER` | `48` | 24pt | cover title |

---

## Page dimensions (DXA, 1440 DXA = 1 inch)

| Token | DXA | Notes |
|-------|-----|-------|
| `MARGIN` | `1440` | 1 inch — all four sides |
| `CONTENT_W` | `9026` | A4 content width at 1" margins (11906 − 2880) |
| `CONTENT_H` | `13958` | A4 content height at 1" margins (16838 − 2880) |

A4 is the Australian standard. docx-js defaults to A4 — confirm page size is not
overridden unless the document is explicitly for a US recipient.

---

## Spacing (DXA)

| Use | Value | Notes |
|-----|-------|-------|
| Paragraph spacing after H1 | `spacing: { before: 360, after: 120 }` | |
| Paragraph spacing after H2 | `spacing: { before: 280, after: 80 }` | |
| Body paragraph spacing | `spacing: { before: 0, after: 160 }` | |
| Cover title top offset | `spacing: { before: 2880 }` | 2 inch visual weight |
| Cell padding | `margins: { top: 80, bottom: 80, left: 120, right: 120 }` | |

---

## Numbering config (copy verbatim)

```javascript
numbering: {
  config: [
    {
      reference: "bullets",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
    },
    {
      reference: "numbers",
      levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
    },
  ]
}
```

---

## Quick patterns

**Body paragraph:**
```javascript
new Paragraph({
  spacing: { before: 0, after: 160 },
  children: [new TextRun({ text: "...", font: FONT, size: SIZE_BODY, color: NAVY })]
})
```

**Bold lead phrase:**
```javascript
new Paragraph({
  spacing: { before: 0, after: 160 },
  children: [
    new TextRun({ text: "Key insight. ", font: FONT, size: SIZE_BODY, color: NAVY, bold: true }),
    new TextRun({ text: "Supporting context follows.", font: FONT, size: SIZE_BODY, color: NAVY })
  ]
})
```

**Horizontal rule (CORAL — use instead of table-as-divider):**
```javascript
new Paragraph({
  children: [],
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: CORAL, space: 1 } },
  spacing: { after: 160 }
})
```

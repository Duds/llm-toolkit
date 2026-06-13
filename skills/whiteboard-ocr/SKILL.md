---
name: whiteboard-ocr
description: >
  Transcribe, parse, and structure content from whiteboard photos using a
  multimodal LLM pipeline. Use this skill whenever Dale uploads photos of
  whiteboards, handwritten notes, sticky-note walls, or workshop artefacts
  and wants them transcribed, structured, or turned into a usable document.
  Trigger on phrases like "transcribe this whiteboard", "read my whiteboard",
  "extract the notes from this photo", "turn this into a document", or
  whenever one or more whiteboard/handwriting images are present and the user
  wants content extracted. Also trigger when the user says "OCR this" or
  "parse this image" for handwritten content.
---

# Whiteboard OCR

## Purpose

Extract, structure, and clean content from whiteboard or handwritten images.

## Process

1. **Examine the image** — identify content regions:
   - Headings / titles
   - Lists or bullet points
   - Diagrams or flow arrows
   - Tables or grids
   - Sticky notes
   - Freehand sketches with labels

2. **Transcribe verbatim first** — capture exactly what's written,
   including abbreviations and shorthand. Don't interpret yet.

3. **Structure the output:**
   - Use headers for distinct sections
   - Use lists for bullet-point clusters
   - Use tables for grid content
   - Describe diagrams in plain language with directional arrows noted

4. **Clean up** — fix obvious spelling errors, expand clear abbreviations,
   but preserve the author's terminology and structure.

5. **Flag ambiguity** — if handwriting is illegible or content is unclear,
   mark with `[unclear]` rather than guessing.

## Output format

Default to Markdown. If the user wants a different format (DOCX, plain text),
apply the appropriate skill after transcription.

## Multi-image sessions

If multiple photos of the same whiteboard are provided, merge the transcriptions
into a single coherent document, noting any overlap or duplication.

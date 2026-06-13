---
name: pptx-editor
description: |
  Edit and refactor PowerPoint (.pptx) files programmatically using python-pptx.
  Use this skill when the user needs to: reorder slides, add sections, restructure
  deck narrative, batch modify slide content, or automate PowerPoint changes.
  
  Trigger phrases: "reorder slides", "restructure pptx", "add sections to powerpoint",
  "refactor deck", "reorganize presentation", "batch edit slides", "move slides",
  "create sections", "pptx automation", "programmatic powerpoint".
---

# PPTX Editor Skill

Programmatic PowerPoint editing using `python-pptx` with direct XML manipulation for operations not exposed in the high-level API.

## Prerequisites

```bash
pip install python-pptx lxml
```

## Quick Reference

### Python Path

Use `python3` (or `python` on Windows) when bash doesn't resolve the interpreter:

```bash
python3 script.py
```

### Load and Save

```python
from pptx import Presentation

prs = Presentation('input.pptx')
# ... make changes ...
prs.save('output.pptx')
```

### Quick Read Operations

```python
from pptx import Presentation

prs = Presentation('input.pptx')

# List all slides with titles
for idx, slide in enumerate(prs.slides, 1):
    title = next((s.text_frame.text[:80] for s in slide.shapes
                  if s.has_text_frame and s.text_frame.text.strip()), '(no title)')
    print(f"Slide {idx}: {title}")

# Extract all text from a slide
slide = prs.slides[0]
all_text = '\n'.join(s.text_frame.text for s in slide.shapes if s.has_text_frame)

# Check for notes
if slide.has_notes_slide:
    notes = slide.notes_slide.notes_text_frame.text
```

---

## Reading PPTX Content

Extract text, shapes, and structure from PowerPoint files:

### Extract All Text Content

```python
from pptx import Presentation

def extract_slide_content(pptx_path):
    """Extract text content from all slides."""
    prs = Presentation(pptx_path)
    slides_content = []

    for slide_num, slide in enumerate(prs.slides, 1):
        slide_data = {
            'slide_number': slide_num,
            'slide_id': slide.slide_id,
            'layout': slide.slide_layout.name if slide.slide_layout else None,
            'shapes': []
        }

        for shape in slide.shapes:
            shape_data = {
                'shape_type': str(shape.shape_type),
                'has_text_frame': shape.has_text_frame,
                'has_table': shape.has_table,
                'text': ''
            }

            if shape.has_text_frame:
                texts = []
                for paragraph in shape.text_frame.paragraphs:
                    para_text = ''.join(run.text for run in paragraph.runs)
                    if para_text.strip():
                        texts.append(para_text)
                shape_data['text'] = '\n'.join(texts)

            if shape.has_table:
                table_data = []
                table = shape.table
                for row in table.rows:
                    row_data = [cell.text for cell in row.cells]
                    table_data.append(row_data)
                shape_data['table'] = table_data

            slide_data['shapes'].append(shape_data)

        slides_content.append(slide_data)

    return slides_content


# Usage
content = extract_slide_content('input.pptx')
for slide in content:
    print(f"\n=== Slide {slide['slide_number']} ===")
    for shape in slide['shapes']:
        if shape['text']:
            print(shape['text'])
```

### Get Slide Titles

```python
def get_slide_titles(pptx_path):
    """Extract titles from all slides (first text shape with content)."""
    prs = Presentation(pptx_path)
    titles = []

    for idx, slide in enumerate(prs.slides, 1):
        title = None
        for shape in slide.shapes:
            if shape.has_text_frame:
                text = shape.text_frame.text.strip()
                if text:
                    title = text[:100]  # First 100 chars
                    break
        titles.append({'slide': idx, 'title': title or '(no title)'})

    return titles


# Usage
titles = get_slide_titles('input.pptx')
for t in titles:
    print(f"Slide {t['slide']}: {t['title']}")
```

### Extract Notes and Comments

```python
def extract_notes(pptx_path):
    """Extract speaker notes from all slides."""
    prs = Presentation(pptx_path)
    notes_data = []

    for idx, slide in enumerate(prs.slides, 1):
        note_text = ''
        if slide.has_notes_slide:
            notes_slide = slide.notes_slide
            if notes_slide.notes_text_frame:
                note_text = notes_slide.notes_text_frame.text.strip()

        notes_data.append({
            'slide': idx,
            'has_notes': slide.has_notes_slide,
            'notes': note_text
        })

    return notes_data


# Usage
notes = extract_notes('input.pptx')
for n in notes:
    if n['has_notes']:
        print(f"Slide {n['slide']} notes: {n['notes'][:200]}...")
```

### List Slide Layouts

```python
def list_layouts(pptx_path):
    """List all slide layouts in the presentation."""
    prs = Presentation(pptx_path)
    layouts = []

    for idx, layout in enumerate(prs.slide_layouts, 1):
        layouts.append({
            'index': idx,
            'name': layout.name,
            'slide_count': len(layout.slides) if hasattr(layout, 'slides') else 0
        })

    return layouts


# Usage
layouts = list_layouts('input.pptx')
for l in layouts:
    print(f"Layout {l['index']}: {l['name']}")
```

---

## Slide Reordering

`python-pptx` has no native `slides.move()` — manipulate `sldIdLst` directly:

```python
from pptx import Presentation
from pptx.oxml.ns import qn
from lxml import etree
import copy

prs = Presentation('input.pptx')
sldIdLst = prs.part._element.find(qn('p:sldIdLst'))
slide_ids = list(sldIdLst)

# Define new order: target_order[new_position] = original_index
target_order = [0, 2, 1, 3]  # Move slide 3 (index 2) to position 2

# Rebuild sldIdLst in target order
new_sldIdLst = etree.Element(qn('p:sldIdLst'))
for orig_idx in target_order:
    new_sldIdLst.append(copy.deepcopy(slide_ids[orig_idx]))

# Replace and save
parent = sldIdLst.getparent()
parent.replace(sldIdLst, new_sldIdLst)
prs.save('output.pptx')
```

### Get Slide Info

```python
for idx, slide in enumerate(prs.slides, 1):
    title = ""
    for shape in slide.shapes:
        if shape.has_text_frame:
            text = shape.text_frame.text.strip()
            if text:
                title = text[:80]
                break
    print(f"Slide {idx}: {title}")
```

---

## Adding Sections

PowerPoint sections organize slides into groups. `python-pptx` has no native section API — create `sectionLst` manually:

```python
from pptx import Presentation
from pptx.oxml.ns import qn
from lxml import etree

prs = Presentation('input.pptx')
pres_elem = prs.part._element
sldIdLst = pres_elem.find(qn('p:sldIdLst'))
slide_id_elems = list(sldIdLst)

# Create sectionLst after sldIdLst if it doesn't exist
sectionLst = pres_elem.find(qn('p:sectionLst'))
if sectionLst is None:
    sectionLst = etree.Element(qn('p:sectionLst'))
    sldIdLst.addnext(sectionLst)

# Define sections: (name, start_slide_index)
sections = [
    ("Introduction", 0),
    ("Main Content", 3),
    ("Appendix", 8),
]

for section_name, start_idx in sections:
    if start_idx < len(slide_id_elems):
        section = etree.SubElement(sectionLst, qn('p:section'))
        section.set('name', section_name)
        
        section_sldIdLst = etree.SubElement(section, qn('p:sldIdLst'))
        sldId = etree.SubElement(section_sldIdLst, qn('p:sldId'))
        
        # Copy the relationship ID from the first slide in this section
        first_slide = slide_id_elems[start_idx]
        slide_rId = first_slide.get(qn('r:id'))
        sldId.set('id', slide_rId)

prs.save('output.pptx')
```

---

## XML Element Reference

| Action | Element | Attribute/Notes |
|--------|---------|-----------------|
| Get root | `prs.part._element` | `<p:presentation>` |
| Find slide list | `prs.element.find(qn('p:sldIdLst'))` | `<p:sldIdLst>` |
| Slide ID | `slide_elem.get(qn('r:id'))` | Relationship ID like `rId6` |
| Slide count | `len(prs.slides)` | Number of slides |
| Slide by index | `prs.slides[index]` | 0-based indexing |
| Slide ID property | `slide.slide_id` | Unique slide identifier |
| Check notes | `slide.has_notes_slide` | Boolean |
| Access notes | `slide.notes_slide.notes_text_frame.text` | Speaker notes text |
| Reorder | `sldIdLst.remove(child)` & `insert(i, child)` | Manipulate list position |
| Add sections | `etree.Element(qn('p:sectionLst'))` | Must be after `sldIdLst` |
| Section name | `section.set('name', '...')` | Display name in PowerPoint |

---

## Common Patterns

### Reorder with Section Mapping

```python
# Define target order and which section each slide belongs to
target_order = [0, 1, 5, 2, 3, 4]  # Move slide 6 to position 3
sections_config = [
    ("Cover", 0),      # Slides 1-2
    ("Content", 2),    # Slides 3-5
    ("Appendix", 5),   # Slides 6+
]
```

### Verify Structure

```python
# Check sections were created
sectionLst = pres_elem.find(qn('p:sectionLst'))
if sectionLst is not None:
    for section in sectionLst:
        name = section.get('name')
        print(f"Section: {name}")
```

---

## Complete Example: Refactor Deck

```python
#!/usr/bin/env python3
"""Refactor PowerPoint deck: reorder slides and add sections."""

from pptx import Presentation
from pptx.oxml.ns import qn
from lxml import etree
import copy

# Load
prs = Presentation('input.pptx')
sldIdLst = prs.part._element.find(qn('p:sldIdLst'))
slide_ids = list(sldIdLst)

# Define new slide order (new_position -> original_index)
target_order = [0, 2, 1, 3, 4, 5]

# Reorder
new_sldIdLst = etree.Element(qn('p:sldIdLst'))
for orig_idx in target_order:
    new_sldIdLst.append(copy.deepcopy(slide_ids[orig_idx]))

parent = sldIdLst.getparent()
parent.replace(sldIdLst, new_sldIdLst)

# Add sections
pres_elem = prs.part._element
new_sldIdLst = pres_elem.find(qn('p:sldIdLst'))  # Get updated list
slide_id_elems = list(new_sldIdLst)

sectionLst = etree.Element(qn('p:sectionLst'))
new_sldIdLst.addnext(sectionLst)

sections = [("Intro", 0), ("Body", 2), ("End", 4)]
for name, start_idx in sections:
    if start_idx < len(slide_id_elems):
        section = etree.SubElement(sectionLst, qn('p:section'))
        section.set('name', name)
        sldIdLst_sec = etree.SubElement(section, qn('p:sldIdLst'))
        sldId = etree.SubElement(sldIdLst_sec, qn('p:sldId'))
        sldId.set('id', slide_id_elems[start_idx].get(qn('r:id')))

# Save
prs.save('output.pptx')
```

---

## Limitations

- `python-pptx` cannot natively reorder slides or manage sections — XML manipulation required
- Slide content editing (text, shapes) uses the high-level API; structural changes use XML
- Always work on copies; keep originals as backup

# Design Catalogue

Extended palette and visual-treatment options. SKILL.md has the core design rules and a starter palette set; this file is the deeper reference when you need more variety or specific aesthetics.

## Color Palettes

### Bold & Energetic

| Theme | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| **Pink & Purple** | `F8275B` (pink) | `FF574A` (coral) | `3D2F68` (deep purple) |
| **Retro Rainbow** | `722880` (purple) | `D72D51` (pink) | `EB5C18` (orange) / `F08800` (amber) / `DEB600` (gold) |
| **Vibrant Orange** | `F96D00` (orange) | `F2F2F2` (light gray) | `222831` (charcoal) |
| **Bold Red** | `C0392B` (red) | `E74C3C` (bright red) | `F39C12` (orange) / `F1C40F` (yellow) / `2ECC71` (green) |
| **Lime & Plum** | `7C3A5F` (plum) | `C5DE82` (lime) | `FD8C6E` (coral) / `98ACB5` (blue-gray) |

### Earthy & Natural

| Theme | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| **Vintage Earthy** | `3A6B35` (forest green) | `E3B448` (mustard) / `CBD18F` (sage) | `F4F1DE` (cream) |
| **Coastal Rose** | `AD7670` (old rose) | `B49886` (beaver) | `F3ECDC` (eggshell) / `BFD5BE` (ash gray) |
| **Sage & Terracotta** | `87A96B` (sage) | `E07A5F` (terracotta) | `F4F1DE` (cream) / `2C2C2C` (charcoal) |

### Premium & Editorial

| Theme | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| **Black & Gold** | `000000` (black) | `BF9A4A` (gold) | `F4F6F6` (cream) |
| **Burgundy Luxury** | `5D1D2E` (burgundy) | `951233` (crimson) | `C15937` (rust) / `997929` (gold) |
| **Deep Purple & Emerald** | `181B24` (dark blue) | `B165FB` (purple) | `40695B` (emerald) / `FFFFFF` (white) |

### Cool & Calm

| Theme | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| **Orange & Turquoise** | `667C6F` (grayish turquoise) | `FC993E` (light orange) | `FCFCFC` (white) |
| **Warm Blush** | `A49393` (mauve) | `EED6D3` (blush) / `E8B4B8` (rose) | `FAF7F2` (cream) |

(Core palettes — Midnight Executive, Forest & Moss, Coral Energy, Warm Terracotta, Ocean Gradient, Charcoal Minimal, Teal Trust, Berry & Cream, Sage Calm, Cherry Bold — live in [SKILL.md](SKILL.md#design-ideas).)

---

## Visual Treatment Menus

Pick *one or two* from each menu and commit to them across the deck. Mixing too many treatments produces visual noise.

### Geometric Patterns
- Diagonal section dividers instead of horizontal
- Asymmetric column widths (30/70, 40/60, 25/75)
- Rotated text headers at 90° or 270°
- Circular or hexagonal frames for images
- Triangular accent shapes in corners
- Overlapping shapes for depth

### Border & Frame Treatments
- Thick single-color borders (10-20pt) on one side only
- Double-line borders with contrasting colors
- Corner brackets instead of full frames
- L-shaped borders (top+left or bottom+right)
- Underline accents beneath headers (3-5pt thick)

> **NEVER use thin accent lines under titles.** This is a hallmark AI-tell. If you use an underline, make it bold and intentional (3pt+) or use whitespace/background color instead.

### Typography Treatments
- Extreme size contrast (72pt headlines vs 11pt body)
- All-caps headers with wide letter spacing
- Numbered sections in oversized display type
- Monospace (Courier New) for data/stats/technical content
- Condensed fonts (Arial Narrow) for dense information
- Outlined text for emphasis

### Chart & Data Styling
- Monochrome charts with single accent color for key data
- Horizontal bar charts instead of vertical
- Dot plots instead of bar charts
- Minimal gridlines or none at all
- Data labels directly on elements (no legends)
- Oversized numbers for key metrics

### Layout Innovations
- Full-bleed images with text overlays
- Sidebar column (20-30% width) for navigation/context
- Modular grid systems (3×3, 4×4 blocks)
- Z-pattern or F-pattern content flow
- Floating text boxes over colored shapes
- Magazine-style multi-column layouts

### Background Treatments
- Solid color blocks occupying 40-60% of slide
- Gradient fills (vertical or diagonal only)
- Split backgrounds (two colors, diagonal or vertical)
- Edge-to-edge color bands
- Negative space as a design element

---

## Match Layout to Content (Anti-Patterns)

Most layout failures are content-count mismatches, not visual choices. Count your items *before* you pick the layout.

| Content shape | Use | Don't use |
|---|---|---|
| Single unified narrative or one topic | Single-column or full-bleed | Multi-column (creates fake parallels) |
| Exactly 2 distinct items | Two-column | Three-column (forces filler), single-column (loses comparison) |
| Exactly 3 distinct items | Three-column | Two-column, four-up grid |
| 4+ items | Break across multiple slides, or grid | Cramming into 4-column |
| Real attributed quote | Quote layout | Decorative pull-quote (use quote layouts ONLY for actual quotes from real people, never for emphasis) |
| Image + supporting text | Image+text split | Image+text WITHOUT an actual image — empty placeholder is worse than no layout |
| Chart or table + narrative | Two-column (header full-width, text/chart side-by-side) OR full-slide chart | **NEVER vertically stack** narrative above a chart in one column — kills both |

### Workflow checks
1. **Count content pieces first.** Bullets, items, columns of data, named entities — count them before opening the template.
2. **Verify every placeholder will be filled with meaningful content.** No "Lorem ipsum," no "[insert here]," no "Add subtitle" left in place.
3. **Different template layouts have different shape counts.** When working from a template, list the placeholders for the chosen layout, then map content to them. Don't assume the next layout has the same slot count.
4. **If 4+ items don't fit, break into multiple slides** rather than shrinking everything to fit. Cramped slides are the #1 hallmark of bad decks.

---

## Inspecting an Example Design (Theme Extraction)

When given a reference presentation to emulate, extract its visual system before designing:

1. **Unpack and read the theme:**
   ```bash
   python scripts/office/unpack.py reference.pptx unpacked/
   ```
   Open `unpacked/ppt/theme/theme1.xml`. Look for:
   - `<a:clrScheme>` — the 12 named theme colors (dk1, lt1, dk2, lt2, accent1-6, hlink, folHlink)
   - `<a:fontScheme>` — major (heading) and minor (body) typefaces

2. **Sample actual slide usage:** theme files declare the palette but slides often override. Check `unpacked/ppt/slides/slide1.xml` for `<a:rPr>` (run properties — fonts, sizes, colors) and `<a:solidFill>` (actual fill colors used).

3. **Grep across all slides for color/font patterns:**
   ```bash
   grep -roh 'srgbClr val="[A-F0-9]*"' unpacked/ppt/slides/ | sort | uniq -c | sort -rn
   ```
   The most-used colors are the working palette; anything used once is incidental.

4. **Document what you find** before you start designing — a 4-line palette + 2-line typography note. Then build to it.

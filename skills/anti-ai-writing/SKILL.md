---
name: anti-ai-writing
description: >-
  Transform AI-assisted drafts into authentic, human-sounding content by
  eliminating AI tells and applying proven writing fundamentals. Use this
  skill whenever Dale asks to humanise writing, review a draft for AI
  patterns, write content that must not appear AI-generated, or produce prose
  in a specific author's voice. Also trigger when asked to "clean up" or
  "make this sound like me" — the AI tell scan and humanisation workflow
  apply even when not explicitly named.
---

# Anti-AI Writing

## The problem

AI writing has recognisable patterns: vague openers, padding phrases,
overuse of em-dashes, fake profundity, and the structural tic of listing
three parallel things.

## Banned patterns

**Openers to delete:**
- "In today's world..."
- "It's worth noting that..."
- "At the end of the day..."
- Any sentence starting with "Certainly" or "Absolutely"

**Filler phrases to cut:**
- "delve into", "tapestry", "vibrant", "landscape", "realm"
- "it's important to note", "based on the information provided"
- "as an AI", "as of my last update"
- "Moreover", "Furthermore", "In conclusion"

**Structural tells:**
- Listing exactly three parallel items as if it's a rule
- Every section ending with a one-line summary
- Headers on every paragraph

## Humanisation checklist

1. Does the first sentence earn attention? If not, cut it.
2. Is every sentence doing work? Delete the ones that aren't.
3. Are there any em-dashes used for effect rather than grammar? Cut them.
4. Does it sound like a person wrote it at a specific moment in time?
5. Read aloud — does it sound natural, or like a presentation?

## Process

### Phase 1: Rewrite

1. Scan for banned patterns — mark every instance.
2. Cut or rewrite each one.
3. Break long sentences. Vary sentence length deliberately.
4. Add one specific concrete detail that only the author would know.
5. Check the opening and closing — these are the most likely to be generic.

### Phase 2: Verify (mandatory — do not skip)

After rewriting, run these tool-assisted checks. Do not rely on memory or read-through alone.

**Check 1 — Em-dashes and en-dashes used as em-dashes:**
```bash
grep -n '[—–]' file.md
```
Every match is a candidate for replacement. Replace with period, colon, comma, or parentheses as grammatically appropriate. The only exceptions are:
- Title/subtitle separators ("Topic — Subtitle")
- Date/number ranges ("2024–2025", "N1–N4")

**Check 2 — Passive voice density:**
Scan for patterns like "was amended by", "has been completed", "is required". Convert to active voice ("I amended", "Ruth completed", "we need").

**Check 3 — Filler word count:**
Count occurrences of: "explicitly", "articulate", "leverage", "delve", "tapestry", "landscape", "realm", "going forward". If any appear more than once, cut or replace.

**Check 4 — Template residue:**
If the document has repeated structural patterns (e.g., every section ends with "Owner: ... Output: ..."), break the pattern. Vary endings.

**Check 5 — Sentence length variation:**
Read aloud. If every sentence is 15–25 words, break some into 5–8 word punch lines and extend others to 30+ words. Deliberate variation sounds human; consistent length sounds generated.

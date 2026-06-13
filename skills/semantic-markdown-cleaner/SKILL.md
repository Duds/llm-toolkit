---
name: semantic-markdown-cleaner
description: >
  Transform raw, unstructured text (emails, meeting notes, web extracts, PDF extracts,
  backlog items, whiteboard OCR text, etc.) into enriched, logically structured semantic
  Markdown. Always add YAML frontmatter. Ensure content remains verbatim but with semantic
  syntax. Comply with STANDARDS.md and llm-wiki requirements.

  Use this skill whenever the user pastes raw text, copies content from any source,
  asks to "clean up" or "format" text into markdown, wants to "structure" or "semantic-ify"
  content, or says anything like "make this markdown", "markdownify", "enrich this text",
  "format this properly", "structure this text", "clean up this raw text", or when they
  paste a block of unformatted text and want it organized. Also trigger when the user
  wants to convert meeting notes, email threads, PDF extracts, web page content, whiteboard
  photos (OCR'd text), backlog items, or any unstructured content into proper markdown.
---

# Semantic Markdown Cleaner

Transform raw, unstructured text into enriched, logically structured semantic Markdown while preserving content verbatim.

## Core Principles

1. **Verbatim preservation**: Never alter the actual words, sentences, or meaning of the source text. Only add structural syntax.
2. **Semantic enrichment**: Apply markdown syntax that reveals the implicit structure already present in the text.
3. **Logical hierarchy**: Infer headings, sections, and relationships from visual cues (whitespace, indentation, bullets, numbering, ALL CAPS, underlines, etc.).
4. **Always add frontmatter**: Every output file MUST include YAML frontmatter with appropriate metadata.
5. **Compliance**: Respect project-specific standards (STANDARDS.md, llm-wiki conventions) when present.
6. **ASCII-safe output**: Use plain ASCII characters where possible. Replace em-dashes (`—`) and en-dashes (`–`) with plain hyphens (`-`) to ensure compatibility across all markdown viewers and editors. Preserve special characters from source text only when they are part of the verbatim content.

## Workflow

### Step 1: Analyze the Source

Examine the raw text for these structural cues:

| Cue Type | What to Look For | Markdown Output |
|----------|------------------|-----------------|
| **Title** | First line, often ALL CAPS, centered, or followed by blank lines | `# Title` (H1) |
| **Section headers** | ALL CAPS, Title Case, underlined with `---` or `===`, or followed by colon and newline | `## Section` (H2) or `### Subsection` (H3) |
| **Lists** | Bullet characters (`-`, `*`, `•`), numbers, or letters | Unordered or ordered lists; nested if indented |
| **Action items** | Lines starting with action verbs or containing "TODO", "ACTION", "FOLLOW UP" | `- [ ] Action item` |
| **Decisions** | Phrases like "decided", "agreed", "resolved", "approved" | `> **Decision:** ...` blockquote |
| **Key terms** | First mention of important concepts, names, systems, or deliverables | `**key term**` |
| **Dates/times** | Any date or time reference | Preserve as-is; consider wrapping in backticks if structured |
| **Attendees/people** | Names with roles, email addresses | Consider table format |
| **Tables** | Space-aligned columns, tab-separated values, or CSV-like rows | Proper markdown table |
| **Code/technical** | File paths, commands, code snippets, JSON/XML | Fenced code block with language identifier |
| **Quotes** | Spoken words, attributed statements | `> Quote` blockquote |
| **Emphasis** | Words in ALL CAPS for emphasis (not headings) | `*emphasis*` or `**strong emphasis**` |

### Step 2: Detect Content Type

Infer the document type from structural patterns:

| Type | Identifiers | Frontmatter `type` | Special Handling |
|------|-------------|-------------------|------------------|
| **Meeting notes** | Attendees list, agenda items, time stamps, action items | `meeting` | Attendees table, decisions block, action items checklist |
| **Email/thread** | From/To/Date/Subject headers, quoted replies, signatures | `email` | Preserve thread structure with blockquotes |
| **Requirements** | "Shall", "Must", "Should", numbered requirements, acceptance criteria | `requirements` | Numbered lists, priority indicators |
| **Research/notes** | Informal, bullet-heavy, no clear agenda | `notes` | Liberal use of headings and lists |
| **Backlog item** | Title, description, acceptance criteria, tasks | `backlog` | Checkboxes for tasks, metadata fields |
| **Knowledge page** | Reference material, explanations, how-to content | `knowledge` | Diátaxis classification (`tutorial`, `how-to`, `explanation`, `reference`) |
| **Atom** | Single claim with evidence, confidence level | `atom` | 5P branch classification |
| **Raw source** | Scraped web content, transcript, unprocessed extract | `raw` | Minimal processing; preserve source URL if present |

### Step 3: Generate YAML Frontmatter

ALWAYS include YAML frontmatter at the top:

```yaml
---
title: "Inferred Title"
date: "YYYY-MM-DD"
type: "<detected_type>"
source: "<url/file/meeting_name if known>"
tags: ["inferred", "tags", "from", "content"]
---
```

**Required fields:**
- `title`: Infer from first line or generate descriptive title
- `date`: Extract from text or use today's date in `YYYY-MM-DD` format
- `type`: From content type detection table above

**Optional fields (add when present in source):**
- `source`: URL, filename, meeting name, or "pasted text"
- `author`: From email or meeting notes
- `tags`: 3-5 keywords summarizing content

**Project-specific compliance (EDR):**
If working in the `environment-digital-reform` project or any project with `_llm-wiki/`:

- For `knowledge` type: Add `diataxis: reference` (or `tutorial`, `how-to`, `explanation`)
- For `atom` type: Add `id`, `claim`, `branch`, `tags`, `date`, `sources`, `author`, `confidence`, `status`
- Valid branches: `people`, `process`, `policy`, `platform`, `product`, `meta`
- Valid statuses: `draft`, `review`, `approved`, `deprecated`

### Step 4: Apply Semantic Structure

**Headings hierarchy:**
- Use exactly one H1 (`#`) for the document title
- H2 (`##`) for major sections
- H3 (`###`) for subsections
- Never skip levels (don't go from H2 to H4)

**Lists:**
- Convert all bullet characters (`-`, `*`, `•`, `○`) to standard markdown `-`
- Preserve nesting by indenting 2 spaces per level
- Convert numbered lists to `1.`, `2.` etc.
- For action items: `- [ ] Action description`
- For completed actions: `- [x] Completed action`

**Tables:**
- Convert space-aligned or tabular data to proper markdown tables with `| col1 | col2 |`
- Add header separator `|---|---|`
- Left-align text, right-align numbers

**Emphasis:**
- Bold (`**`) for: key terms, names, system names, deliverables, decisions
- Italic (`*`) for: emphasis, foreign words, document titles
- Never bold entire paragraphs or headings

**Blockquotes:**
- Use `>` for: decisions, quotes, email replies, important callouts
- Nested quotes: `> >` for replies-to-replies

**Code:**
- Inline code (`` ` ``) for: file paths, commands, variable names, short snippets
- Fenced blocks (```` ``` ````) for: multi-line code, JSON, XML, logs
- Always specify language identifier when known

**Links:**
- Convert URLs to `[text](url)` format when text is descriptive
- Leave bare URLs as-is if no descriptive text available
- Create internal wiki links (`[[page-name]]`) when referencing known llm-wiki pages

### Step 5: Content Lifecycle Routing

Based on content type and project structure, suggest the appropriate destination:

| If content is... | Route to... |
|------------------|-------------|
| Raw, unprocessed source material | `_llm-wiki/raw/` |
| Processed knowledge, decisions, patterns | `_llm-wiki/knowledge/` |
| Atomic claim with evidence | `_llm-wiki/atoms/` |
| Working draft, WIP | `_working/` |
| Final deliverable | `deliverables/` |
| Meeting notes (internal) | `_working/` or `_archive/` |
| Backlog item | `TASKS.md` or workstream backlog |

### Step 6: Quality Checks

Before finalizing, verify:

- [ ] Content is verbatim (no words changed, added, or removed)
- [ ] Exactly one H1 heading
- [ ] Heading levels don't skip
- [ ] YAML frontmatter is present and valid
- [ ] Lists use consistent `-` bullets
- [ ] Tables have proper header separators
- [ ] Action items use `- [ ]` checkbox syntax
- [ ] Code blocks have language identifiers
- [ ] No trailing whitespace on lines
- [ ] File ends with single newline

## Special Cases

### Email Threads
- Preserve `From:`, `To:`, `Date:`, `Subject:` as bold labels
- Use nested blockquotes for reply chains
- Strip signatures sparingly (preserve if relevant)

### Whiteboard/OCR Text
- Fix obvious OCR errors only if confidence is high
- Group scattered text into logical sections
- Infer relationships from spatial layout (top-to-bottom, left-to-right)

### PDF Extracts
- Preserve page breaks as horizontal rules (`---`) if meaningful
- Handle multi-column layouts by reading left-to-right, top-to-bottom
- Convert footnotes to inline parentheticals or bottom section

### Backlog Items (Azure DevOps, Jira, etc.)
- Extract: ID, Title, Description, Acceptance Criteria, Tasks
- Format as structured markdown with checkboxes
- Preserve original field names as bold labels

### Meeting Notes with Multiple Topics
- Create H2 for each major topic
- Use H3 for sub-points
- Separate decisions and action items into distinct sections at the end

## Output Format

```markdown
---
title: "Document Title"
date: "2026-06-09"
type: "meeting"
source: "Weekly sync"
tags: ["epbc", "gateway", "decisions"]
---

# Document Title

## Section One

Content with **key terms** and *emphasis*.

- Bullet point one
- Bullet point two
  - Nested item

## Decisions

> **Decision:** We will proceed with option A.

## Action Items

- [ ] Follow up with ICTSD (@ian.mitchell)
- [ ] Draft business case by Friday

## Section Two

| Column A | Column B |
|----------|----------|
| Value 1  | Value 2  |
```

## Prompting the User

After generating the cleaned markdown:

1. **Present the result** with a brief summary of what was detected ("Detected meeting notes with 3 decisions and 5 action items")
2. **Suggest destination** based on content lifecycle routing
3. **Ask for confirmation** before saving: "Shall I save this to `_working/meeting-notes-2026-06-09.md`?"
4. **Offer refinements**: If the user wants changes, apply them without breaking the structure

## Examples

**Example 1: Raw meeting notes**

Input:
```
Team Sync - June 9

ATTENDEES
Dale, Brittany, Ian

AGENDA
1. Gateway update
2. NEPA timeline

DISCUSSION
Brittany said we need to move faster on the business case. Ian agreed and will check with David.

ACTIONS
Dale to draft by Friday
Brittany to review
```

Output:
```markdown
---
title: "Team Sync - June 9"
date: "2026-06-09"
type: "meeting"
source: "Team Sync"
tags: ["gateway", "nepa", "business-case"]
---

# Team Sync - June 9

## Attendees

| Name    | Role |
|---------|------|
| Dale    | —    |
| Brittany| —    |
| Ian     | —    |

## Agenda

1. Gateway update
2. NEPA timeline

## Discussion

**Brittany** said we need to move faster on the **business case**. **Ian** agreed and will check with **David**.

## Action Items

- [ ] **Dale** to draft by Friday
- [ ] **Brittany** to review
```

**Example 2: Email extract**

Input:
```
From: brittany.smith@dcceew.gov.au
To: dale.rogers@dcceew.gov.au
Subject: RE: Gateway scope

Dale,

Can you confirm the scope covers both determine AND prepare?

Thanks,
Brittany

> From: dale.rogers@dcceew.gov.au
> To: brittany.smith@dcceew.gov.au
> Subject: Gateway scope
>
> Yes, scope includes both.
```

Output:
```markdown
---
title: "RE: Gateway scope"
date: "2026-06-09"
type: "email"
source: "Email thread"
tags: ["gateway", "scope"]
---

# RE: Gateway scope

**From:** brittany.smith@dcceew.gov.au  
**To:** dale.rogers@dcceew.gov.au  
**Subject:** RE: Gateway scope

**Brittany** asked:

> Can you confirm the scope covers both **determine** AND **prepare**?

**Dale** replied:

> > Yes, scope includes both.
```

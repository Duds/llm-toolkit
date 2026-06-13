#!/bin/bash
#
# llm-wiki-bootstrap.sh
# Scaffold a new llm-wiki knowledge base
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REFS_DIR="$(dirname "$SCRIPT_DIR")/references"

# Usage
usage() {
    echo "Usage: $0 [OPTIONS] [PATH]"
    echo ""
    echo "Bootstrap a new llm-wiki knowledge base"
    echo ""
    echo "Options:"
    echo "  -n, --name NAME       Wiki name (default: derived from path)"
    echo "  -d, --desc DESC       Wiki description"
    echo "  --dry-run             Show what would be created, don't create"
    echo "  -h, --help            Show this help"
    echo ""
    echo "Path:"
    echo "  Target directory for llm-wiki (default: ./llm-wiki)"
    exit 1
}

# Parse arguments
WIKI_NAME=""
WIKI_DESC=""
DRY_RUN=false
TARGET_PATH=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            WIKI_NAME="$2"
            shift 2
            ;;
        -d|--desc)
            WIKI_DESC="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        -*)
            echo "Unknown option: $1"
            usage
            ;;
        *)
            TARGET_PATH="$1"
            shift
            ;;
    esac
done

# Default target
if [[ -z "$TARGET_PATH" ]]; then
    TARGET_PATH="./llm-wiki"
fi

# Convert to absolute path
TARGET_PATH="$(cd "$(dirname "$TARGET_PATH")" 2>/dev/null && pwd)/$(basename "$TARGET_PATH")"

# Derive name from path if not provided
if [[ -z "$WIKI_NAME" ]]; then
    WIKI_NAME=$(basename "$TARGET_PATH" | tr '-' ' ' | tr '_' ' ' | sed 's/.*/\L&/; s/[a-z]*/\u&/g')
fi

# Default description
if [[ -z "$WIKI_DESC" ]]; then
    WIKI_DESC="LLM-optimized knowledge base for ${WIKI_NAME}."
fi

# Check if target exists
if [[ -d "$TARGET_PATH" ]] && [[ -n "$(ls -A "$TARGET_PATH" 2>/dev/null)" ]]; then
    echo -e "${YELLOW}Warning: $TARGET_PATH already exists and is not empty${NC}"
    echo "Existing files will be preserved. New files will be added."
    if [[ "$DRY_RUN" == false ]]; then
        read -p "Continue? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Aborted."
            exit 1
        fi
    fi
fi

# Show dry run
if [[ "$DRY_RUN" == true ]]; then
    echo "DRY RUN - Would create:"
    echo "  Wiki path: $TARGET_PATH"
    echo "  Wiki name: $WIKI_NAME"
    echo "  Description: $WIKI_DESC"
    echo ""
    echo "  Files to create:"
    echo "    - CLAUDE.md"
    echo "    - README.md"
    echo "    - MIGRATION.md"
    echo "    - index.md"
    echo "    - log.md"
    echo "    - raw/_provenance.md"
    echo "    - knowledge/_template.md"
    echo "    - knowledge/README.md"
    echo "    - atoms/README.md"
    echo ""
    echo "  Directories to create:"
    echo "    - raw/"
    echo "    - raw/assets/"
    echo "    - knowledge/"
    echo "    - atoms/"
    exit 0
fi

# Create directories
echo "Creating directory structure..."
mkdir -p "$TARGET_PATH"/{raw/assets,knowledge,atoms}

# Get current date
CURRENT_DATE=$(date +%Y-%m-%d)

# Helper function to copy template with substitutions
copy_template() {
    local src="$1"
    local dest="$2"

    if [[ -f "$dest" ]]; then
        echo "  Skipping $dest (already exists)"
        return
    fi

    sed -e "s/{{WIKI_NAME}}/$WIKI_NAME/g" \
        -e "s/{{WIKI_DESCRIPTION}}/$WIKI_DESC/g" \
        -e "s/{{DATE}}/$CURRENT_DATE/g" \
        -e "s/{{TIMESTAMP}}/$(date -Iseconds)/g" \
        -e "s/{{PAGE_COUNT}}/0/g" \
        -e "s/{{WORD_COUNT}}/0/g" \
        -e "s/{{LAST_UPDATE}}/$CURRENT_DATE/g" \
        "$src" > "$dest"

    echo "  Created $dest"
}

# Create files from templates
echo "Creating files from templates..."

copy_template "$REFS_DIR/claude-md-template.md" "$TARGET_PATH/CLAUDE.md"
copy_template "$REFS_DIR/readme-template.md" "$TARGET_PATH/README.md"
copy_template "$REFS_DIR/migration-template.md" "$TARGET_PATH/MIGRATION.md"
copy_template "$REFS_DIR/index-template.md" "$TARGET_PATH/index.md"
copy_template "$REFS_DIR/provenance-template.md" "$TARGET_PATH/raw/_provenance.md"
copy_template "$REFS_DIR/knowledge-page-template.md" "$TARGET_PATH/knowledge/_template.md"

# Create log.md
cat > "$TARGET_PATH/log.md" << EOF
# Wiki Log

Append-only chronology of significant wiki events.

## $CURRENT_DATE

- Wiki bootstrapped at $TARGET_PATH
- Initial structure created

EOF
echo "  Created $TARGET_PATH/log.md"

# Create knowledge/README.md
cat > "$TARGET_PATH/knowledge/README.md" << EOF
# Knowledge Folder

Processed, LLM-readable knowledge pages.

## Organization

Organize by topic/domain:

```
knowledge/
├── topic-1/           # e.g., architecture, patterns
├── topic-2/           # e.g., case-studies, decisions
├── topic-3/           # e.g., research, reference
└── _meta/             # Wiki maintenance pages
```

## Creating Pages

1. Copy \`knowledge/_template.md\` to appropriate folder
2. Fill in frontmatter (title, date, tags, sources)
3. Write synthesized content
4. Add cross-references to related pages
5. Update \`index.md\` (or run maintenance)

## Page Standards

- One topic per file
- Use kebab-case filenames
- Include YAML frontmatter
- Cite \`raw/\` sources
- Cross-link related pages
EOF
echo "  Created $TARGET_PATH/knowledge/README.md"

# Create atoms/README.md
cat > "$TARGET_PATH/atoms/README.md" << EOF
# Atoms Folder (Optional)

Atomic claims for advanced knowledge graph use.

## When to Use Atoms

Atoms are single-claim files useful for:
- Complex knowledge bases with many interdependent facts
- Tracking confidence and supersession over time
- Building knowledge graphs with typed relationships

## Structure

\`\`\`yaml
---
claim: "Single-sentence factual claim"
date: YYYY-MM-DD
tags: [tag1, tag2]
sources: [raw/source.md]
confidence: 0.9
superseded-by: atoms/newer-claim.md
---
\`\`\`

## Simple vs. Atomic

For most wikis, \`knowledge/\` pages are sufficient. Use \`atoms/\` only when:
- You need granular fact tracking
- Claims evolve independently
- You're building a knowledge graph

Most users can ignore this folder.
EOF
echo "  Created $TARGET_PATH/atoms/README.md"

# Summary
echo ""
echo -e "${GREEN}LLM-Wiki bootstrapped successfully!${NC}"
echo ""
echo "Location: $TARGET_PATH"
echo ""
echo "Structure created:"
echo "  CLAUDE.md          - Wiki schema and instructions"
echo "  README.md          - Human guide"
echo "  MIGRATION.md       - Source tracking manifest"
echo "  index.md           - Content catalog"
echo "  log.md             - Append-only chronology"
echo "  raw/               - Immutable sources"
echo "  knowledge/         - Processed pages"
echo "  atoms/             - Atomic claims (optional)"
echo ""
echo "Next steps:"
echo "  1. Review CLAUDE.md and customize for your domain"
echo "  2. Run llm-wiki-crawl to discover existing content"
echo "  3. Add first source to raw/ and process to knowledge/"

#!/usr/bin/env bash
# validate-docs.sh
# Validates documentation structure and content

set -euo pipefail

ERRORS=0
WARNINGS=0

echo "=== Documentation Validation ==="
echo ""

# Check for README
if [[ ! -f "README.md" ]]; then
    echo "❌ ERROR: README.md not found"
    ((ERRORS++))
else
    echo "✓ README.md exists"

    # Check README sections
    for section in "Installation" "Usage" "Documentation"; do
        if grep -q "^## $section" README.md; then
            echo "  ✓ README has '$section' section"
        else
            echo "  ⚠ WARNING: README missing '$section' section"
            ((WARNINGS++))
        fi
    done
fi

echo ""

# Check for docs directory
if [[ -d "docs" ]]; then
    echo "✓ docs/ directory exists"

    # Check for broken internal links
    echo "  Checking internal links..."
    find docs -name "*.md" -exec grep -l '\[.*\](.*\.md)' {} \; | while read -r file; do
        grep -oP '\[.*?\]\(\K[^)]+\.md' "$file" | while read -r link; do
            target=$(dirname "$file")/$link
            if [[ ! -f "$target" ]]; then
                echo "  ❌ ERROR: Broken link in $file -> $link"
                ((ERRORS++))
            fi
        done
    done
else
    echo "⚠ WARNING: docs/ directory not found"
    ((WARNINGS++))
fi

echo ""

# Check ADR format if ADRs exist
if [[ -d "docs/adr" ]] || [[ -d "adr" ]]; then
    ADR_DIR=$( [[ -d "docs/adr" ]] && echo "docs/adr" || echo "adr" )
    echo "✓ ADR directory found: $ADR_DIR"

    for adr in "$ADR_DIR"/adr-*.md; do
        if [[ -f "$adr" ]]; then
            if grep -q "^## Status" "$adr"; then
                echo "  ✓ $(basename "$adr") has Status section"
            else
                echo "  ⚠ WARNING: $(basename "$adr") missing Status section"
                ((WARNINGS++))
            fi
        fi
    done
else
    echo "ℹ No ADR directory found (optional)"
fi

echo ""

# Check code examples
if [[ -d "docs" ]]; then
    echo "Checking code examples..."
    find docs -name "*.md" -exec grep -l '```' {} \; | while read -r file; do
        # Check for language specifiers
        if grep -q '```$' "$file"; then
            echo "  ⚠ WARNING: $file has code blocks without language specifier"
            ((WARNINGS++))
        fi
    done
fi

echo ""
echo "=== Validation Complete ==="
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"

if [[ $ERRORS -gt 0 ]]; then
    exit 1
fi

exit 0

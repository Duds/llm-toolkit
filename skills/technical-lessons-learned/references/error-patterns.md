# Error Patterns Reference

> Catalog of common errors encountered in Claude Code sessions with root causes and fixes.
> Last updated: 2026-04-23

---

## Python on Windows

### PW-1: Python Not on PATH

**Error:**
```
Exit code 127
/usr/bin/bash: line 19: : command not found
```

**Context:** Running `python` or `python3` in bash on Windows

**Root Cause:** Python is installed but not on the bash PATH. `which python` returns empty.

**Fix:**
```bash
# Use full path
PYTHON="C:/Users/$USER/AppData/Local/Programs/Python/Python312/python"
"$PYTHON" script.py
```

**Prevention:**
- Document Python path in project CLAUDE.md
- Create helper function in scripts
- Check Python exists before use

---

### PW-2: Path Format Mismatch

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: '/c/Users/...'
```

**Context:** Python file operations with bash-style paths

**Root Cause:** Python on Windows expects Windows paths (`C:\`), not bash paths (`/c/`).

**Fix:**
```python
# Good - Windows style with forward slashes
path = "C:/Users/$USER/Projects/file.txt"

# Bad - Bash style
path = "/c/Users/$USER/Projects/file.txt"
```

**Prevention:**
- Always use Windows-style paths in Python on Windows
- Add path normalization helper:
```python
def normalize_path(path):
    """Convert bash path to Windows path if needed."""
    if path.startswith('/c/'):
        return 'C:/' + path[3:]
    return path
```

---

### PW-3: Unicode Encoding Errors

**Error:**
```
UnicodeEncodeError: 'charmap' codec can't encode character '→' in position 6671
```

**Context:** Writing unicode characters on Windows

**Root Cause:** Windows default encoding is cp1252, not UTF-8.

**Fix:**
```python
# Always specify encoding
with open(file, 'w', encoding='utf-8') as f:
    f.write(content)
```

**Prevention:**
- Never use default encoding for file writes
- Avoid stdout redirection for unicode content
- Use file writes instead of shell redirections

---

### PW-4: Missing Dependencies

**Error:**
```
ModuleNotFoundError: No module named 'pandas'
ModuleNotFoundError: No module named 'tabulate'
```

**Context:** Running Python scripts with imports

**Root Cause:** Required package not installed.

**Fix:**
```bash
python -m pip install pandas openpyxl tabulate
```

**Prevention:**
- Create `requirements.txt`:
```
pandas>=2.0
openpyxl>=3.0
tabulate>=0.9
python-pptx>=0.6
```
- Add dependency check to scripts:
```python
def check_dependencies():
    required = ['pandas', 'openpyxl', 'pptx']
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print(f"Install: pip install {' '.join(missing)}")
        sys.exit(1)
```

---

## python-pptx

### PP-1: Wrong Import Name

**Error:**
```
ImportError: cannot import name 'RgbColor' from 'pptx.dml.color'
```

**Context:** Importing color classes

**Root Cause:** Wrong case - should be `RGBColor`, not `RgbColor`.

**Fix:**
```python
# Wrong
from pptx.dml.color import RgbColor

# Correct
from pptx.dml.color import RGBColor
```

**Prevention:**
- Check python-pptx documentation
- Test imports before full script execution

---

### PP-2: Slide Layout Index Out of Range

**Error:**
```
IndexError: slide layout index out of range
```

**Context:** Accessing slide layouts

**Root Cause:** Presentation has fewer layouts than expected.

**Fix:**
```python
# Check available layouts first
print(f"Layouts: {len(prs.slide_layouts)}")
for i, layout in enumerate(prs.slide_layouts):
    print(f"  {i}: {layout.name}")

# Use index 0 as safe default
blank_layout = prs.slide_layouts[0]
```

**Prevention:**
- Always check layout count before accessing
- Handle single-layout presentations

---

### PP-3: Invalid Shape Type

**Error:**
```
AttributeError: type object 'MSO_AUTO_SHAPE_TYPE' has no attribute 'STRAIGHT_CONNECTOR_1'
```

**Context:** Adding connector shapes

**Root Cause:** Enum value doesn't exist or wrong name.

**Fix:**
```python
# Use LINE instead of STRAIGHT_CONNECTOR_1
from pptx.enum.shapes import MSO_SHAPE

# Or use add_shape with LINE
line = slide.shapes.add_shape(
    MSO_SHAPE.LINE,
    Inches(1), Inches(1),
    Inches(2), Inches(0)
)
```

**Prevention:**
- Check valid enum values in docs
- Test shape creation separately
- Have visual fallback (omit connectors if not supported)

---

### PP-4: File Permission Denied

**Error:**
```
PermissionError: [Errno 13] Permission denied: '...pptx'
```

**Context:** Saving presentation

**Root Cause:** File is open in PowerPoint.

**Fix:**
- Close PowerPoint
- Or save to different filename

**Prevention:**
```python
import os

output_path = "presentation.pptx"
if os.path.exists(output_path):
    try:
        # Test if writable
        with open(output_path, 'a'):
            pass
    except PermissionError:
        output_path = "presentation_new.pptx"
        print(f"Original locked, saving to: {output_path}")
```

---

## File Operations

### FO-1: Office Temp Files

**Issue:** Files like `~$document.pptx` appear

**Context:** Office documents open

**Root Cause:** Office creates temp lock files.

**Impact:**
- Clutter in listings
- Scripts may process them

**Fix:**
```python
import glob

# Filter temp files
files = [f for f in glob.glob('*.pptx') if not f.startswith('~$')]
```

**Prevention:**
- Add to `.gitignore`:
```
~$*
```
- Filter in all file operations

---

### FO-2: Cross-Platform Path Issues

**Error:**
```
rm: cannot remove 'C:/Users/...': No such file or directory
```

**Context:** Using bash rm with Windows paths

**Root Cause:** Bash expects forward slashes but Windows paths may not work.

**Fix:**
```bash
# Use bash-style paths with rm
rm "/c/Users/$USER/Projects/file.txt"

# Or use PowerShell
powershell -Command "Remove-Item 'C:\Users\...'"
```

**Prevention:**
- Use consistent path style per tool
- Bash tools → bash paths (`/c/`)
- Python → Windows paths (`C:/`)
- PowerShell → Windows paths (`C:\`)

---

## Telemetry & Hooks

### TH-1: Hook Processing Errors

**Error:**
```
[2026-04-23T...Z] Read ERROR detected
[2026-04-23T...Z] Error type: unknown
```

**Context:** Hook executed but failed

**Root Cause:** Hook couldn't process tool response format.

**Fix:**
- Review hook script for JSON parsing
- Check for encoding issues
- Verify expected response schema

**Prevention:**
- Add try/except in hook scripts
- Log hook inputs for debugging
- Test with various response types

---

### TH-2: Telemetry Log Reading

**Issue:** Need to analyze telemetry for patterns

**Files:**
- `~/.claude/bash-audit.log` - Command history
- `~/.claude/telemetry/read-errors.log` - Read failures
- `~/.claude/telemetry/read-debug.log` - Debug info
- `~/.claude/telemetry/read-operations.log` - Operation flow

**Analysis:**
```bash
# Find errors
grep "ERROR" ~/.claude/telemetry/read-errors.log

# Count by type
grep "Error type:" ~/.claude/telemetry/read-errors.log | sort | uniq -c

# Find DENY commands
grep "\[DENY\]" ~/.claude/bash-audit.log
```

---

## Skill-Specific

### SC-1: Skill Not Triggering

**Symptoms:**
- User mentions skill topic
- Skill doesn't load
- Generic response given

**Diagnosis:**
1. Check skill description in SKILL.md
2. Verify skill is symlinked: `ls ~/.claude/skills/<name>/`
3. Check description covers user's phrasing

**Fix:**
- Update description with trigger phrases
- Add more "when to use" contexts
- Make description "pushy" (see skill-creator skill)

---

### SC-2: Skill Description Too Narrow

**Symptoms:**
- Skill triggers only on exact phrases
- Misses related contexts

**Fix:**
Expand description to include:
- Synonyms for key terms
- Related concepts
- Edge case scenarios
- Competing skills to differentiate from

Example:
```yaml
# Too narrow
description: Convert Visio files to Mermaid

# Better
description: >-
  Convert Visio (.vsd/.vsdx) files to Mermaid (.mmd) diagrams.
  Use whenever the user says "convert visio to mermaid", "vsd to mmd",
  "visio diagram conversion", "mermaid from visio", or needs to migrate
  Microsoft Visio diagrams to text-based Mermaid format for version control
  or documentation.
```

---

## Quick Reference Card

| Error | Likely Cause | Quick Fix |
|-------|-------------|-----------|
| `command not found` | Not on PATH | Use full path |
| `FileNotFoundError` | Wrong path format | Use Windows paths in Python |
| `UnicodeEncodeError` | cp1252 encoding | Add `encoding='utf-8'` |
| `ModuleNotFoundError` | Missing package | `pip install <pkg>` |
| `Permission denied` | File locked | Close app or rename |
| `IndexError` | Wrong layout index | Check `len(prs.slide_layouts)` |
| `AttributeError` on enum | Wrong name | Check documentation |
| `~$` files | Office temp | Filter with `not f.startswith('~$')` |

---

## Prevention Checklist

When writing scripts/skills:

- [ ] Test Python path on Windows
- [ ] Use Windows paths in Python file operations
- [ ] Specify `encoding='utf-8'` for all file writes
- [ ] Check dependencies exist
- [ ] Handle file permission errors gracefully
- [ ] Filter Office temp files
- [ ] Check array lengths before indexing
- [ ] Verify enum names in docs
- [ ] Test on Windows if applicable
- [ ] Document Windows-specific requirements

---
name: technical-lessons-learned
description: >-
  Capture and apply technical lessons learned from errors, telemetry, and skill-maker
  feedback. Use this skill whenever Dale says "lessons learned", "capture learning",
  "analyze errors", "review telemetry", "what went wrong", "error analysis",
  "skill improvement", or "improve this skill". Also trigger when Dale wants to
  understand patterns in failures, create error runbooks, or improve Claude Code
  workflows based on past mistakes. This skill analyzes bash errors, tool failures,
  telemetry logs, and skill-maker suggestions to create actionable improvements.
---

# Technical Lessons Learned

## Purpose

Analyze errors, telemetry, and skill-maker feedback to extract actionable lessons
and prevent future failures. This skill transforms reactive debugging into
proactive improvement by capturing patterns, root causes, and systemic fixes.

---

## When to Use

| Scenario | Action |
|----------|--------|
| Session had multiple errors | Run post-session analysis |
| Skill not triggering correctly | Analyze description + telemetry |
| Recurring tool failures | Check telemetry logs for patterns |
| User says "what went wrong" | Immediate error analysis |
| Skill needs improvement | Review maker suggestions + errors |
| Creating error runbook | Compile lessons into reference doc |

---

## Analysis Workflow

### Step 1: Gather Evidence

Read telemetry sources in parallel:

```
~/.claude/bash-audit.log           # All bash commands and results
~/.claude/telemetry/read-errors.log    # Read tool failures
~/.claude/telemetry/read-debug.log     # Read tool debug info
~/.claude/telemetry/read-operations.log # Read operation history
~/.claude/history.jsonl            # Session history (if needed)
```

Also check for session-specific logs:
- `~/.claude/projects/<project-dir>/*.jsonl` — session transcripts
- `~/.claude/sessions/` — session metadata

### Step 2: Categorize Errors

Group errors by type:

| Category | Examples | Root Cause Pattern |
|----------|----------|-------------------|
| **Path Issues** | File not found, permission denied | Wrong path format (bash vs Windows) |
| **Import Errors** | Module not found, attribute error | Missing dependencies, version mismatch |
| **Encoding Issues** | UnicodeEncodeError, codec errors | Default encoding on Windows (cp1252) |
| **Permission Errors** | Access denied, file locked | File open in another app, wrong perms |
| **Tool Misuse** | Invalid arguments, wrong flags | Skill documentation gaps |
| **Hook Failures** | Hook blocked, hook error | Hook logic errors, missing dependencies |

### Step 3: Extract Patterns

For each error category, identify:

1. **Immediate cause** — What exactly failed?
2. **Root cause** — Why did it fail?
3. **Contributing factors** — What made it worse?
4. **Systemic fix** — How do we prevent this class of errors?

### Step 4: Generate Lessons

Format each lesson as:

```markdown
### Lesson: [Brief Title]

**Error:** [What happened]

**Root Cause:** [Why it happened]

**Fix Applied:** [What fixed it]

**Prevention:** [How to avoid in future]

**Applies To:** [Which skills/workflows]
```

### Step 5: Update Artifacts

Apply lessons to:

1. **SKILL.md** — Update affected skills with prevention steps
2. **CLAUDE.md** — Add "Known Issues" section if not present
3. **References** — Create error runbook in `references/error-patterns.md`
4. **Hooks** — Add validation if error class is preventable

---

## Common Error Patterns & Solutions

### Pattern 1: Python Path Issues (Windows)

**Error:**
```
Exit code 127
/usr/bin/bash: line 19: : command not found
```

**Root Cause:**
Python is not on PATH in bash shell on Windows. `which python` returns empty.

**Solution:**
Use full path to Python executable:
```bash
PYTHON="C:/Users/$USER/AppData/Local/Programs/Python/Python312/python"
"$PYTHON" script.py
```

**Prevention:**
- Always use full path on Windows
- Check Python exists before running: `ls "$PYTHON" 2>/dev/null || echo "Python not found"`
- Document Python path in project CLAUDE.md

---

### Pattern 2: Windows Path Format Confusion

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: '/c/Users/...'
```

**Root Cause:**
Python on Windows expects Windows paths (`C:\Users\...`), not bash paths (`/c/Users/...`).

**Solution:**
Use Windows-style paths with forward slashes:
```python
# Good
path = "C:/Users/$USER/Projects/file.txt"

# Bad
path = "/c/Users/$USER/Projects/file.txt"
```

**Prevention:**
- Skills using Python must document path requirements
- Add path normalization helper in scripts

---

### Pattern 3: Unicode Encoding Errors

**Error:**
```
UnicodeEncodeError: 'charmap' codec can't encode character '→' in position 6671
```

**Root Cause:**
Windows default encoding is cp1252, not UTF-8. Writing special characters to stdout fails.

**Solution:**
Always specify encoding when opening files:
```python
# Good
with open(file, 'w', encoding='utf-8') as f:
    f.write(content)

# Bad
with open(file, 'w') as f:  # Uses default encoding
    f.write(content)
```

**Prevention:**
- Always use `encoding='utf-8'` for file operations
- Avoid stdout redirection for unicode content on Windows
- Use file writes instead of shell redirections

---

### Pattern 4: Missing Dependencies

**Error:**
```
ModuleNotFoundError: No module named 'pandas'
```

**Root Cause:**
Required Python package not installed in environment.

**Solution:**
```bash
python -m pip install pandas openpyxl tabulate
```

**Prevention:**
- Create `requirements.txt` for project scripts
- Add dependency check with helpful error messages:
```python
try:
    import pandas
except ImportError:
    print("Error: pandas required. Run: pip install pandas")
    sys.exit(1)
```

---

### Pattern 5: File Permission Errors

**Error:**
```
PermissionError: [Errno 13] Permission denied: '...pptx'
```

**Root Cause:**
File is open in another application (PowerPoint, Word, Excel).

**Solution:**
- Close the application using the file
- Or save to a different filename

**Prevention:**
- Check file writability before operations
- Save to temp file, then move
- Document file locking behavior in CLAUDE.md

---

### Pattern 6: Office Temp Files

**Issue:**
Temp files like `~$filename.pptx` appear when Office documents are open.

**Impact:**
- Clutter in file listings
- Scripts may attempt to process them

**Solution:**
Exclude temp files in scripts:
```python
import glob
files = [f for f in glob.glob('*.pptx') if not f.startswith('~$')]
```

**Prevention:**
- Add `~$*` to `.gitignore`
- Filter temp files in all file operations
- Document in STANDARDS.md hygiene section

---

### Pattern 7: Import Name Errors

**Error:**
```
ImportError: cannot import name 'RgbColor' from 'pptx.dml.color'
```

**Root Cause:**
Wrong case or name in import statement.

**Solution:**
Check correct name in documentation:
```python
# Wrong
from pptx.dml.color import RgbColor

# Correct
from pptx.dml.color import RGBColor
```

**Prevention:**
- Test imports before running full script
- Use IDE autocomplete or check docs
- Add import test to script header

---

### Pattern 8: Slide Layout Index Errors

**Error:**
```
IndexError: slide layout index out of range
```

**Root Cause:**
Trying to access slide layout index that doesn't exist in presentation.

**Solution:**
Check available layouts first:
```python
print(f"Number of layouts: {len(prs.slide_layouts)}")
for idx, layout in enumerate(prs.slide_layouts):
    print(f"Layout {idx}: {layout.name}")
```

**Prevention:**
- Always check layout count before accessing
- Use layout 0 (blank) as safe default

---

### Pattern 9: Shape/Connector Attribute Errors

**Error:**
```
AttributeError: type object 'MSO_AUTO_SHAPE_TYPE' has no attribute 'STRAIGHT_CONNECTOR_1'
```

**Root Cause:**
Wrong enum name for shape type.

**Solution:**
Use correct enum value or alternative approach:
```python
# Instead of connector (which may not exist)
# Use simple line shapes or omit connectors
```

**Prevention:**
- Check python-pptx documentation for valid enums
- Test shape creation separately
- Have fallback for unsupported shapes

---

### Pattern 10: Hook Event Errors

**Error:**
Telemetry shows Read ERROR detected with "Error type: unknown"

**Root Cause:**
Hook executed but couldn't process response format.

**Solution:**
Review hook implementation for:
- JSON parsing errors
- Missing fields in expected schema
- Encoding issues in hook script

**Prevention:**
- Add error handling in hooks
- Log hook inputs/outputs for debugging
- Test hooks with various tool responses

---

## Telemetry Analysis Guide

### Reading bash-audit.log

Format:
```
YYYY-MM-DD HH:MM:SS [ALLOW|DENY] command
```

Look for:
- `[DENY]` — Blocked commands (permission issues)
- Exit codes in subsequent lines — Non-zero = error
- Repeated commands — Indicates retry loops

### Reading read-errors.log

Each entry shows:
- Timestamp
- Error type
- Session context
- Tool input/output that caused error

Look for patterns:
- Same file causing multiple errors
- Same error type recurring
- Hook involvement in errors

### Reading read-operations.log

Shows hook execution flow:
- `HOOK_CALLED` — Hook triggered
- `PARAMS` — What was passed to tool
- `Hook completed` — Hook finished

Look for:
- Hooks that don't complete
- Multiple hooks on same operation
- Parameter mismatches

---

## Skill Improvement Checklist

When improving a skill based on errors:

- [ ] Update SKILL.md with error prevention steps
- [ ] Add validation for common error cases
- [ ] Document Windows-specific requirements
- [ ] Add dependency checks
- [ ] Include path format guidance
- [ ] Test on Windows if applicable
- [ ] Update description if triggering issues
- [ ] Add examples showing correct usage

---

## Creating Error Runbooks

For complex error patterns, create a runbook in `references/`:

```markdown
# Error Runbook: [Pattern Name]

## Symptoms
[What the user sees]

## Quick Diagnosis
[How to confirm this is the issue]

## Immediate Fix
[Steps to resolve now]

## Prevention
[How to avoid in future]

## Related Errors
[Other errors with same root cause]

## References
[Links to docs, issues, etc.]
```

---

## Output Format

After analysis, provide:

```markdown
## Lessons Learned Analysis — [Date]

### Errors Found: N

### Error Categories
| Category | Count | Root Cause |
|----------|-------|------------|
| Path Issues | N | ... |
| Import Errors | N | ... |
| ... | ... | ... |

### Key Lessons

#### Lesson 1: [Title]
**Applies to:** [Skill/Workflow]
**Fix:** [What to change]
**Prevention:** [How to avoid]

#### Lesson 2: [Title]
...

### Recommended Actions

1. **Immediate:** [Quick fixes]
2. **Short-term:** [Skill updates]
3. **Long-term:** [Systemic improvements]

### Artifacts Updated
- [ ] SKILL.md for [skill]
- [ ] CLAUDE.md — Added "Known Issues"
- [ ] references/error-patterns.md
- [ ] Hook validation added
```

---

## Integration with Other Skills

| Skill | Integration |
|-------|-------------|
| `5s` | Add error pattern checks to hygiene audit |
| `skill-creator` | Use lessons to improve skill drafts |
| `troubleshoot` | Cross-reference error patterns |
| `close-and-learn` | Feed lessons into session close |

---

## Notes

- Always check telemetry before assuming cause
- Document Windows-specific fixes explicitly
- Test fixes on actual Windows environment
- Update skills proactively, not just reactively
- Share lessons across similar skills

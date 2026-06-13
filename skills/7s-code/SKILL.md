---
name: 7s-code
description: >-
  Audit a specific code project using the 7S methodology. Chained from the
  7s skill via "--code" flag. Also trigger directly when Dale says "audit this
  project", "code hygiene", "check this repo", or "/7s --code". Audits the
  current working directory (or a named project path) for dead weight,
  structure, freshness, safety, and security. READ-ONLY — reports only.
---

# 7S Code Audit

Chained from `/7s --code`. Audits a single code project root.

The project root is the current working directory, or the path the user
specifies. Read-only — no modifications.

---

## Step 0: Identify Project

Confirm the project path and read its `AGENT.md` for `type:` and `status:`.
If no `AGENT.md` exists, proceed but note it as a finding.

---

## S1: Seiri — Sort (Dead weight)

- Commented-out code blocks (3+ consecutive commented lines)
- TODO/FIXME/HACK comments in files not modified in 30+ days
- Config files for tools not present in `package.json` / `requirements.txt` / equivalent
- Stale feature branches with no commits in 60+ days
- `node_modules/`, `__pycache__/`, `.venv/`, build artifacts tracked in git

---

## S2: Seiton — Set in Order (Structure)

- Root-level `README.md` exists and is non-trivial (>5 lines)
- Source directory clearly named (`src/`, `lib/`, or equivalent)
- Tests co-located with source OR in `tests/` — not both
- No more than 8 config files at root (config sprawl)
- `.editorconfig` or equivalent formatting config present
- `AGENT.md` present (required for Claude Code projects)
- `TASKS.md` present

---

## S3: Seiso — Shine (Freshness)

- Dependencies not updated in 12+ months (stale = security risk)
- Lock files present (`package-lock.json`, `yarn.lock`, `poetry.lock`, etc.)
- `.env.example` present if `.env` files are in use
- Last commit date — if no commits in 60+ days in an `active` project, flag

---

## S4: Seiketsu — Standardize (Standards compliance)

- Linter config present (`.eslintrc`, `pyproject.toml [tool.ruff]`, etc.)
- `.gitignore` present and non-trivial
- CI configuration present (`.github/workflows/`, `.gitlab-ci.yml`, etc.)

### S4b: Health score

Start at 100. Deduct: 10 per Critical, 4 per Notable, 1 per Suggestion.

### S4c: Report

```
## 7S Code Audit — [project-name] — [date]

### Health Score: [score]/100 — [Grade]

| S | Phase | Critical | Notable | Suggestions | Impact |
|---|-------|----------|---------|-------------|--------|
| S1 | Seiri — Sort | n | n | n | -nn |
| S2 | Seiton — Set in Order | n | n | n | -nn |
| S3 | Seiso — Shine | n | n | n | -nn |
| S4 | Seiketsu — Standardize | n | n | n | -nn |
| S6 | Seibi — Safety | n | n | n | -nn |
| S7 | Shuhi — Security | n | n | n | -nn |

[Findings by phase]

### Suggested next actions
1. [CRITICAL] ...
2. [NOTABLE] ...
```

---

## S6: Seibi — Safety (Code)

- All symlinks in the project resolve
- Lock file committed and in sync with manifest
- `.gitignore` covers `node_modules/`, build artifacts, `.env` files
- CI config present and not obviously broken

---

## S7: Shuhi — Security (Code)

- Run `~/bin/key-scan <project-path>` — flag any hits as Critical
- No `.env` files in the project directory (`.env.example` only)
- No private keys or certificate files committed
- Check `git log --all -- ".env*" "*.pem" "*.key"` for historical exposure

---

## Notes

- Read-only — use Glob and Grep, not shell commands that modify files
- This skill is invoked by `/7s --code` or directly as `/7s-code`
- Return to `/7s` for the workspace-level audit

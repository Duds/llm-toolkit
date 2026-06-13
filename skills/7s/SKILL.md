---
name: 7s
description: >-
  Audit the Projects workspace against STANDARDS.md using the 7S methodology
  (Seiri, Seiton, Seiso, Seiketsu, Shitsuke, Seibi, Shuhi). Use this skill
  whenever Dale says "7s", "run 7s", "5s", "run 5s", "tidy the workspace",
  "audit my projects", "check project hygiene", "what needs cleaning up",
  "workspace audit", or "/7s". Also trigger if Dale asks whether projects are
  compliant, named correctly, or whether any projects should be archived.
  This skill is READ-ONLY — it detects and reports issues but never applies
  fixes. To fix issues, it chains to the workspace-cleanup squad via
  invoke-squad. Also trigger on: "fix these audit issues", "apply 7S fixes",
  "fix my workspace", "clean up projects" — these phrases run the audit first,
  then offer to invoke the cleanup squad.
  Mode routing: "--code" chains to 7s-code skill. "--inbox" chains to
  7s-inbox skill.
---

# 7S — Workspace Audit

## The 7S Framework

The classic 5S lean methodology extended with two additional disciplines for
software and AI workspaces. All seven S's are native Japanese kanji terms that
romanise to S.

| Step | Japanese | Romanisation | English | Software meaning |
|------|----------|-------------|---------|-----------------|
| S1 | 整理 | Seiri | Sort | Remove what doesn't belong |
| S2 | 整頓 | Seiton | Set in Order | Naming, structure, organisation |
| S3 | 清掃 | Seiso | Shine | Hygiene — temp files, OS metadata, mirrors |
| S4 | 清潔 | Seiketsu | Standardize | Compliance check + health score + report |
| S5 | 躾 | Shitsuke | Sustain | Audit log, schedule cadence, pre-commit hook |
| S6 | 整備 | Seibi | Safety | Infrastructure health — symlinks, hooks, dependencies |
| S7 | 守秘 | Shuhi | Security | Credential protection — secrets, permissions, git history |

**Seibi (整備):** Maintenance and upkeep in lean manufacturing — keeping
equipment in safe working order. In software: broken symlinks, missing hooks,
uninstalled dependencies, vulnerable packages.

**Shuhi (守秘):** Confidentiality and secret-keeping (守 = guard, 秘 = secret).
In software: credentials outside `~/.mcp-env`, world-readable `.env` files,
secrets committed to git history.

---

## Mode Routing

| Invocation | Action |
|------------|--------|
| `/7s` (default) | Run full workspace audit — Steps 0 → S1–S7 |
| `/7s --code` | Chain to `7s-code` skill for code project audit |
| `/7s --inbox` | Chain to `7s-inbox` skill for inbox cleaner |

---

## Step 0: Pre-flight — Load Context and Scan Workspace

Run in parallel before any S-phase begins.

### 0a: Load Standards and Context

Read the following in parallel:

1. `Projects/STANDARDS.md` — if missing, stop and say:
   > "STANDARDS.md not found. This file defines the rules the 7S audit checks
   > against. Want me to create it?"
2. `Projects/TASKS.md` — note which projects are referenced as active work.
3. Most recent `Projects/_plans/YYYY-MM-DD-week-priorities.md` — note which
   projects appear as this week's focus.

From STANDARDS.md extract: §1 Naming, §2 Structure, §3 Lifecycle, §4 Hygiene,
§5 Document formats, §6 Task management.

### 0b: Scan Workspace Root

List all items at `Projects/` root (one level only). Categorise each:

| Category | Criteria |
|----------|----------|
| **Tooling** | Dot-prefixed (`.claude`) — skip entirely |
| **Reserved** | Underscore-prefixed (`_archive`, `_plans`, `_tasks`, `_templates`) — naming check only |
| **Projects** | All other directories — full audit |
| **Loose files** | Files directly at workspace root — flag if not on allowlist |

For each project directory, read its `AGENT.md` to extract `status:` and
`type:` from YAML frontmatter.

---

## S1: Seiri (整理) — Sort

Remove what doesn't belong from the workspace root.

**Flag as Critical:**
- Files at workspace root not on the §1.3 allowlist (`AGENT.md`, `TASKS.md`,
  `STANDARDS.md`, or a recognised reserved dir)
- Projects with `status: complete` or `status: archive` still at root more
  than 30 days after that status was set

**Flag as Notable:**
- Directories that don't match any project type or naming pattern
- Projects with no `AGENT.md` (type undetectable)
- Duplicate or near-duplicate project names

**Flag as Suggestion:**
- Projects absent from both TASKS.md and current week plan with no file
  activity in 90+ days — candidates for archival

---

## S2: Seiton (整頓) — Set in Order

Naming conventions and structural completeness.

### S2a: Naming (§1)

| Check | Severity |
|-------|----------|
| Project dirs not kebab-case (uppercase, spaces, underscores) | Notable |
| Loose files at root not on §1.3 allowlist | Notable |
| Date-stamped files missing `YYYY-MM-DD-` prefix | Suggestion |
| `_plans/` files not following date-stamp naming | Suggestion |

### S2b: Structure (§2)

For each project directory:

| Check | Severity |
|-------|----------|
| Missing `AGENT.md` | Critical |
| Missing `TASKS.md` | Notable |
| `type: code` but no `.claude/` directory | Notable |
| `type: program` but a stream subdir has no `AGENT.md` or `TASKS.md` | Notable |
| `type: llm-wiki` but missing required folders (`raw/`, `wiki/`) | Notable |
| `type: dcceew` but no `docs/` directory | Suggestion |

### S2c: Cross-reference

| Check | Severity |
|-------|----------|
| Active project absent from both TASKS.md and current week plan | Suggestion |
| Project referenced in TASKS.md but not found in workspace | Notable |

---

## S3: Seiso (清掃) — Shine

Hygiene across all project directories. Scan recursively, skip `.claude/`,
`_archive/`, `_templates/`.

### S3a: Temp and OS files

**Flag as Notable:**
- `~$*` — Office lock files
- `*.tmp`, `*.bak` — temp/backup files
- `.DS_Store`, `Thumbs.db`, `desktop.ini` — OS metadata
- Empty directories
- Broken symlinks (in project dirs — infrastructure symlinks checked in S6)

### S3b: Unsanctioned versioning

**Flag as Notable:**
- Files with `DRAFT`, `WIP`, `COPY`, `OLD`, `BACKUP` in name at a project root
- Versioned filenames using wrong pattern (`_v0.1` instead of `-v0_1`)
- Version chains where older versions remain in active directories

**Flag as Suggestion:**
- Projects with no file activity in 90+ days
- TASKS.md not modified in 60+ days in an `active` project
- Large binary files (>10MB) not in a designated assets folder

### S3c: Versioned document audit (§1.4, §1.5)

| Check | Severity |
|-------|----------|
| Wrong version pattern (`_v0.1` not `-v0_1`) | Notable |
| Multiple versions in same active directory | Notable |
| Old versions not archived | Suggestion |

Detect chains: group files by base name, flag where older versions aren't in
`_archive/`.

### S3d: Mirror file audit (§5)

For each `.pptx`, `.docx`, `.xlsx`, `.pdf` in `artefacts/`, `docs/`,
`deliverables/`:

| Check | Severity |
|-------|----------|
| No corresponding `.md` mirror exists | Notable |
| Mirror older than source (stale) | Notable |
| Office temp file (`~$*`) present | Notable |

---

## S4: Seiketsu (清潔) — Standardize

Compliance verification, scoring, and the unified audit report. This S is the
output surface for the entire audit.

### S4a: Compliance check

**Lifecycle status (§3):**

| Check | Severity |
|-------|----------|
| `AGENT.md` missing `status:` frontmatter | Notable |
| `AGENT.md` missing `type:` frontmatter | Notable |
| `status: complete` project at root for 30+ days | Notable |
| `AGENT.md` frontmatter malformed YAML | Critical |

**TASKS.md quality:**

| Check | Severity |
|-------|----------|
| TASKS.md empty or header-only | Suggestion |
| TASKS.md not modified in 60+ days in an `active` project | Suggestion |

**Week plan alignment:**

| Check | Severity |
|-------|----------|
| No week plan found in `_plans/` | Notable |
| Most recent week plan older than 14 days | Suggestion |

### S4b: Health score

**Start at 100. Deduct:**
- 10 points per Critical finding
- 4 points per Notable finding
- 1 point per Suggestion

**Grade:**
- 90–100: **A — Clean**
- 75–89: **B — Minor issues**
- 60–74: **C — Needs attention**
- 40–59: **D — Action required**
- <40: **F — Poor health**

### S4c: Unified report

Present once, after all S-phases complete:

```
## 7S Workspace Audit — [date]

### Health Score: [score]/100 — [Grade]

| S | Phase | Critical | Notable | Suggestions | Impact |
|---|-------|----------|---------|-------------|--------|
| S1 | Seiri — Sort | n | n | n | -nn |
| S2 | Seiton — Set in Order | n | n | n | -nn |
| S3 | Seiso — Shine | n | n | n | -nn |
| S4 | Seiketsu — Standardize | n | n | n | -nn |
| S5 | Shitsuke — Sustain | n | n | n | -nn |
| S6 | Seibi — Safety | n | n | n | -nn |
| S7 | Shuhi — Security | n | n | n | -nn |
| — | Versioned Docs | n | n | n | -nn |
| — | Mirror Files | n | n | n | -nn |
| | **Total** | **n** | **n** | **n** | **[score]/100** |

Projects audited: N | Compliant: N | Issues: N

---

### S1 Seiri — Sort
[table: severity | path | issue | suggested action]

### S2 Seiton — Set in Order
[table: severity | path | issue | suggested action]

### S3 Seiso — Shine
[table: severity | path | issue | suggested action]

### S4 Seiketsu — Standardize
[table: severity | path | issue | suggested action]

### S6 Seibi — Safety
[table: severity | path | issue | suggested action]
[or: "Clean — no infrastructure issues"]

### S7 Shuhi — Security
[table: severity | path:line | issue | suggested action]
[or: "Clean — no credentials found outside ~/.mcp-env"]

### Versioned Documents
[table: severity | path | issue | suggested action]

### Mirror Files
[table: severity | path | issue | suggested action]

---

### Suggested fixes (ordered by impact)
1. [CRITICAL] ...
2. [NOTABLE] ...
```

### S4d: Cleanup squad handoff

**The 7S skill is read-only.** After presenting the report, ask:
> "Would you like me to fix these? I can invoke the workspace-cleanup squad."

If confirmed:
1. Call `invoke-squad workspace-cleanup`
2. Pass findings summary (score, grade, critical list, notable list)
3. Squad lead (`workspace-auditor`) validates dependencies and plans fixes
4. `structure-fixer` handles AGENT.md, frontmatter, renames
5. `hygiene-cleaner` handles temp files, mirrors, version chains
6. `workspace-auditor` re-runs audit and reports new score

---

## S5: Shitsuke (躾) — Sustain

Turn a one-off audit into a discipline.

### S5a: Audit log

Record this audit in `~/Projects/_plans/7s-audit-log.md`.

If the file doesn't exist, create it:
```markdown
# 7S Audit Log

| Date | Score | Grade | Critical | Notable | Suggestions | Notes |
|------|-------|-------|----------|---------|-------------|-------|
```

Append a row for this audit, then read back the last 5 rows and display a
trend line:
- Score improving → "Trend: improving ↑"
- Score stable (±3 pts) → "Trend: stable →"
- Score declining → "Trend: declining ↓ — consider scheduling a fix session"

### S5b: Schedule cadence

If no schedule is already set, ask:

> "To keep this clean, pick a cadence:"
>
> A. **Weekly** — every Monday morning
> B. **Fortnightly** — every second Monday (already set via cron)
> C. **Hook into orient** — mini key-scan at every session start
> D. **Manual only**

- A or B: invoke `schedule` skill with `/7s` as the task
- C: invoke `update-config` to add pre-orient hook running `~/bin/key-scan ~/Projects`
- D: acknowledge, no action

If a schedule already exists, report it and ask if cadence should change.

### S5c: Pre-commit hook

If any S7 Shuhi findings exist, recommend:

> "Secrets were found outside `~/.mcp-env`. Want me to wire `key-scan` as a
> pre-commit hook on `~/Projects/dotfiles`?"

If confirmed, write and chmod `~/Projects/dotfiles/.git/hooks/pre-commit`:
```bash
#!/usr/bin/env bash
~/bin/key-scan . && exit 0
echo "key-scan: secrets detected — commit blocked. Move secrets to ~/.mcp-env."
exit 1
```

This is the only write action the 7S skill takes directly.

---

## S6: Seibi (整備) — Safety

Infrastructure health — the workspace equivalent of equipment maintenance.
A broken symlink or missing hook is a silent failure waiting to happen.

### S6a: Symlink health

```bash
find ~/.claude/skills -type l | while read l; do [ ! -e "$l" ] && echo "BROKEN: $l"; done
find ~/.claude/agents -type l | while read l; do [ ! -e "$l" ] && echo "BROKEN: $l"; done
find ~/.claude/squads -type l | while read l; do [ ! -e "$l" ] && echo "BROKEN: $l"; done
find ~/.claude/hooks  -type l | while read l; do [ ! -e "$l" ] && echo "BROKEN: $l"; done
find ~/bin            -type l | while read l; do [ ! -e "$l" ] && echo "BROKEN: $l"; done
```

| Result | Severity |
|--------|----------|
| Any broken symlink in `~/.claude/` or `~/bin/` | Critical |
| Symlink target exists but not executable (hooks/scripts) | Notable |

### S6b: Hook health

Parse `~/.claude/settings.json` for hook command paths. For each:

| Check | Severity |
|-------|----------|
| Hook file referenced but missing from disk | Critical |
| Hook file exists but not executable | Notable |

### S6c: Dependency health (code projects)

For each project with `type: code`:

| Check | Severity |
|-------|----------|
| `package.json` present but no `node_modules/` (never installed) | Notable |
| Lock file absent | Notable |
| Dependencies not updated in 12+ months | Suggestion |

### S6d: Knowledge base health

| Check | Severity |
|-------|----------|
| `~/_llm-wiki/` directory missing | Notable |
| `~/_llm-wiki/index.md` not updated within 7 days of last wiki change | Notable |

---

## S7: Shuhi (守秘) — Security

Credential protection. Any secret outside `~/.mcp-env` is Critical.

### S7a: Key-scan

```bash
~/bin/key-scan ~/Projects
```

| Result | Severity |
|--------|----------|
| "no secrets found" | Clean |
| Any hit | Critical per file:line |

Output format per finding:
- Severity: Critical
- Path: `<file>:<line>`
- Issue: Potential `[Pattern Type]` credential outside `~/.mcp-env`
- Action: Move to `~/.mcp-env`, replace with env var reference

**Never print key values.** key-scan suppresses them — do not read the file.

### S7b: Env file check

```bash
find ~/Projects -name ".env*" -not -path "*/.git/*" -not -path "*/node_modules/*"
find ~/Projects -name "*.pem" -o -name "*.key" -o -name "*.p12" 2>/dev/null | grep -v ".git"
```

| Check | Severity |
|-------|----------|
| `.env` file present (outside `~/.mcp-env`) | Critical |
| `.env.local`, `.env.production`, etc. found | Critical |
| Private key files (`.pem`, `.key`, `.p12`) in project dirs | Critical |
| `credentials.json`, `service-account.json` found | Critical |

### S7c: Git history check

For each git-tracked project:

```bash
git -C <project> log --all --full-history -- "*.env" ".env*" "*.pem" "*.key" 2>/dev/null
```

| Result | Severity |
|--------|----------|
| `.env` or key file in git history | Critical |

Suggested action: `git filter-repo` to purge + rotate all exposed credentials.

### S7d: Pre-commit hook verification

```bash
[ -x ~/Projects/dotfiles/.git/hooks/pre-commit ] && echo "OK" || echo "MISSING"
```

| Result | Severity |
|--------|----------|
| Hook missing or not executable | Notable |

---

## Notes

- Read-only by default — never change anything without confirmation
- Skip `.claude/` entirely — tooling, not workspace content
- Skip `_archive/` content — archived projects are out of scope
- Always re-read STANDARDS.md at the start of each run — never use cached version
- Run all S-phases before presenting output — single unified report
- Code audit → chain to `7s-code` skill
- Inbox cleaner → chain to `7s-inbox` skill

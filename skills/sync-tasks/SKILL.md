# sync-tasks

Sync TASKS.md tickets to GitHub Issues in Duds/ir5-os.

## When to use
Trigger when user runs `/sync-tasks`, asks to "sync tasks to GitHub", or says "push tasks to issues".

## What it does
Runs `sync-tasks.py` and reports the result summary. One-way: TASKS.md → GitHub Issues.

## Steps

1. Run the sync script:

```bash
python3 /Users/dalerogers/Documents/projects/ir5-os/scripts/sync-tasks.py
```

2. Report the result line from the output:
   - "Sync complete — created: N, updated: M, closed: P, skipped: Q"
   - If it fails, show the error

3. If any issues were created or updated, offer to open the GitHub issues page:
   - URL: https://github.com/Duds/ir5-os/issues

## Flags
- `--dry-run`: show what would change without creating/updating issues

## Notes
- Daily automated sync runs at 7:30 AM via launchd (com.dalerogers.sync-tasks)
- Logs at: ~/.claude/logs/sync-tasks.log
- Script: ~/Documents/projects/ir5-os/scripts/sync-tasks.py

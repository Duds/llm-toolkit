Hermes Workspace runs as launchd daemon `ai.hermes.workspace` on port 5173. Startup script at `~/.local/bin/hermes-workspace-start` sources nvm, switches to Node 24, then execs npm run dev. Direct nvm-in-launchd approach fails with tty ioctl errors; wrapper script is required. Workspace in portable mode sends X-Hermes-Session-Id unconditionally via openai-compat-api.ts; gateway needs API_SERVER_KEY configured to accept session continuity.

User's personal filing system is local-first, cloud-independent. Taxonomy: numbered folders (00-INBOX, 10-ADMIN, 20-CAREER, etc.) with date-prefixed filenames. Google Drive and iCloud Documents migrated to local. Job apps in ~/20-CAREER/02-JOB-APPLICATIONS/YYYY/YYYY-MM-DD_ORG_ROLE/ with subfolders 01-ROLE-DESCRIPTION through 07-OUTCOME. New job app script at ~/90-CONFIG/scripts/new-job-app.sh.

Gmail MCP configured in Hermes: gmail_search, gmail_read, gmail_triage_inbox, gmail_smart_archive, gmail_newsletter_cleanup, gmail_detect_followups, gmail_send_email, gmail_reply_to_thread. User has numbered label system (1-Work through 9-For-Deletion). Wants automated email filtering. Keeps Paint on Plastic and Chesapeake Light Craft emails in inbox.

Signal gateway: running on `127.0.0.1:8080`, connected to account `+614****4492`. Signal export data parsed and analyzed, 2,703 outgoing messages from user to Jane used for tone calibration. Protocol document drafted with 7 sections: scope, tone calibration, operating rules, time/boundaries, instruction authority, examples, review/escalation.

Hermes MCP servers configured: gmail-local (enabled), gcal-local (configured), azure (configured). Gmail MCP has 21 tools including triage, smart archive, newsletter cleanup, follow-up detection, financial tracking, interview tracking.

User has three-tier task management system: Portfolio (~/TASKS.md), Project (project/TASKS.md), Wiki (llm-wiki/wiki/tasks/). Task ID scheme: `<PREFIX>-<NNN>` (P-001 for portfolio, RO-001 for Rock Oracle, IR5-001 for IR5 OS). Sync script at `~/30-PROJECTS/ir5-os/scripts/sync-tasks.py` syncs to GitHub Issues in Duds/ir5-os.

User's llm-toolkit repo at `~/30-PROJECTS/llm-toolkit/` is the portable agent configuration for cross-harness use. Intended to deploy to `~/.agents/` as the single source of truth. Contains ~50 skills, 1 squad, hooks, templates, harness integrations.

ir5-os project decides what the tooling layer should look like. llm-toolkit is the portable implementation. dotfiles/claude/ is the live Mac instance. Skill refactors from ir5-os/ROADMAP.md should land in llm-toolkit first, then flow to dotfiles/claude/.

15 skills drifted between llm-toolkit and dotfiles/claude/skills. dotfiles/claude is the more mature version in samples checked. 11 skills exist only in llm-toolkit and should be added to dotfiles/claude. 10 agents in dotfiles/claude/agents should be promoted to llm-toolkit/agents.

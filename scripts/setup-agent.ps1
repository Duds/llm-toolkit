# ~/.agent/scripts/setup-agent.ps1
# Master setup script — run once to plumb everything together
# Usage: powershell ~/.agent/scripts/setup-agent.ps1

$ErrorActionPreference = "Stop"
$AgentRoot = "$env:USERPROFILE\.agent"
$ClaudeDir = "$env:USERPROFILE\.claude"
$KimiDir = "$env:USERPROFILE\.kimi"

Write-Host "=== ~/.agent Master Setup ===" -ForegroundColor Cyan
Write-Host ""

# 1. Verify directory structure
$RequiredDirs = @(
    "skills", "agents", "squads", "hooks",
    "harness-integrations/claude",
    "harness-integrations/kimi",
    "harness-integrations/openai",
    "templates", "scripts"
)

Write-Host "Checking directory structure..." -ForegroundColor Yellow
foreach ($Dir in $RequiredDirs) {
    $Path = Join-Path $AgentRoot $Dir
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Force -Path $Path | Out-Null
        Write-Host "  Created: $Dir" -ForegroundColor Green
    } else {
        Write-Host "  OK $Dir" -ForegroundColor DarkGray
    }
}
Write-Host ""

# 2. Migrate skills
$MigrateSkills = Read-Host "Migrate skills from legacy paths? (y/N)"
if ($MigrateSkills -eq 'y') {
    $MigrateScript = Join-Path $AgentRoot "scripts\migrate-skills.ps1"
    if (Test-Path $MigrateScript) {
        & $MigrateScript
    } else {
        Write-Warning "migrate-skills.ps1 not found. Run it manually later."
    }
}
Write-Host ""

# 3. Configure Claude Code
Write-Host "Configuring Claude Code integration..." -ForegroundColor Yellow
$ClaudeSettingsSource = Join-Path $AgentRoot "harness-integrations\claude\settings.json"
$ClaudeSettingsDest = Join-Path $ClaudeDir "settings.json"

if (Test-Path $ClaudeSettingsSource) {
    if (Test-Path $ClaudeSettingsDest) {
        $Backup = "$ClaudeSettingsDest.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Copy-Item $ClaudeSettingsDest $Backup -Force
        Write-Host "  Backed up existing Claude settings to $Backup" -ForegroundColor DarkGray
    }
    Write-Host "  Source: $ClaudeSettingsSource" -ForegroundColor DarkGray
    Write-Host "  Dest:   $ClaudeSettingsDest" -ForegroundColor DarkGray
    Write-Host "  ACTION REQUIRED: Merge harness-integrations/claude/settings.json into ~/.claude/settings.json" -ForegroundColor Yellow
} else {
    Write-Warning "Claude integration template not found"
}
Write-Host ""

# 4. Configure Kimi
Write-Host "Configuring Kimi integration..." -ForegroundColor Yellow
$KimiConfigSource = Join-Path $AgentRoot "harness-integrations\kimi\agent-config.yaml"
$KimiConfigDest = Join-Path $KimiDir "config.yaml"

if (Test-Path $KimiConfigSource) {
    if (Test-Path $KimiConfigDest) {
        $Backup = "$KimiConfigDest.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Copy-Item $KimiConfigDest $Backup -Force
        Write-Host "  Backed up existing Kimi config to $Backup" -ForegroundColor DarkGray
    }
    Write-Host "  Source: $KimiConfigSource" -ForegroundColor DarkGray
    Write-Host "  Dest:   $KimiConfigDest" -ForegroundColor DarkGray
    Write-Host "  ACTION REQUIRED: Include harness-integrations/kimi/agent-config.yaml in ~/.kimi/config.yaml" -ForegroundColor Yellow
} else {
    Write-Warning "Kimi integration template not found"
}
Write-Host ""

# 5. Verify sample squad
$SampleSquad = Join-Path $AgentRoot "squads\workspace-cleanup\SQUAD.md"
if (Test-Path $SampleSquad) {
    Write-Host "OK Sample squad available: workspace-cleanup" -ForegroundColor Green
} else {
    Write-Warning "Sample squad not found. Expected at $SampleSquad"
}
Write-Host ""

# 6. Summary
Write-Host "=== Setup Summary ===" -ForegroundColor Cyan
Write-Host "Unified agent root:  $AgentRoot"
Write-Host "Skills path:         $AgentRoot\skills"
Write-Host "Agents path:         $AgentRoot\agents"
Write-Host "Squads path:         $AgentRoot\squads"
Write-Host "Hooks path:          $AgentRoot\hooks"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Merge harness integration configs into your harness settings"
Write-Host "  2. Run: powershell ~/.agent/scripts/migrate-skills.ps1"
Write-Host "  3. Run: powershell ~/.agent/scripts/migrate-projects.ps1 -ProjectRoot C:\Users\DaleROGERS\Projects"
Write-Host "  4. Add AGENT.md to active projects"
Write-Host "  5. Add hooks to your harness startup (see ~/.agent/hooks/)"
Write-Host ""
Write-Host "To verify: List contents of ~/.agent/skills, ~/.agent/agents, ~/.agent/squads" -ForegroundColor DarkGray

# ~/.agent/scripts/migrate-skills.ps1
# Migrate skills from legacy locations into ~/.agent/skills/
# Run once: powershell ~/.agent/scripts/migrate-skills.ps1

$ErrorActionPreference = "Stop"
$AgentRoot = "$env:USERPROFILE\.agent"
$SkillsDir = "$AgentRoot\skills"
$BackupDir = "$AgentRoot\_migration-backup\skills-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

# Legacy sources
$LegacySources = @(
    "$env:USERPROFILE\.claude\skills"
)

Write-Host "=== ~/.agent Skill Migration ===" -ForegroundColor Cyan
Write-Host "Destination: $SkillsDir"
Write-Host "Backup:      $BackupDir"
Write-Host ""

# Create backup dir
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

foreach ($Source in $LegacySources) {
    if (-not (Test-Path $Source)) {
        Write-Host "Skipping (not found): $Source" -ForegroundColor DarkGray
        continue
    }

    Write-Host "Processing: $Source" -ForegroundColor Yellow

    $Items = Get-ChildItem -Path $Source -Directory
    foreach ($Item in $Items) {
        $DestPath = Join-Path $SkillsDir $Item.Name

        if (Test-Path $DestPath) {
            Write-Host "  SKIP (already exists): $($Item.Name)" -ForegroundColor DarkYellow
            continue
        }

        # Copy to backup first
        $BackupPath = Join-Path $BackupDir "$($Item.Name)-from-$(Split-Path $Source -Leaf)"
        Copy-Item -Path $Item.FullName -Destination $BackupPath -Recurse -Force

        # Move to unified location
        Move-Item -Path $Item.FullName -Destination $DestPath -Force
        Write-Host "  MOVED: $($Item.Name) -> $DestPath" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Migration complete. Backup saved to: $BackupDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Review ~/.agent/skills/ for any duplicates or conflicts"
Write-Host "  2. Update ~/.agent/config.yaml to point to ~/.agent/skills"
Write-Host "  3. Delete legacy ~/.claude/skills directory once verified"

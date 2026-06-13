# ~/.agent/scripts/migrate-projects.ps1
# Migrate project CLAUDE.md files to AGENT.md standard
# Usage: powershell ~/.agent/scripts/migrate-projects.ps1 -ProjectRoot "C:\Users\DaleROGERS\Projects"

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectRoot
)

$ErrorActionPreference = "Stop"
$TemplatePath = "$env:USERPROFILE\.agent\templates\AGENT.md"

Write-Host "=== Project AGENT.md Migration ===" -ForegroundColor Cyan
Write-Host "Scanning: $ProjectRoot" -ForegroundColor White
Write-Host ""

if (-not (Test-Path $TemplatePath)) {
    Write-Error "Template not found: $TemplatePath. Run this after ~/.agent is set up."
    exit 1
}

$Template = Get-Content -Path $TemplatePath -Raw

# Find all projects with CLAUDE.md but no AGENT.md
$Projects = Get-ChildItem -Path $ProjectRoot -Directory | Where-Object {
    $ClaudeMd = Join-Path $_.FullName "CLAUDE.md"
    $AgentMd = Join-Path $_.FullName "AGENT.md"
    (Test-Path $ClaudeMd) -and (-not (Test-Path $AgentMd))
}

Write-Host "Found $($Projects.Count) projects to migrate:" -ForegroundColor Yellow
foreach ($Project in $Projects) {
    Write-Host "  - $($Project.Name)"
}
Write-Host ""

if ($Projects.Count -eq 0) {
    Write-Host "No projects need migration. All have AGENT.md or none have CLAUDE.md." -ForegroundColor Green
    exit 0
}

$Confirm = Read-Host "Proceed with migration? (y/N)"
if ($Confirm -ne 'y') {
    Write-Host "Cancelled." -ForegroundColor DarkGray
    exit 0
}

foreach ($Project in $Projects) {
    $ClaudeMd = Join-Path $Project.FullName "CLAUDE.md"
    $AgentMd = Join-Path $Project.FullName "AGENT.md"

    Write-Host "Migrating: $($Project.Name)..." -ForegroundColor Yellow -NoNewline

    # Read existing CLAUDE.md content
    $Existing = Get-Content -Path $ClaudeMd -Raw

    # Extract YAML frontmatter if present
    $Frontmatter = ""
    if ($Existing -match '^---\s*\n(.*?)\n---\s*\n') {
        $Frontmatter = $matches[1]
    }

    # Parse frontmatter fields
    $Name = if ($Frontmatter -match 'name:\s*(.+)') { $matches[1].Trim() } else { $Project.Name }
    $Description = if ($Frontmatter -match 'description:\s*(.+)') { $matches[1].Trim() } else { "" }
    $Type = if ($Frontmatter -match 'type:\s*(.+)') { $matches[1].Trim() } else { "code" }
    $Status = if ($Frontmatter -match 'status:\s*(.+)') { $matches[1].Trim() } else { "active" }

    # Build AGENT.md from template
    $AgentContent = $Template `
        -replace 'name: project-name', "name: $Name" `
        -replace 'description: One-line description', "description: $Description" `
        -replace 'type: code', "type: $Type" `
        -replace 'status: active', "status: $Status" `
        -replace 'last-updated: YYYY-MM-DD', "last-updated: $(Get-Date -Format 'yyyy-MM-dd')"

    # Append migration note and original content
    $AgentContent += "`n`n---`n`n## Migrated from CLAUDE.md`n`nOriginal file preserved at: ``CLAUDE.md``\n\n"
    $AgentContent += "### Original Content`n`n```markdown`n$Existing`n```\n"

    # Write AGENT.md
    Set-Content -Path $AgentMd -Value $AgentContent -Encoding UTF8

    # Rename CLAUDE.md to CLAUDE.md.bak
    Rename-Item -Path $ClaudeMd -NewName "CLAUDE.md.bak"

    Write-Host " DONE" -ForegroundColor Green
}

Write-Host ""
Write-Host "Migration complete. Summary:" -ForegroundColor Cyan
Write-Host "  - $($Projects.Count) projects migrated"
Write-Host "  - Original CLAUDE.md renamed to CLAUDE.md.bak"
Write-Host "  - New AGENT.md created with cross-model standard frontmatter"
Write-Host ""
Write-Host "Review each AGENT.md and adjust the 'models' and 'skills' sections." -ForegroundColor White

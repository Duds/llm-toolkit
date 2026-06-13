# ~/.agent/hooks/on-project-open.ps1
# PowerShell version for Windows harnesses (Claude Code, etc.)
# Runs when a project is opened — detects AGENT.md and sets session context

param(
    [string]$ProjectPath = (Get-Location).Path
)

$AgentFile = Join-Path $ProjectPath "AGENT.md"
$FallbackFile = Join-Path $ProjectPath "CLAUDE.md"
$ConfigFile = "$env:USERPROFILE\.agent\config.yaml"

Write-Host "=== ~/.agent Session Start ===" -ForegroundColor Cyan

# Detect AGENT.md or fallback to CLAUDE.md
$ConfigFilePath = $null
if (Test-Path $AgentFile) {
    $ConfigFilePath = $AgentFile
    Write-Host "✓ AGENT.md detected" -ForegroundColor Green
}
elseif (Test-Path $FallbackFile) {
    $ConfigFilePath = $FallbackFile
    Write-Host "○ CLAUDE.md detected (legacy — consider migrating to AGENT.md)" -ForegroundColor Yellow
}

if ($ConfigFilePath) {
    $Content = Get-Content -Path $ConfigFilePath -Raw
    
    # Parse YAML frontmatter
    if ($Content -match '^---\s*\n(.*?)\n---') {
        $Frontmatter = $matches[1]
        
        $ProjectName = if ($Frontmatter -match '^name:\s*(.+)$') { $matches[1].Trim() } else { "unknown" }
        $ProjectType = if ($Frontmatter -match '^type:\s*(.+)$') { $matches[1].Trim() } else { "unknown" }
        $ProjectStatus = if ($Frontmatter -match '^status:\s*(.+)$') { $matches[1].Trim() } else { "unknown" }
        
        Write-Host "  Project: $ProjectName"
        Write-Host "  Type:    $ProjectType"
        Write-Host "  Status:  $ProjectStatus"
        
        # Preferred model
        $DefaultModel = if ($Frontmatter -match '^\s+default:\s*(.+)$') { $matches[1].Trim() } else { "auto" }
        if ($DefaultModel -ne "auto") {
            Write-Host "  Model:   $DefaultModel"
        }
        
        # Skills check
        $SkillsSection = $false
        $Lines = $Content -split "`n"
        foreach ($Line in $Lines) {
            if ($Line -match '^skills:') { $SkillsSection = $true; continue }
            if ($SkillsSection -and $Line -match '^\s+-\s*(.+)$') {
                $Skill = $matches[1].Trim()
                $SkillPath = "$env:USERPROFILE\.agent\skills\$Skill"
                if (Test-Path $SkillPath) {
                    Write-Host "    ✓ $Skill" -ForegroundColor Green
                } else {
                    Write-Host "    ○ $Skill (not in ~/.agent/skills/)" -ForegroundColor Yellow
                }
            }
            if ($SkillsSection -and $Line -match '^\S' -and $Line -notmatch '^skills:') { $SkillsSection = $false }
        }
        
        # Squads check
        $SquadsSection = $false
        foreach ($Line in $Lines) {
            if ($Line -match '^squads:') { $SquadsSection = $true; continue }
            if ($SquadsSection -and $Line -match '^\s+on-demand:') { continue }
            if ($SquadsSection -and $Line -match '^\s+-\s*(.+)$') {
                $Squad = $matches[1].Trim()
                $SquadPath = "$env:USERPROFILE\.agent\squads\$Squad"
                if (Test-Path $SquadPath) {
                    Write-Host "    ✓ $Squad" -ForegroundColor Green
                } else {
                    Write-Host "    ○ $Squad (not in ~/.agent/squads/)" -ForegroundColor Yellow
                }
            }
            if ($SquadsSection -and $Line -match '^\S' -and $Line -notmatch '^squads:') { $SquadsSection = $false }
        }
    }
}
else {
    Write-Host "○ No AGENT.md found in $ProjectPath" -ForegroundColor Yellow
    Write-Host "  Run: cp ~/.agent/templates/AGENT.md ./AGENT.md"
}

# Global config check
if (Test-Path $ConfigFile) {
    Write-Host "✓ ~/.agent/config.yaml loaded" -ForegroundColor Green
} else {
    Write-Host "○ ~/.agent/config.yaml not found" -ForegroundColor Yellow
}

Write-Host "================================" -ForegroundColor Cyan

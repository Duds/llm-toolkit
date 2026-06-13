# Wire .agent skills, agents, and squads to Roo Code global storage
# No admin required — uses directory junctions instead of symbolic links

$rooStorage = "$env:APPDATA\Code\User\globalStorage\rooveterinaryinc.roo-cline"
$skillsDir = "$rooStorage\skills"
$agentSkills = "$env:USERPROFILE\.agent\skills"
$agentAgents = "$env:USERPROFILE\.agent\agents"
$agentSquads = "$env:USERPROFILE\.agent\squads"
$roomodesPath = "$env:USERPROFILE\.roomodes"

# ─── SKILLS ──────────────────────────────────────────────────────────────────

New-Item -ItemType Directory -Path $skillsDir -Force | Out-Null

# Remove old junctions and recreate
if (Test-Path $skillsDir) {
    Get-ChildItem $skillsDir | Remove-Item -Recurse -Force
}

$skillCount = 0
if (Test-Path $agentSkills) {
    Get-ChildItem $agentSkills -Directory | ForEach-Object {
        $link = Join-Path $skillsDir $_.Name
        New-Item -ItemType Junction -Path $link -Target $_.FullName -Force | Out-Null
        $skillCount++
    }
}

Write-Host "Wired $skillCount skills" -ForegroundColor Green

# ─── AGENTS + SQUADS -> .roomodes ───────────────────────────────────────────

function Parse-YamlFrontmatter {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $null }
    $raw = Get-Content -Path $Path -Raw
    # Normalize CRLF to LF for reliable matching
    $content = $raw -replace '\r\n', "`n"
    if ($content -notmatch '^---\s*\n([\s\S]*?)\n---') { return $null }

    $lines = $matches[1] -split "`n"
    $result = @{}
    $pendingKey = $null
    $pendingValue = $null

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        # Check for key: value (including block scalar indicators like >-, |, etc.)
        if ($line -match '^(\w+):\s*(.*)$') {
            # Save previous pending value if any
            if ($pendingKey) {
                $result[$pendingKey] = $pendingValue.Trim()
                $pendingKey = $null
                $pendingValue = $null
            }
            $key = $matches[1].Trim()
            $val = $matches[2].Trim()
            $val = $val.Trim('"').Trim("'")

            # Block scalar indicator? Collect subsequent indented lines
            if ($val -match '^(>[-+]?\d*|\|[-+]?\d*)$') {
                $pendingKey = $key
                $pendingValue = ""
                # Skip to next line to collect indented content
                continue
            }
            $result[$key] = $val
        }
        elseif ($pendingKey -and $line -match '^\s+(.+)$') {
            $pendingValue += $matches[1].Trim() + " "
        }
        elseif ($pendingKey -and $line -match '^\S') {
            # Non-indented line ends block scalar
            $result[$pendingKey] = $pendingValue.Trim()
            $pendingKey = $null
            $pendingValue = $null
        }
    }
    # Save any remaining pending value
    if ($pendingKey) {
        $result[$pendingKey] = $pendingValue.Trim()
    }
    return $result
}

$customModes = @()

# Parse agents
$agentCount = 0
if (Test-Path $agentAgents) {
    Get-ChildItem $agentAgents -Directory | ForEach-Object {
        $agentMd = Join-Path $_.FullName "AGENT.md"
        $meta = Parse-YamlFrontmatter -Path $agentMd
        if ($meta -and $meta['name'] -and $meta['description']) {
            $slug = ($meta['name'] -replace '\s+', '-' -replace '[^a-zA-Z0-9\-]', '').ToLower()
            $name = $meta['name']
            $desc = $meta['description']
            $instr = "You are the $name agent. Operate according to your AGENT.md definition."
            $customModes += @{
                slug = $slug
                name = $name
                roleDefinition = $desc
                customInstructions = $instr
                groups = @("read", "edit", "browser", "command", "mcp")
            }
            $agentCount++
        }
    }
}

# Parse squads (and nested agents)
$squadCount = 0
if (Test-Path $agentSquads) {
    Get-ChildItem $agentSquads -Directory | ForEach-Object {
        $squadMd = Join-Path $_.FullName "SQUAD.md"
        $meta = Parse-YamlFrontmatter -Path $squadMd
        if ($meta -and $meta['name'] -and $meta['description']) {
            $slug = ($meta['name'] -replace '\s+', '-' -replace '[^a-zA-Z0-9\-]', '').ToLower()
            $name = $meta['name']
            $desc = $meta['description']
            $instr = "You are the $name squad lead. Coordinate squad members per SQUAD.md workflow. Invoke other modes for member tasks."
            $customModes += @{
                slug = $slug
                name = $name
                roleDefinition = $desc
                customInstructions = $instr
                groups = @("read", "edit", "browser", "command", "mcp")
            }
            $squadCount++
        }

        # Also pick up agents inside squad/agents/
        $squadAgentsDir = Join-Path $_.FullName "agents"
        if (Test-Path $squadAgentsDir) {
            Get-ChildItem $squadAgentsDir -Directory | ForEach-Object {
                $agentMd = Join-Path $_.FullName "AGENT.md"
                $meta = Parse-YamlFrontmatter -Path $agentMd
                if ($meta -and $meta['name'] -and $meta['description']) {
                    $slug = ($meta['name'] -replace '\s+', '-' -replace '[^a-zA-Z0-9\-]', '').ToLower()
                    $name = $meta['name']
                    $desc = $meta['description']
                    $instr = "You are the $name agent. Operate according to your AGENT.md definition."
                    $customModes += @{
                        slug = $slug
                        name = $name
                        roleDefinition = $desc
                        customInstructions = $instr
                        groups = @("read", "edit", "browser", "command", "mcp")
                    }
                    $agentCount++
                }
            }
        }
    }
}

# Write .roomodes JSON
$roomodesData = @{ customModes = $customModes }
$json = $roomodesData | ConvertTo-Json -Depth 10
$json | Set-Content -Path $roomodesPath -Encoding UTF8 -Force

Write-Host "Wired $agentCount agents + $squadCount squads to $roomodesPath" -ForegroundColor Green

# ─── HOOKS ───────────────────────────────────────────────────────────────────

$hooksDir = "$env:USERPROFILE\.agent\hooks"
$hookFiles = if (Test-Path $hooksDir) { (Get-ChildItem $hooksDir -File).Name } else { @() }

if ($hookFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "Hooks detected (harness-specific, not wired to Roo):" -ForegroundColor Yellow
    foreach ($h in $hookFiles) {
        Write-Host "  - $h" -ForegroundColor DarkYellow
    }
    Write-Host "  Hooks run in Claude Code / Kimi CLI context, not Roo Code." -ForegroundColor DarkGray
}

# ─── SUMMARY ─────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Roo Code wired to .agent folder" -ForegroundColor Cyan
Write-Host "  Skills:  $skillCount"
Write-Host "  Agents:  $agentCount"
Write-Host "  Squads:  $squadCount"
Write-Host "  Hooks:   $($hookFiles.Count) (not wired - harness-specific)"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Restart VS Code: to pick up skills and custom modes."

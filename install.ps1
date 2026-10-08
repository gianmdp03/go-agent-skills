<#[
Install both Agent Skills into Google Antigravity without overwriting existing copies.
Usage:
  .\install.ps1 -Scope Global
  .\install.ps1 -Scope Workspace -WorkspacePath 'C:\path\to\project'
#>
[CmdletBinding()]
param(
    [ValidateSet('Global', 'Workspace')]
    [string]$Scope = 'Global',
    [string]$WorkspacePath = (Get-Location).Path
)
$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
if ($Scope -eq 'Global') {
    $TargetRoot = Join-Path $HOME '.gemini\config\skills'
} else {
    if (-not (Test-Path -LiteralPath $WorkspacePath -PathType Container)) {
        throw "Workspace directory does not exist: $WorkspacePath"
    }
    $TargetRoot = Join-Path $WorkspacePath '.agents\skills'
}
foreach ($Name in @('go-backend','spring-to-go')) {
    $Source = Join-Path $Root $Name
    $Target = Join-Path $TargetRoot $Name
    if (-not (Test-Path -LiteralPath (Join-Path $Source 'SKILL.md'))) {
        throw "Skill source missing: $Source"
    }
    if (Test-Path -LiteralPath $Target) {
        throw "Aborted: skill already installed at $Target. Back it up/remove it manually before reinstalling."
    }
}
New-Item -ItemType Directory -Path $TargetRoot -Force | Out-Null
foreach ($Name in @('go-backend','spring-to-go')) {
    Copy-Item -LiteralPath (Join-Path $Root $Name) -Destination (Join-Path $TargetRoot $Name) -Recurse -ErrorAction Stop
    Write-Host "Installed: $(Join-Path $TargetRoot $Name)"
}
Write-Host 'Open/restart Antigravity and ask for go-backend or spring-to-go.'

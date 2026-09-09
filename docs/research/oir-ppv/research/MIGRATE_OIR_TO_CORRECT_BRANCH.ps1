param(
    [string]$Repo = 'D:\WORK\RESEARCH\MindForge'
)

$ErrorActionPreference = 'Stop'
$ExpectedPitHead = '8d57175f5b5ce7195b6132fec7863331080ac1fe'
$ExpectedPitOrigin = '8a1628d0fba93029f9b9bd6825865145278ff0c9'
$ExpectedOirHead = '461fdf80243a283140f15996748a017546cd7a91'
$Commits = @('9533ce5','f7e446d','33da436','8d57175')
$OirPath = 'docs/research/oir-ppv'

Set-Location $Repo

function Invoke-Git {
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$GitArgs
    )

    & git.exe @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "git $($GitArgs -join ' ') failed with exit $LASTEXITCODE"
    }
}

function Get-GitText {
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$GitArgs
    )

    $output = & git.exe @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "git $($GitArgs -join ' ') failed with exit $LASTEXITCODE"
    }
    return ($output | Out-String).Trim()
}

Write-Host '[1/8] Verify frozen preconditions'
$branch = Get-GitText branch --show-current
$pitHead = Get-GitText rev-parse research/pit
$pitOrigin = Get-GitText rev-parse origin/research/pit
$oirHead = Get-GitText rev-parse oir-ppv-research

if ($branch -ne 'research/pit') { throw "Expected active branch research/pit, got $branch" }
if ($pitHead -ne $ExpectedPitHead) { throw "research/pit changed: $pitHead" }
if ($pitOrigin -ne $ExpectedPitOrigin) { throw "origin/research/pit changed: $pitOrigin" }
if ($oirHead -ne $ExpectedOirHead) { throw "oir-ppv-research changed: $oirHead" }

$pitOnly = Get-GitText log --format=%H origin/research/pit..research/pit
$pitOnlyCommits = @($pitOnly -split "`r?`n" | Where-Object { $_ })
if ($pitOnlyCommits.Count -ne 4) {
    throw "Expected exactly 4 commits ahead on research/pit, found $($pitOnlyCommits.Count)"
}

foreach ($commit in $Commits) {
    & git.exe merge-base --is-ancestor $commit research/pit
    if ($LASTEXITCODE -ne 0) {
        throw "Expected migration commit $commit is not contained in research/pit"
    }
}

Write-Host '[2/8] Preserve OIR working tree in an external filesystem backup'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backup = Join-Path (Split-Path $Repo -Parent) "MindForge-OIR-MIGRATION-BACKUP-$stamp"
$src = Join-Path $Repo 'docs\research\oir-ppv'
$dst = Join-Path $backup 'docs\research\oir-ppv'
New-Item -ItemType Directory -Path $dst -Force | Out-Null

& robocopy.exe $src $dst /E /COPY:DAT /DCOPY:DAT /R:1 /W:1 /XJ /NFL /NDL /NP
$robocopyExit = $LASTEXITCODE
if ($robocopyExit -ge 8) {
    throw "robocopy backup failed with exit $robocopyExit. Partial backup retained at $backup"
}
Write-Host "Backup created: $backup"

Write-Host '[3/8] Create a Git safety stash for OIR working/untracked files'
Invoke-Git stash push -u -m "oir-ppv-branch-migration-$stamp" -- $OirPath
$stashLines = & git.exe stash list --format='%gd %s'
if ($LASTEXITCODE -ne 0) { throw 'Unable to inspect git stash list' }
$stashLine = $stashLines | Where-Object { $_ -match [regex]::Escape("oir-ppv-branch-migration-$stamp") } | Select-Object -First 1
if (-not $stashLine) { throw 'Migration stash was not created' }
$stashRef = ($stashLine -split '\s+', 2)[0]
Write-Host "Safety stash retained as: $stashRef"

Write-Host '[4/8] Switch to canonical OIR branch'
Invoke-Git switch oir-ppv-research

Write-Host '[5/8] Migrate the four OIR commits onto oir-ppv-research'
foreach ($commit in $Commits) {
    Invoke-Git cherry-pick $commit
}

Write-Host '[6/8] Restore current OIR working files from filesystem backup'
& robocopy.exe $dst $src /E /COPY:DAT /DCOPY:DAT /R:1 /W:1 /XJ /NFL /NDL /NP
$restoreExit = $LASTEXITCODE
if ($restoreExit -ge 8) {
    throw "robocopy restore failed with exit $restoreExit. Backup and safety stash are preserved."
}

Write-Host '[7/8] Restore research/pit pointer to origin/research/pit'
Invoke-Git branch -f research/pit origin/research/pit

Write-Host '[8/8] Verify branch scope, provenance, and local-only task policy'
$active = Get-GitText branch --show-current
$newPit = Get-GitText rev-parse research/pit
$newOir = Get-GitText rev-parse oir-ppv-research

if ($active -ne 'oir-ppv-research') { throw "Expected active OIR branch, got $active" }
if ($newPit -ne $ExpectedPitOrigin) { throw "research/pit not restored: $newPit" }

$remainingPitCommits = Get-GitText log --format=%H origin/research/pit..research/pit
if ($remainingPitCommits) {
    throw "research/pit still has commits ahead of origin/research/pit: $remainingPitCommits"
}

Write-Host '--- OIR migrated commits ---'
Invoke-Git log --oneline -8 oir-ppv-research

Write-Host '--- research/pit vs origin (must be empty) ---'
Invoke-Git log --oneline origin/research/pit..research/pit

Write-Host '--- OIR status ---'
Invoke-Git status --short --branch

Write-Host '--- tasks ignore policy ---'
$taskProbe = 'docs/research/oir-ppv/research/tasks/DEV_TASK_008_1.md'
& git.exe check-ignore -v $taskProbe
if ($LASTEXITCODE -ne 0) {
    throw "$taskProbe is not ignored on oir-ppv-research"
}

Write-Host "MIGRATION COMPLETE. Active branch: $active"
Write-Host "OIR HEAD: $newOir"
Write-Host "PIT HEAD: $newPit"
Write-Host "Filesystem backup: $backup"
Write-Host "Safety stash kept intentionally: $stashRef"
Write-Host 'Delete the backup/stash only after QA accepts the migrated repository.'

param(
    [string]$FixtureName = "llama3.2:1b"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $RepoRoot

$LockPath = Join-Path $RepoRoot "artifacts\model-training-pipeline\infra\owrq\IMPLEMENTATION_LOCK.json"
$AuthPath = Join-Path $RepoRoot "artifacts\model-training-pipeline\infra\owrq\LOCAL_EXECUTION_AUTHORIZATION.json"
if(-not (Test-Path $LockPath -PathType Leaf)){throw "OWRQ implementation lock missing"}
if(-not (Test-Path $AuthPath -PathType Leaf)){throw "OWRQ local execution authorization missing"}

$Lock=Get-Content $LockPath -Raw | ConvertFrom-Json
$Auth=Get-Content $AuthPath -Raw | ConvertFrom-Json
if($Lock.status -ne "LOCKED_OWRQ_INFRA_IMPLEMENTATION"){throw "Invalid OWRQ implementation lock"}
if($Auth.status -ne "AUTHORIZED_OWRQ_LOCAL_QUALIFICATION"){throw "OWRQ local qualification not authorized"}

$Head=(& git rev-parse HEAD).Trim()
$Dirty=@(& git status --porcelain --untracked-files=no)
if($Dirty.Count -gt 0){throw "Tracked worktree must be clean for OWRQ qualification"}
& git merge-base --is-ancestor ([string]$Lock.implementation_commit) $Head *> $null
if($LASTEXITCODE -ne 0){throw "OWRQ implementation lock is not an ancestor of HEAD"}

$LockBlob=(& git hash-object -- $LockPath).Trim()
if([string]$Auth.implementation_lock_git_blob_sha1 -ne $LockBlob){throw "Authorization does not bind current OWRQ lock"}

$WrapperBlob=(& git hash-object -- $PSCommandPath).Trim()
$AdapterBlob=(& git hash-object -- "tools/ollama_windows_adapter.py").Trim()
$QualifierBlob=(& git hash-object -- "tools/owrq_qualify.py").Trim()
if($WrapperBlob -ne [string]$Lock.exact_blobs.wrapper_git_blob_sha1){throw "OWRQ wrapper blob mismatch"}
if($AdapterBlob -ne [string]$Lock.exact_blobs.adapter_git_blob_sha1){throw "OWRQ adapter blob mismatch"}
if($QualifierBlob -ne [string]$Lock.exact_blobs.qualifier_git_blob_sha1){throw "OWRQ qualifier blob mismatch"}

$AttemptId=(Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssfffZ")
$OutputRoot=Join-Path $RepoRoot (".local\OWRQ\attempt-"+$AttemptId)

& python "tools/owrq_qualify.py" --output-root $OutputRoot --fixture-name $FixtureName
$Rc=$LASTEXITCODE

$Report=Join-Path $OutputRoot "OWRQ_QUALIFICATION_REPORT.json"
$Qualified=Join-Path $OutputRoot "QUALIFIED_RUNTIME_SCOPE.json"
Write-Host "OWRQ report: $Report"
if(Test-Path $Qualified -PathType Leaf){Write-Host "Qualified runtime scope: $Qualified"}
exit $Rc

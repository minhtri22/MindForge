param(
    [string]$QualifiedRuntimePath = "",
    [string]$ReportPath = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Program = "M6R2_PARITY_REPLICATION"
$ExpectedQ4Size = [int64]397807456
$ExpectedQ4Sha256 = "ca9ac3104fa025619f34eaf941f4bac95787cc4aba2818d3e972766bc02cb977"
$ExpectedQ4Manifest = "e47700cab51bcf82174aa437ed767032f7ff29e3e1594690f5b9ff91e4762e0b"
$ExpectedModelfileSha256 = "5db25cbceaaa6b359b73f7edde1f54acb6a95f27a4803f5d28ad1b65012e1946"
$ExpectedFixtureBlob = "450d83d38130765fe4a74fb18bab90177328218f"
$ExpectedProfileBlob = "1214e551c250e73b7a8cbbde71201fdd17e49ae1"
$ExpectedReasoningBlob = "3813ae3ff00a49f2f97ccbda7833e0bf299ff1e4"
$LF = [char]10

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $RepoRoot

$S2AuthPath = Join-Path $RepoRoot "artifacts\model-training-pipeline\m6r2\S2_INFRA_BINDING_AUTHORIZATION.json"
$S3AuthPath = Join-Path $RepoRoot "artifacts\model-training-pipeline\m6r2\S3_EXECUTION_AUTHORIZATION.json"
$WorkRoot = Join-Path $RepoRoot ".local\M6R2-PARITY"
$PackageDir = Join-Path $WorkRoot "package"
$EvidenceDir = Join-Path $WorkRoot "evidence"
$OutcomeDir = Join-Path $WorkRoot "outcome-ledger"
$AttemptStatePath = Join-Path $WorkRoot "outcome-exposure-state.json"

if ([string]::IsNullOrWhiteSpace($ReportPath)) {
    $ReportPath = Join-Path $WorkRoot "report\M6R2_PARITY_REPORT.json"
}

function Write-Utf8NoBom {
    param([string]$Path,[string]$Content)
    $Encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path,$Content,$Encoding)
}
function Write-AtomicJson {
    param([string]$Path,$Object)
    $Parent = Split-Path $Path -Parent
    New-Item -ItemType Directory -Force -Path $Parent | Out-Null
    $Tmp = $Path + ".tmp"
    Write-Utf8NoBom $Tmp (($Object | ConvertTo-Json -Depth 80) + [Environment]::NewLine)
    Move-Item -Force $Tmp $Path
}
function Get-Sha256File {
    param([string]$Path)
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}
function Get-Sha256Text {
    param([string]$Text)
    $Bytes = [Text.Encoding]::UTF8.GetBytes($Text)
    $Sha = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($Sha.ComputeHash($Bytes))).Replace("-","").ToLowerInvariant() }
    finally { $Sha.Dispose() }
}
function Get-Q4Identity {
    param([System.IO.FileInfo]$File)
    $Sha = Get-Sha256File $File.FullName
    $Rows = '[{"name":"model-q4_k_m.gguf","sha256":"' + $Sha + '","size":' + [string]$File.Length + '}]'
    $Manifest = Get-Sha256Text $Rows
    return [ordered]@{
        path = $File.FullName
        size = [int64]$File.Length
        sha256 = $Sha
        aggregate_manifest_hash = $Manifest
        exact_identity = (($File.Name -ceq "model-q4_k_m.gguf") -and ([int64]$File.Length -eq $ExpectedQ4Size) -and ($Sha -eq $ExpectedQ4Sha256) -and ($Manifest -eq $ExpectedQ4Manifest))
    }
}
function Invoke-NativeCaptured {
    param([string]$FilePath,[string[]]$Arguments,[string]$StdoutPath,[string]$StderrPath,[string]$WorkingDirectory="")
    foreach ($P in @($StdoutPath,$StderrPath)) { if (Test-Path $P -PathType Leaf) { Remove-Item -Force $P } }
    $Params = @{
        FilePath=$FilePath
        ArgumentList=$Arguments
        NoNewWindow=$true
        Wait=$true
        PassThru=$true
        RedirectStandardOutput=$StdoutPath
        RedirectStandardError=$StderrPath
    }
    if (-not [string]::IsNullOrWhiteSpace($WorkingDirectory)) { $Params.WorkingDirectory=$WorkingDirectory }
    $Proc = Start-Process @Params
    return [ordered]@{return_code=[int]$Proc.ExitCode;stdout_path=$StdoutPath;stderr_path=$StderrPath}
}
function Get-ModelNames {
    param($TagsResponse)
    if ($null -eq $TagsResponse -or $null -eq $TagsResponse.models) { return @() }
    return @($TagsResponse.models | ForEach-Object { [string]$_.name } | Sort-Object -Unique)
}
function Assert-FutureExecutionAuthorized {
    if (-not (Test-Path $S2AuthPath -PathType Leaf)) { throw "M6R2 S2 infra-binding execution is not authorized" }
    if (-not (Test-Path $S3AuthPath -PathType Leaf)) { throw "M6R2 S3 scientific execution is not authorized" }
    $S2 = Get-Content $S2AuthPath -Raw | ConvertFrom-Json
    $S3 = Get-Content $S3AuthPath -Raw | ConvertFrom-Json
    if ($S2.status -ne "AUTHORIZED_ONE_CONSOLIDATED_INFRA_BINDING") { throw "Invalid M6R2 S2 authorization" }
    if ($S3.status -ne "AUTHORIZED_ONE_FRESH_M6R2_OUTCOME_EXECUTION") { throw "Invalid M6R2 S3 authorization" }
    return [ordered]@{s2=$S2;s3=$S3}
}
function Assert-FrozenStudyBlobs {
    foreach ($Check in @(
        @("tests/fixtures/eval_v1/manifest.json",$ExpectedFixtureBlob),
        @("docs/model-training-pipeline/profiles/qwen2.5-0.5b-instruct-r0.yaml",$ExpectedProfileBlob),
        @("pipeline/reasoning.py",$ExpectedReasoningBlob)
    )) {
        $Actual = (& git hash-object -- $Check[0]).Trim()
        if ($Actual -ne $Check[1]) { throw "Frozen study blob mismatch: $($Check[0])" }
    }
}
function Read-And-VerifyQualifiedRuntime {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path) -or -not (Test-Path $Path -PathType Leaf)) {
        throw "BLOCKED_INFRA_BINDING: qualified OWRQ artifact missing"
    }
    $Verify = & python -m pipeline.m6r2_contract verify-binding $Path 2>&1
    if ($LASTEXITCODE -ne 0) { throw "BLOCKED_INFRA_BINDING: $($Verify -join [Environment]::NewLine)" }
    return ($Verify -join [Environment]::NewLine | ConvertFrom-Json)
}
function Assert-NoPriorOutcomeExposure {
    New-Item -ItemType Directory -Force -Path $OutcomeDir | Out-Null
    $Scan = & python -m pipeline.m6r2_contract scan-prior $OutcomeDir 2>&1
    if ($LASTEXITCODE -ne 0) { throw "INVALID_PROVENANCE: prior outcome ledger cannot be scanned" }
    $State = ($Scan -join [Environment]::NewLine | ConvertFrom-Json)
    if ($State.outcome_exposed -eq $true) { throw "M6R2 scientific outcome already exposed; rerun forbidden" }
    if ($State.ambiguous_pending_request -eq $true) { throw "INVALID_PROVENANCE: prior request has ambiguous outcome exposure" }
    if (Test-Path $AttemptStatePath -PathType Leaf) {
        $Attempt = Get-Content $AttemptStatePath -Raw | ConvertFrom-Json
        if ($Attempt.consumed -eq $true) { throw "M6R2 scientific attempt already consumed" }
    }
}
function Save-ExposureState {
    param([string]$TaskId,[string]$Reason)
    $State = [ordered]@{
        schema="mindforge-model-pipeline-m6r2-outcome-exposure-state-v1"
        consumed=$true
        consumed_at=(Get-Date).ToUniversalTime().ToString("o")
        task_id=$TaskId
        reason=$Reason
    }
    Write-AtomicJson $AttemptStatePath $State
}
function Test-ResponseExposure {
    param($Response)
    $Content = ""
    $Thinking = ""
    if ($null -ne $Response.message) {
        if ($null -ne $Response.message.PSObject.Properties["content"]) { $Content=[string]$Response.message.content }
        if ($null -ne $Response.message.PSObject.Properties["thinking"]) { $Thinking=[string]$Response.message.thinking }
    }
    return ((-not [string]::IsNullOrWhiteSpace($Content)) -or (-not [string]::IsNullOrWhiteSpace($Thinking)))
}

# MAIN — S1 implementation exists, but current branch intentionally lacks S2/S3 authorizations.
$FutureAuth = Assert-FutureExecutionAuthorized
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "git not found" }
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "python not found" }

$Head = (& git rev-parse HEAD).Trim()
$Dirty = @(& git status --porcelain --untracked-files=no)
if ($Dirty.Count -gt 0) { throw "Tracked worktree must be clean" }

Assert-FrozenStudyBlobs
Assert-NoPriorOutcomeExposure
$Binding = Read-And-VerifyQualifiedRuntime -Path $QualifiedRuntimePath

# From this point onward all runtime work is infrastructure/setup until the first eval response exposes model output.
$OllamaExe = [string]$Binding.ollama_executable_path
if ((Get-Sha256File $OllamaExe) -ne [string]$Binding.ollama_executable_sha256) {
    throw "BLOCKED_INFRA_BINDING: ollama executable hash drift"
}

$Q4Path = Join-Path $RepoRoot ".local\M6-LOCAL-Q4-RECONSTRUCTION\output\model-q4_k_m.gguf"
if (-not (Test-Path $Q4Path -PathType Leaf)) { throw "INVALID_PROVENANCE: exact Q4 parent missing" }
$Q4Identity = Get-Q4Identity (Get-Item $Q4Path)
if (-not $Q4Identity.exact_identity) { throw "INVALID_PROVENANCE: Q4 parent identity mismatch" }

New-Item -ItemType Directory -Force -Path $PackageDir,$EvidenceDir,$OutcomeDir,(Split-Path $ReportPath -Parent) | Out-Null
$PackageQ4 = Join-Path $PackageDir "model-q4_k_m.gguf"
Copy-Item -LiteralPath $Q4Path -Destination $PackageQ4 -Force
if (-not (Get-Q4Identity (Get-Item $PackageQ4)).exact_identity) { throw "INVALID_PROVENANCE: packaged Q4 identity mismatch" }

$ModelfileText = @(
    "FROM ./model-q4_k_m.gguf",
    "PARAMETER num_ctx 2048",
    "PARAMETER num_predict 128",
    "PARAMETER temperature 0",
    "PARAMETER top_p 1",
    "PARAMETER top_k 0",
    "PARAMETER seed 42",
    ""
) -join $LF
$Modelfile = Join-Path $PackageDir "Modelfile"
Write-Utf8NoBom $Modelfile $ModelfileText
if ((Get-Sha256File $Modelfile) -ne $ExpectedModelfileSha256) { throw "INVALID_PROVENANCE: frozen Modelfile mismatch" }

$HostAddress = [string]$Binding.host
$OldHost = $env:OLLAMA_HOST
$OldKv = $env:OLLAMA_KV_CACHE_TYPE
$ServerProc = $null
$CreatedOwnedModel = $false
$ModelName = "pipeline-test-m6r2-" + $Head.Substring(0,12) + "-" + $ExpectedQ4Sha256.Substring(0,12)
$InitialNames = @()
$Rows = @()
$OutcomeExposed = $false
$Classification = "UNADJUDICATED"
$ErrorRecord = $null

try {
    # Process-scoped environment reproduces the independently-qualified OWRQ scope.
    $env:OLLAMA_HOST = $HostAddress
    $env:OLLAMA_KV_CACHE_TYPE = [string]$Binding.kv_cache_type
    # Deliberately do not set OLLAMA_FLASH_ATTENTION.

    $ServerStdout = Join-Path $EvidenceDir "ollama-serve.stdout.log"
    $ServerStderr = Join-Path $EvidenceDir "ollama-serve.stderr.log"
    $ServerProc = Start-Process -FilePath $OllamaExe -ArgumentList @("serve") -PassThru -RedirectStandardOutput $ServerStdout -RedirectStandardError $ServerStderr

    $Healthy=$false
    $Tags=$null
    for($i=0;$i -lt 60;$i++){
        Start-Sleep -Seconds 1
        try {
            $Tags=Invoke-RestMethod -Method Get -Uri ("http://"+$HostAddress+"/api/tags") -TimeoutSec 2
            $Healthy=$true
            break
        } catch {}
    }
    if(-not $Healthy){ throw "INVALID_INFRA_PREOUTCOME: qualified runtime did not become healthy" }

    $InitialNames=@(Get-ModelNames $Tags)
    if(@($InitialNames | Where-Object { $_ -eq $ModelName -or $_ -eq ($ModelName+":latest") }).Count -gt 0){
        throw "INVALID_INFRA_PREOUTCOME: owned namespace collision"
    }

    $CreateOut=Join-Path $EvidenceDir "ollama-create.stdout.log"
    $CreateErr=Join-Path $EvidenceDir "ollama-create.stderr.log"
    $Create=Invoke-NativeCaptured -FilePath $OllamaExe -Arguments @("create",$ModelName,"-f","Modelfile") -StdoutPath $CreateOut -StderrPath $CreateErr -WorkingDirectory $PackageDir
    if($Create.return_code -ne 0){ throw "INVALID_INFRA_PREOUTCOME: ollama create failed" }
    $CreatedOwnedModel=$true

    $ShowBody=@{model=$ModelName} | ConvertTo-Json -Compress
    try { $null=Invoke-RestMethod -Method Post -Uri ("http://"+$HostAddress+"/api/show") -ContentType "application/json" -Body $ShowBody -TimeoutSec 30 }
    catch { throw "INVALID_INFRA_PREOUTCOME: /api/show failed after create" }

    $Fixture=Get-Content "tests/fixtures/eval_v1/manifest.json" -Raw | ConvertFrom-Json
    $Index=0
    foreach($Task in $Fixture.tasks){
        $Index++
        $RequestKey=("{0:D2}-{1}" -f $Index,[string]$Task.id)
        $StartPath=Join-Path $OutcomeDir ("request-"+$RequestKey+"-start.json")
        Write-AtomicJson $StartPath ([ordered]@{
            schema="mindforge-model-pipeline-m6r2-request-start-v1"
            task_id=[string]$Task.id
            started_at=(Get-Date).ToUniversalTime().ToString("o")
            outcome_exposed_before_request=$OutcomeExposed
        })

        $Request=[ordered]@{
            model=$ModelName
            messages=@([ordered]@{role="user";content=[string]$Task.prompt})
            stream=$false
            keep_alive=0
            options=[ordered]@{num_ctx=2048;num_predict=128;temperature=0;top_p=1;top_k=0;seed=42}
        }
        $Body=$Request | ConvertTo-Json -Depth 20 -Compress
        try {
            $Response=Invoke-RestMethod -Method Post -Uri ("http://"+$HostAddress+"/api/chat") -ContentType "application/json" -Body $Body -TimeoutSec 300
        } catch {
            $NoResponsePath=Join-Path $OutcomeDir ("request-"+$RequestKey+"-complete-no-response.json")
            Write-AtomicJson $NoResponsePath ([ordered]@{
                schema="mindforge-model-pipeline-m6r2-no-response-v1"
                task_id=[string]$Task.id
                completed_at=(Get-Date).ToUniversalTime().ToString("o")
                error=$_.Exception.Message
                outcome_exposed_before_request=$OutcomeExposed
            })
            if($OutcomeExposed){ throw "INVALID_INFRA_POSTOUTCOME: /api/chat failed after outcome exposure" }
            throw "INVALID_INFRA_PREOUTCOME: /api/chat produced no model response"
        }

        $ResponsePath=Join-Path $OutcomeDir ("request-"+$RequestKey+"-response.json")
        Write-AtomicJson $ResponsePath $Response

        $ThisExposes=Test-ResponseExposure $Response
        if($ThisExposes -and -not $OutcomeExposed){
            $OutcomeExposed=$true
            Save-ExposureState -TaskId ([string]$Task.id) -Reason "first durable eval_v1 response with non-empty content or thinking"
        }

        $RowJson=& python -c "import json,sys; from pipeline.m6r2_contract import row_from_response; task=json.loads(sys.argv[1]); resp=json.loads(sys.argv[2]); print(json.dumps(row_from_response(task,resp)))" (($Task | ConvertTo-Json -Compress)) (($Response | ConvertTo-Json -Depth 40 -Compress))
        if($LASTEXITCODE -ne 0){ throw "INVALID_PROVENANCE: row normalization failed" }
        $Rows += ($RowJson | ConvertFrom-Json)
    }

    $RowsPath=Join-Path $OutcomeDir "completed-rows.json"
    Write-AtomicJson $RowsPath ([ordered]@{rows=$Rows})
    $AdjJson=& python -m pipeline.m6r2_contract adjudicate-rows $RowsPath 2>&1
    if($LASTEXITCODE -ne 0){ throw "INVALID_PROVENANCE: parity adjudication failed" }
    $Adj=$AdjJson -join [Environment]::NewLine | ConvertFrom-Json
    $Classification=[string]$Adj.scientific_verdict

    $Report=[ordered]@{
        schema="mindforge-model-pipeline-m6r2-parity-report-v1"
        program=$Program
        completed_at=(Get-Date).ToUniversalTime().ToString("o")
        classification=$Classification
        scientific_attempt_consumed=$OutcomeExposed
        repo_head=$Head
        q4=$Q4Identity
        infra_binding=$Binding
        rows=$Rows
        adjudication=$Adj
        m6_status="FAIL_PACKAGE_CLOSED"
        m6r_status="FAIL_RUNTIME_CLOSED"
        m7_authorized=$false
        bulk_training_authorized=$false
    }
    Write-AtomicJson $ReportPath $Report
}
catch {
    $Message=$_.Exception.Message
    if($Message -like "BLOCKED_INFRA_BINDING:*"){ $Classification="BLOCKED_INFRA_BINDING" }
    elseif($Message -like "INVALID_INFRA_POSTOUTCOME:*"){ $Classification="INVALID_INFRA_POSTOUTCOME" }
    elseif($Message -like "INVALID_INFRA_PREOUTCOME:*"){ $Classification="INVALID_INFRA_PREOUTCOME" }
    elseif($Message -like "INVALID_PROVENANCE:*"){ $Classification="INVALID_PROVENANCE" }
    else { $Classification="INVALID_PROVENANCE" }
    $ErrorRecord=[ordered]@{message=$Message;type=$_.Exception.GetType().FullName;script_stack=$_.ScriptStackTrace}
    Write-AtomicJson $ReportPath ([ordered]@{
        schema="mindforge-model-pipeline-m6r2-parity-report-v1"
        program=$Program
        completed_at=(Get-Date).ToUniversalTime().ToString("o")
        classification=$Classification
        scientific_attempt_consumed=$OutcomeExposed
        scientific_fail=$false
        error=$ErrorRecord
        m6_status="FAIL_PACKAGE_CLOSED"
        m6r_status="FAIL_RUNTIME_CLOSED"
        m7_authorized=$false
        bulk_training_authorized=$false
    })
}
finally {
    if($CreatedOwnedModel){
        $RmOut=Join-Path $EvidenceDir "ollama-rm.stdout.log"
        $RmErr=Join-Path $EvidenceDir "ollama-rm.stderr.log"
        try { $null=Invoke-NativeCaptured -FilePath $OllamaExe -Arguments @("rm",$ModelName) -StdoutPath $RmOut -StderrPath $RmErr } catch {}
    }
    if($null -ne $ServerProc -and -not $ServerProc.HasExited){
        Stop-Process -Id $ServerProc.Id -Force -ErrorAction SilentlyContinue
        $ServerProc.WaitForExit(10000) | Out-Null
    }
    $env:OLLAMA_HOST=$OldHost
    $env:OLLAMA_KV_CACHE_TYPE=$OldKv
}

Write-Host "M6R2 classification: $Classification"
Write-Host "Report: $ReportPath"
if($Classification -eq "PASS_PARITY"){exit 0}else{exit 2}

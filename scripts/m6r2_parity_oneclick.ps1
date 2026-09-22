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
$ExpectedAdapterContract = "mindforge-owrq-runtime-adapter-v1"
$LF = [char]10

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $RepoRoot

$S1LockPath = Join-Path $RepoRoot "artifacts\model-training-pipeline\m6r2\S1_IMPLEMENTATION_LOCK.json"
$S2AuthPath = Join-Path $RepoRoot "artifacts\model-training-pipeline\m6r2\S2_INFRA_BINDING_AUTHORIZATION.json"
$S3AuthPath = Join-Path $RepoRoot "artifacts\model-training-pipeline\m6r2\S3_EXECUTION_AUTHORIZATION.json"
$WorkRoot = Join-Path $RepoRoot ".local\M6R2-PARITY"
$PackageDir = Join-Path $WorkRoot "package"
$EvidenceDir = Join-Path $WorkRoot "evidence"
$OutcomeDir = Join-Path $WorkRoot "outcome-ledger"
$AttemptStatePath = Join-Path $WorkRoot "outcome-exposure-state.json"
$SessionPath = Join-Path $EvidenceDir "adapter-session.json"
$CleanupPath = Join-Path $EvidenceDir "adapter-cleanup.json"

if ([string]::IsNullOrWhiteSpace($ReportPath)) { $ReportPath = Join-Path $WorkRoot "report\M6R2_PARITY_REPORT.json" }

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
        path=$File.FullName
        size=[int64]$File.Length
        sha256=$Sha
        aggregate_manifest_hash=$Manifest
        exact_identity=(($File.Name -ceq "model-q4_k_m.gguf") -and ([int64]$File.Length -eq $ExpectedQ4Size) -and ($Sha -eq $ExpectedQ4Sha256) -and ($Manifest -eq $ExpectedQ4Manifest))
    }
}
function Assert-FutureExecutionAuthorized {
    foreach($P in @($S1LockPath,$S2AuthPath,$S3AuthPath)){
        if(-not (Test-Path $P -PathType Leaf)){ throw "M6R2 runtime execution is not authorized: missing $(Split-Path $P -Leaf)" }
    }
    $Lock=Get-Content $S1LockPath -Raw | ConvertFrom-Json
    $S2=Get-Content $S2AuthPath -Raw | ConvertFrom-Json
    $S3=Get-Content $S3AuthPath -Raw | ConvertFrom-Json

    if($Lock.status -ne "LOCKED_S1_ZERO_SCIENCE_IMPLEMENTATION"){ throw "Invalid M6R2 S1 lock status" }
    if($S2.status -ne "AUTHORIZED_ONE_CONSOLIDATED_INFRA_BINDING"){ throw "Invalid M6R2 S2 authorization" }
    if($S3.status -ne "AUTHORIZED_ONE_FRESH_M6R2_OUTCOME_EXECUTION"){ throw "Invalid M6R2 S3 authorization" }
    if([int]$S3.attempts_authorized -ne 1){ throw "M6R2 S3 must authorize exactly one outcome attempt" }

    $LockBlob=(& git hash-object -- $S1LockPath).Trim()
    $S2Blob=(& git hash-object -- $S2AuthPath).Trim()
    if([string]$S2.s1_implementation_lock_git_blob_sha1 -ne $LockBlob){ throw "S2 does not bind current S1 lock" }
    if([string]$S3.s1_implementation_lock_git_blob_sha1 -ne $LockBlob){ throw "S3 does not bind current S1 lock" }
    if([string]$S3.s2_authorization_git_blob_sha1 -ne $S2Blob){ throw "S3 does not bind current S2 authorization" }

    $ScriptBlob=(& git hash-object -- $PSCommandPath).Trim()
    $ContractBlob=(& git hash-object -- "pipeline/m6r2_contract.py").Trim()
    if($ScriptBlob -ne [string]$Lock.exact_blobs.runner_git_blob_sha1){ throw "M6R2 runner blob mismatch" }
    if($ContractBlob -ne [string]$Lock.exact_blobs.contract_git_blob_sha1){ throw "M6R2 contract blob mismatch" }

    return [ordered]@{lock=$Lock;s2=$S2;s3=$S3;lock_blob=$LockBlob;s2_blob=$S2Blob}
}
function Assert-FrozenStudyBlobs {
    foreach($Check in @(
        @("tests/fixtures/eval_v1/manifest.json",$ExpectedFixtureBlob),
        @("docs/model-training-pipeline/profiles/qwen2.5-0.5b-instruct-r0.yaml",$ExpectedProfileBlob),
        @("pipeline/reasoning.py",$ExpectedReasoningBlob)
    )){
        $Actual=(& git hash-object -- $Check[0]).Trim()
        if($Actual -ne $Check[1]){ throw "INVALID_PROVENANCE: frozen study blob mismatch: $($Check[0])" }
    }
}
function Read-And-VerifyQualifiedRuntime {
    param([string]$Path,$S2)
    if([string]::IsNullOrWhiteSpace($Path) -or -not (Test-Path $Path -PathType Leaf)){ throw "BLOCKED_INFRA_BINDING: qualified OWRQ artifact missing" }
    $ActualSha=Get-Sha256File $Path
    if($ActualSha -ne [string]$S2.qualified_runtime_artifact_sha256){ throw "BLOCKED_INFRA_BINDING: qualified OWRQ artifact hash mismatch" }

    $Verify=& python -m pipeline.m6r2_contract verify-binding $Path 2>&1
    if($LASTEXITCODE -ne 0){ throw "BLOCKED_INFRA_BINDING: $($Verify -join [Environment]::NewLine)" }
    $Binding=$Verify -join [Environment]::NewLine | ConvertFrom-Json

    $AdapterPath=Join-Path $RepoRoot ([string]$Binding.runtime_adapter_entrypoint)
    if(-not (Test-Path $AdapterPath -PathType Leaf)){ throw "BLOCKED_INFRA_BINDING: qualified adapter entrypoint missing" }
    $AdapterBlob=(& git hash-object -- $AdapterPath).Trim()
    if($AdapterBlob -ne [string]$Binding.runtime_adapter_git_blob_sha1){ throw "BLOCKED_INFRA_BINDING: qualified adapter blob drift" }
    if([string]$Binding.runtime_adapter_contract_version -ne $ExpectedAdapterContract){ throw "BLOCKED_INFRA_BINDING: adapter contract drift" }

    if($null -ne $S2.PSObject.Properties["required_scope"]){
        $Scope=$S2.required_scope
        foreach($Pair in @(
            @("ollama_version",[string]$Binding.ollama_version,[string]$Scope.ollama_version),
            @("ollama_executable_sha256",[string]$Binding.ollama_executable_sha256,[string]$Scope.ollama_executable_sha256),
            @("runtime_adapter_git_blob_sha1",[string]$Binding.runtime_adapter_git_blob_sha1,[string]$Scope.runtime_adapter_git_blob_sha1),
            @("local_machine_fingerprint_sha256",[string]$Binding.local_machine_fingerprint_sha256,[string]$Scope.local_machine_fingerprint_sha256),
            @("host",[string]$Binding.host,[string]$Scope.host),
            @("kv_cache_type",[string]$Binding.kv_cache_type,[string]$Scope.kv_cache_type),
            @("flash_attention_mode",[string]$Binding.flash_attention_mode,[string]$Scope.flash_attention_mode)
        )){
            if($Pair[1] -ne $Pair[2]){ throw "BLOCKED_INFRA_BINDING: scope mismatch $($Pair[0])" }
        }
    }
    return [ordered]@{binding=$Binding;adapter_path=$AdapterPath;artifact_sha256=$ActualSha}
}
function Assert-NoPriorOutcomeExposure {
    New-Item -ItemType Directory -Force -Path $OutcomeDir | Out-Null
    $Scan=& python -m pipeline.m6r2_contract scan-prior $OutcomeDir 2>&1
    if($LASTEXITCODE -ne 0){ throw "INVALID_PROVENANCE: prior outcome ledger cannot be scanned" }
    $State=$Scan -join [Environment]::NewLine | ConvertFrom-Json
    if($State.outcome_exposed -eq $true){ throw "INVALID_PROVENANCE: prior scientific outcome already exposed; rerun forbidden" }
    if($State.ambiguous_pending_request -eq $true){ throw "INVALID_PROVENANCE: prior request has ambiguous outcome exposure" }
    if(Test-Path $AttemptStatePath -PathType Leaf){
        $Attempt=Get-Content $AttemptStatePath -Raw | ConvertFrom-Json
        if($Attempt.consumed -eq $true){ throw "INVALID_PROVENANCE: M6R2 scientific attempt already consumed" }
    }
}
function Save-ExposureState {
    param([string]$TaskId,[string]$Reason)
    Write-AtomicJson $AttemptStatePath ([ordered]@{
        schema="mindforge-model-pipeline-m6r2-outcome-exposure-state-v1"
        consumed=$true
        consumed_at=(Get-Date).ToUniversalTime().ToString("o")
        task_id=$TaskId
        reason=$Reason
    })
}
function Test-ResponseExposure {
    param($Response)
    $Content=""
    $Thinking=""
    if($null -ne $Response.message){
        if($null -ne $Response.message.PSObject.Properties["content"]){$Content=[string]$Response.message.content}
        if($null -ne $Response.message.PSObject.Properties["thinking"]){$Thinking=[string]$Response.message.thinking}
    }
    return ((-not [string]::IsNullOrWhiteSpace($Content)) -or (-not [string]::IsNullOrWhiteSpace($Thinking)))
}
function Invoke-QualifiedAdapter {
    param([string]$AdapterPath,[string[]]$Arguments)
    $Output=& python $AdapterPath @Arguments 2>&1
    $Rc=$LASTEXITCODE
    return [ordered]@{return_code=$Rc;output=@($Output)}
}
function Get-EvidenceManifest {
    $Items=@()
    foreach($Dir in @($EvidenceDir,$OutcomeDir)){
        if(Test-Path $Dir -PathType Container){
            foreach($F in @(Get-ChildItem -LiteralPath $Dir -File | Sort-Object FullName)){
                $Items += [ordered]@{
                    relative_path=$F.FullName.Substring($WorkRoot.Length).TrimStart("\")
                    size=[int64]$F.Length
                    sha256=Get-Sha256File $F.FullName
                }
            }
        }
    }
    return [ordered]@{files=$Items;manifest_sha256=Get-Sha256Text (($Items | ConvertTo-Json -Depth 20 -Compress))}
}

# MAIN — current S1 branch intentionally lacks S2/S3 authorizations.
if(-not (Get-Command git -ErrorAction SilentlyContinue)){throw "git not found"}
if(-not (Get-Command python -ErrorAction SilentlyContinue)){throw "python not found"}
$FutureAuth=Assert-FutureExecutionAuthorized

$OutcomeExposed=$false
$Classification="UNADJUDICATED"
$Rows=@()
$SessionOpened=$false
$CleanupPass=$true
$NoMutationPass=$true
$BindingInfo=$null
$Q4Identity=$null
$Head=(& git rev-parse HEAD).Trim()

New-Item -ItemType Directory -Force -Path $WorkRoot,$PackageDir,$EvidenceDir,$OutcomeDir,(Split-Path $ReportPath -Parent) | Out-Null

try {
    $Dirty=@(& git status --porcelain --untracked-files=no)
    if($Dirty.Count -gt 0){throw "INVALID_PROVENANCE: tracked worktree must be clean"}

    Assert-FrozenStudyBlobs
    Assert-NoPriorOutcomeExposure
    $BindingInfo=Read-And-VerifyQualifiedRuntime -Path $QualifiedRuntimePath -S2 $FutureAuth.s2
    $Binding=$BindingInfo.binding
    $AdapterPath=$BindingInfo.adapter_path

    $Q4Path=Join-Path $RepoRoot ".local\M6-LOCAL-Q4-RECONSTRUCTION\output\model-q4_k_m.gguf"
    if(-not (Test-Path $Q4Path -PathType Leaf)){throw "INVALID_PROVENANCE: exact Q4 parent missing"}
    $Q4Identity=Get-Q4Identity (Get-Item $Q4Path)
    if(-not $Q4Identity.exact_identity){throw "INVALID_PROVENANCE: Q4 parent identity mismatch"}

    $PackageQ4=Join-Path $PackageDir "model-q4_k_m.gguf"
    Copy-Item -LiteralPath $Q4Path -Destination $PackageQ4 -Force
    if(-not (Get-Q4Identity (Get-Item $PackageQ4)).exact_identity){throw "INVALID_PROVENANCE: packaged Q4 identity mismatch"}

    $ModelfileText=@(
        "FROM ./model-q4_k_m.gguf",
        "PARAMETER num_ctx 2048",
        "PARAMETER num_predict 128",
        "PARAMETER temperature 0",
        "PARAMETER top_p 1",
        "PARAMETER top_k 0",
        "PARAMETER seed 42",
        ""
    ) -join $LF
    $Modelfile=Join-Path $PackageDir "Modelfile"
    Write-Utf8NoBom $Modelfile $ModelfileText
    if((Get-Sha256File $Modelfile) -ne $ExpectedModelfileSha256){throw "INVALID_PROVENANCE: frozen Modelfile mismatch"}

    $ModelName="pipeline-test-m6r2-"+$Head.Substring(0,12)+"-"+$ExpectedQ4Sha256.Substring(0,12)
    $Open=Invoke-QualifiedAdapter -AdapterPath $AdapterPath -Arguments @(
        "session-open",
        "--qualified-runtime",$QualifiedRuntimePath,
        "--q4-path",$PackageQ4,
        "--modelfile-path",$Modelfile,
        "--model-name",$ModelName,
        "--evidence-dir",$EvidenceDir,
        "--session-out",$SessionPath
    )
    if($Open.return_code -ne 0 -or -not (Test-Path $SessionPath -PathType Leaf)){throw "INVALID_INFRA_PREOUTCOME: qualified adapter session-open failed"}
    $Session=Get-Content $SessionPath -Raw | ConvertFrom-Json
    if($Session.status -ne "READY"){throw "INVALID_INFRA_PREOUTCOME: adapter session not ready"}
    $SessionOpened=$true

    $Fixture=Get-Content "tests/fixtures/eval_v1/manifest.json" -Raw | ConvertFrom-Json
    $Index=0
    foreach($Task in $Fixture.tasks){
        $Index++
        $RequestKey=("{0:D2}-{1}" -f $Index,[string]$Task.id)
        $TaskPath=Join-Path $OutcomeDir ("request-"+$RequestKey+"-task.json")
        $RequestPath=Join-Path $OutcomeDir ("request-"+$RequestKey+"-request.json")
        $StartPath=Join-Path $OutcomeDir ("request-"+$RequestKey+"-start.json")
        $ResponsePath=Join-Path $OutcomeDir ("request-"+$RequestKey+"-response.json")
        $TransportPath=Join-Path $OutcomeDir ("request-"+$RequestKey+"-transport.json")
        $NoResponsePath=Join-Path $OutcomeDir ("request-"+$RequestKey+"-complete-no-response.json")

        Write-AtomicJson $TaskPath $Task
        Write-AtomicJson $RequestPath ([ordered]@{
            messages=@([ordered]@{role="user";content=[string]$Task.prompt})
            stream=$false
            keep_alive=0
            options=[ordered]@{num_ctx=2048;num_predict=128;temperature=0;top_p=1;top_k=0;seed=42}
        })
        Write-AtomicJson $StartPath ([ordered]@{
            schema="mindforge-model-pipeline-m6r2-request-start-v1"
            task_id=[string]$Task.id
            started_at=(Get-Date).ToUniversalTime().ToString("o")
            outcome_exposed_before_request=$OutcomeExposed
        })

        $Chat=Invoke-QualifiedAdapter -AdapterPath $AdapterPath -Arguments @(
            "chat",
            "--session-file",$SessionPath,
            "--request-file",$RequestPath,
            "--response-file",$ResponsePath,
            "--transport-evidence-file",$TransportPath
        )

        if(Test-Path $ResponsePath -PathType Leaf){
            $Response=Get-Content $ResponsePath -Raw | ConvertFrom-Json
            $ThisExposes=Test-ResponseExposure $Response
            if($ThisExposes -and -not $OutcomeExposed){
                $OutcomeExposed=$true
                Save-ExposureState -TaskId ([string]$Task.id) -Reason "first durable eval_v1 response with non-empty content or thinking"
            }
        } else {
            Write-AtomicJson $NoResponsePath ([ordered]@{
                schema="mindforge-model-pipeline-m6r2-no-response-v1"
                task_id=[string]$Task.id
                completed_at=(Get-Date).ToUniversalTime().ToString("o")
                adapter_return_code=$Chat.return_code
                outcome_exposed_before_request=$OutcomeExposed
            })
        }

        if($Chat.return_code -ne 0){
            $PositiveInfra=$false
            if(Test-Path $TransportPath -PathType Leaf){
                $Transport=Get-Content $TransportPath -Raw | ConvertFrom-Json
                $PositiveInfra=($Transport.positive_infra_failure -eq $true)
            }
            if($OutcomeExposed){throw "INVALID_INFRA_POSTOUTCOME: qualified adapter chat failed after outcome exposure"}
            if($PositiveInfra){throw "INVALID_INFRA_PREOUTCOME: qualified adapter supplied positive infra failure evidence"}
            throw "INVALID_PROVENANCE: chat failed before outcome exposure without positive infra evidence"
        }

        if(-not (Test-Path $ResponsePath -PathType Leaf)){throw "INVALID_PROVENANCE: adapter returned success without durable response"}
        $RowJson=& python -m pipeline.m6r2_contract row-from-files $TaskPath $ResponsePath 2>&1
        if($LASTEXITCODE -ne 0){throw "INVALID_PROVENANCE: row normalization failed"}
        $Rows += ($RowJson -join [Environment]::NewLine | ConvertFrom-Json)
    }

    $RowsPath=Join-Path $OutcomeDir "completed-rows.json"
    Write-AtomicJson $RowsPath ([ordered]@{rows=$Rows})
    $AdjJson=& python -m pipeline.m6r2_contract adjudicate-rows $RowsPath 2>&1
    if($LASTEXITCODE -ne 0){throw "INVALID_PROVENANCE: parity adjudication failed"}
    $Adj=$AdjJson -join [Environment]::NewLine | ConvertFrom-Json
    $Classification=[string]$Adj.scientific_verdict
}
catch {
    $Message=$_.Exception.Message
    if($Message -like "BLOCKED_INFRA_BINDING:*"){$Classification="BLOCKED_INFRA_BINDING"}
    elseif($Message -like "INVALID_INFRA_POSTOUTCOME:*"){$Classification="INVALID_INFRA_POSTOUTCOME"}
    elseif($Message -like "INVALID_INFRA_PREOUTCOME:*"){$Classification="INVALID_INFRA_PREOUTCOME"}
    else {$Classification="INVALID_PROVENANCE"}
}
finally {
    if($SessionOpened -and $null -ne $BindingInfo){
        $Close=Invoke-QualifiedAdapter -AdapterPath $BindingInfo.adapter_path -Arguments @(
            "session-close",
            "--session-file",$SessionPath,
            "--cleanup-out",$CleanupPath
        )
        if($Close.return_code -ne 0 -or -not (Test-Path $CleanupPath -PathType Leaf)){
            $CleanupPass=$false
            $NoMutationPass=$false
        } else {
            $Cleanup=Get-Content $CleanupPath -Raw | ConvertFrom-Json
            $CleanupPass=($Cleanup.owned_cleanup_pass -eq $true)
            $NoMutationPass=($Cleanup.initial_final_model_sets_match -eq $true)
        }
        if(-not $CleanupPass -or -not $NoMutationPass){
            if($OutcomeExposed){$Classification="INVALID_INFRA_POSTOUTCOME"}else{$Classification="INVALID_INFRA_PREOUTCOME"}
        }
    }

    $Manifest=Get-EvidenceManifest
    $Report=[ordered]@{
        schema="mindforge-model-pipeline-m6r2-parity-report-v1"
        program=$Program
        completed_at=(Get-Date).ToUniversalTime().ToString("o")
        classification=$Classification
        scientific_attempt_consumed=$OutcomeExposed
        scientific_fail=($Classification -eq "FAIL_PARITY" -or $Classification -eq "FAIL_REASONING_MAPPING")
        repo_head=$Head
        q4=$Q4Identity
        infra_binding=$BindingInfo
        rows=$Rows
        cleanup=[ordered]@{owned_cleanup_pass=$CleanupPass;initial_final_model_sets_match=$NoMutationPass}
        evidence_manifest=$Manifest
        m6_status="FAIL_PACKAGE_CLOSED"
        m6r_status="FAIL_RUNTIME_CLOSED"
        m7_authorized=$false
        bulk_training_authorized=$false
    }
    Write-AtomicJson $ReportPath $Report
}

Write-Host "M6R2 classification: $Classification"
Write-Host "Report: $ReportPath"
if($Classification -eq "PASS_PARITY"){exit 0}else{exit 2}

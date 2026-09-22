param(
    [string[]]$AdditionalSearchRoot = @(),
    [string]$ReportPath = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Program = "M6_LOCAL_WINDOWS_VENUE_PREFLIGHT"
$ExpectedBranch = "research/model-pipeline-m6-ollama"
$VenueAmendmentCommit = "4aed637eb8bb41cc5e67c7b079402cf16d6948d2"
$VenueAmendmentBlob = "5d67202f3103f36736cf0e7973c054cf6df658fd"
$Q4ReconstructionAuthorizationCommit = "9506e5fc205e641aba942a0bc9ff2fbaa7d881a5"
$Q4ReconstructionAuthorizationBlob = "f26754440d710904f45eb1d7916d334484f43bb5"
$ExpectedLlamaCommit = "ce8caa6e60a03093351d6016a818720e0d46f0fb"
$ExpectedOllamaVersion = "0.34.2"

$F16 = [ordered]@{
    filename = "model-f16.gguf"
    size_bytes = [int64]994156384
    sha256 = "437c300945705b9a255322366eab3017e890ac6d997716eb7d1351b2e76f4d4b"
    aggregate_manifest_hash = "eb1113def8177252743eb462aa06d24925387f6c5544f27a115850bc6f0efbb8"
}
$Q4 = [ordered]@{
    filename = "model-q4_k_m.gguf"
    size_bytes = [int64]397807456
    sha256 = "ca9ac3104fa025619f34eaf941f4bac95787cc4aba2818d3e972766bc02cb977"
    aggregate_manifest_hash = "e47700cab51bcf82174aa437ed767032f7ff29e3e1594690f5b9ff91e4762e0b"
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $RepoRoot

$LockPath = Join-Path $RepoRoot "artifacts\model-training-pipeline\m6\local_windows\LOCAL_WINDOWS_PREFLIGHT_LOCK.json"
if (-not (Test-Path $LockPath -PathType Leaf)) {
    throw "Local Windows preflight lock missing: $LockPath"
}
$Lock = Get-Content $LockPath -Raw | ConvertFrom-Json

if ([string]::IsNullOrWhiteSpace($ReportPath)) {
    $ReportDir = Join-Path $RepoRoot ".local\M6-LOCAL-PREFLIGHT\report"
    New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
    $ReportPath = Join-Path $ReportDir "M6_LOCAL_WINDOWS_PREFLIGHT_REPORT.json"
} else {
    $ReportPath = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $ReportPath))
    New-Item -ItemType Directory -Force -Path (Split-Path $ReportPath -Parent) | Out-Null
}

function Write-Utf8NoBom {
    param([string]$Path,[string]$Content)
    $Encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path,$Content,$Encoding)
}

function Get-Sha256File {
    param([string]$Path)
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}

function Get-Sha256Text {
    param([string]$Text)
    $Bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $Sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([System.BitConverter]::ToString($Sha.ComputeHash($Bytes))).Replace("-","").ToLowerInvariant()
    } finally {
        $Sha.Dispose()
    }
}

function Test-GitAncestor {
    param([string]$Ancestor,[string]$Descendant)
    & git merge-base --is-ancestor $Ancestor $Descendant *> $null
    return ($LASTEXITCODE -eq 0)
}

function Get-CandidateRecord {
    param([System.IO.FileInfo]$File,[hashtable]$Expected)

    $Sha = Get-Sha256File $File.FullName
    $ManifestJson = '[{"name":"' + $Expected.filename + '","sha256":"' + $Sha + '","size":' + [string]$File.Length + '}]'
    $ManifestHash = Get-Sha256Text $ManifestJson
    $Checks = [ordered]@{
        filename_exact = ($File.Name -ceq $Expected.filename)
        size_exact = ([int64]$File.Length -eq [int64]$Expected.size_bytes)
        sha256_exact = ($Sha -eq $Expected.sha256)
        aggregate_manifest_exact = ($ManifestHash -eq $Expected.aggregate_manifest_hash)
    }
    $Exact = ($Checks.filename_exact -and $Checks.size_exact -and $Checks.sha256_exact -and $Checks.aggregate_manifest_exact)
    return [ordered]@{
        path = $File.FullName
        length = [int64]$File.Length
        sha256 = $Sha
        aggregate_manifest_hash = $ManifestHash
        checks = $Checks
        exact_identity = $Exact
    }
}

function Get-CommandInventory {
    param([string]$Name,[string[]]$FallbackPaths = @())
    $Candidates = @()
    $Cmd = Get-Command $Name -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -ne $Cmd -and $Cmd.Source) { $Candidates += $Cmd.Source }
    foreach ($Path in $FallbackPaths) {
        if (-not [string]::IsNullOrWhiteSpace($Path) -and (Test-Path $Path -PathType Leaf)) {
            $Candidates += (Resolve-Path $Path).Path
        }
    }
    $Candidates = @($Candidates | Select-Object -Unique)
    return $Candidates
}

$Report = [ordered]@{
    schema = "mindforge-model-pipeline-m6-local-windows-preflight-report-v1"
    program = $Program
    started_at = (Get-Date).ToUniversalTime().ToString("o")
    completed_at = $null
    overall_status = "RUNNING"
    classification = "UNADJUDICATED"
    repo = [ordered]@{}
    host = [ordered]@{}
    governance = [ordered]@{}
    search = [ordered]@{}
    artifacts = [ordered]@{}
    runtime = [ordered]@{}
    boundaries = [ordered]@{
        model_download_executed = $false
        f16_regeneration_executed = $false
        hf_to_gguf_conversion_executed = $false
        llama_quantize_executed = $false
        llama_cli_inference_executed = $false
        ollama_server_started = $false
        ollama_create_executed = $false
        ollama_chat_executed = $false
        fixture_evaluation_executed = $false
        scientific_adjudication_executed = $false
        q4_reconstruction_authorization_consumed = $false
        m7_authorized = $false
        bulk_training_authorized = $false
    }
    next_valid_action = $null
    error = $null
}

function Save-Report {
    $Report.completed_at = (Get-Date).ToUniversalTime().ToString("o")
    Write-Utf8NoBom -Path $ReportPath -Content (($Report | ConvertTo-Json -Depth 30) + [Environment]::NewLine)
}

try {
    Write-Host "=== MindForge M6 Local Windows Preflight ==="
    Write-Host "Repo: $RepoRoot"
    Write-Host "Report: $ReportPath"

    if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "git not found in PATH" }

    $Head = (& git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) { throw "Not inside a Git repository" }
    $Branch = (& git branch --show-current).Trim()
    if ($Branch -ne $ExpectedBranch) {
        throw "Wrong branch. expected=$ExpectedBranch actual=$Branch"
    }

    $TrackedStatus = @(& git status --porcelain --untracked-files=no)
    if ($TrackedStatus.Count -gt 0) {
        throw "Tracked working tree is dirty: $($TrackedStatus -join '; ')"
    }

    if (-not (Test-GitAncestor -Ancestor $VenueAmendmentCommit -Descendant $Head)) {
        throw "Venue-independence amendment is not an ancestor of current HEAD"
    }
    if (-not (Test-GitAncestor -Ancestor ([string]$Lock.implementation_commit) -Descendant $Head)) {
        throw "Locked local-preflight implementation is not an ancestor of current HEAD"
    }

    $ScriptBlob = (& git hash-object -- $PSCommandPath).Trim()
    if ($ScriptBlob -ne [string]$Lock.script_git_blob_sha1) {
        throw "Preflight script blob mismatch expected=$($Lock.script_git_blob_sha1) actual=$ScriptBlob"
    }

    $AmendmentPath = "artifacts/model-training-pipeline/m6/VENUE_INDEPENDENCE_GOVERNANCE_AMENDMENT.json"
    $AmendmentBlob = (& git hash-object -- $AmendmentPath).Trim()
    if ($AmendmentBlob -ne $VenueAmendmentBlob) {
        throw "Venue amendment blob mismatch"
    }

    $ReconPath = "artifacts/model-training-pipeline/m6/parent_artifact/DETERMINISTIC_RECONSTRUCTION_AUTHORIZATION.json"
    $ReconBlob = (& git hash-object -- $ReconPath).Trim()
    if ($ReconBlob -ne $Q4ReconstructionAuthorizationBlob) {
        throw "Q4 reconstruction authorization blob mismatch"
    }

    $Report.repo = [ordered]@{
        root = $RepoRoot
        branch = $Branch
        head = $Head
        tracked_worktree_clean = $true
        script_git_blob_sha1 = $ScriptBlob
    }
    $Report.governance = [ordered]@{
        venue_independence_amendment_commit = $VenueAmendmentCommit
        venue_independence_amendment_blob = $AmendmentBlob
        local_preflight_implementation_commit = [string]$Lock.implementation_commit
        local_preflight_lock_blob_expected = [string]$Lock.lock_git_blob_sha1
        q4_reconstruction_authorization_commit = $Q4ReconstructionAuthorizationCommit
        q4_reconstruction_authorization_blob = $ReconBlob
        q4_reconstruction_authorization_consumed = $false
    }

    $OS = Get-CimInstance Win32_OperatingSystem
    $CPU = Get-CimInstance Win32_Processor | Select-Object -First 1
    $Computer = Get-CimInstance Win32_ComputerSystem
    $Report.host = [ordered]@{
        computer_name = $env:COMPUTERNAME
        os_caption = $OS.Caption
        os_version = $OS.Version
        os_build = $OS.BuildNumber
        architecture = $OS.OSArchitecture
        cpu = $CPU.Name.Trim()
        logical_processors = $CPU.NumberOfLogicalProcessors
        memory_bytes = [int64]$Computer.TotalPhysicalMemory
        powershell_version = $PSVersionTable.PSVersion.ToString()
        git_version = (& git --version).Trim()
        cmake = if (Get-Command cmake -ErrorAction SilentlyContinue) { ((& cmake --version | Select-Object -First 1).Trim()) } else { $null }
    }

    $SearchRoots = @()
    $SearchRoots += $RepoRoot
    $ParentRoot = Split-Path $RepoRoot -Parent
    if (-not [string]::IsNullOrWhiteSpace($ParentRoot)) { $SearchRoots += $ParentRoot }
    foreach ($Extra in $AdditionalSearchRoot) {
        if ([string]::IsNullOrWhiteSpace($Extra)) { continue }
        if (Test-Path $Extra -PathType Container) {
            $SearchRoots += (Resolve-Path $Extra).Path
        }
    }
    $SearchRoots = @($SearchRoots | Select-Object -Unique)

    $F16Candidates = @()
    $Q4Candidates = @()
    foreach ($Root in $SearchRoots) {
        Write-Host "Searching bounded root: $Root"
        foreach ($File in @(Get-ChildItem -LiteralPath $Root -Recurse -File -Filter $F16.filename -ErrorAction SilentlyContinue)) {
            $F16Candidates += Get-CandidateRecord -File $File -Expected $F16
        }
        foreach ($File in @(Get-ChildItem -LiteralPath $Root -Recurse -File -Filter $Q4.filename -ErrorAction SilentlyContinue)) {
            $Q4Candidates += Get-CandidateRecord -File $File -Expected $Q4
        }
    }

    $F16Candidates = @($F16Candidates | Sort-Object path -Unique)
    $Q4Candidates = @($Q4Candidates | Sort-Object path -Unique)
    $ExactF16 = @($F16Candidates | Where-Object { $_.exact_identity })
    $ExactQ4 = @($Q4Candidates | Where-Object { $_.exact_identity })

    $Report.search = [ordered]@{
        roots = $SearchRoots
        whole_drive_scan = $false
        f16_candidate_count = $F16Candidates.Count
        q4_candidate_count = $Q4Candidates.Count
        exact_f16_count = $ExactF16.Count
        exact_q4_count = $ExactQ4.Count
    }
    $Report.artifacts = [ordered]@{
        frozen_f16 = $F16
        frozen_q4 = $Q4
        f16_candidates = $F16Candidates
        q4_candidates = $Q4Candidates
        selected_f16 = if ($ExactF16.Count -gt 0) { $ExactF16[0] } else { $null }
        selected_q4 = if ($ExactQ4.Count -gt 0) { $ExactQ4[0] } else { $null }
    }

    $OllamaFallbacks = @(
        (Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"),
        (Join-Path $env:LOCALAPPDATA "Ollama\ollama.exe"),
        (Join-Path $env:ProgramFiles "Ollama\ollama.exe")
    )
    $OllamaPaths = @(Get-CommandInventory -Name "ollama.exe" -FallbackPaths $OllamaFallbacks)
    if ($OllamaPaths.Count -eq 0) {
        $OllamaPaths = @(Get-CommandInventory -Name "ollama" -FallbackPaths $OllamaFallbacks)
    }
    $OllamaInventory = @()
    foreach ($Path in $OllamaPaths) {
        $VersionOutput = @(& $Path --version 2>&1)
        $VersionExit = $LASTEXITCODE
        $OllamaInventory += [ordered]@{
            path = $Path
            sha256 = Get-Sha256File $Path
            version_exit_code = $VersionExit
            version_output = ($VersionOutput -join [Environment]::NewLine)
            expected_version_string_present = (($VersionOutput -join " ") -match [regex]::Escape($ExpectedOllamaVersion))
        }
    }

    $KnownLlamaDirs = @()
    foreach ($Root in $SearchRoots) {
        foreach ($Dir in @(Get-ChildItem -LiteralPath $Root -Recurse -Directory -Filter "llama.cpp" -ErrorAction SilentlyContinue)) {
            if (Test-Path (Join-Path $Dir.FullName ".git")) { $KnownLlamaDirs += $Dir.FullName }
        }
    }
    $KnownLlamaDirs = @($KnownLlamaDirs | Select-Object -Unique)
    $LlamaInventory = @()
    foreach ($Dir in $KnownLlamaDirs) {
        $Commit = (& git -C $Dir rev-parse HEAD 2>$null).Trim()
        $Cli = @(Get-ChildItem -LiteralPath $Dir -Recurse -File -Filter "llama-cli.exe" -ErrorAction SilentlyContinue | Select-Object -First 1)
        $Quant = @(Get-ChildItem -LiteralPath $Dir -Recurse -File -Filter "llama-quantize.exe" -ErrorAction SilentlyContinue | Select-Object -First 1)
        $LlamaInventory += [ordered]@{
            source_path = $Dir
            source_commit = $Commit
            source_commit_exact = ($Commit -eq $ExpectedLlamaCommit)
            llama_cli = if ($Cli.Count -gt 0) { [ordered]@{ path=$Cli[0].FullName; sha256=(Get-Sha256File $Cli[0].FullName) } } else { $null }
            llama_quantize = if ($Quant.Count -gt 0) { [ordered]@{ path=$Quant[0].FullName; sha256=(Get-Sha256File $Quant[0].FullName) } } else { $null }
        }
    }

    $Report.runtime = [ordered]@{
        ollama_expected_version = $ExpectedOllamaVersion
        ollama = $OllamaInventory
        llama_cpp_expected_commit = $ExpectedLlamaCommit
        llama_cpp = $LlamaInventory
    }

    if ($ExactQ4.Count -gt 0 -and $ExactF16.Count -gt 0) {
        $Report.classification = "LOCAL_Q4_AND_F16_ADMITTED"
        $Report.next_valid_action = "OPEN_LOCAL_OLLAMA_M6_EXECUTION_AUTHORIZATION_USING_SELECTED_EXACT_Q4"
    } elseif ($ExactQ4.Count -gt 0) {
        $Report.classification = "LOCAL_Q4_ADMITTED"
        $Report.next_valid_action = "OPEN_LOCAL_OLLAMA_M6_EXECUTION_AUTHORIZATION_USING_SELECTED_EXACT_Q4"
    } elseif ($ExactF16.Count -gt 0) {
        $Report.classification = "LOCAL_F16_ADMITTED"
        $Report.next_valid_action = "CREATE_NEW_LOCAL_Q4_RECONSTRUCTION_ORCHESTRATION_USING_UNCONSUMED_9506E5FC_AUTHORIZATION"
    } elseif (($F16Candidates.Count + $Q4Candidates.Count) -gt 0) {
        $Report.classification = "LOCAL_PARENT_ARTIFACT_IDENTITY_MISMATCH_ONLY"
        $Report.next_valid_action = "FREEZE_LOCAL_MISMATCH_EVIDENCE_AND_OPEN_SEPARATE_LOCAL_ARTIFACT_REGENERATION_DECISION"
    } else {
        $Report.classification = "LOCAL_PARENT_ARTIFACTS_NOT_FOUND"
        $Report.next_valid_action = "OPEN_PREOUTCOME_DETERMINISTIC_LOCAL_ARTIFACT_REGENERATION_AUTHORIZATION"
    }

    $Report.overall_status = "PASS"
    Save-Report

    Write-Host ""
    Write-Host "=== M6 LOCAL WINDOWS PREFLIGHT COMPLETE ==="
    Write-Host "Classification: $($Report.classification)"
    Write-Host "Report JSON: $ReportPath"
    Write-Host "No model regeneration, quantization, inference, scientific Ollama operation, or scientific adjudication was executed."
    exit 0
}
catch {
    $Report.overall_status = "FAIL"
    $Report.classification = "INVALID_LOCAL_PREFLIGHT_INFRASTRUCTURE"
    $Report.error = [ordered]@{
        message = $_.Exception.Message
        type = $_.Exception.GetType().FullName
        script_stack = $_.ScriptStackTrace
    }
    Save-Report
    Write-Error $_
    Write-Host "Report JSON: $ReportPath"
    exit 2
}
finally {
    Save-Report
}

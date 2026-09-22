param(
    [string]$ReportPath = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Program = "M6R_SYSTEM_OLLAMA_REPLICATION"
$ExpectedOllamaVersion = "0.34.2"
$OllamaInstallerUrl = "https://github.com/ollama/ollama/releases/download/v0.34.2/OllamaSetup.exe"
$OllamaInstallerSha256 = "8c9eb7ba71f3c6a62df4c7d204cc4739d90c335e1cbeb07c99fd471544066a8b"
$ExpectedQ4Size = [int64]397807456
$ExpectedQ4Sha256 = "ca9ac3104fa025619f34eaf941f4bac95787cc4aba2818d3e972766bc02cb977"
$ExpectedQ4Manifest = "e47700cab51bcf82174aa437ed767032f7ff29e3e1594690f5b9ff91e4762e0b"
$ExpectedModelfileSha256 = "5db25cbceaaa6b359b73f7edde1f54acb6a95f27a4803f5d28ad1b65012e1946"
$ExpectedFixtureBlob = "450d83d38130765fe4a74fb18bab90177328218f"
$ExpectedProfileBlob = "1214e551c250e73b7a8cbbde71201fdd17e49ae1"
$ExpectedReasoningBlob = "3813ae3ff00a49f2f97ccbda7833e0bf299ff1e4"
$HostAddress = "127.0.0.1:11434"
$LF = [char]10

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $RepoRoot

$LockPath = Join-Path $RepoRoot "artifacts\model-training-pipeline\m6r\system_ollama\SYSTEM_OLLAMA_RUNTIME_LOCK.json"
$AuthPath = Join-Path $RepoRoot "artifacts\model-training-pipeline\m6r\system_ollama\EXECUTION_AUTHORIZATION.json"
if (-not (Test-Path $LockPath -PathType Leaf)) { throw "M6R system Ollama runtime lock missing" }
if (-not (Test-Path $AuthPath -PathType Leaf)) { throw "M6R system Ollama execution authorization missing" }
$Lock = Get-Content $LockPath -Raw | ConvertFrom-Json
$Auth = Get-Content $AuthPath -Raw | ConvertFrom-Json

$WorkRoot = Join-Path $RepoRoot ".local\M6R-SYSTEM-OLLAMA"
$Downloads = Join-Path $WorkRoot "downloads"
$PackageDir = Join-Path $WorkRoot "package"
$EvidenceDir = Join-Path $WorkRoot "evidence"
$AttemptStatePath = Join-Path $WorkRoot "attempt-state.json"
if ([string]::IsNullOrWhiteSpace($ReportPath)) {
    $ReportDir = Join-Path $WorkRoot "report"
    New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
    $ReportPath = Join-Path $ReportDir "M6R_SYSTEM_OLLAMA_REPORT.json"
}
New-Item -ItemType Directory -Force -Path (Split-Path $ReportPath -Parent) | Out-Null

if (Test-Path $AttemptStatePath -PathType Leaf) {
    $ExistingAttemptState = Get-Content $AttemptStatePath -Raw | ConvertFrom-Json
    if ($ExistingAttemptState.consumed -eq $true) {
        throw "M6R system Ollama one-attempt authorization already consumed"
    }
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
function Save-Report {
    $Report.completed_at = (Get-Date).ToUniversalTime().ToString("o")
    Write-Utf8NoBom -Path $ReportPath -Content (($Report | ConvertTo-Json -Depth 80) + [Environment]::NewLine)
}
function Get-ModelNames {
    param($TagsResponse)
    if ($null -eq $TagsResponse -or $null -eq $TagsResponse.models) { return @() }
    return @($TagsResponse.models | ForEach-Object { [string]$_.name } | Sort-Object -Unique)
}
function Test-OutputFormat {
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) { return $false }
    foreach ($Ch in $Value.ToCharArray()) {
        if ([int][char]$Ch -lt 9) { return $false }
    }
    return $true
}

function Find-SystemOllamaExe {
    $Cmd = Get-Command ollama.exe -ErrorAction SilentlyContinue
    if ($null -ne $Cmd) { return $Cmd.Source }
    $Default = Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"
    if (Test-Path $Default -PathType Leaf) { return $Default }
    return $null
}
function Invoke-NativeCaptured {
    param(
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$StdoutPath,
        [string]$StderrPath,
        [string]$WorkingDirectory = ""
    )
    foreach ($P in @($StdoutPath,$StderrPath)) {
        if (Test-Path $P -PathType Leaf) { Remove-Item -Force $P }
    }
    $Params = @{
        FilePath = $FilePath
        ArgumentList = $Arguments
        NoNewWindow = $true
        Wait = $true
        PassThru = $true
        RedirectStandardOutput = $StdoutPath
        RedirectStandardError = $StderrPath
    }
    if (-not [string]::IsNullOrWhiteSpace($WorkingDirectory)) { $Params.WorkingDirectory = $WorkingDirectory }
    $Proc = Start-Process @Params
    return [ordered]@{
        return_code = [int]$Proc.ExitCode
        stdout = if (Test-Path $StdoutPath) { Get-Content $StdoutPath -Raw } else { "" }
        stderr = if (Test-Path $StderrPath) { Get-Content $StderrPath -Raw } else { "" }
        stdout_path = $StdoutPath
        stderr_path = $StderrPath
    }
}
function Test-OllamaSigner {
    param([string]$Path)
    $Sig = Get-AuthenticodeSignature -FilePath $Path
    if ($Sig.Status -ne "Valid") { return $false }
    return ($Sig.SignerCertificate.Subject -match "(^|, )O=Ollama Inc\.(,|$)")
}

$Report = [ordered]@{
    schema = "mindforge-model-pipeline-m6r-system-ollama-report-v1"
    program = $Program
    started_at = (Get-Date).ToUniversalTime().ToString("o")
    completed_at = $null
    overall_status = "RUNNING"
    classification = "UNADJUDICATED"
    attempt_consumed = $false
    scientific_runtime_started = $false
    repo = [ordered]@{}
    host = [ordered]@{}
    runtime = [ordered]@{}
    parent_q4 = [ordered]@{}
    modelfile = [ordered]@{}
    namespace = [ordered]@{}
    create = [ordered]@{}
    chat = [ordered]@{}
    parity = [ordered]@{}
    reasoning_mapping = [ordered]@{}
    cleanup = [ordered]@{}
    gates = [ordered]@{}
    evidence_manifest = [ordered]@{}
    boundaries = [ordered]@{
        installed_ollama_upgrade_authorized = $true
        installed_ollama_upgrade_executed = $false
        ollama_pull_executed = $false
        q4_requantization_executed = $false
        llama_cli_inference_executed = $false
        fixture_modified = $false
        threshold_modified = $false
        m7_authorized = $false
        bulk_training_authorized = $false
    }
    error = $null
}

$ServerProc = $null
$ServerStartedByScript = $false
$OllamaExe = $null
$UpgradeExecuted = $false
$CreatedOwnedModel = $false
$OwnershipMarker = $null
$ModelName = $null
$InitialNames = @()
$InitialTagsCaptured = $false
$PreCleanupClass = $null

$PresenceGate = $false
$VersionGate = $false
$ApiHealthyGate = $false
$Q4Gate = $false
$ModelfileGate = $false
$CollisionGate = $false
$CreateGate = $false
$ChatGate = $false
$AllOutputsGate = $false
$VectorGate = $false
$AccuracyGate = $false
$FormatGate = $false
$ReasoningGate = $false
$CleanupGate = $false
$NoMutationGate = $false
$EvidenceGate = $false

try {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "git not found" }

    $Head = (& git rev-parse HEAD).Trim()
    $Branch = (& git branch --show-current).Trim()
    $Dirty = @(& git status --porcelain --untracked-files=no)
    if ($Dirty.Count -gt 0) { throw "Tracked working tree is dirty: $($Dirty -join '; ')" }

    & git merge-base --is-ancestor ([string]$Lock.implementation_commit) $Head *> $null
    if ($LASTEXITCODE -ne 0) { throw "Locked M6R implementation is not an ancestor of HEAD" }

    $ScriptBlob = (& git hash-object -- $PSCommandPath).Trim()
    if ($ScriptBlob -ne [string]$Lock.exact_blobs.script_git_blob_sha1) { throw "M6R system Ollama script blob mismatch" }
    $ActualAuthBlob = (& git hash-object -- "artifacts/model-training-pipeline/m6r/system_ollama/EXECUTION_AUTHORIZATION.json").Trim()
    if ($ActualAuthBlob -ne [string]$Lock.execution_authorization_git_blob_sha1) { throw "M6R execution authorization blob mismatch" }
    if ($Auth.status -ne "AUTHORIZED_ONE_M6R_SYSTEM_OLLAMA_EXECUTION") { throw "M6R system Ollama execution is not authorized" }

    foreach ($Check in @(
        @("tests/fixtures/eval_v1/manifest.json",$ExpectedFixtureBlob),
        @("docs/model-training-pipeline/profiles/qwen2.5-0.5b-instruct-r0.yaml",$ExpectedProfileBlob),
        @("pipeline/reasoning.py",$ExpectedReasoningBlob)
    )) {
        $Actual = (& git hash-object -- $Check[0]).Trim()
        if ($Actual -ne $Check[1]) { throw "Frozen contract blob mismatch: $($Check[0])" }
    }

    $Report.repo = [ordered]@{
        root = $RepoRoot
        branch = $Branch
        head = $Head
        tracked_worktree_clean = $true
        script_git_blob_sha1 = $ScriptBlob
    }

    $OS = Get-CimInstance Win32_OperatingSystem
    $CPU = Get-CimInstance Win32_Processor | Select-Object -First 1
    $DriveName = [IO.Path]::GetPathRoot($RepoRoot).Substring(0,1)
    $Drive = Get-PSDrive -Name $DriveName
    $Report.host = [ordered]@{
        os = $OS.Caption
        build = $OS.BuildNumber
        cpu = $CPU.Name.Trim()
        powershell = $PSVersionTable.PSVersion.ToString()
        free_bytes = [int64]$Drive.Free
    }
    if ([int64]$Drive.Free -lt 4GB) { throw "Insufficient free disk for M6R system Ollama upgrade/package headroom" }

    $Q4Path = Join-Path $RepoRoot ".local\M6-LOCAL-Q4-RECONSTRUCTION\output\model-q4_k_m.gguf"
    if (-not (Test-Path $Q4Path -PathType Leaf)) {
        $Report.classification = "INVALID_PROVENANCE"
        throw "Exact reconstructed Q4 parent missing"
    }
    $Q4Identity = Get-Q4Identity (Get-Item $Q4Path)
    $Q4Gate = [bool]$Q4Identity.exact_identity
    if (-not $Q4Gate) {
        $Report.classification = "INVALID_PROVENANCE"
        throw "Q4 parent identity mismatch"
    }
    $Report.parent_q4 = $Q4Identity

    New-Item -ItemType Directory -Force -Path $Downloads,$EvidenceDir | Out-Null
    if (Test-Path $PackageDir) { Remove-Item -Recurse -Force $PackageDir }
    New-Item -ItemType Directory -Force -Path $PackageDir | Out-Null

    $OllamaExe = Find-SystemOllamaExe
    if ([string]::IsNullOrWhiteSpace($OllamaExe)) { throw "Installed Ollama not found; fresh installation is outside M6R scope" }
    $PresenceGate = $true

    $VersionStdout = Join-Path $EvidenceDir "ollama-version.stdout.log"
    $VersionStderr = Join-Path $EvidenceDir "ollama-version.stderr.log"
    $VersionRun = Invoke-NativeCaptured -FilePath $OllamaExe -Arguments @("--version") -StdoutPath $VersionStdout -StderrPath $VersionStderr
    if ($VersionRun.return_code -ne 0) { throw "Installed ollama --version failed" }
    $VersionOutput = (($VersionRun.stdout + [Environment]::NewLine + $VersionRun.stderr).Trim())
    $VersionMatch = [regex]::Match($VersionOutput,"(?<![0-9])([0-9]+\.[0-9]+\.[0-9]+)(?![0-9])")
    if (-not $VersionMatch.Success) { throw "Unable to parse installed Ollama version: $VersionOutput" }
    $ObservedVersion = $VersionMatch.Groups[1].Value
    $TargetVersionObj = [version]$ExpectedOllamaVersion
    $ObservedVersionObj = [version]$ObservedVersion
    if ($ObservedVersionObj -gt $TargetVersionObj) { throw "Installed Ollama $ObservedVersion is newer than frozen target $ExpectedOllamaVersion; downgrade is not authorized" }

    $InstallerPath = Join-Path $Downloads "OllamaSetup-v0.34.2.exe"
    if ($ObservedVersionObj -lt $TargetVersionObj) {
        $NeedInstallerDownload = $true
        if (Test-Path $InstallerPath -PathType Leaf) {
            if ((Get-Sha256File $InstallerPath) -eq $OllamaInstallerSha256) { $NeedInstallerDownload = $false }
            else { Remove-Item -Force $InstallerPath }
        }
        if ($NeedInstallerDownload) {
            $Curl = Get-Command curl.exe -ErrorAction SilentlyContinue
            if ($null -eq $Curl) { throw "curl.exe required for exact M6R installer download" }
            $CurlOut = Join-Path $EvidenceDir "installer-download.stdout.log"
            $CurlErr = Join-Path $EvidenceDir "installer-download.stderr.log"
            $CurlArgs = @("--fail","--location","--retry","5","--retry-delay","5","--connect-timeout","30","--silent","--show-error","--output",$InstallerPath,$OllamaInstallerUrl)
            $CurlRun = Invoke-NativeCaptured -FilePath $Curl.Source -Arguments $CurlArgs -StdoutPath $CurlOut -StderrPath $CurlErr
            if ($CurlRun.return_code -ne 0) { throw "Exact Ollama installer download failed rc=$($CurlRun.return_code): $($CurlRun.stderr)" }
        }
        $InstallerSha = Get-Sha256File $InstallerPath
        if ($InstallerSha -ne $OllamaInstallerSha256) { throw "Pinned Ollama installer SHA256 mismatch" }
        if (-not (Test-OllamaSigner $InstallerPath)) { throw "Pinned Ollama installer Authenticode signer mismatch" }

        $InstallerOut = Join-Path $EvidenceDir "ollama-installer.stdout.log"
        $InstallerErr = Join-Path $EvidenceDir "ollama-installer.stderr.log"
        $InstallerRun = Invoke-NativeCaptured -FilePath $InstallerPath -Arguments @("/VERYSILENT","/NORESTART","/SUPPRESSMSGBOXES") -StdoutPath $InstallerOut -StderrPath $InstallerErr
        if ($InstallerRun.return_code -ne 0) { throw "Ollama upgrade failed rc=$($InstallerRun.return_code)" }
        $UpgradeExecuted = $true
        $Report.boundaries.installed_ollama_upgrade_executed = $true
        Start-Sleep -Seconds 3
        $OllamaExe = Find-SystemOllamaExe
        if ([string]::IsNullOrWhiteSpace($OllamaExe)) { throw "Installed Ollama executable missing after upgrade" }
        $VersionRun = Invoke-NativeCaptured -FilePath $OllamaExe -Arguments @("--version") -StdoutPath $VersionStdout -StderrPath $VersionStderr
        if ($VersionRun.return_code -ne 0) { throw "Post-upgrade ollama --version failed" }
        $VersionOutput = (($VersionRun.stdout + [Environment]::NewLine + $VersionRun.stderr).Trim())
        if ($VersionOutput -notmatch [regex]::Escape($ExpectedOllamaVersion)) { throw "Post-upgrade Ollama version mismatch: $VersionOutput" }
        $ObservedVersion = $ExpectedOllamaVersion
    }
    if ($ObservedVersion -ne $ExpectedOllamaVersion) { throw "Installed Ollama exact version lock failed: $ObservedVersion" }
    $VersionGate = $true

    $Report.runtime = [ordered]@{
        mode = "installed_system_ollama"
        version = $ObservedVersion
        version_output = $VersionOutput
        executable_path = $OllamaExe
        executable_sha256 = (Get-Sha256File $OllamaExe)
        host = $HostAddress
        existing_user_model_store = $true
        upgrade_executed = $UpgradeExecuted
        installer_url = $OllamaInstallerUrl
        installer_sha256 = $OllamaInstallerSha256
        installer_signature_required = "Ollama Inc."
    }

    $PackageQ4 = Join-Path $PackageDir "model-q4_k_m.gguf"
    Copy-Item -LiteralPath $Q4Path -Destination $PackageQ4
    $PackageIdentity = Get-Q4Identity (Get-Item $PackageQ4)
    if (-not $PackageIdentity.exact_identity) { throw "Packaged Q4 copy failed identity reverification" }

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
    $ModelfileSha = Get-Sha256File $Modelfile
    $ModelfileGate = ($ModelfileSha -eq $ExpectedModelfileSha256)
    if (-not $ModelfileGate) { throw "Frozen Modelfile SHA256 mismatch" }
    $Report.modelfile = [ordered]@{
        path = $Modelfile
        sha256 = $ModelfileSha
        bytes = (Get-Item $Modelfile).Length
    }

    $env:OLLAMA_HOST = $HostAddress
    $Healthy = $false
    $Tags = $null
    for ($i=0; $i -lt 10; $i++) {
        try {
            $Tags = Invoke-RestMethod -Method Get -Uri ("http://" + $HostAddress + "/api/tags") -TimeoutSec 2
            $Healthy = $true
            break
        } catch { Start-Sleep -Seconds 1 }
    }
    if (-not $Healthy) {
        $ServerStdout = Join-Path $EvidenceDir "ollama-system-serve.stdout.log"
        $ServerStderr = Join-Path $EvidenceDir "ollama-system-serve.stderr.log"
        $ServerProc = Start-Process -FilePath $OllamaExe -ArgumentList @("serve") -PassThru -RedirectStandardOutput $ServerStdout -RedirectStandardError $ServerStderr
        $ServerStartedByScript = $true
        for ($i=0; $i -lt 60; $i++) {
            Start-Sleep -Seconds 1
            try {
                $Tags = Invoke-RestMethod -Method Get -Uri ("http://" + $HostAddress + "/api/tags") -TimeoutSec 2
                $Healthy = $true
                break
            } catch {}
        }
    }
    if (-not $Healthy) { throw "Installed Ollama 0.34.2 API did not become healthy on 127.0.0.1:11434" }
    $ApiHealthyGate = $true
    $Report.runtime.service_started_by_script = $ServerStartedByScript
    $InitialNames = @(Get-ModelNames $Tags)
    $InitialTagsCaptured = $true
    $RunId = "m6r-" + $Head.Substring(0,12)
    $ModelName = "pipeline-test-m6r-" + $Head.Substring(0,12) + "-" + $ExpectedQ4Sha256.Substring(0,12)
    $RenderedNames = @($ModelName,($ModelName + ":latest"))
    if (@($InitialNames | Where-Object { $RenderedNames -contains $_ }).Count -gt 0) { throw "Ephemeral model namespace collision" }
    $CollisionGate = $true

    $OwnershipMarker = Get-Sha256Text ($RunId + $LF + $ModelName + $LF + $ExpectedQ4Sha256 + $LF)
    $Report.namespace = [ordered]@{
        run_id = $RunId
        model_name = $ModelName
        ownership_marker = $OwnershipMarker
        initial_model_names = $InitialNames
        collision_free = $true
        created_by_current_run = $false
    }
    Save-Report

    $AttemptState = [ordered]@{
        schema = "mindforge-model-pipeline-m6r-system-ollama-attempt-state-v1"
        consumed = $true
        consumed_at = (Get-Date).ToUniversalTime().ToString("o")
        repo_head = $Head
        model_name = $ModelName
        q4_sha256 = $ExpectedQ4Sha256
        trigger = "immediately_before_ollama_create"
    }
    $AttemptTmp = $AttemptStatePath + ".tmp"
    Write-Utf8NoBom $AttemptTmp (($AttemptState | ConvertTo-Json -Depth 10) + [Environment]::NewLine)
    Move-Item -Force $AttemptTmp $AttemptStatePath

    $Report.attempt_consumed = $true
    $Report.scientific_runtime_started = $true
    Save-Report

    $CreateStdout = Join-Path $EvidenceDir "ollama-create.stdout.log"
    $CreateStderr = Join-Path $EvidenceDir "ollama-create.stderr.log"
    try {
        $CreateRun = Invoke-NativeCaptured -FilePath $OllamaExe -Arguments @("create",$ModelName,"-f","Modelfile") -StdoutPath $CreateStdout -StderrPath $CreateStderr -WorkingDirectory $PackageDir
        $CreateRc = $CreateRun.return_code
    } catch {
        $Report.classification = "FAIL_PACKAGE"
        $Report.overall_status = "FAIL"
        $PreCleanupClass = $Report.classification
        throw "Owned Ollama model create process failed: $($_.Exception.Message)"
    }
    $Report.create = [ordered]@{
        return_code = $CreateRc
        stdout_path = $CreateStdout
        stderr_path = $CreateStderr
        stdout_sha256 = (Get-Sha256File $CreateStdout)
        stderr_sha256 = (Get-Sha256File $CreateStderr)
    }
    if ($CreateRc -ne 0) {
        $Report.classification = "FAIL_PACKAGE"
        $Report.overall_status = "FAIL"
        $PreCleanupClass = $Report.classification
        throw "Owned Ollama model create failed"
    }
    $CreatedOwnedModel = $true
    $CreateGate = $true
    $Report.namespace.created_by_current_run = $true
    Save-Report

    $Fixture = Get-Content "tests/fixtures/eval_v1/manifest.json" -Raw | ConvertFrom-Json
    $Rows = @()
    $UnexpectedNativeThinking = $false

    foreach ($Task in $Fixture.tasks) {
        $Request = [ordered]@{
            model = $ModelName
            messages = @([ordered]@{role="user";content=[string]$Task.prompt})
            stream = $false
            keep_alive = 0
            options = [ordered]@{
                num_ctx = 2048
                num_predict = 128
                temperature = 0
                top_p = 1
                top_k = 0
                seed = 42
            }
        }
        $Body = $Request | ConvertTo-Json -Depth 20 -Compress
        try {
            $Response = Invoke-RestMethod -Method Post -Uri ("http://" + $HostAddress + "/api/chat") -ContentType "application/json" -Body $Body -TimeoutSec 300
        } catch {
            $Report.classification = "FAIL_RUNTIME"
            $Report.overall_status = "FAIL"
            $PreCleanupClass = $Report.classification
            throw "Ollama /api/chat failed for $($Task.id): $($_.Exception.Message)"
        }

        $RawPath = Join-Path $EvidenceDir ("chat-" + [string]$Task.id + ".json")
        Write-Utf8NoBom $RawPath (($Response | ConvertTo-Json -Depth 40) + [Environment]::NewLine)
        $Content = [string]$Response.message.content
        $Thinking = $null
        if ($null -ne $Response.message.PSObject.Properties["thinking"]) {
            $Thinking = [string]$Response.message.thinking
        }
        if (-not [string]::IsNullOrWhiteSpace($Thinking)) { $UnexpectedNativeThinking = $true }

        $FormatValid = Test-OutputFormat $Content
        $Success = ($Content.Trim() -ceq ([string]$Task.expected).Trim())
        $Rows += [ordered]@{
            id = [string]$Task.id
            type = [string]$Task.type
            expected = [string]$Task.expected
            output = $Content
            output_sha256 = (Get-Sha256Text $Content)
            format_valid = $FormatValid
            task_success = $Success
            native_thinking = $Thinking
            raw_response_path = $RawPath
            raw_response_sha256 = (Get-Sha256File $RawPath)
        }
    }

    $ChatGate = ($Rows.Count -eq 2)
    $TaskVector = @($Rows | ForEach-Object { [bool]$_.task_success })
    $SuccessCount = @($Rows | Where-Object { $_.task_success }).Count
    $Accuracy = [double]$SuccessCount / [double]$Rows.Count
    $AllOutputsGate = (@($Rows | Where-Object { -not $_.format_valid }).Count -eq 0)
    $FrozenVector = @($false,$false)
    $VectorGate = (($TaskVector.Count -eq $FrozenVector.Count) -and (($TaskVector -join ",") -eq ($FrozenVector -join ",")))
    $AccuracyGate = ([math]::Abs($Accuracy - 0.0) -lt 1e-12)
    $FormatGate = $AllOutputsGate
    $ReasoningGate = (-not $UnexpectedNativeThinking)

    $Report.chat = [ordered]@{
        fixture_set_id = [string]$Fixture.fixture_set_id
        rows = $Rows
        task_vector = $TaskVector
        accuracy = $Accuracy
        all_outputs_nonempty = $AllOutputsGate
        native_think_field_sent = $false
    }
    $Report.parity = [ordered]@{
        llama_parent_task_vector = $FrozenVector
        ollama_task_vector = $TaskVector
        llama_parent_accuracy = 0.0
        ollama_accuracy = $Accuracy
        task_vector_match = $VectorGate
        accuracy_match = $AccuracyGate
        format_parity = $FormatGate
        exact_text_required = $false
    }
    $Report.reasoning_mapping = [ordered]@{
        capability_profile = "qwen2.5-0.5b-instruct-r0-v1"
        transport = "tagged_text"
        model_native_reasoning_assumed = $false
        native_think_field_sent = $false
        supports_hide_via_post_parser = $true
        supports_disable = $false
        unexpected_nonempty_native_thinking_field = $UnexpectedNativeThinking
        pass = $ReasoningGate
        generated_reasoning_quality_claimed = $false
    }

    if (-not $AllOutputsGate) {
        $Report.classification = "FAIL_RUNTIME"
        $Report.overall_status = "FAIL"
    } elseif (-not $VectorGate -or -not $AccuracyGate) {
        $Report.classification = "FAIL_PARITY"
        $Report.overall_status = "FAIL"
    } elseif (-not $ReasoningGate) {
        $Report.classification = "FAIL_REASONING_MAPPING"
        $Report.overall_status = "FAIL"
    } else {
        $Report.classification = "PASS"
        $Report.overall_status = "PASS"
    }
    $PreCleanupClass = $Report.classification
    Save-Report
}
catch {
    if ($null -eq $PreCleanupClass) {
        if ($Report.scientific_runtime_started) {
            if ($Report.classification -eq "UNADJUDICATED") {
                $Report.classification = "FAIL_RUNTIME"
            }
        } elseif ($Report.classification -eq "UNADJUDICATED") {
            $Report.classification = "INVALID_INFRASTRUCTURE"
        }
    }
    if ($Report.overall_status -eq "RUNNING") { $Report.overall_status = "FAIL" }
    $Report.error = [ordered]@{
        message = $_.Exception.Message
        type = $_.Exception.GetType().FullName
        script_stack = $_.ScriptStackTrace
    }
}
finally {
    if ($CreatedOwnedModel) {
        $ExpectedMarker = Get-Sha256Text ($Report.namespace.run_id + $LF + $ModelName + $LF + $ExpectedQ4Sha256 + $LF)
        if ($OwnershipMarker -ne $ExpectedMarker) {
            $CleanupGate = $false
            $Report.cleanup = [ordered]@{attempted=$false;authorized=$false;reason="ownership_marker_mismatch"}
        } else {
            $RmStdout = Join-Path $EvidenceDir "ollama-rm.stdout.log"
            $RmStderr = Join-Path $EvidenceDir "ollama-rm.stderr.log"
            try {
                $RmRun = Invoke-NativeCaptured -FilePath $OllamaExe -Arguments @("rm",$ModelName) -StdoutPath $RmStdout -StderrPath $RmStderr
                $RmRc = $RmRun.return_code
                $CleanupGate = ($RmRc -eq 0)
                $Report.cleanup = [ordered]@{
                    attempted = $true
                    authorized = $true
                    return_code = $RmRc
                    stdout_path = $RmStdout
                    stderr_path = $RmStderr
                    stdout_sha256 = (Get-Sha256File $RmStdout)
                    stderr_sha256 = (Get-Sha256File $RmStderr)
                }
            } catch {
                $CleanupGate = $false
                $Report.cleanup = [ordered]@{attempted=$true;authorized=$true;reason="owned_model_remove_process_failed";message=$_.Exception.Message}
            }
        }
    } else {
        $CleanupGate = $true
        $Report.cleanup = [ordered]@{attempted=$false;authorized=$false;reason="no_owned_model_created"}
    }

    $FinalNames = @()
    try {
        $FinalTags = Invoke-RestMethod -Method Get -Uri ("http://" + $HostAddress + "/api/tags") -TimeoutSec 5
        $FinalNames = @(Get-ModelNames $FinalTags)
        if ($InitialTagsCaptured) { $NoMutationGate = (($InitialNames -join $LF) -eq ($FinalNames -join $LF)) }
    } catch { $NoMutationGate = $false }
    $Report.cleanup.final_model_names = $FinalNames
    $Report.cleanup.initial_final_model_sets_match = $NoMutationGate

    if ($ServerStartedByScript -and $null -ne $ServerProc -and -not $ServerProc.HasExited) {
        Stop-Process -Id $ServerProc.Id -Force -ErrorAction SilentlyContinue
        $ServerProc.WaitForExit(10000) | Out-Null
    }

    $EvidenceFiles = @()
    if (Test-Path $EvidenceDir) {
        foreach ($File in @(Get-ChildItem -LiteralPath $EvidenceDir -File | Sort-Object Name)) {
            $EvidenceFiles += [ordered]@{
                name = $File.Name
                size = [int64]$File.Length
                sha256 = (Get-Sha256File $File.FullName)
            }
        }
    }
    $ManifestJson = ($EvidenceFiles | ConvertTo-Json -Depth 10 -Compress)
    $ManifestHash = Get-Sha256Text $ManifestJson
    $EvidenceGate = (-not [string]::IsNullOrWhiteSpace($ManifestHash))
    $Report.evidence_manifest = [ordered]@{
        files = $EvidenceFiles
        sha256 = $ManifestHash
        frozen = $EvidenceGate
    }

    $Report.gates = [ordered]@{
        system_ollama_present = $PresenceGate
        system_ollama_exact_version_lock = $VersionGate
        system_ollama_api_healthy = $ApiHealthyGate
        source_q4_identity_exact = $Q4Gate
        modelfile_deterministic_and_frozen = $ModelfileGate
        ephemeral_namespace_collision_safe = $CollisionGate
        ollama_create_owned_model_only = $CreateGate
        ollama_chat_real_runtime = $ChatGate
        all_outputs_nonempty = $AllOutputsGate
        task_vector_equals_frozen_llama_parent = $VectorGate
        runtime_accuracy_equals_frozen_llama_parent = $AccuracyGate
        format_parity_with_frozen_llama_parent = $FormatGate
        reasoning_runtime_mapping_pass = $ReasoningGate
        cleanup_owned_artifact_only = $CleanupGate
        no_unowned_model_mutation = $NoMutationGate
        runtime_evidence_manifest_frozen = $EvidenceGate
    }

    $AllGatesPass = $true
    foreach ($Value in $Report.gates.Values) {
        if (-not [bool]$Value) { $AllGatesPass = $false; break }
    }

    if ($Report.scientific_runtime_started) {
        if (-not $CleanupGate -or -not $NoMutationGate) {
            $Report.classification = "FAIL_CLEANUP_SAFETY"
            $Report.overall_status = "FAIL"
        } elseif ($PreCleanupClass -eq "PASS" -and $AllGatesPass) {
            $Report.classification = "PASS"
            $Report.overall_status = "PASS"
        } elseif ($PreCleanupClass -eq "PASS" -and -not $AllGatesPass) {
            $Report.classification = "FAIL_RUNTIME"
            $Report.overall_status = "FAIL"
        } elseif ($null -ne $PreCleanupClass) {
            $Report.classification = $PreCleanupClass
            $Report.overall_status = "FAIL"
        }
    }

    Save-Report
    Write-Host "M6R system Ollama classification: $($Report.classification)"
    Write-Host "Report: $ReportPath"
}

if ($Report.overall_status -eq "PASS") { exit 0 } else { exit 2 }

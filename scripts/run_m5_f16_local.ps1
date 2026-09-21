param(
    [string]$ReportDir = "local-reports\m5-f16"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ScientificCodeSha = "8dd08cbd7cd1b9050f6ae7eda6f3ab41d6edbc0a"
$InvalidGithubRunId = 35577280214
$TaskName = "M5_F16_REQUALIFICATION"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $RepoRoot

$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$ReportRoot = Join-Path $RepoRoot $ReportDir
New-Item -ItemType Directory -Force -Path $ReportRoot | Out-Null
$ReportPath = Join-Path $ReportRoot ("M5_F16_LOCAL_REPORT_{0}.json" -f $Timestamp)
$WorkRoot = Join-Path $RepoRoot ".local-exec\m5-f16-work"
$ToolRoot = Join-Path $WorkRoot "tools"
$RunsRoot = Join-Path $WorkRoot "runs"
$PipelineVenv = Join-Path $WorkRoot "pipeline-venv"
$ConverterVenv = Join-Path $ToolRoot "convert-venv"
$LlamaSource = Join-Path $ToolRoot "llama.cpp"
$BuildManifest = Join-Path $ToolRoot "build_manifest.json"
$HarnessJson = Join-Path $WorkRoot "m5-f16-result.json"
$ConverterProbeJson = Join-Path $ToolRoot "converter_probe.json"
$PersistentCacheRoot = Join-Path $RepoRoot ".local-cache\m5-f16-hf"
$PersistentHfCache = Join-Path $PersistentCacheRoot "hf-cache"
$PrefetchJson = Join-Path $WorkRoot "hf-prefetch.json"
$PrefetchStderr = Join-Path $WorkRoot "hf-prefetch-stderr.log"

$Report = [ordered]@{
    schema = "mindforge-local-execution-report-v1"
    governance_mode = "LOCAL_EXECUTION_FALLBACK"
    task = $TaskName
    reason = "GITHUB_RUNNER_SHUTDOWN_BEFORE_SCIENTIFIC_OUTCOME"
    invalid_github_run_id = $InvalidGithubRunId
    scientific_code_sha = $ScientificCodeSha
    started_at = (Get-Date).ToUniversalTime().ToString("o")
    completed_at = $null
    overall_status = "RUNNING"
    scientific_outcome = "UNADJUDICATED"
    quantization_executed = $false
    quantization_authorized = $false
    repo = [ordered]@{}
    host = [ordered]@{}
    provenance = [ordered]@{}
    stages = @()
    artifacts = [ordered]@{}
    f16_result = $null
    error = $null
}

function Write-Utf8NoBom {
    param(
        [string]$Path,
        [string]$Content
    )
    $Encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Content, $Encoding)
}

function Save-Report {
    $Report.completed_at = (Get-Date).ToUniversalTime().ToString("o")
    $Json = $Report | ConvertTo-Json -Depth 20
    Write-Utf8NoBom -Path $ReportPath -Content ($Json + [Environment]::NewLine)
}

function Add-Stage {
    param(
        [string]$Name,
        [string]$Status,
        [int]$ExitCode = 0,
        [string]$Detail = ""
    )
    $Report.stages += [ordered]@{
        name = $Name
        status = $Status
        exit_code = $ExitCode
        detail = $Detail
        at = (Get-Date).ToUniversalTime().ToString("o")
    }
    Save-Report
}

function Invoke-Checked {
    param(
        [string]$Stage,
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$WorkingDirectory = $RepoRoot,
        [string]$StdoutPath = ""
    )
    Push-Location $WorkingDirectory
    try {
        if ($StdoutPath) {
            & $FilePath @Arguments 2>&1 | Tee-Object -FilePath $StdoutPath
        } else {
            & $FilePath @Arguments
        }
        $Code = $LASTEXITCODE
    } finally {
        Pop-Location
    }
    if ($Code -ne 0) {
        Add-Stage -Name $Stage -Status "FAIL" -ExitCode $Code -Detail ("command failed: {0}" -f $FilePath)
        throw "Stage '$Stage' failed with exit code $Code"
    }
    Add-Stage -Name $Stage -Status "PASS" -ExitCode 0
}

function Get-Sha256 {
    param([string]$Path)
    if (-not (Test-Path $Path -PathType Leaf)) { return $null }
    return (Get-FileHash -Algorithm SHA256 -Path $Path).Hash.ToLowerInvariant()
}

function Resolve-Python312 {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3.12 -c "import sys; assert sys.version_info[:2] == (3,12); print(sys.executable)" *> $null
        if ($LASTEXITCODE -eq 0) {
            return [ordered]@{ command = "py"; prefix = @("-3.12") }
        }
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        & python -c "import sys; assert sys.version_info[:2] == (3,12); print(sys.executable)" *> $null
        if ($LASTEXITCODE -eq 0) {
            return [ordered]@{ command = "python"; prefix = @() }
        }
    }
    throw "Python 3.12 not found. Install Python 3.12 or make 'py -3.12' available."
}

try {
    Write-Host "=== MindForge Local Execution Fallback: M5 F16 ==="
    Write-Host "Scientific code SHA: $ScientificCodeSha"
    Write-Host "Report: $ReportPath"

    if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "git not found in PATH" }

    if (-not (Get-Command cmake -ErrorAction SilentlyContinue)) {
        $VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
        if (Test-Path $VsWhere) {
            $VsRoot = (& $VsWhere -latest -products * -property installationPath).Trim()
            if (-not [string]::IsNullOrWhiteSpace($VsRoot)) {
                $VsCmake = Join-Path $VsRoot "Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"
                if (Test-Path $VsCmake) {
                    $env:Path = "$(Split-Path $VsCmake);$env:Path"
                }
            }
        }
    }
    if (-not (Get-Command cmake -ErrorAction SilentlyContinue)) { throw "cmake not found in PATH or Visual Studio Build Tools" }

    # Remove only the deterministic untracked residue created by the M1 test
    # suite in a prior interrupted local fallback run. Do not broadly clean the
    # worktree or evidence/report directories.
    $KnownM1Residue = Join-Path $RepoRoot ".tmp-m1-test-resume"
    if (Test-Path $KnownM1Residue) {
        Remove-Item -Recurse -Force $KnownM1Residue
    }

    $GitHead = (& git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) { throw "Not inside a Git repository" }
    $Branch = (& git branch --show-current).Trim()
    $Status = (& git status --porcelain)
    $Report.repo = [ordered]@{
        root = $RepoRoot
        helper_head = $GitHead
        branch = $Branch
        scientific_code_sha = $ScientificCodeSha
        tracked_worktree_clean = ([string]::IsNullOrWhiteSpace(($Status -join "")))
        runner_script_sha256 = (Get-FileHash -Algorithm SHA256 -Path $PSCommandPath).Hash.ToLowerInvariant()
    }

    $AllowedDirtyPrefixes = @(
        ".local-exec/",
        ".local-cache/",
        "local-reports/"
    )
    $UnexpectedDirty = @()
    foreach ($Line in $Status) {
        if ([string]::IsNullOrWhiteSpace($Line)) { continue }
        $PathPart = $Line.Substring([Math]::Min(3, $Line.Length)).Trim().Replace("\", "/")
        $Allowed = $false
        foreach ($Prefix in $AllowedDirtyPrefixes) {
            if ($PathPart.StartsWith($Prefix)) { $Allowed = $true; break }
        }
        if (-not $Allowed) { $UnexpectedDirty += $Line }
    }
    if ($UnexpectedDirty.Count -gt 0) {
        throw "Unexpected dirty working tree entries: $($UnexpectedDirty -join '; ')"
    }

    $ExpectedBlobs = [ordered]@{
        "pipeline/m2.py" = "51a023e46b48f9d177b506cfa4e409a4f85d930b"
        "pipeline/m2_model.py" = "8c257d3bb767cc2f17b58a0905452bb7f9ae52db"
        "pipeline/m2_worker.py" = "479f1c0efc90bd7e4874ef1f292a1e906a43e5f5"
        "pipeline/m5.py" = "d0e2932ad0761bc22d881a181c001cc586fe714b"
        "pipeline/m5_converter_probe.py" = "5466dce5d67b090dbb66009d4a72fda4582f3c10"
        "tools/m5_f16_requalification.py" = "7be53a3ef4d8871bd1cf60e0ab45535c0906183f"
        "docs/model-training-pipeline/runtime/llama_cpp.lock.json" = "9cef982e91d067f7110397ecb5e66ba92af25d38"
        "docs/model-training-pipeline/examples/end_to_end_small.yaml" = "4fff2473b8f64f7db8f037d0fa40087c7efda4ca"
        "artifacts/model-training-pipeline/m5_1/M5_1_RESULT_EVIDENCE.json" = "07d8adc2539176234833a213e213dd7962ea11b7"
        "requirements-pipeline-m5.txt" = "81f16dbcf8879a0bcda9c699d87d2f7aa2a8b0d0"
    }
    $BlobChecks = @()
    foreach ($Rel in $ExpectedBlobs.Keys) {
        if (-not (Test-Path $Rel -PathType Leaf)) { throw "Required scientific file missing: $Rel" }
        $Actual = (& git hash-object -- $Rel).Trim()
        $Expected = $ExpectedBlobs[$Rel]
        $BlobChecks += [ordered]@{
            path = $Rel
            expected_git_blob_sha1 = $Expected
            actual_git_blob_sha1 = $Actual
            match = ($Actual -eq $Expected)
        }
        if ($Actual -ne $Expected) {
            throw "Scientific provenance mismatch for $Rel expected=$Expected actual=$Actual"
        }
    }
    $Report.provenance.scientific_blob_checks = $BlobChecks
    $Report.provenance.all_scientific_blobs_match = $true
    Add-Stage -Name "scientific_provenance" -Status "PASS"

    $OS = Get-CimInstance Win32_OperatingSystem
    $CPU = Get-CimInstance Win32_Processor | Select-Object -First 1
    $Computer = Get-CimInstance Win32_ComputerSystem
    $Report.host = [ordered]@{
        os_caption = $OS.Caption
        os_version = $OS.Version
        os_build = $OS.BuildNumber
        architecture = $OS.OSArchitecture
        cpu = $CPU.Name.Trim()
        logical_processors = $CPU.NumberOfLogicalProcessors
        memory_bytes = [int64]$Computer.TotalPhysicalMemory
        powershell_version = $PSVersionTable.PSVersion.ToString()
        git_version = (& git --version).Trim()
        cmake_version = ((& cmake --version | Select-Object -First 1).Trim())
    }

    $BasePython = Resolve-Python312
    $Report.host.python_launcher = $BasePython.command
    $Report.host.python_prefix = $BasePython.prefix

    # Preserve any partial/complete HF cache from an interrupted prior local
    # invocation before resetting ephemeral execution state. This is
    # infrastructure-only and does not preserve run/adjudication outputs.
    $OldEphemeralHfCache = Join-Path $RunsRoot ".hf-cache"
    if (Test-Path $OldEphemeralHfCache) {
        $OldCacheItem = Get-Item -Force $OldEphemeralHfCache
        $IsJunctionOrLink = [bool]($OldCacheItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint)
        if ($IsJunctionOrLink) {
            # A prior patched invocation already bound this path to the
            # persistent cache. Remove only the link before deleting WorkRoot.
            Remove-Item -Force $OldEphemeralHfCache
        } else {
            # Migrate partial bytes from pre-patch interrupted runs so the
            # exact pinned prefetch can resume instead of starting over.
            New-Item -ItemType Directory -Force -Path $PersistentHfCache | Out-Null
            & robocopy.exe $OldEphemeralHfCache $PersistentHfCache /E /R:2 /W:2 /NFL /NDL /NJH /NJS /NP | Out-Null
            $RoboCode = $LASTEXITCODE
            if ($RoboCode -gt 7) {
                throw "Failed to preserve prior HF cache; robocopy exit code $RoboCode"
            }
        }
    }

    if (Test-Path $WorkRoot) {
        Remove-Item -Recurse -Force $WorkRoot
    }
    New-Item -ItemType Directory -Force -Path $ToolRoot, $RunsRoot, $PersistentHfCache | Out-Null

    $CreatePipelineVenvArgs = @($BasePython.prefix) + @("-m","venv",$PipelineVenv)
    & $BasePython.command @CreatePipelineVenvArgs
    if ($LASTEXITCODE -ne 0) { throw "Failed to create pipeline venv" }
    $PipelinePython = Join-Path $PipelineVenv "Scripts\python.exe"
    Invoke-Checked -Stage "install_pipeline_dependencies" -FilePath $PipelinePython -Arguments @("-m","pip","install","-r","requirements-pipeline-m5.txt")

    # Complete the exact pinned HF snapshot in a persistent cache before the
    # scientific harness. Retries are finite infrastructure retries only.
    $PrefetchArgs = @(
        "-m","scripts.prefetch_m5_f16_hf",
        "-c","docs/model-training-pipeline/examples/end_to_end_small.yaml",
        "--workspace",".",
        "--cache-dir",$PersistentHfCache,
        "--attempts","3",
        "--json"
    )
    $QuotedPrefetchArgs = @()
    foreach ($Arg in $PrefetchArgs) {
        $Text = [string]$Arg
        if ($Text -match '[\s"]') {
            $QuotedPrefetchArgs += ('"' + ($Text -replace '"', '\\"') + '"')
        } else {
            $QuotedPrefetchArgs += $Text
        }
    }
    $PrefetchProcess = Start-Process `
        -FilePath $PipelinePython `
        -ArgumentList $QuotedPrefetchArgs `
        -WorkingDirectory $RepoRoot `
        -NoNewWindow `
        -Wait `
        -PassThru `
        -RedirectStandardOutput $PrefetchJson `
        -RedirectStandardError $PrefetchStderr
    $PrefetchExit = [int]$PrefetchProcess.ExitCode
    $Report.artifacts.hf_prefetch = [ordered]@{
        path = $PrefetchJson
        sha256 = Get-Sha256 $PrefetchJson
        stderr_path = $PrefetchStderr
        stderr_sha256 = Get-Sha256 $PrefetchStderr
    }
    if ($PrefetchExit -ne 0) {
        $Tail = if (Test-Path $PrefetchStderr) { ((Get-Content $PrefetchStderr -Tail 80) -join [Environment]::NewLine) } else { "" }
        Add-Stage -Name "hf_pinned_snapshot_prefetch" -Status "FAIL" -ExitCode $PrefetchExit -Detail $Tail
        throw "Pinned HF snapshot prefetch failed with exit code $PrefetchExit"
    }
    $PrefetchResult = Get-Content $PrefetchJson -Raw | ConvertFrom-Json
    if ($PrefetchResult.status -ne "PASS" -or $PrefetchResult.snapshot_path_tail_matches_revision -ne $true) {
        throw "Pinned HF snapshot prefetch did not prove exact revision identity"
    }
    $Report.provenance.hf_prefetch = [ordered]@{
        model_id = $PrefetchResult.model_id
        revision = $PrefetchResult.revision
        snapshot_path_tail = $PrefetchResult.snapshot_path_tail
        snapshot_manifest_hash = $PrefetchResult.snapshot_manifest_hash
        file_count = $PrefetchResult.file_count
        attempts = $PrefetchResult.attempts
    }
    Add-Stage -Name "hf_pinned_snapshot_prefetch" -Status "PASS" -ExitCode 0 -Detail $PrefetchResult.snapshot_manifest_hash

    # M2 is intentionally unchanged and still addresses runs_root/.hf-cache.
    # A directory junction maps that exact path onto the persistent cache.
    $RunsHfCache = Join-Path $RunsRoot ".hf-cache"
    if (Test-Path $RunsHfCache) {
        Remove-Item -Recurse -Force $RunsHfCache
    }
    New-Item -ItemType Junction -Path $RunsHfCache -Target $PersistentHfCache | Out-Null
    Add-Stage -Name "hf_cache_binding" -Status "PASS" -ExitCode 0 -Detail $PersistentHfCache

    $TestFiles = @(
        "tests/test_model_pipeline_m0.py",
        "tests/test_model_pipeline_m1.py",
        "tests/test_model_pipeline_m2_unit.py",
        "tests/test_model_pipeline_m3.py",
        "tests/test_model_pipeline_m4.py",
        "tests/test_model_pipeline_m5.py",
        "tests/test_model_pipeline_m5_f16_requalification.py"
    )
    foreach ($TestFile in $TestFiles) {
        Invoke-Checked -Stage ("pytest:" + $TestFile) -FilePath $PipelinePython -Arguments @("-m","pytest","-q",$TestFile)
    }

    $Lock = Get-Content "docs/model-training-pipeline/runtime/llama_cpp.lock.json" -Raw | ConvertFrom-Json
    New-Item -ItemType Directory -Force -Path $LlamaSource | Out-Null
    Invoke-Checked -Stage "llama_git_init" -FilePath "git" -Arguments @("init",$LlamaSource)
    Invoke-Checked -Stage "llama_git_remote" -FilePath "git" -Arguments @("-C",$LlamaSource,"remote","add","origin",$Lock.source_url)
    Invoke-Checked -Stage "llama_git_fetch" -FilePath "git" -Arguments @("-C",$LlamaSource,"fetch","--depth","1","origin",$Lock.commit_sha)
    Invoke-Checked -Stage "llama_git_checkout" -FilePath "git" -Arguments @("-C",$LlamaSource,"checkout","--detach","FETCH_HEAD")
    $ActualLlamaSha = (& git -C $LlamaSource rev-parse HEAD).Trim()
    if ($ActualLlamaSha -ne $Lock.commit_sha) {
        throw "llama.cpp SHA mismatch expected=$($Lock.commit_sha) actual=$ActualLlamaSha"
    }
    Add-Stage -Name "llama_commit_identity" -Status "PASS" -Detail $ActualLlamaSha

    & $PipelinePython -m venv $ConverterVenv
    if ($LASTEXITCODE -ne 0) { throw "Failed to create converter venv" }
    $ConverterPython = Join-Path $ConverterVenv "Scripts\python.exe"
    Invoke-Checked -Stage "converter_pip_upgrade" -FilePath $ConverterPython -Arguments @("-m","pip","install","--upgrade","pip")
    $ConverterReq = Join-Path $LlamaSource "requirements\requirements-convert_hf_to_gguf.txt"
    Invoke-Checked -Stage "converter_dependencies" -FilePath $ConverterPython -Arguments @("-m","pip","install","-r",$ConverterReq)

    $ProbeLines = @(& $ConverterPython "pipeline/m5_converter_probe.py")
    $ProbeExit = $LASTEXITCODE
    Write-Utf8NoBom -Path $ConverterProbeJson -Content (($ProbeLines -join [Environment]::NewLine) + [Environment]::NewLine)
    if ($ProbeExit -ne 0) { throw "Converter import probe failed" }
    $Probe = Get-Content $ConverterProbeJson -Raw | ConvertFrom-Json
    foreach ($Name in @("torch","transformers","numpy","sentencepiece","protobuf","gguf")) {
        if (-not $Probe.$Name.import_ok) { throw "Converter import failed for $Name" }
    }
    $Report.artifacts.converter_probe = [ordered]@{
        path = $ConverterProbeJson
        sha256 = Get-Sha256 $ConverterProbeJson
    }
    Add-Stage -Name "converter_import_probe" -Status "PASS"

    $BuildDir = Join-Path $LlamaSource "build"
    $ConfigureArgs = @("-S",$LlamaSource,"-B",$BuildDir) + @($Lock.build.flags)
    Invoke-Checked -Stage "llama_cmake_configure" -FilePath "cmake" -Arguments $ConfigureArgs

    $BuildArgs = @("--build",$BuildDir,"--config","Release","--target") + @($Lock.build.targets) + @("--parallel","2")
    Invoke-Checked -Stage "llama_cmake_build" -FilePath "cmake" -Arguments $BuildArgs

    $CliCandidates = @(Get-ChildItem -Path $BuildDir -Recurse -File -Filter "llama-cli.exe")
    $QuantCandidates = @(Get-ChildItem -Path $BuildDir -Recurse -File -Filter "llama-quantize.exe")
    if ($CliCandidates.Count -ne 1) { throw "Expected exactly one llama-cli.exe, found $($CliCandidates.Count)" }
    if ($QuantCandidates.Count -ne 1) { throw "Expected exactly one llama-quantize.exe, found $($QuantCandidates.Count)" }
    $LlamaCli = $CliCandidates[0].FullName
    $LlamaQuantize = $QuantCandidates[0].FullName

    $Manifest = [ordered]@{
        schema = "mindforge-llama-cpp-build-v1"
        source_commit = $ActualLlamaSha
        flags = @($Lock.build.flags)
        targets = @($Lock.build.targets)
        configure_command = @("cmake") + $ConfigureArgs
        build_command = @("cmake") + $BuildArgs
        platform = "windows-local-fallback"
        llama_cli = [ordered]@{ path = $LlamaCli; sha256 = Get-Sha256 $LlamaCli }
        llama_quantize = [ordered]@{ path = $LlamaQuantize; sha256 = Get-Sha256 $LlamaQuantize }
    }
    $ManifestJson = $Manifest | ConvertTo-Json -Depth 10
    Write-Utf8NoBom -Path $BuildManifest -Content ($ManifestJson + [Environment]::NewLine)
    $Report.artifacts.build_manifest = [ordered]@{
        path = $BuildManifest
        sha256 = Get-Sha256 $BuildManifest
    }
    Add-Stage -Name "llama_build_manifest" -Status "PASS"

    $env:HF_HUB_DISABLE_TELEMETRY = "1"
    $env:HF_HUB_OFFLINE = "1"
    $env:TOKENIZERS_PARALLELISM = "false"
    $env:OMP_NUM_THREADS = "1"
    $env:MKL_NUM_THREADS = "1"

    $HarnessArgs = @(
        "-m","tools.m5_f16_requalification",
        "-c","docs/model-training-pipeline/examples/end_to_end_small.yaml",
        "--workspace",".",
        "--runs-root",$RunsRoot,
        "--llama-source",$LlamaSource,
        "--llama-cli",$LlamaCli,
        "--llama-quantize",$LlamaQuantize,
        "--converter-python",$ConverterPython,
        "--build-manifest",$BuildManifest,
        "--json"
    )

    $HarnessStderr = Join-Path $WorkRoot "m5-f16-stderr.log"

    # Windows PowerShell 5.1 turns native stderr into PowerShell error records.
    # With ErrorActionPreference=Stop that can terminate the runner before the
    # native process exit code is captured. Redirect at the process boundary
    # instead so scientific PASS/FAIL comes only from the Python harness.
    $QuotedHarnessArgs = @()
    foreach ($Arg in $HarnessArgs) {
        $Text = [string]$Arg
        if ($Text -match '[\s"]') {
            $QuotedHarnessArgs += ('"' + ($Text -replace '"', '\\"') + '"')
        } else {
            $QuotedHarnessArgs += $Text
        }
    }
    $HarnessProcess = Start-Process `
        -FilePath $PipelinePython `
        -ArgumentList $QuotedHarnessArgs `
        -WorkingDirectory $RepoRoot `
        -NoNewWindow `
        -Wait `
        -PassThru `
        -RedirectStandardOutput $HarnessJson `
        -RedirectStandardError $HarnessStderr
    $HarnessExit = [int]$HarnessProcess.ExitCode

    $Report.artifacts.harness_stdout = [ordered]@{
        path = $HarnessJson
        sha256 = Get-Sha256 $HarnessJson
    }
    $Report.artifacts.harness_stderr = [ordered]@{
        path = $HarnessStderr
        sha256 = Get-Sha256 $HarnessStderr
        tail = if (Test-Path $HarnessStderr) {
            ((Get-Content $HarnessStderr -Tail 80) -join [Environment]::NewLine)
        } else {
            ""
        }
    }

    if (Test-Path $HarnessJson -PathType Leaf) {
        $HarnessRaw = Get-Content $HarnessJson -Raw
        if (-not [string]::IsNullOrWhiteSpace($HarnessRaw)) {
            try {
                $Parsed = $HarnessRaw | ConvertFrom-Json
                $Report.f16_result = $Parsed
                $Report.scientific_outcome = $Parsed.status
                $Report.quantization_executed = [bool]$Parsed.quantization_executed
                $Report.quantization_authorized = [bool]$Parsed.quantization_authorized
            } catch {
                $Report.f16_result = [ordered]@{
                    parse_error = $_.Exception.Message
                }
            }
        }
    }

    $ResultCandidates = @(Get-ChildItem -Path $RunsRoot -Recurse -File -Filter "M5_F16_REQUALIFICATION_RESULT.json" -ErrorAction SilentlyContinue)
    if ($ResultCandidates.Count -eq 1) {
        $ScientificResultPath = $ResultCandidates[0].FullName
        $ScientificResult = Get-Content $ScientificResultPath -Raw | ConvertFrom-Json
        $Report.artifacts.scientific_result = [ordered]@{
            path = $ScientificResultPath
            sha256 = Get-Sha256 $ScientificResultPath
        }
        $Report.f16_result = $ScientificResult
        $Report.scientific_outcome = $ScientificResult.status
        $Report.quantization_executed = [bool]$ScientificResult.quantization_executed
        $Report.quantization_authorized = [bool]$ScientificResult.quantization_authorized
    } elseif ($ResultCandidates.Count -gt 1) {
        throw "Multiple M5_F16_REQUALIFICATION_RESULT.json files found; refusing ambiguous evidence"
    }

    if ($HarnessExit -ne 0) {
        Add-Stage -Name "f16_requalification" -Status "FAIL" -ExitCode $HarnessExit -Detail "Harness returned non-zero."
        if ($null -ne $Report.f16_result -and $Report.f16_result.status -eq "FAIL" -and $ResultCandidates.Count -eq 1) {
            $Report.overall_status = "SCIENTIFIC_FAIL"
            $Report.scientific_outcome = "FAIL"
        } else {
            $Report.overall_status = "EXECUTION_FAIL"
            $Report.scientific_outcome = "UNADJUDICATED"
            $Report.error = [ordered]@{
                message = "Harness exited before a scientific result artifact was produced."
                stderr_tail = $Report.artifacts.harness_stderr.tail
            }
        }
        Save-Report
        Write-Host "Report written: $ReportPath"
        exit $HarnessExit
    }

    if ($null -eq $Report.f16_result -or $Report.f16_result.status -ne "PASS") {
        throw "Harness exited zero but did not emit PASS result"
    }
    if ($Report.f16_result.quantization_executed -ne $false) {
        throw "Governance violation: quantization was executed"
    }
    if ($Report.f16_result.m6_authorized -ne $false) {
        throw "Governance violation: M6 was authorized"
    }

    Add-Stage -Name "f16_requalification" -Status "PASS" -ExitCode 0 -Detail $Report.f16_result.result_hash
    $Report.overall_status = "PASS"
    $Report.scientific_outcome = "PASS"
    Save-Report

    Write-Host ""
    Write-Host "=== LOCAL F16 REQUALIFICATION PASS ==="
    Write-Host "Report JSON: $ReportPath"
    Write-Host "Upload this JSON file back to ChatGPT."
    exit 0
}
catch {
    $Report.overall_status = "EXECUTION_FAIL"
    if ($Report.scientific_outcome -eq "UNADJUDICATED") {
        $Report.scientific_outcome = "UNADJUDICATED"
    }
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

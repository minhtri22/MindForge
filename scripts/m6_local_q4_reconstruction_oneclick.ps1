param(
    [string]$ReportPath = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Program = "M6_LOCAL_Q4_DETERMINISTIC_RECONSTRUCTION"
$ExpectedLlamaCommit = "ce8caa6e60a03093351d6016a818720e0d46f0fb"
$Q4AuthorizationCommit = "9506e5fc205e641aba942a0bc9ff2fbaa7d881a5"
$Q4AuthorizationBlob = "f26754440d710904f45eb1d7916d334484f43bb5"
$VenueAmendmentCommit = "4aed637eb8bb41cc5e67c7b079402cf16d6948d2"
$VenueAmendmentBlob = "5d67202f3103f36736cf0e7973c054cf6df658fd"

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
$LockPath = Join-Path $RepoRoot "artifacts\model-training-pipeline\m6\local_windows\q4_reconstruction\LOCAL_Q4_RECONSTRUCTION_LOCK.json"
if (-not (Test-Path $LockPath -PathType Leaf)) { throw "Local Q4 reconstruction lock missing: $LockPath" }
$Lock = Get-Content $LockPath -Raw | ConvertFrom-Json

$WorkRoot = Join-Path $RepoRoot ".local\M6-LOCAL-Q4-RECONSTRUCTION"
$BuildRoot = Join-Path $WorkRoot "build"
$OutputRoot = Join-Path $WorkRoot "output"
if ([string]::IsNullOrWhiteSpace($ReportPath)) {
    $ReportDir = Join-Path $WorkRoot "report"
    New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
    $ReportPath = Join-Path $ReportDir "M6_LOCAL_Q4_RECONSTRUCTION_REPORT.json"
}
New-Item -ItemType Directory -Force -Path (Split-Path $ReportPath -Parent) | Out-Null

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
    try { return ([BitConverter]::ToString($Sha.ComputeHash($Bytes))).Replace("-","").ToLowerInvariant() }
    finally { $Sha.Dispose() }
}
function Get-Identity {
    param([System.IO.FileInfo]$File,[System.Collections.IDictionary]$Expected)
    $Sha = Get-Sha256File $File.FullName
    $ManifestJson = '[{"name":"' + $Expected.filename + '","sha256":"' + $Sha + '","size":' + [string]$File.Length + '}]'
    $ManifestHash = Get-Sha256Text $ManifestJson
    $Checks = [ordered]@{
        filename_exact = ($File.Name -ceq $Expected.filename)
        size_exact = ([int64]$File.Length -eq [int64]$Expected.size_bytes)
        sha256_exact = ($Sha -eq $Expected.sha256)
        aggregate_manifest_exact = ($ManifestHash -eq $Expected.aggregate_manifest_hash)
    }
    return [ordered]@{
        path=$File.FullName
        length=[int64]$File.Length
        sha256=$Sha
        aggregate_manifest_hash=$ManifestHash
        checks=$Checks
        exact_identity=($Checks.filename_exact -and $Checks.size_exact -and $Checks.sha256_exact -and $Checks.aggregate_manifest_exact)
    }
}
function Save-Report {
    $Report.completed_at=(Get-Date).ToUniversalTime().ToString("o")
    Write-Utf8NoBom -Path $ReportPath -Content (($Report | ConvertTo-Json -Depth 40)+[Environment]::NewLine)
}

$Report=[ordered]@{
    schema="mindforge-model-pipeline-m6-local-q4-reconstruction-report-v1"
    program=$Program
    started_at=(Get-Date).ToUniversalTime().ToString("o")
    completed_at=$null
    overall_status="RUNNING"
    classification="UNADJUDICATED"
    authorization_consumed=$false
    reconstruction_started=$false
    repo=[ordered]@{}
    host=[ordered]@{}
    input_f16=$null
    llama_cpp=[ordered]@{}
    build=[ordered]@{}
    reconstruction=[ordered]@{}
    boundaries=[ordered]@{
        f16_regeneration_executed=$false
        hf_to_gguf_conversion_executed=$false
        llama_cli_inference_executed=$false
        fixture_evaluation_executed=$false
        scientific_adjudication_executed=$false
        ollama_server_started=$false
        ollama_create_executed=$false
        ollama_chat_executed=$false
        m6_scientific_execution_executed=$false
        m7_authorized=$false
        bulk_training_authorized=$false
    }
    error=$null
}

try {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "git not found" }

    $CMakeResolution = [ordered]@{
        source = "PATH"
        path = $null
        vswhere_path = $null
        visual_studio_root = $null
    }
    $CMakeCommand = Get-Command cmake -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -eq $CMakeCommand) {
        $VsWhere = "${env:ProgramFiles(x86)}\\Microsoft Visual Studio\\Installer\\vswhere.exe"
        if (Test-Path $VsWhere -PathType Leaf) {
            $CMakeResolution.vswhere_path = $VsWhere
            $VsRoot = (& $VsWhere -latest -products * -property installationPath).Trim()
            if (-not [string]::IsNullOrWhiteSpace($VsRoot)) {
                $CMakeResolution.visual_studio_root = $VsRoot
                $VsCmake = Join-Path $VsRoot "Common7\\IDE\\CommonExtensions\\Microsoft\\CMake\\CMake\\bin\\cmake.exe"
                if (Test-Path $VsCmake -PathType Leaf) {
                    $env:Path = "$(Split-Path $VsCmake);$env:Path"
                    $CMakeCommand = Get-Command cmake -ErrorAction SilentlyContinue | Select-Object -First 1
                    if ($null -ne $CMakeCommand) {
                        $CMakeResolution.source = "VISUAL_STUDIO_VSWHERE"
                        $CMakeResolution.path = $VsCmake
                    }
                }
            }
        }
    }
    if ($null -eq $CMakeCommand) {
        throw "cmake not found in PATH or Visual Studio CMake discovery"
    }
    if ($null -eq $CMakeResolution.path) {
        $CMakeResolution.path = $CMakeCommand.Source
    }

    $Head=(& git rev-parse HEAD).Trim()
    $Branch=(& git branch --show-current).Trim()
    $Dirty=@(& git status --porcelain --untracked-files=no)
    if ($Dirty.Count -gt 0) { throw "Tracked working tree is dirty: $($Dirty -join '; ')" }

    & git merge-base --is-ancestor ([string]$Lock.implementation_commit) $Head *> $null
    if ($LASTEXITCODE -ne 0) { throw "Locked Q4 reconstruction implementation is not an ancestor of HEAD" }

    $ScriptBlob=(& git hash-object -- $PSCommandPath).Trim()
    if ($ScriptBlob -ne [string]$Lock.exact_blobs.script_git_blob_sha1) { throw "Script blob mismatch" }
    $AuthBlob=(& git hash-object -- "artifacts/model-training-pipeline/m6/parent_artifact/DETERMINISTIC_RECONSTRUCTION_AUTHORIZATION.json").Trim()
    if ($AuthBlob -ne $Q4AuthorizationBlob) { throw "Q4 reconstruction authorization blob mismatch" }
    $AmendmentBlob=(& git hash-object -- "artifacts/model-training-pipeline/m6/VENUE_INDEPENDENCE_GOVERNANCE_AMENDMENT.json").Trim()
    if ($AmendmentBlob -ne $VenueAmendmentBlob) { throw "Venue amendment blob mismatch" }

    $Report.repo=[ordered]@{root=$RepoRoot;branch=$Branch;head=$Head;tracked_worktree_clean=$true;script_git_blob_sha1=$ScriptBlob}
    $OS=Get-CimInstance Win32_OperatingSystem
    $CPU=Get-CimInstance Win32_Processor | Select-Object -First 1
    $Report.host=[ordered]@{
        os=$OS.Caption;build=$OS.BuildNumber;cpu=$CPU.Name.Trim()
        powershell=$PSVersionTable.PSVersion.ToString()
        cmake=((& cmake --version | Select-Object -First 1).Trim())
        cmake_resolution=$CMakeResolution
    }

    $SearchRoot=Split-Path $RepoRoot -Parent
    $F16Candidates=@(Get-ChildItem -LiteralPath $SearchRoot -Recurse -File -Filter $F16.filename -ErrorAction SilentlyContinue)
    $F16Rows=@($F16Candidates | ForEach-Object { Get-Identity -File $_ -Expected $F16 })
    $ExactF16=@($F16Rows | Where-Object {$_.exact_identity})
    if ($ExactF16.Count -lt 1) { throw "Exact frozen F16 not found" }
    $SelectedF16=$ExactF16[0]
    $Report.input_f16=$SelectedF16

    $LlamaDirs=@(Get-ChildItem -LiteralPath $SearchRoot -Recurse -Directory -Filter "llama.cpp" -ErrorAction SilentlyContinue | Where-Object { Test-Path (Join-Path $_.FullName ".git") })
    $ExactLlama=@()
    foreach($Dir in $LlamaDirs){
        $Commit=(& git -C $Dir.FullName rev-parse HEAD 2>$null).Trim()
        if($Commit -eq $ExpectedLlamaCommit){$ExactLlama += $Dir.FullName}
    }
    if($ExactLlama.Count -lt 1){throw "Exact llama.cpp source commit not found"}
    $LlamaSource=$ExactLlama[0]

    $RuntimeLock=Get-Content "docs/model-training-pipeline/runtime/llama_cpp.lock.json" -Raw | ConvertFrom-Json
    if($RuntimeLock.commit_sha -ne $ExpectedLlamaCommit){throw "llama.cpp runtime lock commit drift"}
    $Flags=@($RuntimeLock.build.flags)
    $Report.llama_cpp=[ordered]@{source_path=$LlamaSource;source_commit=$ExpectedLlamaCommit;flags=$Flags}

    if(Test-Path $BuildRoot){Remove-Item -Recurse -Force $BuildRoot}
    New-Item -ItemType Directory -Force -Path $BuildRoot,$OutputRoot | Out-Null

    $ConfigureArgs=@("-S",$LlamaSource,"-B",$BuildRoot)+$Flags
    & cmake @ConfigureArgs
    if($LASTEXITCODE -ne 0){throw "cmake configure failed"}

    $BuildArgs=@("--build",$BuildRoot,"--config","Release","--target","llama-quantize","--parallel","2")
    & cmake @BuildArgs
    if($LASTEXITCODE -ne 0){throw "cmake llama-quantize build failed"}

    $QuantCandidates=@(Get-ChildItem -LiteralPath $BuildRoot -Recurse -File -Filter "llama-quantize.exe")
    if($QuantCandidates.Count -ne 1){throw "Expected exactly one freshly built llama-quantize.exe, found $($QuantCandidates.Count)"}
    $Quant=$QuantCandidates[0].FullName
    $QuantSha=Get-Sha256File $Quant
    $Report.build=[ordered]@{
        configure_command=@("cmake")+$ConfigureArgs
        build_command=@("cmake")+$BuildArgs
        llama_quantize_path=$Quant
        llama_quantize_sha256=$QuantSha
        executable_sha_policy="venue_specific_record_only"
    }
    Save-Report

    $Output=Join-Path $OutputRoot $Q4.filename
    if(Test-Path $Output){Remove-Item -Force $Output}

    # Attempt is consumed immediately before the one authorized quantizer process starts.
    $Report.authorization_consumed=$true
    $Report.reconstruction_started=$true
    Save-Report

    & $Quant $SelectedF16.path $Output "Q4_K_M"
    $QuantExit=$LASTEXITCODE
    if($QuantExit -ne 0){throw "llama-quantize failed after attempt start with exit code $QuantExit"}
    if(-not (Test-Path $Output -PathType Leaf)){throw "Quantizer exited 0 but Q4 output is missing"}

    $Q4Identity=Get-Identity -File (Get-Item $Output) -Expected $Q4
    $Report.reconstruction=[ordered]@{
        command=@($Quant,$SelectedF16.path,$Output,"Q4_K_M")
        quantizer_exit_code=$QuantExit
        output=$Q4Identity
    }

    if($Q4Identity.exact_identity){
        $Report.classification="ADMITTED_DETERMINISTIC_RECONSTRUCTION"
        $Report.overall_status="PASS"
    } else {
        $Report.classification="RECONSTRUCTION_IDENTITY_MISMATCH"
        $Report.overall_status="COMPLETE_NONMATCH"
        Save-Report
        Remove-Item -Force $Output
    }
    Save-Report
    Write-Host "Classification: $($Report.classification)"
    Write-Host "Report: $ReportPath"
    exit 0
}
catch {
    if($Report.reconstruction_started){
        $Report.classification="INVALID_INFRASTRUCTURE_AFTER_ATTEMPT"
    } else {
        $Report.classification="INVALID_INFRASTRUCTURE_BEFORE_ATTEMPT"
    }
    $Report.overall_status="FAIL"
    $Report.error=[ordered]@{message=$_.Exception.Message;type=$_.Exception.GetType().FullName;script_stack=$_.ScriptStackTrace}
    Save-Report
    Write-Error $_
    Write-Host "Report: $ReportPath"
    exit 2
}
finally { Save-Report }

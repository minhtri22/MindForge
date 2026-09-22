param(
    [string]$OutputRoot = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Program = "M6R_RUNTIME_FAILURE_DECOMPOSITION"
$Phase = "RFD-C1_EXISTING_EVIDENCE_ONLY"
$RunStartUtc = [DateTimeOffset]::Parse("2026-09-22T14:09:47.4135943Z")
$RunEndUtc = [DateTimeOffset]::Parse("2026-09-22T14:09:56.6906965Z")
$ContextBeforeSeconds = 120
$ContextAfterSeconds = 120
$ContextStartUtc = $RunStartUtc.AddSeconds(-$ContextBeforeSeconds)
$ContextEndUtc = $RunEndUtc.AddSeconds($ContextAfterSeconds)

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $RepoRoot

if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    $OutputRoot = Join-Path $RepoRoot ".local\M6R-RUNTIME-FAILURE-DECOMPOSITION\RFD-C1"
}
$RawDir = Join-Path $OutputRoot "raw"
$ExcerptDir = Join-Path $OutputRoot "excerpts"
New-Item -ItemType Directory -Force -Path $OutputRoot,$RawDir,$ExcerptDir | Out-Null
$ReportPath = Join-Path $OutputRoot "RFD_C1_EXISTING_EVIDENCE_REPORT.json"

function Write-Utf8NoBom {
    param([string]$Path,[string]$Content)
    $Encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path,$Content,$Encoding)
}
function Get-Sha256File {
    param([string]$Path)
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}
function Convert-LineTimestampToUtc {
    param(
        [string]$Line,
        [System.TimeZoneInfo]$LocalTimeZone
    )

    $Rfc = [regex]::Match($Line,'(?<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))')
    if ($Rfc.Success) {
        try {
            $Dto = [DateTimeOffset]::Parse(
                $Rfc.Groups["ts"].Value,
                [Globalization.CultureInfo]::InvariantCulture,
                [Globalization.DateTimeStyles]::AllowWhiteSpaces
            )
            return $Dto.ToUniversalTime()
        } catch {}
    }

    $Gin = [regex]::Match($Line,'(?<ts>\d{4}/\d{2}/\d{2}\s*-\s*\d{2}:\d{2}:\d{2})')
    if ($Gin.Success) {
        try {
            $Normalized = ($Gin.Groups["ts"].Value -replace '\s*-\s*',' - ')
            $Dt = [DateTime]::ParseExact(
                $Normalized,
                "yyyy/MM/dd - HH:mm:ss",
                [Globalization.CultureInfo]::InvariantCulture,
                [Globalization.DateTimeStyles]::None
            )
            $Unspecified = [DateTime]::SpecifyKind($Dt,[DateTimeKind]::Unspecified)
            $Offset = $LocalTimeZone.GetUtcOffset($Unspecified)
            return ([DateTimeOffset]::new($Unspecified,$Offset)).ToUniversalTime()
        } catch {}
    }

    $Plain = [regex]::Match($Line,'(?<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
    if ($Plain.Success) {
        try {
            $Dt = [DateTime]::ParseExact(
                $Plain.Groups["ts"].Value,
                "yyyy-MM-dd HH:mm:ss",
                [Globalization.CultureInfo]::InvariantCulture,
                [Globalization.DateTimeStyles]::None
            )
            $Unspecified = [DateTime]::SpecifyKind($Dt,[DateTimeKind]::Unspecified)
            $Offset = $LocalTimeZone.GetUtcOffset($Unspecified)
            return ([DateTimeOffset]::new($Unspecified,$Offset)).ToUniversalTime()
        } catch {}
    }

    return $null
}
function Get-SafeEvidenceName {
    param([string]$Name)
    return ($Name -replace '[^A-Za-z0-9._-]','_')
}

$Head = (& git rev-parse HEAD).Trim()
$Branch = (& git branch --show-current).Trim()
$Dirty = @(& git status --porcelain --untracked-files=no)
if ($Dirty.Count -gt 0) { throw "Tracked worktree must be clean before forensic collection" }

$LocalTz = [TimeZoneInfo]::Local
$LogRoot = Join-Path $env:LOCALAPPDATA "Ollama"
$SourceFiles = @()
if (Test-Path $LogRoot -PathType Container) {
    $ServerCurrent = Join-Path $LogRoot "server.log"
    if (Test-Path $ServerCurrent -PathType Leaf) { $SourceFiles += Get-Item -LiteralPath $ServerCurrent }
    $SourceFiles += @(Get-ChildItem -LiteralPath $LogRoot -File -Filter "server-*.log" -ErrorAction SilentlyContinue)
    $AppLog = Join-Path $LogRoot "app.log"
    if (Test-Path $AppLog -PathType Leaf) { $SourceFiles += Get-Item -LiteralPath $AppLog }
}
$SourceFiles = @($SourceFiles | Sort-Object FullName -Unique)

$Report = [ordered]@{
    schema = "mindforge-model-pipeline-m6r-rfd-c1-existing-evidence-report-v1"
    program = $Program
    phase = $Phase
    collected_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    repo = [ordered]@{
        root = $RepoRoot
        branch = $Branch
        head = $Head
        tracked_worktree_clean = $true
    }
    frozen_window = [ordered]@{
        run_start_utc = $RunStartUtc.ToString("o")
        run_end_utc = $RunEndUtc.ToString("o")
        context_start_utc = $ContextStartUtc.ToString("o")
        context_end_utc = $ContextEndUtc.ToString("o")
        context_before_seconds = $ContextBeforeSeconds
        context_after_seconds = $ContextAfterSeconds
    }
    local_time = [ordered]@{
        windows_time_zone_id = $LocalTz.Id
        base_utc_offset = $LocalTz.BaseUtcOffset.ToString()
        run_start_local = [TimeZoneInfo]::ConvertTime($RunStartUtc,$LocalTz).ToString("o")
        run_end_local = [TimeZoneInfo]::ConvertTime($RunEndUtc,$LocalTz).ToString("o")
    }
    source_root = $LogRoot
    source_root_exists = (Test-Path $LogRoot -PathType Container)
    sources = @()
    totals = [ordered]@{
        files_found = $SourceFiles.Count
        lines_read = 0
        timestamp_parsed_lines = 0
        exact_window_lines = 0
        context_window_lines = 0
        textual_time_candidates = 0
    }
    exact_window_evidence = @()
    context_window_evidence = @()
    textual_time_candidates = @()
    collection_integrity_pass = $true
    evidence_adequacy = "UNADJUDICATED"
    mechanism_class = "UNRESOLVED"
    mechanism_assignment_performed = $false
    forbidden_actions_executed = [ordered]@{
        ollama_process_invocation = $false
        ollama_api_request = $false
        service_state_change = $false
        debug_mode_change = $false
        model_store_mutation = $false
        inference_request = $false
    }
}

foreach ($File in $SourceFiles) {
    $SourceShaBefore = Get-Sha256File $File.FullName
    $SafeName = Get-SafeEvidenceName $File.Name
    $RawCopy = Join-Path $RawDir $SafeName
    Copy-Item -LiteralPath $File.FullName -Destination $RawCopy -Force
    $RawCopySha = Get-Sha256File $RawCopy
    if ($RawCopySha -ne $SourceShaBefore) {
        $Report.collection_integrity_pass = $false
        throw "Raw evidence copy SHA256 mismatch for $($File.FullName)"
    }

    $FileExact = @()
    $FileContext = @()
    $FileTextual = @()
    $LineCount = 0
    $ParsedCount = 0
    $LineNumber = 0

    foreach ($Line in [IO.File]::ReadLines($File.FullName)) {
        $LineNumber++
        $LineCount++
        $ParsedUtc = Convert-LineTimestampToUtc -Line $Line -LocalTimeZone $LocalTz

        if ($null -ne $ParsedUtc) {
            $ParsedCount++
            if ($ParsedUtc -ge $ContextStartUtc -and $ParsedUtc -le $ContextEndUtc) {
                $Entry = [ordered]@{
                    source = $File.Name
                    line_number = $LineNumber
                    parsed_utc = $ParsedUtc.ToString("o")
                    line = $Line
                }
                $FileContext += $Entry
                $Report.context_window_evidence += $Entry
            }
            if ($ParsedUtc -ge $RunStartUtc -and $ParsedUtc -le $RunEndUtc) {
                $Entry = [ordered]@{
                    source = $File.Name
                    line_number = $LineNumber
                    parsed_utc = $ParsedUtc.ToString("o")
                    line = $Line
                }
                $FileExact += $Entry
                $Report.exact_window_evidence += $Entry
            }
        } elseif (
            $Line -match '2026[-/]09[-/]22' -and
            ($Line -match '14:0[7-9]|14:1[0-1]' -or $Line -match '21:0[7-9]|21:1[0-1]')
        ) {
            $Entry = [ordered]@{
                source = $File.Name
                line_number = $LineNumber
                line = $Line
                reason = "textual_time_candidate_unparsed"
            }
            $FileTextual += $Entry
            $Report.textual_time_candidates += $Entry
        }
    }

    $SourceShaAfter = Get-Sha256File $File.FullName
    $SourceChangedDuringCollection = ($SourceShaAfter -ne $SourceShaBefore)
    $RawMatchesObservedSourceState = (($RawCopySha -eq $SourceShaBefore) -or ($RawCopySha -eq $SourceShaAfter))
    if (-not $RawMatchesObservedSourceState) {
        $Report.collection_integrity_pass = $false
    }

    $ExactPath = Join-Path $ExcerptDir ($SafeName + ".exact-window.json")
    $ContextPath = Join-Path $ExcerptDir ($SafeName + ".context-window.json")
    $TextualPath = Join-Path $ExcerptDir ($SafeName + ".textual-candidates.json")
    Write-Utf8NoBom $ExactPath (($FileExact | ConvertTo-Json -Depth 20) + [Environment]::NewLine)
    Write-Utf8NoBom $ContextPath (($FileContext | ConvertTo-Json -Depth 20) + [Environment]::NewLine)
    Write-Utf8NoBom $TextualPath (($FileTextual | ConvertTo-Json -Depth 20) + [Environment]::NewLine)

    $Report.sources += [ordered]@{
        name = $File.Name
        source_path = $File.FullName
        source_size = [int64]$File.Length
        source_last_write_utc = $File.LastWriteTimeUtc.ToString("o")
        source_sha256_before = $SourceShaBefore
        source_sha256_after = $SourceShaAfter
        source_changed_during_collection = $SourceChangedDuringCollection
        raw_copy_path = $RawCopy
        raw_copy_sha256 = $RawCopySha
        raw_copy_matches_observed_source_state = $RawMatchesObservedSourceState
        lines_read = $LineCount
        timestamp_parsed_lines = $ParsedCount
        exact_window_line_count = $FileExact.Count
        context_window_line_count = $FileContext.Count
        textual_time_candidate_count = $FileTextual.Count
        exact_excerpt_path = $ExactPath
        exact_excerpt_sha256 = (Get-Sha256File $ExactPath)
        context_excerpt_path = $ContextPath
        context_excerpt_sha256 = (Get-Sha256File $ContextPath)
        textual_candidates_path = $TextualPath
        textual_candidates_sha256 = (Get-Sha256File $TextualPath)
    }

    $Report.totals.lines_read += $LineCount
    $Report.totals.timestamp_parsed_lines += $ParsedCount
    $Report.totals.exact_window_lines += $FileExact.Count
    $Report.totals.context_window_lines += $FileContext.Count
    $Report.totals.textual_time_candidates += $FileTextual.Count
}

if (-not $Report.source_root_exists) {
    $Report.evidence_adequacy = "NO_OLLAMA_LOG_DIRECTORY"
} elseif ($Report.totals.files_found -eq 0) {
    $Report.evidence_adequacy = "NO_EXPECTED_LOG_FILES"
} elseif ($Report.totals.context_window_lines -gt 0) {
    $Report.evidence_adequacy = "TIMESTAMPED_CONTEXT_EVIDENCE_PRESENT"
} elseif ($Report.totals.textual_time_candidates -gt 0) {
    $Report.evidence_adequacy = "ONLY_UNPARSED_TEXTUAL_TIME_CANDIDATES"
} else {
    $Report.evidence_adequacy = "NO_WINDOW_EVIDENCE_FOUND"
}

Write-Utf8NoBom $ReportPath (($Report | ConvertTo-Json -Depth 80) + [Environment]::NewLine)

Write-Host "RFD-C1 existing-evidence collection complete"
Write-Host "Evidence adequacy: $($Report.evidence_adequacy)"
Write-Host "Files found: $($Report.totals.files_found)"
Write-Host "Exact-window lines: $($Report.totals.exact_window_lines)"
Write-Host "Context-window lines: $($Report.totals.context_window_lines)"
Write-Host "Report: $ReportPath"

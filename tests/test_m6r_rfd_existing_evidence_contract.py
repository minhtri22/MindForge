from pathlib import Path
import json

SCRIPT = Path("scripts/m6r_rfd_collect_existing_evidence.ps1")
PREREG = Path("artifacts/model-training-pipeline/m6r-rfd/PREREGISTRATION.json")

def t():
    return SCRIPT.read_text(encoding="utf-8")

def test_program_and_phase_are_forensic_only():
    x=t()
    assert 'M6R_RUNTIME_FAILURE_DECOMPOSITION' in x
    assert 'RFD-C1_EXISTING_EVIDENCE_ONLY' in x
    assert 'mechanism_assignment_performed = $false' in x
    assert 'mechanism_class = "UNRESOLVED"' in x

def test_exact_m6r_window_is_frozen():
    x=t()
    assert '2026-09-22T14:09:47.4135943Z' in x
    assert '2026-09-22T14:09:56.6906965Z' in x
    assert '$ContextBeforeSeconds = 120' in x
    assert '$ContextAfterSeconds = 120' in x

def test_only_expected_existing_log_sources_are_collected():
    x=t()
    assert '"server.log"' in x
    assert '"server-*.log"' in x
    assert '"app.log"' in x
    assert 'Join-Path $env:LOCALAPPDATA "Ollama"' in x

def test_raw_evidence_is_hash_preserved():
    x=t()
    assert '$SourceShaBefore = Get-Sha256File' in x
    assert 'Copy-Item -LiteralPath' in x
    assert '$RawCopySha -ne $SourceShaBefore' in x
    assert '$SourceShaAfter = Get-Sha256File' in x
    assert 'source_changed_during_collection = $SourceChangedDuringCollection' in x
    assert 'raw_copy_matches_observed_source_state = $RawMatchesObservedSourceState' in x

def test_active_log_append_is_recorded_not_misclassified_as_source_mutation():
    x=t()
    assert '$SourceChangedDuringCollection = ($SourceShaAfter -ne $SourceShaBefore)' in x
    assert '$RawMatchesObservedSourceState' in x
    assert 'throw "Source log changed during collection' not in x

def test_timestamp_parser_supports_offset_and_local_forms():
    x=t()
    assert 'DateTimeOffset' in x
    assert 'yyyy/MM/dd - HH:mm:ss' in x
    assert 'yyyy-MM-dd HH:mm:ss' in x
    assert 'GetUtcOffset' in x
    assert 'TimeZoneInfo' in x

def test_collection_does_not_invoke_ollama_or_api_or_service_actions():
    x=t()
    forbidden = [
        'Invoke-RestMethod',
        'Invoke-WebRequest',
        'Start-Process',
        'Stop-Process',
        'ollama.exe',
        '/api/chat',
        '/api/generate',
        'OLLAMA_DEBUG',
        'SetEnvironmentVariable',
    ]
    for token in forbidden:
        assert token not in x

def test_no_model_store_mutation_primitives():
    x=t()
    assert 'Remove-Item' not in x
    assert 'Move-Item' not in x
    assert 'Rename-Item' not in x

def test_report_explicitly_marks_no_forbidden_actions():
    x=t()
    for field in [
        'ollama_process_invocation = $false',
        'ollama_api_request = $false',
        'service_state_change = $false',
        'debug_mode_change = $false',
        'model_store_mutation = $false',
        'inference_request = $false',
    ]:
        assert field in x

def test_unparsed_lines_are_not_assigned_timestamps():
    x=t()
    assert 'textual_time_candidate_unparsed' in x
    assert 'ONLY_UNPARSED_TEXTUAL_TIME_CANDIDATES' in x

def test_prereg_forbids_rerun_and_m6r2():
    p=json.loads(PREREG.read_text(encoding="utf-8"))
    assert p["collection_phase"]["mode"]=="EXISTING_EVIDENCE_ONLY"
    assert p["origin"]["m6r_reopened"] is False
    assert p["origin"]["rescue_rerun"] is False
    assert p["downstream"]["m6r2_authorized"] is False
    assert p["adjudication_rules"]["no_m6r_rerun_to_fill_missing_evidence"] is True

def test_mechanism_classes_are_frozen_but_assignment_deferred():
    p=json.loads(PREREG.read_text(encoding="utf-8"))
    assert p["adjudication_rules"]["no_mechanism_assignment_during_collection"] is True
    assert p["mechanism_classes"] == [
        "MODEL_LOAD_OR_GGUF_COMPATIBILITY",
        "MEMORY_OR_BACKEND_ALLOCATION",
        "INTEL_GPU_OR_RUNTIME_BACKEND",
        "CONTEXT_TEMPLATE_OR_TOKENIZER",
        "OLLAMA_SERVER_OTHER",
        "UNRESOLVED",
    ]

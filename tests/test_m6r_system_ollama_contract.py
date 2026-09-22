from pathlib import Path

SCRIPT = Path("scripts/m6r_system_ollama_oneclick.ps1")
PREREG = Path("artifacts/model-training-pipeline/m6r/PREREGISTRATION.json")

def text():
    return SCRIPT.read_text(encoding="utf-8")

def test_program_and_system_venue():
    t=text()
    assert 'M6R_SYSTEM_OLLAMA_REPLICATION' in t
    assert '127.0.0.1:11434' in t
    assert 'installed_system_ollama' in t
    assert 'OLLAMA_MODELS' not in t

def test_exact_target_and_installer_are_pinned():
    t=text()
    assert '$ExpectedOllamaVersion = "0.34.2"' in t
    assert 'OllamaSetup.exe' in t
    assert '8c9eb7ba71f3c6a62df4c7d204cc4739d90c335e1cbeb07c99fd471544066a8b' in t
    assert 'Test-OllamaSigner' in t
    assert 'O=Ollama Inc' in t

def test_upgrade_is_bounded_not_install_or_downgrade():
    t=text()
    assert 'fresh installation is outside M6R scope' in t
    assert 'downgrade is not authorized' in t
    assert '/VERYSILENT' in t and '/NORESTART' in t and '/SUPPRESSMSGBOXES' in t

def test_native_process_io_isolated():
    t=text()
    assert 'function Invoke-NativeCaptured' in t
    assert 'Start-Process @Params' in t
    assert 'RedirectStandardOutput' in t
    assert 'RedirectStandardError' in t
    assert '@(& $OllamaExe' not in t

def test_create_stage_has_explicit_fail_package_mapping():
    t=text()
    create=t.index('$CreateRun = Invoke-NativeCaptured')
    fail=t.index('$Report.classification = "FAIL_PACKAGE"', create)
    assert create < fail
    assert 'Owned Ollama model create process failed' in t

def test_attempt_marker_precedes_create():
    t=text()
    marker=t.index('Move-Item -Force $AttemptTmp $AttemptStatePath')
    consumed=t.index('$Report.attempt_consumed = $true')
    create=t.index('$CreateRun = Invoke-NativeCaptured')
    assert marker < consumed < create

def test_q4_identity_frozen():
    t=text()
    assert '397807456' in t
    assert 'ca9ac3104fa025619f34eaf941f4bac95787cc4aba2818d3e972766bc02cb977' in t
    assert 'e47700cab51bcf82174aa437ed767032f7ff29e3e1594690f5b9ff91e4762e0b' in t

def test_modelfile_and_inference_frozen():
    t=text()
    assert '5db25cbceaaa6b359b73f7edde1f54acb6a95f27a4803f5d28ad1b65012e1946' in t
    for x in ['num_ctx = 2048','num_predict = 128','temperature = 0','top_p = 1','top_k = 0','seed = 42']:
        assert x in t
    assert 'stream = $false' in t

def test_fixture_profile_reasoning_blobs_frozen():
    t=text()
    assert '450d83d38130765fe4a74fb18bab90177328218f' in t
    assert '1214e551c250e73b7a8cbbde71201fdd17e49ae1' in t
    assert '3813ae3ff00a49f2f97ccbda7833e0bf299ff1e4' in t

def test_user_model_store_is_snapshotted_and_restored():
    t=text()
    assert '$InitialNames = @(Get-ModelNames $Tags)' in t
    assert '$FinalNames = @(Get-ModelNames $FinalTags)' in t
    assert 'initial_final_model_sets_match' in t
    assert 'Where-Object { $RenderedNames -contains $_ }' in t

def test_cleanup_is_owned_only():
    t=text()
    assert '$ExpectedMarker = Get-Sha256Text' in t
    assert 'ownership_marker_mismatch' in t
    assert '@("rm",$ModelName)' in t

def test_no_pull_requantize_or_llama_cli_inference():
    t=text()
    assert 'ollama_pull_executed = $false' in t
    assert 'q4_requantization_executed = $false' in t
    assert 'llama_cli_inference_executed = $false' in t
    assert ' pull ' not in t.lower()

def test_reasoning_contract_no_native_think_request():
    t=text()
    assert 'native_think_field_sent = $false' in t
    assert 'unexpected_nonempty_native_thinking_field' in t
    assert 'think =' not in t.lower()

def test_system_service_is_preserved_if_preexisting():
    t=text()
    assert '$ServerStartedByScript = $false' in t
    assert 'if ($ServerStartedByScript -and' in t

def test_required_gates_include_system_runtime():
    t=text()
    assert 'system_ollama_present = $PresenceGate' in t
    assert 'system_ollama_exact_version_lock = $VersionGate' in t
    assert 'system_ollama_api_healthy = $ApiHealthyGate' in t

def test_m7_and_bulk_training_stay_closed():
    t=text()
    assert 'm7_authorized = $false' in t
    assert 'bulk_training_authorized = $false' in t

def test_prereg_is_fresh_replication_not_m6_rescue():
    import json
    p=json.loads(PREREG.read_text(encoding="utf-8"))
    assert p["program"]=="M6R_SYSTEM_OLLAMA_REPLICATION"
    assert p["relation_to_m6"]["m6_reopened"] is False
    assert p["relation_to_m6"]["rescue_rerun"] is False
    assert p["system_runtime"]["upgrade_allowed_before_attempt"] is True
    assert p["one_attempt"]["retry_to_seek_pass"] is False

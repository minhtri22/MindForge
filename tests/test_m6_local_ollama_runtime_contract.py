from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/m6_local_ollama_runtime_oneclick.ps1"
PREREG = ROOT / "artifacts/model-training-pipeline/m6/local_windows/ollama_runtime/PREREGISTRATION.json"
Q4_EVIDENCE = ROOT / "artifacts/model-training-pipeline/m6/local_windows/LOCAL_Q4_RECONSTRUCTION_EXECUTION_EVIDENCE.json"

def test_q4_reconstruction_is_exact_and_authorization_consumed():
    data = json.loads(Q4_EVIDENCE.read_text(encoding="utf-8"))
    assert data["verdict"] == "PASS"
    assert data["classification"] == "ADMITTED_DETERMINISTIC_RECONSTRUCTION"
    assert data["reconstruction"]["authorization_consumed"] is True
    out = data["reconstruction"]["output"]
    assert out["exact_identity"] is True
    assert out["size_bytes"] == 397807456
    assert out["sha256"] == "ca9ac3104fa025619f34eaf941f4bac95787cc4aba2818d3e972766bc02cb977"

def test_prereg_pins_isolated_ollama_0342_not_installed_0340():
    data = json.loads(PREREG.read_text(encoding="utf-8"))
    rt = data["runtime"]
    assert rt["observed_installed_version"] == "0.34.0"
    assert rt["exact_runtime_version"] == "0.34.2"
    assert rt["installed_ollama_may_be_used"] is False
    assert rt["installation_or_update_required"] is False
    assert rt["asset_sha256"] == "8f3fd071a2a2f9497b562f43502c77c2b701a99d1ee5dfda28da8c786373063b"

def test_modelfile_is_exact_m6_specific_contract():
    data = json.loads(PREREG.read_text(encoding="utf-8"))
    text = data["frozen_modelfile"]["text"]
    assert len(text.encode()) == 152
    assert hashlib.sha256(text.encode()).hexdigest() == "5db25cbceaaa6b359b73f7edde1f54acb6a95f27a4803f5d28ad1b65012e1946"
    assert "num_predict 128" in text
    assert "temperature 0" in text

def test_reasoning_mapping_uses_profile_tagged_transport_not_native_think():
    data = json.loads(PREREG.read_text(encoding="utf-8"))
    mapping = data["reasoning_mapping"]
    assert mapping["model_native_reasoning_assumed"] is False
    assert mapping["transport"] == "tagged_text"
    assert mapping["native_ollama_think_field_sent"] is False
    assert mapping["off_supported"] is False
    script = SCRIPT.read_text(encoding="utf-8")
    assert "native_think_field_sent = $false" in script
    assert '"think"' not in script

def test_script_pins_exact_asset_q4_and_contract_blobs():
    text = SCRIPT.read_text(encoding="utf-8")
    for token in [
        "v0.34.2/ollama-windows-amd64.zip",
        "8f3fd071a2a2f9497b562f43502c77c2b701a99d1ee5dfda28da8c786373063b",
        "ca9ac3104fa025619f34eaf941f4bac95787cc4aba2818d3e972766bc02cb977",
        "e47700cab51bcf82174aa437ed767032f7ff29e3e1594690f5b9ff91e4762e0b",
        "450d83d38130765fe4a74fb18bab90177328218f",
        "1214e551c250e73b7a8cbbde71201fdd17e49ae1",
        "3813ae3ff00a49f2f97ccbda7833e0bf299ff1e4",
        "127.0.0.1:11467",
    ]:
        assert token in text

def test_attempt_consumed_immediately_before_owned_create():
    text = SCRIPT.read_text(encoding="utf-8")
    consumed = text.index("$Report.attempt_consumed = $true")
    started = text.index("$Report.scientific_runtime_started = $true")
    create = text.index("& $OllamaExe create $ModelName")
    q4 = text.index("Q4 parent identity mismatch")
    version = text.index("Pinned Ollama version mismatch")
    assert q4 < consumed
    assert version < consumed
    assert consumed < started < create

def test_namespace_cleanup_is_owned_and_isolated():
    text = SCRIPT.read_text(encoding="utf-8")
    assert '"pipeline-test-" + $RunId' in text
    assert "$env:OLLAMA_MODELS = $ModelsDir" in text
    assert "$env:OLLAMA_HOST = $HostAddress" in text
    assert "ownership_marker_mismatch" in text
    assert "& $OllamaExe rm $ModelName" in text
    assert "initial_final_model_sets_match" in text

def test_parity_uses_exact_answer_vector_not_exact_text():
    text = SCRIPT.read_text(encoding="utf-8")
    assert '$Success = ($Content.Trim() -ceq ([string]$Task.expected).Trim())' in text
    assert "$FrozenVector = @($false,$false)" in text
    assert "exact_text_required = $false" in text
    assert "task_vector_match = $VectorGate" in text
    assert "accuracy_match = $AccuracyGate" in text

def test_no_quantization_llama_cli_pull_or_installed_ollama_mutation():
    text = SCRIPT.read_text(encoding="utf-8").lower()
    for token in ["llama-quantize.exe","llama-cli.exe","ollama pull","programs\\ollama\\ollama.exe","winget","choco"]:
        assert token not in text

def test_required_gate_names_are_frozen_before_runtime():
    data = json.loads(PREREG.read_text(encoding="utf-8"))
    expected = [
      "ollama_exact_version_lock","source_q4_identity_exact",
      "modelfile_deterministic_and_frozen","ephemeral_namespace_collision_safe",
      "ollama_create_owned_model_only","ollama_chat_real_runtime",
      "all_outputs_nonempty","task_vector_equals_frozen_llama_parent",
      "runtime_accuracy_equals_frozen_llama_parent",
      "format_parity_with_frozen_llama_parent","reasoning_runtime_mapping_pass",
      "cleanup_owned_artifact_only","no_unowned_model_mutation",
      "runtime_evidence_manifest_frozen",
    ]
    assert data["required_gates"] == expected


def test_create_failure_is_not_mislabeled_cleanup_failure_when_no_model_exists():
    text = SCRIPT.read_text(encoding="utf-8")
    assert '$CleanupGate = $true' in text
    assert '$Report.classification = $PreCleanupClass' in text
    assert 'no_owned_model_created' in text
    assert '-not $CleanupGate -or -not $NoMutationGate' in text


def test_one_attempt_has_durable_fail_closed_consumption_ledger():
    text = SCRIPT.read_text(encoding="utf-8")
    assert 'attempt-state.json' in text
    assert 'authorization already consumed' in text
    assert 'consumed = $true' in text
    assert 'immediately_before_ollama_create' in text
    marker = text.index('trigger = "immediately_before_ollama_create"')
    move = text.index('Move-Item -Force $AttemptTmp $AttemptStatePath')
    report_consumed = text.index('$Report.attempt_consumed = $true')
    create = text.index('& $OllamaExe create $ModelName')
    assert marker < move < report_consumed < create


def test_asset_download_transport_repair_is_pre_create_and_hash_guarded():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "Get-Command curl.exe" in text
    assert '"--retry","5"' in text
    assert "Start-Process -FilePath $Curl.Source" in text
    assert "-RedirectStandardError $CurlStderr" in text
    assert '"--silent","--show-error"' in text
    assert "Invoke-WebRequest -Uri $OllamaAssetUrl" in text
    download = text.index("if ($NeedDownload)")
    asset_hash = text.index("$AssetSha = Get-Sha256File $Zip")
    consumed = text.index("$Report.attempt_consumed = $true")
    create = text.index("& $OllamaExe create $ModelName")
    assert download < asset_hash < consumed < create
    assert 'Pinned Ollama asset SHA256 mismatch' in text

def test_curl_stderr_cannot_become_powershell_terminating_error():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "@(& $Curl.Source" not in text
    assert "2>&1" not in text[text.index("$Curl = Get-Command curl.exe"):text.index("$AssetSha = Get-Sha256File $Zip")]
    assert "$CurlRc = $CurlProc.ExitCode" in text

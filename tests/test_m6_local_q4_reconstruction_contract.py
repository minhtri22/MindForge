from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts/m6_local_q4_reconstruction_oneclick.ps1"
PREREG=ROOT/"artifacts/model-training-pipeline/m6/local_windows/q4_reconstruction/PREREGISTRATION.json"
PREFLIGHT_EVIDENCE=ROOT/"artifacts/model-training-pipeline/m6/local_windows/LOCAL_WINDOWS_PREFLIGHT_EXECUTION_EVIDENCE.json"

def test_local_preflight_admitted_exact_f16():
    data=json.loads(PREFLIGHT_EVIDENCE.read_text(encoding="utf-8"))
    assert data["verdict"]=="PASS"
    assert data["classification"]=="LOCAL_F16_ADMITTED"
    assert data["admitted_f16"]["exact_identity"] is True
    assert data["q4"]["admitted"] is False
    assert data["governance"]["q4_reconstruction_authorization_consumed"] is False

def test_prereg_binds_frozen_reconstruction_contract():
    data=json.loads(PREREG.read_text(encoding="utf-8"))
    assert data["status"]=="FROZEN_PREOUTCOME"
    assert data["authorization_commit"]=="9506e5fc205e641aba942a0bc9ff2fbaa7d881a5"
    assert data["runtime"]["llama_cpp_commit"]=="ce8caa6e60a03093351d6016a818720e0d46f0fb"
    assert data["runtime"]["quantization_type"]=="Q4_K_M"
    assert data["execution_contract"]["reconstruction_attempts_authorized"]==1
    assert data["execution_contract"]["rerun_until_match"] is False

def test_script_has_exact_f16_q4_and_source_identities():
    text=SCRIPT.read_text(encoding="utf-8")
    for value in [
      "437c300945705b9a255322366eab3017e890ac6d997716eb7d1351b2e76f4d4b",
      "ca9ac3104fa025619f34eaf941f4bac95787cc4aba2818d3e972766bc02cb977",
      "ce8caa6e60a03093351d6016a818720e0d46f0fb",
      "Q4_K_M",
      "9506e5fc205e641aba942a0bc9ff2fbaa7d881a5",
    ]:
      assert value in text

def test_script_builds_fresh_quantizer_and_does_not_run_science():
    text=SCRIPT.read_text(encoding="utf-8")
    assert '"--target","llama-quantize"' in text
    assert 'executable_sha_policy="venue_specific_record_only"' in text
    forbidden=["llama-cli.exe","ollama create","ollama run","ollama pull","/api/chat","fixture_evaluation_executed=$true","scientific_adjudication_executed=$true"]
    lower=text.lower()
    for item in forbidden:
      assert item.lower() not in lower

def test_attempt_consumed_immediately_before_quantizer():
    text=SCRIPT.read_text(encoding="utf-8")
    consumed=text.index("$Report.authorization_consumed=$true")
    started=text.index("$Report.reconstruction_started=$true")
    invoke=text.index('& $Quant $SelectedF16.path $Output "Q4_K_M"')
    assert consumed < started < invoke

def test_mismatch_output_is_deleted_and_not_scientific_fail():
    text=SCRIPT.read_text(encoding="utf-8")
    assert 'RECONSTRUCTION_IDENTITY_MISMATCH' in text
    assert 'Remove-Item -Force $Output' in text
    assert 'scientific_adjudication_executed=$false' in text

def test_no_ollama_execution_in_reconstruction_package():
    text=SCRIPT.read_text(encoding="utf-8").lower()
    assert "ollama.exe" not in text
    assert "ollama serve" not in text


def test_cmake_has_visual_studio_fallback_before_attempt():
    text=SCRIPT.read_text(encoding="utf-8")
    assert "vswhere.exe" in text
    assert "VISUAL_STUDIO_VSWHERE" in text
    assert "Common7\\\\IDE\\\\CommonExtensions\\\\Microsoft\\\\CMake\\\\CMake\\\\bin\\\\cmake.exe" in text
    fallback=text.index("vswhere.exe")
    consumed=text.index("$Report.authorization_consumed=$true")
    assert fallback < consumed


def test_missing_cmake_remains_pre_attempt_infrastructure_failure():
    text=SCRIPT.read_text(encoding="utf-8")
    assert 'throw "cmake not found in PATH or Visual Studio CMake discovery"' in text
    cmake_fail=text.index('throw "cmake not found in PATH or Visual Studio CMake discovery"')
    consumed=text.index("$Report.authorization_consumed=$true")
    assert cmake_fail < consumed

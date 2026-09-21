"""F16-only requalification after the bounded M2 tokenizer export repair.

This harness intentionally never invokes llama-quantize. A PASS only authorizes a
later, separately-governed quantization qualification.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from pipeline.canonical import sha256_file, sha256_object
from pipeline.errors import PipelineError
from pipeline.io import atomic_write_json, atomic_write_text
from pipeline.loader import load_experiment_config, load_model_profile
from pipeline.m2 import run_m2_qualification
from pipeline.m5 import (
    absolute_preserving_symlink,
    build_gguf_manifest,
    evaluate_runtime_parity,
    qualify_reasoning_runtime_mapping,
    run_hf_fixture,
    run_llama_fixture,
    verify_llama_cpp_lock,
)


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def _run(
    command: list[str],
    *,
    cwd: Path | None = None,
) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "return_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "combined": completed.stdout + completed.stderr,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True)
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--runs-root", required=True)
    parser.add_argument("--llama-source", required=True)
    parser.add_argument("--llama-cli", required=True)
    parser.add_argument("--llama-quantize", required=True)
    parser.add_argument("--converter-python", required=True)
    parser.add_argument("--build-manifest", required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    repo_root = Path(args.workspace).resolve()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = (repo_root / config_path).resolve()
    runs_root = Path(args.runs_root)
    if not runs_root.is_absolute():
        runs_root = (repo_root / runs_root).absolute()

    llama_source = Path(args.llama_source).resolve()
    llama_cli = Path(args.llama_cli).resolve()
    llama_quantize = Path(args.llama_quantize).resolve()
    converter_python = absolute_preserving_symlink(args.converter_python)
    build_manifest = Path(args.build_manifest).resolve()

    m5_1 = _read(
        repo_root / "artifacts/model-training-pipeline/m5_1/M5_1_RESULT_EVIDENCE.json"
    )
    adjudication = m5_1.get("adjudication", {})
    if adjudication.get("case") != "A_FAIL_B_PASS":
        raise RuntimeError("M5.1 does not authorize M2 tokenizer export repair")
    if adjudication.get("mechanism") != "M2_CANONICAL_TOKENIZER_EXPORT_FIDELITY_DEFECT":
        raise RuntimeError("unexpected M5.1 mechanism")
    if m5_1.get("boundaries", {}).get("quantization_authorized") is not False:
        raise RuntimeError("M5.1 boundary is not frozen with quantization disabled")

    config = load_experiment_config(config_path, repo_root)
    profile = load_model_profile(config, repo_root)
    lock = _read(repo_root / "docs/model-training-pipeline/runtime/llama_cpp.lock.json")
    if str(config.export["gguf"]["high_fidelity"]).lower() != "f16":
        raise RuntimeError("bounded repair requalification requires f16")
    if lock.get("high_fidelity_policy") != "f16":
        raise RuntimeError("runtime lock high-fidelity policy drifted from f16")
    if lock.get("commit_sha") != m5_1["frozen_runtime"]["llama_cpp_commit"]:
        raise RuntimeError("llama.cpp commit changed after M5.1")
    if lock["converter"]["git_blob_sha1"] != m5_1["frozen_runtime"]["converter_git_blob_sha1"]:
        raise RuntimeError("converter blob changed after M5.1")

    lock_evidence = verify_llama_cpp_lock(
        lock=lock,
        source_dir=llama_source,
        llama_cli=llama_cli,
        llama_quantize=llama_quantize,
        converter_python=converter_python,
        build_manifest=build_manifest,
    )

    m2 = run_m2_qualification(config_path, repo_root, runs_root)
    canonical_hf = m2.run_dir / "canonical_hf"
    m2_adjudication = _read(m2.run_dir / "m2/m2_adjudication.json")
    fidelity_gate = m2_adjudication["gates"].get("canonical_tokenizer_source_fidelity")
    if not isinstance(fidelity_gate, dict) or fidelity_gate.get("pass") is not True:
        raise RuntimeError("repaired M2 canonical tokenizer fidelity gate is not PASS")

    final_phase = config.phases[-1].id
    resumed = _read(m2.run_dir / "m2/phases" / final_phase / "resumed/result.json")
    canonical = resumed.get("canonical")
    if not isinstance(canonical, dict):
        raise RuntimeError("M2 final phase lacks canonical evidence")

    expected_source_hash = m5_1["arm_B"]["tokenizer_asset_manifest_hash"]
    if canonical.get("tokenizer_asset_manifest_hash") != expected_source_hash:
        raise RuntimeError(
            "repaired canonical tokenizer manifest does not equal M5.1 pinned-source arm"
        )
    if canonical.get("tokenizer_source_preserved_exactly") is not True:
        raise RuntimeError("M2 did not attest exact tokenizer-source preservation")

    output_dir = m2.run_dir / "m5_f16_requalification"
    output_dir.mkdir(parents=True, exist_ok=False)
    atomic_write_json(output_dir / "llama_cpp_lock_evidence.json", lock_evidence)

    converter = llama_source / lock["converter"]["path"]
    capability = _run(
        [str(converter_python), str(converter), "--print-supported-models"],
        cwd=llama_source,
    )
    required_arch = lock["converter"]["required_supported_architecture"]
    capability_pass = capability["return_code"] == 0 and required_arch in capability["combined"]
    atomic_write_text(output_dir / "converter_supported_models.txt", capability["combined"])

    cli_version = _run([str(llama_cli), "--version"])
    cli_help = _run([str(llama_cli), "--help"])
    required_flags = ("--no-display-prompt", "--simple-io", "--log-disable")
    cli_pass = (
        cli_version["return_code"] == 0
        and cli_help["return_code"] == 0
        and all(flag in cli_help["combined"] for flag in required_flags)
    )
    atomic_write_text(output_dir / "llama_cli_version.txt", cli_version["combined"])

    hf_baseline = run_hf_fixture(
        canonical_hf=canonical_hf,
        fixture_path=repo_root / config.fixture_set,
        inference=config.inference,
    )
    atomic_write_json(output_dir / "hf_baseline.json", hf_baseline)

    gguf_path = output_dir / "model-f16.gguf"
    conversion = _run(
        [
            str(converter_python),
            str(converter),
            str(canonical_hf),
            "--outtype",
            "f16",
            "--outfile",
            str(gguf_path),
        ],
        cwd=llama_source,
    )
    conversion_pass = (
        conversion["return_code"] == 0
        and gguf_path.is_file()
        and gguf_path.stat().st_size > 0
    )
    atomic_write_text(output_dir / "conversion_f16.log", conversion["combined"])

    manifest: dict[str, Any] | None = None
    runtime: dict[str, Any] | None = None
    parity: dict[str, Any] | None = None
    runtime_error: dict[str, str] | None = None
    reasoning_mapping: dict[str, Any] | None = None

    if conversion_pass:
        manifest = build_gguf_manifest(gguf_path, "f16")
        atomic_write_json(output_dir / "manifest_f16.json", manifest)
        try:
            runtime = run_llama_fixture(
                llama_cli=llama_cli,
                model_path=gguf_path,
                hf_baseline=hf_baseline,
                inference=config.inference,
            )
            parity = evaluate_runtime_parity(hf_baseline, runtime)
            atomic_write_json(output_dir / "runtime_f16.json", runtime)
            atomic_write_json(output_dir / "parity_f16.json", parity)
            if parity["pass"]:
                reasoning_mapping = qualify_reasoning_runtime_mapping(
                    profile=profile,
                    repo_root=repo_root,
                    artifact_hash=manifest["aggregate_hash"],
                )
                atomic_write_json(
                    output_dir / "reasoning_runtime_mapping.json", reasoning_mapping
                )
        except PipelineError as error:
            runtime_error = {
                "error_type": type(error).__name__,
                "error_code": error.code,
                "error": str(error),
            }

    parity_pass = bool(parity and parity.get("pass") is True)
    reasoning_pass = bool(reasoning_mapping and reasoning_mapping.get("pass") is True)

    gates = {
        "m5_1_mechanism_authorizes_m2_repair": True,
        "m2_pass": m2.status == "PASS",
        "m2_canonical_tokenizer_source_fidelity": fidelity_gate.get("pass") is True,
        "m2_tokenizer_manifest_equals_m5_1_source_arm": (
            canonical.get("tokenizer_asset_manifest_hash") == expected_source_hash
        ),
        "llama_cpp_exact_lock": (
            lock_evidence["source_commit_match"] is True
            and lock_evidence["converter_blob_match"] is True
        ),
        "converter_capability_qwen2": capability_pass,
        "real_llama_cli_binary": cli_pass,
        "f16_conversion": conversion_pass,
        "f16_real_inference": bool(runtime and runtime.get("all_outputs_nonempty") is True),
        "f16_hf_llama_task_format_parity": parity_pass,
        "reasoning_runtime_mapping": reasoning_pass,
        "quantization_not_executed": True,
        "bulk_training_not_started": m2.public_bulk_download_started is False,
    }
    failed = [name for name, passed in gates.items() if not passed]
    pass_f16 = not failed

    result = {
        "schema": "mindforge-model-pipeline-m5-f16-requalification-v1",
        "status": "PASS" if pass_f16 else "FAIL",
        "m5_status": (
            "HIGH_FIDELITY_PASS_QUANTIZATION_NOT_EXECUTED"
            if pass_f16
            else "OPEN_HIGH_FIDELITY_FAIL"
        ),
        "m5_1_result_hash": m5_1["diagnostic"]["result_hash"],
        "m2": {
            "run_id": m2.run_id,
            "canonical_directory_hash": m2.canonical_directory_hash,
            "adjudication_hash": m2.adjudication_hash,
            "tokenizer_asset_manifest_hash": canonical["tokenizer_asset_manifest_hash"],
            "tokenizer_source_revision": canonical["tokenizer_source_snapshot_revision"],
            "tokenizer_source_preserved_exactly": canonical[
                "tokenizer_source_preserved_exactly"
            ],
        },
        "llama_cpp": {
            "commit": lock["commit_sha"],
            "converter_git_blob_sha1": lock["converter"]["git_blob_sha1"],
            "converter_sha256": sha256_file(converter),
            "llama_cli_sha256": sha256_file(llama_cli),
        },
        "conversion": {
            "return_code": conversion["return_code"],
            "pass": conversion_pass,
            "artifact_manifest": manifest,
        },
        "runtime": runtime,
        "runtime_error": runtime_error,
        "parity": parity,
        "reasoning_runtime_mapping": reasoning_mapping,
        "gates": {name: {"required": True, "pass": bool(value)} for name, value in gates.items()},
        "failed_required_gates": failed,
        "quantization_executed": False,
        "quantization_authorized": pass_f16,
        "m6_authorized": False,
        "bulk_training_authorized": False,
    }
    result_hash = sha256_object(result)
    result["result_hash"] = result_hash
    atomic_write_json(output_dir / "M5_F16_REQUALIFICATION_RESULT.json", result)

    # Preserve hashes/evidence, but do not retain the ~1 GB GGUF in the workflow workspace.
    if gguf_path.exists():
        gguf_path.unlink()

    if args.as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"M5 F16 requalification: {result['status']}")
        print(f"quantization_authorized={result['quantization_authorized']}")
        print(f"result_hash={result_hash}")

    return 0 if pass_f16 else 2


if __name__ == "__main__":
    raise SystemExit(main())

"""M5Q Q8_0-only quantization qualification.

This module implements one separately governed quantization target. It never
selects targets from the general M5 config and never opens downstream runtime
stages. The qualified F16 parent is regenerated and identity-checked before
Q8_0 is allowed to execute.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Mapping

from .canonical import sha256_file, sha256_object
from .errors import PipelineError, RuntimeParityError
from .io import atomic_write_json, atomic_write_text
from .loader import load_experiment_config, load_model_profile
from .m2 import run_m2_qualification
from .m5 import (
    absolute_preserving_symlink,
    build_gguf_manifest,
    qualify_reasoning_runtime_mapping,
    run_hf_fixture,
    run_llama_fixture,
    verify_llama_cpp_lock,
)

Q8_TARGET_KEY = "q8_0"
Q8_QUANTIZER_TYPE = "Q8_0"
PREREG_PATH = Path("artifacts/model-training-pipeline/m5_quantization/PREREGISTRATION.json")


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeParityError(f"expected JSON object: {path}")
    return value


def load_q8_contract(repo_root: Path) -> dict[str, Any]:
    contract = _read_object(repo_root / PREREG_PATH)
    if contract.get("schema") != "mindforge-model-pipeline-m5-quantization-preregistration-v1":
        raise RuntimeParityError("M5Q preregistration schema mismatch")
    if contract.get("status") != "OPEN_SPECIFICATION_ONLY":
        raise RuntimeParityError("M5Q preregistration status drifted")
    parent = contract.get("parent", {})
    if parent.get("f16_status") != "PASS_CLOSED":
        raise RuntimeParityError("M5Q parent F16 is not PASS_CLOSED")
    targets = contract.get("claim_scope", {}).get("targets", [])
    order = contract.get("target_order", {}).get("execution_order", [])
    if not targets or targets[0] != Q8_TARGET_KEY:
        raise RuntimeParityError("Q8_0 is not the first frozen M5Q target")
    if not order or order[0] != Q8_TARGET_KEY:
        raise RuntimeParityError("Q8_0 execution order drifted")
    boundary = contract.get("downstream_boundary", {})
    if boundary.get("m6_authorized_by_target_pass") is not False:
        raise RuntimeParityError("M5Q downstream boundary no longer blocks M6")
    if boundary.get("m6_auto_open") is not False:
        raise RuntimeParityError("M5Q downstream boundary allows automatic M6 open")
    return contract


def build_q8_quantize_command(
    llama_quantize: Path,
    source_f16: Path,
    output_q8: Path,
) -> list[str]:
    return [
        str(llama_quantize),
        str(source_f16),
        str(output_q8),
        Q8_QUANTIZER_TYPE,
    ]


def evaluate_quantized_preservation(
    f16_runtime: Mapping[str, Any],
    q8_runtime: Mapping[str, Any],
) -> dict[str, Any]:
    f16_vector = list(f16_runtime["task_vector"])
    q8_vector = list(q8_runtime["task_vector"])
    format_parity = bool(f16_runtime["all_outputs_nonempty"]) and bool(
        q8_runtime["all_outputs_nonempty"]
    )
    passed = (
        format_parity
        and f16_vector == q8_vector
        and float(f16_runtime["accuracy"]) == float(q8_runtime["accuracy"])
    )
    return {
        "pass": passed,
        "comparator": "qualified_f16_parent",
        "f16_task_vector": f16_vector,
        "q8_task_vector": q8_vector,
        "f16_accuracy": f16_runtime["accuracy"],
        "q8_accuracy": q8_runtime["accuracy"],
        "format_parity": format_parity,
        "exact_text_required": False,
        "absolute_capability_claimed": False,
    }


def total_manifest_size(manifest: Mapping[str, Any]) -> int:
    return sum(int(row["size"]) for row in manifest.get("files", []))


def _run_capture(command: list[str], *, cwd: Path | None = None) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "return_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "combined": completed.stdout
        + ("\n" if completed.stdout and completed.stderr else "")
        + completed.stderr,
        "command_hash": sha256_object(command),
    }


def run_q8_qualification(
    config_path: str | Path,
    repo_root: str | Path,
    runs_root: str | Path,
    *,
    llama_source: str | Path,
    llama_cli: str | Path,
    llama_quantize: str | Path,
    converter_python: str | Path,
    build_manifest: str | Path,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    config_path = Path(config_path)
    if not config_path.is_absolute():
        config_path = (repo_root / config_path).resolve()
    runs_root = Path(runs_root)
    if not runs_root.is_absolute():
        runs_root = (repo_root / runs_root).resolve()

    llama_source = Path(llama_source).resolve()
    llama_cli = Path(llama_cli).resolve()
    llama_quantize = Path(llama_quantize).resolve()
    converter_python = absolute_preserving_symlink(converter_python)
    build_manifest = Path(build_manifest).resolve()

    contract = load_q8_contract(repo_root)
    frozen = contract["frozen_inputs"]
    parent = contract["parent"]
    comparator = contract["comparison_contract"]

    config = load_experiment_config(config_path, repo_root)
    profile = load_model_profile(config, repo_root)
    if config.model.id != frozen["model_id"]:
        raise RuntimeParityError("M5Q model id drifted")
    if config.model.revision != frozen["model_revision"]:
        raise RuntimeParityError("M5Q model revision drifted")
    if config.fixture_set != frozen["fixture_set"]:
        raise RuntimeParityError("M5Q fixture set drifted")
    if str(config.export["gguf"]["high_fidelity"]).lower() != "f16":
        raise RuntimeParityError("M5Q requires the frozen F16 parent dtype")

    for name in (
        "max_new_tokens",
        "temperature",
        "top_p",
        "top_k",
        "seed",
        "context_length",
    ):
        if config.inference[name] != frozen["inference"][name]:
            raise RuntimeParityError(f"M5Q inference contract drifted: {name}")

    lock = _read_object(repo_root / "docs/model-training-pipeline/runtime/llama_cpp.lock.json")
    if lock.get("commit_sha") != frozen["llama_cpp_commit"]:
        raise RuntimeParityError("M5Q llama.cpp commit drifted")
    if lock.get("converter", {}).get("git_blob_sha1") != frozen["converter_git_blob_sha1"]:
        raise RuntimeParityError("M5Q converter identity drifted")

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
    if m2.status != "PASS" or not canonical_hf.is_dir():
        raise RuntimeParityError("M5Q could not regenerate qualified canonical HF")

    output_dir = m2.run_dir / "m5q_q8_0"
    output_dir.mkdir(parents=True, exist_ok=False)
    atomic_write_json(output_dir / "llama_cpp_lock_evidence.json", lock_evidence)

    hf_baseline = run_hf_fixture(
        canonical_hf=canonical_hf,
        fixture_path=repo_root / config.fixture_set,
        inference=config.inference,
    )
    atomic_write_json(output_dir / "hf_prompt_source.json", hf_baseline)

    converter = llama_source / lock["converter"]["path"]
    f16_path = output_dir / "model-f16.gguf"
    f16_conversion = _run_capture(
        [
            str(converter_python),
            str(converter),
            str(canonical_hf),
            "--outtype",
            "f16",
            "--outfile",
            str(f16_path),
        ],
        cwd=llama_source,
    )
    atomic_write_text(output_dir / "conversion_f16.log", f16_conversion["combined"])
    if (
        f16_conversion["return_code"] != 0
        or not f16_path.is_file()
        or f16_path.stat().st_size <= 0
    ):
        raise RuntimeParityError("M5Q could not regenerate the F16 parent artifact")

    f16_manifest = build_gguf_manifest(f16_path, "f16")
    atomic_write_json(output_dir / "manifest_f16_parent.json", f16_manifest)
    if sha256_file(f16_path) != parent["f16_artifact_sha256"]:
        raise RuntimeParityError("M5Q regenerated F16 SHA256 differs from frozen parent")
    if f16_manifest["aggregate_hash"] != parent["f16_artifact_manifest_hash"]:
        raise RuntimeParityError("M5Q regenerated F16 manifest differs from frozen parent")

    f16_runtime = run_llama_fixture(
        llama_cli=llama_cli,
        model_path=f16_path,
        hf_baseline=hf_baseline,
        inference=config.inference,
    )
    atomic_write_json(output_dir / "runtime_f16_parent.json", f16_runtime)
    if list(f16_runtime["task_vector"]) != list(comparator["f16_task_vector"]):
        raise RuntimeParityError("M5Q F16 parent task vector drifted")
    if float(f16_runtime["accuracy"]) != float(comparator["f16_accuracy"]):
        raise RuntimeParityError("M5Q F16 parent accuracy drifted")

    q8_path = output_dir / "model-q8_0.gguf"
    quantize_command = build_q8_quantize_command(llama_quantize, f16_path, q8_path)
    quantization = _run_capture(quantize_command)
    atomic_write_text(output_dir / "quantization_q8_0.log", quantization["combined"])

    quantization_pass = (
        quantization["return_code"] == 0
        and q8_path.is_file()
        and q8_path.stat().st_size > 0
    )
    q8_manifest: dict[str, Any] | None = None
    q8_runtime: dict[str, Any] | None = None
    preservation: dict[str, Any] | None = None
    reasoning_mapping: dict[str, Any] | None = None
    runtime_error: dict[str, str] | None = None

    if quantization_pass:
        q8_manifest = build_gguf_manifest(q8_path, Q8_TARGET_KEY)
        atomic_write_json(output_dir / "manifest_q8_0.json", q8_manifest)
        try:
            q8_runtime = run_llama_fixture(
                llama_cli=llama_cli,
                model_path=q8_path,
                hf_baseline=hf_baseline,
                inference=config.inference,
            )
            atomic_write_json(output_dir / "runtime_q8_0.json", q8_runtime)
            preservation = evaluate_quantized_preservation(f16_runtime, q8_runtime)
            atomic_write_json(output_dir / "preservation_q8_0.json", preservation)
            if preservation["pass"]:
                reasoning_mapping = qualify_reasoning_runtime_mapping(
                    profile=profile,
                    repo_root=repo_root,
                    artifact_hash=q8_manifest["aggregate_hash"],
                )
                atomic_write_json(
                    output_dir / "reasoning_runtime_mapping_q8_0.json",
                    reasoning_mapping,
                )
        except PipelineError as error:
            runtime_error = {
                "error_type": type(error).__name__,
                "error_code": error.code,
                "error": str(error),
            }

    runtime_pass = bool(q8_runtime and q8_runtime.get("all_outputs_nonempty") is True)
    preservation_pass = bool(preservation and preservation.get("pass") is True)
    reasoning_pass = bool(reasoning_mapping and reasoning_mapping.get("pass") is True)
    smaller_than_f16 = bool(
        q8_manifest
        and total_manifest_size(q8_manifest) < total_manifest_size(f16_manifest)
    )

    gates = {
        "parent_f16_identity_exact": True,
        "llama_cpp_exact_lock": (
            lock_evidence["source_commit_match"] is True
            and lock_evidence["converter_blob_match"] is True
        ),
        "quantizer_target_exact": quantize_command[-1] == Q8_QUANTIZER_TYPE,
        "quantizer_return_code_zero": quantization["return_code"] == 0,
        "quantized_artifact_nonempty": bool(
            q8_manifest and total_manifest_size(q8_manifest) > 0
        ),
        "quantized_artifact_manifest_frozen": q8_manifest is not None,
        "real_llama_cli_load_and_infer": runtime_pass,
        "all_runtime_outputs_nonempty": runtime_pass,
        "task_vector_equals_f16_parent": bool(
            preservation
            and preservation["q8_task_vector"] == preservation["f16_task_vector"]
        ),
        "runtime_accuracy_equals_f16_parent": bool(
            preservation
            and float(preservation["q8_accuracy"])
            == float(preservation["f16_accuracy"])
        ),
        "format_parity_with_f16_parent": bool(
            preservation and preservation["format_parity"] is True
        ),
        "reasoning_runtime_mapping_pass": reasoning_pass,
        "artifact_smaller_than_f16": smaller_than_f16,
    }
    failed = [name for name, passed in gates.items() if not passed]

    if not quantization_pass:
        status = "FAIL_QUANTIZATION"
    elif not runtime_pass:
        status = "FAIL_RUNTIME"
    elif not preservation_pass:
        status = "FAIL_PRESERVATION"
    elif not reasoning_pass:
        status = "FAIL_REASONING_MAPPING"
    elif failed:
        status = "FAIL_PRESERVATION"
    else:
        status = "PASS"

    result = {
        "schema": "mindforge-model-pipeline-m5q-q8-qualification-v1",
        "program": "M5Q",
        "target": Q8_TARGET_KEY,
        "quantizer_type": Q8_QUANTIZER_TYPE,
        "status": status,
        "parent": {
            "m5_f16_closure_commit": parent["m5_f16_closure_commit"],
            "f16_result_hash": parent["f16_result_hash"],
            "f16_artifact_sha256": parent["f16_artifact_sha256"],
            "f16_artifact_manifest_hash": parent["f16_artifact_manifest_hash"],
        },
        "m2": {
            "run_id": m2.run_id,
            "canonical_directory_hash": m2.canonical_directory_hash,
            "adjudication_hash": m2.adjudication_hash,
        },
        "llama_cpp": {
            "commit": lock["commit_sha"],
            "converter_git_blob_sha1": lock["converter"]["git_blob_sha1"],
            "llama_cli_sha256": sha256_file(llama_cli),
            "llama_quantize_sha256": sha256_file(llama_quantize),
        },
        "f16_parent_manifest": f16_manifest,
        "f16_parent_runtime": {
            "task_vector": f16_runtime["task_vector"],
            "accuracy": f16_runtime["accuracy"],
            "all_outputs_nonempty": f16_runtime["all_outputs_nonempty"],
        },
        "quantization": {
            "executed": True,
            "target": Q8_TARGET_KEY,
            "quantizer_type": Q8_QUANTIZER_TYPE,
            "return_code": quantization["return_code"],
            "command_hash": quantization["command_hash"],
            "log_hash": sha256_object(quantization["combined"]),
            "artifact_manifest": q8_manifest,
        },
        "runtime": q8_runtime,
        "runtime_error": runtime_error,
        "preservation": preservation,
        "reasoning_runtime_mapping": reasoning_mapping,
        "gates": {
            name: {"required": True, "pass": bool(value)}
            for name, value in gates.items()
        },
        "failed_required_gates": failed,
        "absolute_capability_claimed": False,
        "q4_executed": False,
        "m6_authorized": False,
        "m6_auto_open": False,
        "bulk_training_authorized": False,
    }
    result_hash = sha256_object(result)
    result["result_hash"] = result_hash
    atomic_write_json(output_dir / "M5Q_Q8_QUALIFICATION_RESULT.json", result)

    if f16_path.exists():
        f16_path.unlink()
    if q8_path.exists():
        q8_path.unlink()

    return result

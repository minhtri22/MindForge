"""M6 Ollama packaging/runtime contract — zero-runtime implementation.

This module contains pure deterministic contract logic only. It MUST NOT invoke
an Ollama executable or perform network/runtime side effects.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping

M6_TARGET_KEY = "q4_k_m"
M6_QUANTIZER_TYPE = "Q4_K_M"
FROZEN_Q4_SHA256 = "ca9ac3104fa025619f34eaf941f4bac95787cc4aba2818d3e972766bc02cb977"
FROZEN_Q4_MANIFEST = "e47700cab51bcf82174aa437ed767032f7ff29e3e1594690f5b9ff91e4762e0b"
FROZEN_Q4_SIZE = 397807456
FROZEN_TASK_VECTOR = [False, False]
FROZEN_ACCURACY = 0.0
OLLAMA_LOCK_PATH = Path("docs/model-training-pipeline/runtime/ollama.lock.json")

FROZEN_INFERENCE: dict[str, Any] = {
    "max_new_tokens": 128,
    "temperature": 0.0,
    "top_p": 1.0,
    "top_k": 0,
    "seed": 42,
    "context_length": 2048,
    "stream": False,
}


class M6ContractError(ValueError):
    """Raised when a zero-runtime M6 contract is violated."""


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_ollama_lock(path: str | Path) -> dict[str, Any]:
    lock = json.loads(Path(path).read_text(encoding="utf-8"))
    if lock.get("schema") != "mindforge-ollama-runtime-lock-v1":
        raise M6ContractError("Ollama lock schema mismatch")
    if lock.get("status") != "SPECIFICATION_LOCK_FOR_IMPLEMENTATION":
        raise M6ContractError("Ollama lock status mismatch")
    if lock.get("version") != "0.34.2" or lock.get("tag") != "v0.34.2":
        raise M6ContractError("Ollama exact version drifted")
    stage = lock.get("implementation_stage", {})
    forbidden = (
        "executable_invocation_authorized",
        "version_probe_authorized",
        "install_update_authorized",
        "download_authorized",
    )
    if any(stage.get(name) is not False for name in forbidden):
        raise M6ContractError("Ollama implementation-stage runtime boundary drifted")
    assets = lock.get("runtime_assets", {})
    for platform in ("windows_amd64", "linux_amd64"):
        digest = str(assets.get(platform, {}).get("digest", ""))
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
            raise M6ContractError(f"invalid pinned Ollama asset digest: {platform}")
    return lock


def verify_frozen_q4_identity(identity: Mapping[str, Any]) -> bool:
    return (
        identity.get("target_key") == M6_TARGET_KEY
        and identity.get("quantizer_type") == M6_QUANTIZER_TYPE
        and identity.get("sha256") == FROZEN_Q4_SHA256
        and identity.get("aggregate_manifest_hash") == FROZEN_Q4_MANIFEST
        and int(identity.get("size", -1)) == FROZEN_Q4_SIZE
    )


def _format_number(value: int | float) -> str:
    if isinstance(value, bool):
        raise M6ContractError("boolean is not a numeric Modelfile parameter")
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return format(value, ".15g")


def render_modelfile(
    *,
    gguf_filename: str = "model-q4_k_m.gguf",
    inference: Mapping[str, Any] = FROZEN_INFERENCE,
) -> str:
    if Path(gguf_filename).name != gguf_filename:
        raise M6ContractError("Modelfile GGUF source must be a basename")
    if not gguf_filename.endswith(".gguf"):
        raise M6ContractError("Modelfile source must be GGUF")

    required = dict(FROZEN_INFERENCE)
    actual = {name: inference.get(name) for name in required}
    if actual != required:
        raise M6ContractError("M6 inference contract drifted")

    # stream is request-layer behavior, not a Modelfile PARAMETER.
    lines = [
        f"FROM ./{gguf_filename}",
        f"PARAMETER num_ctx {_format_number(inference['context_length'])}",
        f"PARAMETER num_predict {_format_number(inference['max_new_tokens'])}",
        f"PARAMETER temperature {_format_number(inference['temperature'])}",
        f"PARAMETER top_p {_format_number(inference['top_p'])}",
        f"PARAMETER top_k {_format_number(inference['top_k'])}",
        f"PARAMETER seed {_format_number(inference['seed'])}",
    ]
    return "\n".join(lines) + "\n"


def modelfile_contract(
    *,
    gguf_filename: str = "model-q4_k_m.gguf",
) -> dict[str, Any]:
    text = render_modelfile(gguf_filename=gguf_filename)
    return {
        "schema": "mindforge-m6-modelfile-contract-v1",
        "target": M6_TARGET_KEY,
        "source_gguf": gguf_filename,
        "bytes_utf8": len(text.encode("utf-8")),
        "sha256": sha256_text(text),
        "text": text,
        "stream": False,
        "parameters_derived_from_frozen_inference": True,
        "independent_generation_defaults_added": False,
    }


_RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")


def ephemeral_model_name(run_id: str, artifact_sha256: str = FROZEN_Q4_SHA256) -> str:
    if not _RUN_ID_RE.fullmatch(run_id):
        raise M6ContractError("run_id is not safe for ephemeral Ollama namespace")
    if not re.fullmatch(r"[0-9a-f]{64}", artifact_sha256):
        raise M6ContractError("artifact SHA256 must be lowercase hex")
    return f"pipeline-test-{run_id.lower()}-{artifact_sha256[:12]}"


def ownership_manifest(run_id: str, model_name: str) -> dict[str, Any]:
    expected = ephemeral_model_name(run_id)
    if model_name != expected:
        raise M6ContractError("model name does not match owned ephemeral namespace")
    marker = sha256_text(f"{run_id}\n{model_name}\n{FROZEN_Q4_SHA256}\n")
    return {
        "schema": "mindforge-m6-ollama-ownership-v1",
        "run_id": run_id,
        "model_name": model_name,
        "artifact_sha256": FROZEN_Q4_SHA256,
        "ownership_marker": marker,
        "created_by_current_run": False,
        "cleanup_authorized": False,
    }


def mark_created(manifest: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(manifest)
    expected = ownership_manifest(str(result["run_id"]), str(result["model_name"]))
    if result.get("ownership_marker") != expected["ownership_marker"]:
        raise M6ContractError("ownership marker mismatch")
    result["created_by_current_run"] = True
    result["cleanup_authorized"] = True
    return result


def cleanup_is_authorized(model_name: str, manifest: Mapping[str, Any]) -> bool:
    if model_name != manifest.get("model_name"):
        return False
    try:
        expected = ownership_manifest(
            str(manifest.get("run_id", "")),
            str(manifest.get("model_name", "")),
        )
    except M6ContractError:
        return False
    return (
        manifest.get("ownership_marker") == expected["ownership_marker"]
        and manifest.get("created_by_current_run") is True
        and manifest.get("cleanup_authorized") is True
    )


def build_cleanup_command(
    ollama_executable: str,
    model_name: str,
    manifest: Mapping[str, Any],
) -> list[str]:
    if not cleanup_is_authorized(model_name, manifest):
        raise M6ContractError("cleanup refused for unowned Ollama model")
    return [ollama_executable, "rm", model_name]


def build_create_command(
    ollama_executable: str,
    model_name: str,
    modelfile_path: str | Path,
) -> list[str]:
    if not model_name.startswith("pipeline-test-"):
        raise M6ContractError("refusing create outside ephemeral namespace")
    return [ollama_executable, "create", model_name, "-f", str(modelfile_path)]


def reasoning_mapping(mode: str, *, supports_disable: bool = False) -> dict[str, Any]:
    if mode not in {"visible", "hidden", "off"}:
        raise M6ContractError("unknown reasoning mode")
    if mode == "visible":
        return {
            "mode": mode,
            "think": True,
            "postprocess_hide": False,
            "supported": True,
        }
    if mode == "hidden":
        return {
            "mode": mode,
            "think": True,
            "postprocess_hide": True,
            "supported": True,
        }
    return {
        "mode": mode,
        "think": False if supports_disable else None,
        "postprocess_hide": False,
        "supported": bool(supports_disable),
    }


def build_chat_request(
    model_name: str,
    prompt: str,
    *,
    reasoning_mode: str = "visible",
    supports_disable: bool = False,
) -> dict[str, Any]:
    if not model_name.startswith("pipeline-test-"):
        raise M6ContractError("chat model must be an M6 ephemeral model")
    mapping = reasoning_mapping(reasoning_mode, supports_disable=supports_disable)
    if not mapping["supported"]:
        raise M6ContractError("requested reasoning mode is unsupported")
    request = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {
            "num_ctx": FROZEN_INFERENCE["context_length"],
            "num_predict": FROZEN_INFERENCE["max_new_tokens"],
            "temperature": FROZEN_INFERENCE["temperature"],
            "top_p": FROZEN_INFERENCE["top_p"],
            "top_k": FROZEN_INFERENCE["top_k"],
            "seed": FROZEN_INFERENCE["seed"],
        },
        "think": mapping["think"],
    }
    return request


def evaluate_ollama_parity(
    llama_parent: Mapping[str, Any],
    ollama_runtime: Mapping[str, Any],
) -> dict[str, Any]:
    parent_vector = list(llama_parent["task_vector"])
    ollama_vector = list(ollama_runtime["task_vector"])
    format_parity = bool(llama_parent["all_outputs_nonempty"]) and bool(
        ollama_runtime["all_outputs_nonempty"]
    )
    passed = (
        format_parity
        and parent_vector == ollama_vector
        and float(llama_parent["accuracy"]) == float(ollama_runtime["accuracy"])
    )
    return {
        "pass": passed,
        "comparator": "frozen_m5_q4_llama_cpp_parent",
        "llama_parent_task_vector": parent_vector,
        "ollama_task_vector": ollama_vector,
        "llama_parent_accuracy": llama_parent["accuracy"],
        "ollama_accuracy": ollama_runtime["accuracy"],
        "format_parity": format_parity,
        "exact_text_required": False,
        "absolute_capability_claimed": False,
    }


def terminal_boundary() -> dict[str, bool]:
    return {
        "m7_authorized": False,
        "m7_auto_open": False,
        "bulk_training_authorized": False,
        "m6_pass_claim_authorized": False,
    }

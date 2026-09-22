from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

PROGRAM = "M6R2_PARITY_REPLICATION"
EXPECTED_OLLAMA_VERSION = "0.34.2"
EXPECTED_Q4_SIZE = 397_807_456
EXPECTED_Q4_SHA256 = "ca9ac3104fa025619f34eaf941f4bac95787cc4aba2818d3e972766bc02cb977"
EXPECTED_Q4_MANIFEST = "e47700cab51bcf82174aa437ed767032f7ff29e3e1594690f5b9ff91e4762e0b"
EXPECTED_MODELFILE_SHA256 = "5db25cbceaaa6b359b73f7edde1f54acb6a95f27a4803f5d28ad1b65012e1946"
EXPECTED_FIXTURE_BLOB = "450d83d38130765fe4a74fb18bab90177328218f"
EXPECTED_PROFILE_BLOB = "1214e551c250e73b7a8cbbde71201fdd17e49ae1"
EXPECTED_REASONING_BLOB = "3813ae3ff00a49f2f97ccbda7833e0bf299ff1e4"
FROZEN_PARENT_VECTOR = [False, False]
FROZEN_PARENT_ACCURACY = 0.0

SCIENCE_VERDICTS = {"PASS_PARITY", "FAIL_PARITY", "FAIL_REASONING_MAPPING"}
INFRA_STATES = {
    "BLOCKED_INFRA_BINDING",
    "INVALID_INFRA_PREOUTCOME",
    "INVALID_INFRA_POSTOUTCOME",
    "INVALID_PROVENANCE",
}


class ContractError(ValueError):
    pass


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def response_texts(response: Mapping[str, Any]) -> tuple[str, str]:
    message = response.get("message")
    if not isinstance(message, Mapping):
        return "", ""
    content = message.get("content")
    thinking = message.get("thinking")
    return (
        content if isinstance(content, str) else "",
        thinking if isinstance(thinking, str) else "",
    )


def response_exposes_outcome(response: Mapping[str, Any]) -> bool:
    content, thinking = response_texts(response)
    return _nonempty(content) or _nonempty(thinking)


def validate_owrq_binding(binding: Mapping[str, Any]) -> Dict[str, Any]:
    if binding.get("schema") != "mindforge-owrq-qualified-runtime-scope-v1":
        raise ContractError("unexpected OWRQ qualification schema")
    if binding.get("status") != "QUALIFIED_RUNTIME_SCOPE":
        raise ContractError("OWRQ scope is not qualified")

    runtime = binding.get("runtime")
    environment = binding.get("runtime_environment")
    target = binding.get("target_scope")
    adapter = binding.get("adapter")
    api = binding.get("api_contract")

    for name, obj in [
        ("runtime", runtime),
        ("runtime_environment", environment),
        ("target_scope", target),
        ("adapter", adapter),
        ("api_contract", api),
    ]:
        if not isinstance(obj, Mapping):
            raise ContractError(f"missing binding object: {name}")

    if runtime.get("ollama_version") != EXPECTED_OLLAMA_VERSION:
        raise ContractError("Ollama version is outside M6R2 qualified scope")
    if not _nonempty(runtime.get("ollama_executable_sha256")):
        raise ContractError("missing ollama executable SHA256")
    if not _nonempty(runtime.get("ollama_executable_path")):
        raise ContractError("missing qualified ollama executable path")
    if environment.get("OLLAMA_KV_CACHE_TYPE") != "f16":
        raise ContractError("qualified runtime must bind OLLAMA_KV_CACHE_TYPE=f16")
    if environment.get("OLLAMA_FLASH_ATTENTION_forced") is not False:
        raise ContractError("M6R2 may not bind a qualification that forces flash attention")
    if not _nonempty(target.get("local_machine_fingerprint_sha256")):
        raise ContractError("missing local target fingerprint")
    if not _nonempty(adapter.get("runtime_adapter_git_blob_sha1")):
        raise ContractError("missing qualified runtime adapter blob")
    if not _nonempty(api.get("host")):
        raise ContractError("missing qualified API host")
    if api.get("chat_endpoint") != "/api/chat":
        raise ContractError("unexpected chat API contract")

    return {
        "qualification_sha256": binding.get("qualification_sha256"),
        "ollama_version": runtime["ollama_version"],
        "ollama_executable_path": runtime["ollama_executable_path"],
        "ollama_executable_sha256": runtime["ollama_executable_sha256"],
        "runtime_adapter_git_blob_sha1": adapter["runtime_adapter_git_blob_sha1"],
        "local_machine_fingerprint_sha256": target["local_machine_fingerprint_sha256"],
        "host": api["host"],
        "kv_cache_type": environment["OLLAMA_KV_CACHE_TYPE"],
        "flash_attention_forced": environment["OLLAMA_FLASH_ATTENTION_forced"],
    }


def row_from_response(task: Mapping[str, Any], response: Mapping[str, Any]) -> Dict[str, Any]:
    content, thinking = response_texts(response)
    format_valid = _nonempty(content) and all(ord(ch) >= 9 for ch in content)
    expected = str(task["expected"]).strip()
    success = content.strip() == expected
    return {
        "id": str(task["id"]),
        "type": str(task["type"]),
        "expected": str(task["expected"]),
        "output": content,
        "native_thinking": thinking,
        "format_valid": format_valid,
        "task_success": success,
        "outcome_exposed": response_exposes_outcome(response),
    }


def adjudicate_completed_rows(rows: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    if len(rows) != 2:
        raise ContractError("M6R2 frozen eval_v1 requires exactly two completed rows")

    exposed = any(bool(r.get("outcome_exposed")) for r in rows)
    if not exposed:
        raise ContractError("completed scientific adjudication requires outcome exposure")

    all_outputs_nonempty = all(_nonempty(r.get("output")) and bool(r.get("format_valid")) for r in rows)
    unexpected_native_thinking = any(_nonempty(r.get("native_thinking")) for r in rows)
    task_vector = [bool(r.get("task_success")) for r in rows]
    accuracy = sum(1 for x in task_vector if x) / len(task_vector)
    vector_match = task_vector == FROZEN_PARENT_VECTOR
    accuracy_match = abs(accuracy - FROZEN_PARENT_ACCURACY) < 1e-12
    format_parity = all_outputs_nonempty

    if unexpected_native_thinking:
        verdict = "FAIL_REASONING_MAPPING"
    elif not all_outputs_nonempty or not vector_match or not accuracy_match or not format_parity:
        verdict = "FAIL_PARITY"
    else:
        verdict = "PASS_PARITY"

    return {
        "program": PROGRAM,
        "attempt_consumed": True,
        "scientific_verdict": verdict,
        "task_vector": task_vector,
        "accuracy": accuracy,
        "all_outputs_nonempty": all_outputs_nonempty,
        "task_vector_match": vector_match,
        "accuracy_match": accuracy_match,
        "format_parity": format_parity,
        "reasoning_runtime_mapping_pass": not unexpected_native_thinking,
        "unexpected_nonempty_native_thinking": unexpected_native_thinking,
    }


def classify_failure(*, outcome_exposed: bool, positive_infra_failure: bool, binding_failed: bool = False) -> Dict[str, Any]:
    if binding_failed:
        return {
            "classification": "BLOCKED_INFRA_BINDING",
            "attempt_consumed": False,
            "scientific_fail": False,
        }
    if outcome_exposed:
        return {
            "classification": "INVALID_INFRA_POSTOUTCOME",
            "attempt_consumed": True,
            "scientific_fail": False,
        }
    if positive_infra_failure:
        return {
            "classification": "INVALID_INFRA_PREOUTCOME",
            "attempt_consumed": False,
            "scientific_fail": False,
        }
    return {
        "classification": "INVALID_PROVENANCE",
        "attempt_consumed": False,
        "scientific_fail": False,
    }


def scan_prior_outcome_directory(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"outcome_exposed": False, "ambiguous_pending_request": False, "responses": 0}

    responses = 0
    exposed = False
    starts: set[str] = set()
    terminals: set[str] = set()

    for p in sorted(path.glob("request-*-start.json")):
        starts.add(p.name.removesuffix("-start.json"))
    for p in sorted(path.glob("request-*-complete-no-response.json")):
        terminals.add(p.name.removesuffix("-complete-no-response.json"))
    for p in sorted(path.glob("request-*-response.json")):
        key = p.name.removesuffix("-response.json")
        terminals.add(key)
        data = json.loads(p.read_text(encoding="utf-8"))
        responses += 1
        if response_exposes_outcome(data):
            exposed = True

    ambiguous = bool(starts - terminals)
    return {
        "outcome_exposed": exposed,
        "ambiguous_pending_request": ambiguous,
        "responses": responses,
    }


def _load(path: str) -> Mapping[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    vb = sub.add_parser("verify-binding")
    vb.add_argument("path")

    sp = sub.add_parser("scan-prior")
    sp.add_argument("path")

    ar = sub.add_parser("adjudicate-rows")
    ar.add_argument("path")

    args = parser.parse_args()
    if args.cmd == "verify-binding":
        print(json.dumps(validate_owrq_binding(_load(args.path)), sort_keys=True))
    elif args.cmd == "scan-prior":
        print(json.dumps(scan_prior_outcome_directory(Path(args.path)), sort_keys=True))
    elif args.cmd == "adjudicate-rows":
        data = _load(args.path)
        rows = data["rows"]
        print(json.dumps(adjudicate_completed_rows(rows), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
